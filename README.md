# 🏥 DR-PACT Demo: AI-Driven Contract Testing for Medical Devices

> **Hackathon Showcase**: Demonstrating how AI agents can automatically generate contract tests between microservices, preventing deadly integration errors in medical device software.

## 📋 The Problem

In medical device software, integration errors between services can be **life-threatening**. When a TypeScript frontend wrapper and a Python algorithm backend disagree on data formats (e.g., `mg/dL` vs `mmol/L` for glucose), patients can receive dangerous insulin doses.

## 💡 The Solution

**DR-PACT** (Doctor Pact) uses an AI agent to:
1. **Read** your TypeScript HTTP client code
2. **Analyze** the request/response structures
3. **Generate** Pact contract tests automatically
4. **Verify** the Python provider satisfies the contract

## 🏗️ Project Structure

```
dr-pact-demo/
├── agent/                  # 🤖 The AI "Brain"
│   ├── generator.py        # Main script - calls LLM API
│   ├── prompt.txt          # System prompt for the LLM
│   └── requirements.txt    # Python dependencies
│
├── consumer-ts/            # 📱 TypeScript Wrapper Service
│   ├── src/
│   │   └── insulinClient.ts   # HTTP client we want to test
│   ├── tests/
│   │   └── contract.spec.ts   # AI-generated Pact tests
│   ├── package.json
│   └── jest.config.js
│
├── provider-py/            # 🧮 Python Algorithm Service
│   ├── app.py              # Flask API (insulin calculations)
│   ├── tests/
│   │   └── test_pact.py    # Provider verification tests
│   └── requirements.txt
│
└── pacts/                  # 📄 Contract JSON files
    └── InsulinWrapperService-RiskAlgoService.json
```

## 🚀 Quick Start

### 1. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install agent dependencies
pip install -r agent/requirements.txt

# Install provider dependencies
pip install -r provider-py/requirements.txt
```

### 2. Setup TypeScript Consumer

```bash
cd consumer-ts
npm install
cd ..
```

### 3. Configure API Keys

```bash
# Copy the example env file
cp agent/.env.example agent/.env

# Edit and add your API key (choose one):
# - OPENAI_API_KEY for GPT-4o
# - ANTHROPIC_API_KEY for Claude 3.5 Sonnet
```

### 4. Run the Demo!

```bash
# Generate contract tests using AI
python agent/generator.py --provider openai --verify

# Or use Anthropic
python agent/generator.py --provider anthropic --verify
```

## 🎭 Demo Script (For Hackathon Presentation)

### Act 1: "The Happy Path" (2 min)
1. Show `insulinClient.ts` - explain it's a TypeScript wrapper
2. Show `app.py` - explain it's the Python algorithm
3. Run `python agent/generator.py --verify`
4. Show generated contract test and passing results

### Act 2: "The Catastrophe" (3 min)
1. **Break the Provider**: Change `recommended_bolus_units` to `recommended_dose` in `app.py`
2. Run consumer tests → They still pass! (Mock doesn't know)
3. Run provider verification → **FAILS!** Contract catches the bug!
4. Show the error message highlighting the mismatch

### Act 3: "The Save" (2 min)
1. Fix the provider
2. Show both tests passing
3. Emphasize: "This could have been a 10x insulin overdose"

## 🧪 Manual Testing Commands

```bash
# Start the Python provider
cd provider-py
python app.py

# In another terminal - run consumer contract tests
cd consumer-ts
npm test

# Verify provider against contracts
cd provider-py
pytest tests/test_pact.py -v
```

## 🔌 API Endpoints

### Health Check
```http
GET /health
```

### Calculate Bolus
```http
POST /calculate/bolus
Content-Type: application/json

{
  "patient_id": "patient-001",
  "current_glucose_mg_dl": 180,
  "carbs_grams": 45,
  "insulin_on_board_units": 1.5
}
```

### Calculate Basal Adjustment
```http
POST /calculate/basal-adjustment
Content-Type: application/json

{
  "patient_id": "patient-001",
  "glucose_readings": [120, 135, 150, 165, 180, 195],
  "current_basal_rate": 1.0
}
```

## ⚠️ Disclaimer

This is a **DEMO PROJECT** for educational and hackathon purposes only. 

**NOT FOR ACTUAL MEDICAL USE.**

Real insulin dosing algorithms require:
- FDA/CE certification
- Clinical validation
- Patient-specific parameters
- Professional medical oversight

## 🏆 Hackathon Tips

1. **Side-by-Side View**: Open `insulinClient.ts` and `app.py` side by side
2. **Break Things On Purpose**: The demo is about showing what happens when things go wrong
3. **Medical Narrative**: Use terms like "hypoglycemia", "bolus", "patient safety"
4. **Show the JSON**: The Pact contract file is human-readable - show it!
5. **Time the Demo**: Practice to fit in 5-7 minutes

## 📚 Learn More

- [Pact Documentation](https://docs.pact.io/)
- [Contract Testing](https://martinfowler.com/bliki/ContractTest.html)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic Claude](https://docs.anthropic.com/)

---

Built with ❤️ for patient safety.
