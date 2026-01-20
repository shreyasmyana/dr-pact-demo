# 🏥 DR-PACT: AI-Powered Contract Testing Architecture

## 🤖 The AI Agent: The Brain of DR-PACT

The **AI Agent** is the core innovation - it automatically generates Pact contract tests by analyzing **both Consumer AND Provider code**.

### Key Innovation: Dual-Code Analysis

Unlike traditional contract testing where developers manually write tests, DR-PACT's AI Agent:
1. **Reads Consumer code** to understand HTTP endpoints, request/response structures
2. **Reads Provider code** to understand validation rules and constraints
3. **Intelligently generates contracts** that satisfy provider requirements

### How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  📄 Consumer│     │  🤖 AI      │     │  🧪 Pact    │     │  ✅ Verified │
│    Code     │ ──► │   Agent     │ ──► │   Tests     │ ──► │   Contract  │
│             │     │             │     │             │     │             │
│  + Provider │     │ Analyzes    │     │ Generated   │     │ Safe to     │
│    Code     │     │ Both Files  │     │ Automatically│    │ Deploy!     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Single Command Demo

```bash
python agent/generator.py --provider groq --verify

# Output:
# 📖 Loading system prompt...
# 📄 Loading consumer source code from: consumer-ts/src/insulinClient.ts
# 📄 Loading provider source code from: provider-py/app.py
#    ✅ Provider code loaded - will analyze validation requirements
# 🧠 AI Provider: GROQ
# 🤖 Calling Groq Llama 3.3 70B (FREE)...
# ✅ Contract test written to: consumer-ts/tests/contract.spec.ts
# 🧪 Running contract tests...
# ✅ All contract tests passed!
```

---

## 🧠 Intelligent Provider Analysis

The AI Agent doesn't just read code - it **understands validation logic**:

### Example: Array Length Detection

**Provider Code (Python):**
```python
def calculate_basal_adjustment():
    readings = data['glucose_readings']
    if len(readings) < 2:
        return jsonify({"error": "Need at least 2 readings"}), 400
```

**AI Agent Detects:**
- Array field: `glucose_readings`
- Minimum length: 2
- Error condition: Returns 400 if < 2 elements

**Generated Contract:**
```typescript
body: like({
  glucose_readings: eachLike(number(120), 2),  // Min 2 elements!
})
```

The AI automatically uses `eachLike(item, 2)` to ensure the contract satisfies provider validation.

---

## 📁 Current Demo Setup (Monorepo)

### Folder Structure

```
dr-pact-demo/
├── agent/                          🤖 AI AGENT
│   ├── generator.py               # Main AI script (reads both codes)
│   ├── prompt.txt                 # Generalized LLM prompt
│   └── requirements.txt           # Python dependencies
├── consumer-ts/
│   ├── src/insulinClient.ts       # HTTP client code (Consumer)
│   └── tests/contract.spec.ts     # ← AI GENERATED!
├── provider-py/
│   ├── app.py                     # Flask API (Provider)
│   └── tests/test_pact.py         # Provider verification tests
└── pacts/
    └── *.json                     # Generated contracts
```

### Demo Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. 🤖 AI Agent Reads Both Codes                                │
│     python agent/generator.py --provider groq                   │
│     └── Analyzes insulinClient.ts AND app.py                    │
├─────────────────────────────────────────────────────────────────┤
│  2. 🧠 LLM Generates Smart Tests                                │
│     └── Creates contract.spec.ts with correct array lengths,    │
│         field types, and provider-aware matchers                │
├─────────────────────────────────────────────────────────────────┤
│  3. 🧪 Consumer Tests Run                                       │
│     cd consumer-ts && npm test                                  │
│     └── Generates pacts/*.json                                  │
├─────────────────────────────────────────────────────────────────┤
│  4. ✅ Provider Verifies                                        │
│     cd provider-py && pytest tests/test_pact.py                 │
│     └── Checks real Flask API against contract                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🌐 Production Setup (Multi-Repo Microservices)

### Architecture with AI Agent

```
                    ┌─────────────────────────────────────────┐
                    │        🤖 DR-PACT AI AGENT              │
                    │   (GitHub Action / Shared Service)      │
                    │                                         │
                    │   Reads Consumer + Provider code        │
                    │   Generates contracts intelligently     │
                    └────────────────┬────────────────────────┘
                                     │ generates & publishes
                                     ▼
                    ┌─────────────────────────────────────────┐
                    │          📦 PACT BROKER                 │
                    │     (Central Hub for Contracts)         │
                    │                                         │
                    │   pactflow.io / self-hosted             │
                    └────────────────┬────────────────────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            │                        │                        │
            ▼                        ▼                        ▼
    ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
    │   Repo A      │      │   Repo B      │      │   Repo C      │
    │  Consumer 1   │      │  Consumer 2   │      │   Provider    │
    └───────────────┘      └───────────────┘      └───────────────┘
```

### AI Agent as GitHub Action

```yaml
# .github/workflows/contract-tests.yml
name: DR-PACT Contract Testing
on: [push, pull_request]

jobs:
  generate-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Checkout provider repo for validation analysis
      - name: Checkout Provider
        uses: actions/checkout@v4
        with:
          repository: org/provider-service
          path: provider
      
      # 🤖 AI Agent generates contract tests
      - name: Generate Pact Tests with AI
        run: python agent/generator.py --provider groq
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
      
      # Run generated tests
      - name: Run Contract Tests
        run: cd consumer && npm test
      
      # Publish to broker
      - name: Publish Pact to Broker
        run: |
          pact-broker publish ./pacts \
            --consumer-app-version=${{ github.sha }} \
            --broker-base-url=${{ secrets.PACT_BROKER_URL }}
```

---

## 📊 Demo vs Production Comparison

| Aspect | Demo (Monorepo) | Production (Multi-Repo) |
|--------|-----------------|------------------------|
| **🤖 AI Agent Location** | `agent/generator.py` | GitHub Action / Shared service |
| **📄 Code Sources** | Local files | Cross-repo checkout |
| **🧠 LLM Provider** | Groq API (free tier) | Groq / OpenAI / Self-hosted |
| **📝 Prompt** | Generalized `prompt.txt` | Same prompt, works with any code |
| **📦 Contract Storage** | `./pacts/` folder | Pact Broker (cloud) |
| **🔄 Trigger** | Manual: `python generator.py` | Automatic: PR/push webhook |
| **✅ Verification** | `pytest test_pact.py` | Provider CI + Broker webhook |

---

## ✨ Why AI-Powered Contract Testing?

### 1. 🤖 Intelligent Dual-Code Analysis

```
Traditional Approach:
  Developer manually reads provider docs
  Developer writes Pact tests by hand
  Risk of missing validation requirements
  Hours of work per endpoint

DR-PACT Approach:
  AI reads Consumer code → understands structure
  AI reads Provider code → understands validation
  AI generates accurate contracts automatically
  Seconds per endpoint, no human error
```

### 2. 🧠 Automatic Constraint Detection

The AI Agent automatically detects and handles:

| Provider Constraint | AI Detection | Generated Contract |
|---------------------|--------------|-------------------|
| `if len(arr) < 2` | Min array length = 2 | `eachLike(item, 2)` |
| `if field not in data` | Required field | Field included in body |
| `if value < 0` | Min value = 0 | Appropriate example value |
| `return error, 400` | Error condition | Avoided in test data |

### 3. 🔄 Generalized Prompt

The prompt is **not hardcoded** for specific projects:

```
✅ Works with ANY Consumer/Provider pair
✅ Extracts names from actual code
✅ Adapts to different languages (TS, Python, Go, etc.)
✅ Handles various API patterns (REST, GraphQL hints)
```

### 4. 🛡️ Catch Breaking Changes Early

```
Developer changes provider:
  "glucose_readings" → "readings"

Without DR-PACT:
  Deploy → Production error → Patient risk

With DR-PACT:
  AI regenerates contract → Provider verification fails
  ❌ "Missing field: glucose_readings"
  → Caught before deployment!
```

---

## 🔄 Complete AI-Powered Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: 🤖 AI Agent Reads Both Codes                           │
│  ────────────────────────────────────                           │
│  • Consumer: HTTP methods, paths, body structures               │
│  • Provider: Validation rules, error conditions                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: 🧠 LLM Generates Smart Contract Tests                  │
│  ─────────────────────────────────────────────                  │
│  • Correct matchers for each field type                         │
│  • Array lengths matching provider requirements                 │
│  • Proper assertions (expect.any(Array), etc.)                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: 🧪 Consumer Tests Run                                  │
│  ──────────────────────────────                                 │
│  • Jest + Pact executes generated tests                         │
│  • Tests run against mock server                                │
│  • Generates pacts/*.json contract file                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: ✅ Provider Verification                               │
│  ─────────────────────────────────                              │
│  • Real API tested against contract                             │
│  • All fields, types, constraints verified                      │
│  • Pass ✅ or Fail ❌ with clear error messages                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: 🚀 Safe to Deploy                                      │
│  ──────────────────────────                                     │
│  • Contract verification passed                                 │
│  • No integration issues will reach production                  │
│  • can-i-deploy check passes                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Commands

```bash
# 🤖 AI Agent: Generate and verify (single command!)
python agent/generator.py --provider groq --verify

# Step by step:

# 1. AI generates tests (reads both consumer & provider)
python agent/generator.py --provider groq

# 2. Run consumer tests (generates pact)
cd consumer-ts && npm test

# 3. Verify provider against contract
cd provider-py && pytest tests/test_pact.py -v
```

---

## 🎯 Demo Script: Show Contract Violation

```bash
# 1. First, show everything works
python agent/generator.py --provider groq --verify
# ✅ All tests pass!

# 2. Now break the provider (simulate a bug)
# Edit provider-py/app.py:
#   Change "recommended_bolus_units" → "recommended_dose"

# 3. Run verification again
cd provider-py && pytest tests/test_pact.py -v
# ❌ CONTRACT VIOLATION DETECTED!
# Missing fields: ['recommended_bolus_units']

# 4. This is caught BEFORE deployment!
```

---

## 🏥 Hackathon Pitch Summary

> **DR-PACT** combines **Agentic AI** with **Contract Testing**:
>
> 1. **Dual-Code Analysis** - AI reads BOTH Consumer AND Provider code
> 2. **Intelligent Constraint Detection** - Automatically finds validation rules
> 3. **Generalized Prompt** - Works with ANY Consumer/Provider pair
> 4. **Accurate Contract Generation** - No manual work, no human error
>
> **Result**: Faster development, fewer integration failures, safer deployments!

---

*DR-PACT: AI-Driven Contract Testing*  
*Powered by Groq Llama 3.3 70B (FREE)*
