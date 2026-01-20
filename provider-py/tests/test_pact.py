"""
Pact Provider Verification Tests

This test verifies that the Python Provider (RiskAlgoService) 
fulfills all contracts published by consumers.

Run with: pytest tests/test_pact.py -v
"""

import pytest
import json
import requests
import subprocess
from pathlib import Path

# Configuration
PROVIDER_URL = "http://localhost:7001"
PROJECT_ROOT = Path(__file__).parent.parent.parent
PACTS_DIR = PROJECT_ROOT / "pacts"
CONSUMER_DIR = PROJECT_ROOT / "consumer-ts"


class TestProviderContract:
    """Provider contract verification test suite."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup before each test - ensure provider is running."""
        try:
            response = requests.get(f"{PROVIDER_URL}/health", timeout=2)
            if response.status_code != 200:
                pytest.skip("Provider not healthy")
        except requests.exceptions.ConnectionError:
            pytest.skip("Provider not running - start with 'python app.py'")
    
    def test_clear_and_regenerate_contracts(self):
        """Step 1: Clear old pacts and regenerate fresh contracts."""
        # Clear old pact files
        for pact_file in PACTS_DIR.glob("*.json"):
            if not pact_file.name.startswith("."):
                pact_file.unlink()
        
        # Regenerate contracts by running consumer tests
        result = subprocess.run(
            ["npm", "test"],
            cwd=CONSUMER_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode == 0, f"Consumer tests failed: {result.stderr[-500:]}"
        
        # Verify pact file was generated
        pact_files = list(PACTS_DIR.glob("*.json"))
        assert len(pact_files) > 0, "No pact files generated"
        print(f"\n✅ Generated {len(pact_files)} fresh pact file(s)")
    
    def test_provider_health_check(self):
        """Verify provider health endpoint."""
        response = requests.get(f"{PROVIDER_URL}/health", timeout=5)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "RiskAlgoService"
        print("\n✅ Provider health check passed")
    
    def test_provider_satisfies_contract(self):
        """
        Main contract verification test.
        
        Verifies that the Provider satisfies all Consumer contracts by:
        1. Reading the Pact JSON from ../pacts/
        2. Replaying each interaction against the running Flask app
        3. Failing if any response doesn't match the contract
        """
        pact_files = [f for f in PACTS_DIR.glob("*.json") if not f.name.startswith(".")]
        
        if not pact_files:
            pytest.skip("No pact files found - run consumer tests first")
        
        total_interactions = 0
        passed_interactions = 0
        failures = []
        
        for pact_file in pact_files:
            print(f"\n📄 Verifying: {pact_file.name}")
            
            with open(pact_file) as f:
                pact = json.load(f)
            
            for interaction in pact.get("interactions", []):
                total_interactions += 1
                description = interaction["description"]
                
                success, message = self._verify_interaction(interaction)
                
                if success:
                    passed_interactions += 1
                    print(f"  ✅ {description}")
                else:
                    failures.append((description, message))
                    print(f"  ❌ {description}: {message}")
        
        # Summary
        print(f"\n📊 Results: {passed_interactions}/{total_interactions} passed")
        
        assert len(failures) == 0, f"Contract violations detected:\n" + \
            "\n".join([f"  • {desc}: {msg}" for desc, msg in failures])
        
        print("\n✅ All contracts verified! Provider matches Consumer expectations.")
    
    def _verify_interaction(self, interaction: dict) -> tuple:
        """Verify a single interaction against the running provider."""
        request_data = interaction["request"]
        expected_response = interaction["response"]
        
        method = request_data["method"]
        path = request_data["path"]
        url = f"{PROVIDER_URL}{path}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                body = request_data.get("body", {})
                response = requests.post(url, json=body, timeout=5)
            else:
                return False, f"Unsupported method: {method}"
            
            # Check status code
            expected_status = expected_response["status"]
            if response.status_code != expected_status:
                return False, f"Expected status {expected_status}, got {response.status_code}"
            
            # Check response body fields
            actual_body = response.json()
            expected_body = expected_response.get("body", {})
            
            missing_fields = []
            for field in expected_body.keys():
                if field not in actual_body:
                    missing_fields.append(field)
            
            if missing_fields:
                # Build detailed error message
                error_msg = self._build_field_mismatch_error(
                    missing_fields, 
                    list(actual_body.keys()),
                    expected_body,
                    actual_body,
                    path
                )
                return False, error_msg
            
            return True, "OK"
            
        except requests.exceptions.ConnectionError:
            return False, "Could not connect to provider"
        except Exception as e:
            return False, str(e)

    def _build_field_mismatch_error(self, missing_fields, actual_fields, expected_body, actual_body, endpoint):
        """Build a detailed, actionable error message for field mismatches."""
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"🚨 CONTRACT VIOLATION DETECTED")
        lines.append(f"{'='*70}")
        lines.append(f"\n📍 Endpoint: {endpoint}")
        lines.append(f"\n❌ MISSING FIELDS (expected by Consumer but not in Provider response):")
        
        for field in missing_fields:
            expected_value = expected_body.get(field, "N/A")
            lines.append(f"   • '{field}'")
        
        # Check for similar field names (possible typos)
        lines.append(f"\n📋 ACTUAL FIELDS returned by Provider:")
        for field in actual_fields:
            lines.append(f"   • '{field}': {actual_body.get(field)}")
        
        # Suggest fixes by finding similar field names
        lines.append(f"\n💡 POSSIBLE FIXES:")
        for missing in missing_fields:
            similar = self._find_similar_fields(missing, actual_fields)
            if similar:
                lines.append(f"   • Consumer expects '{missing}' → Provider returns '{similar}'")
                lines.append(f"     FIX: In provider-py/app.py, rename '{similar}' to '{missing}'")
            else:
                lines.append(f"   • Add field '{missing}' to provider response in app.py")
        
        lines.append(f"\n{'='*70}\n")
        return "\n".join(lines)
    
    def _find_similar_fields(self, target: str, candidates: list) -> str:
        """Find a similar field name (for typo detection)."""
        target_words = set(target.lower().replace('_', ' ').split())
        
        best_match = None
        best_score = 0
        
        for candidate in candidates:
            candidate_words = set(candidate.lower().replace('_', ' ').split())
            # Calculate word overlap
            common_words = target_words & candidate_words
            score = len(common_words)
            
            if score > best_score:
                best_score = score
                best_match = candidate
        
        # Return match only if there's meaningful overlap
        return best_match if best_score > 0 else None


class TestBolusCalculation:
    """Specific tests for bolus calculation endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure provider is running."""
        try:
            requests.get(f"{PROVIDER_URL}/health", timeout=2)
        except requests.exceptions.ConnectionError:
            pytest.skip("Provider not running")
    
    def test_normal_bolus_calculation(self):
        """Test normal insulin bolus calculation."""
        response = requests.post(
            f"{PROVIDER_URL}/calculate/bolus",
            json={
                "patient_id": "test-patient",
                "current_glucose_mg_dl": 180,
                "carbs_grams": 45,
                "insulin_on_board_units": 1.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for expected field with helpful error
        if "recommended_bolus_units" not in data:
            actual_fields = list(data.keys())
            similar = self._find_similar_field("recommended_bolus_units", actual_fields)
            error_msg = f"""
{'='*70}
🚨 FIELD NAME MISMATCH IN BOLUS RESPONSE
{'='*70}

❌ Expected field: 'recommended_bolus_units'
📋 Actual fields returned: {actual_fields}

💡 POSSIBLE ISSUE:
   Provider returns '{similar}' instead of 'recommended_bolus_units'

🔧 FIX IN provider-py/app.py:
   Change: "{similar}": recommended_bolus
   To:     "recommended_bolus_units": recommended_bolus

{'='*70}
"""
            pytest.fail(error_msg)
        
        assert "risk_level" in data
        assert data["recommended_bolus_units"] >= 0
        print(f"\n✅ Bolus calculation: {data['recommended_bolus_units']} units")
    
    def test_hypoglycemia_returns_zero_insulin(self):
        """SAFETY TEST: Hypoglycemia must return 0 insulin."""
        response = requests.post(
            f"{PROVIDER_URL}/calculate/bolus",
            json={
                "patient_id": "test-patient",
                "current_glucose_mg_dl": 55,  # Hypoglycemia!
                "carbs_grams": 0,
                "insulin_on_board_units": 0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for expected field with helpful error
        if "recommended_bolus_units" not in data:
            actual_fields = list(data.keys())
            similar = self._find_similar_field("recommended_bolus_units", actual_fields)
            error_msg = f"""
{'='*70}
🚨 FIELD NAME MISMATCH IN BOLUS RESPONSE
{'='*70}

❌ Expected field: 'recommended_bolus_units'
📋 Actual fields returned: {actual_fields}

💡 POSSIBLE ISSUE:
   Provider returns '{similar}' instead of 'recommended_bolus_units'

🔧 FIX IN provider-py/app.py:
   Change: "{similar}": recommended_bolus
   To:     "recommended_bolus_units": recommended_bolus

{'='*70}
"""
            pytest.fail(error_msg)
        
        # CRITICAL SAFETY CHECK
        assert data["recommended_bolus_units"] == 0, \
            "SAFETY VIOLATION: Insulin recommended during hypoglycemia!"
        assert data["risk_level"] == "high"
        assert any("hypoglycemia" in w.lower() for w in data["warnings"])
        
        print("\n✅ Hypoglycemia safety check passed - 0 insulin recommended")
    
    def _find_similar_field(self, target: str, candidates: list) -> str:
        """Find a similar field name (for typo detection)."""
        target_words = set(target.lower().replace('_', ' ').split())
        
        best_match = None
        best_score = 0
        
        for candidate in candidates:
            candidate_words = set(candidate.lower().replace('_', ' ').split())
            common_words = target_words & candidate_words
            score = len(common_words)
            
            if score > best_score:
                best_score = score
                best_match = candidate
        
        return best_match if best_score > 0 else "unknown"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
