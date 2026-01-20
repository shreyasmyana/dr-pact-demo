"""
Provider: Insulin Risk Algorithm Service
A Flask API that calculates insulin bolus dosage based on patient data.

WARNING: This is a DEMO for hackathon purposes only.
NOT for actual medical use.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Medical constants (simplified for demo)
INSULIN_SENSITIVITY_FACTOR = 50  # mg/dL drop per unit of insulin
TARGET_GLUCOSE = 100  # mg/dL
CARB_RATIO = 10  # grams of carbs per unit of insulin


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for service discovery."""
    return jsonify({
        "status": "healthy",
        "service": "RiskAlgoService",
        "version": "1.0.0"
    })


@app.route('/calculate/bolus', methods=['POST'])
def calculate_bolus():
    """
    Calculate insulin bolus dosage.
    
    Request Body:
    {
        "patient_id": "string",
        "current_glucose_mg_dl": number,
        "carbs_grams": number,
        "insulin_on_board_units": number
    }
    
    Response:
    {
        "patient_id": "string",
        "recommended_bolus_units": number,
        "correction_units": number,
        "carb_coverage_units": number,
        "risk_level": "low" | "medium" | "high",
        "warnings": string[]
    }
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['patient_id', 'current_glucose_mg_dl', 'carbs_grams', 'insulin_on_board_units']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    patient_id = data['patient_id']
    current_glucose = data['current_glucose_mg_dl']
    carbs = data['carbs_grams']
    insulin_on_board = data['insulin_on_board_units']
    
    # Calculate correction dose (to bring glucose to target)
    glucose_delta = current_glucose - TARGET_GLUCOSE
    correction_units = max(0, glucose_delta / INSULIN_SENSITIVITY_FACTOR)
    
    # Calculate carb coverage
    carb_coverage_units = carbs / CARB_RATIO
    
    # Total bolus minus insulin already active
    total_bolus = correction_units + carb_coverage_units - insulin_on_board
    recommended_bolus = max(0, round(total_bolus, 2))
    
    # Determine risk level
    warnings = []
    if recommended_bolus > 15:
        risk_level = "high"
        warnings.append("Unusually high dose - please verify inputs")
    elif recommended_bolus > 8:
        risk_level = "medium"
        warnings.append("Moderate dose - monitor closely")
    else:
        risk_level = "low"
    
    if current_glucose < 70:
        risk_level = "high"
        warnings.append("Hypoglycemia detected - do not administer insulin")
        recommended_bolus = 0
    
    return jsonify({
        "patient_id": patient_id,
        "recommended_bolus_units": recommended_bolus,
        "correction_units": round(correction_units, 2),
        "carb_coverage_units": round(carb_coverage_units, 2),
        "risk_level": risk_level,
        "warnings": warnings
    })


@app.route('/calculate/basal-adjustment', methods=['POST'])
def calculate_basal_adjustment():
    """
    Calculate basal rate adjustment based on glucose trends.
    
    Request Body:
    {
        "patient_id": "string",
        "glucose_readings": number[],  # Last 6 readings (every 5 min)
        "current_basal_rate": number   # units per hour
    }
    
    Response:
    {
        "patient_id": "string",
        "adjusted_basal_rate": number,
        "adjustment_percentage": number,
        "trend": "rising" | "falling" | "stable",
        "action": "increase" | "decrease" | "maintain"
    }
    """
    data = request.get_json()
    
    patient_id = data['patient_id']
    readings = data['glucose_readings']
    current_basal = data['current_basal_rate']
    
    # Simple trend analysis
    if len(readings) < 2:
        return jsonify({"error": "Need at least 2 glucose readings"}), 400
    
    # Calculate trend (rate of change)
    trend_delta = readings[-1] - readings[0]
    
    if trend_delta > 30:
        trend = "rising"
        action = "increase"
        adjustment = min(0.3, trend_delta / 100)  # Max 30% increase
    elif trend_delta < -30:
        trend = "falling"
        action = "decrease"
        adjustment = max(-0.5, trend_delta / 100)  # Max 50% decrease for safety
    else:
        trend = "stable"
        action = "maintain"
        adjustment = 0
    
    adjusted_basal = round(current_basal * (1 + adjustment), 2)
    
    return jsonify({
        "patient_id": patient_id,
        "adjusted_basal_rate": adjusted_basal,
        "adjustment_percentage": round(adjustment * 100, 1),
        "trend": trend,
        "action": action
    })


if __name__ == '__main__':
    print("🏥 Starting RiskAlgoService (Insulin Algorithm Provider)")
    print("📍 Endpoints:")
    print("   GET  /health              - Health check")
    print("   POST /calculate/bolus     - Calculate bolus dosage")
    print("   POST /calculate/basal-adjustment - Adjust basal rate")
    app.run(host='0.0.0.0', port=7001, debug=True)
