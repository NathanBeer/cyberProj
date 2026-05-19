# Cyber Attack Detection Agent — MITRE ATT&CK

Detects web application attacks in HTTP requests using a trained ML classifier and a
Claude-powered agent that maps findings to the MITRE ATT&CK framework.

---

## Architecture

```
HTTP Request
     │
     ▼
┌─────────────────────────────────────────────────────┐
│                  Detection Agent                     │
│                                                     │
│  ┌──────────────┐    ┌──────────────────────────┐  │
│  │ ML Classifier│    │  Claude API (tool use)   │  │
│  │ RandomForest │───▶│  - run_ml_classifier     │  │
│  │ CSIC 2010    │    │  - detect_attack_pattern │  │
│  └──────────────┘    │  - get_mitre_technique   │  │
│                      │  - extract_features      │  │
│  ┌──────────────┐    └──────────────────────────┘  │
│  │ Rule Engine  │              │                    │
│  │ Regex-based  │◀─────────────┘                    │
│  └──────────────┘                                   │
└─────────────────────────────────────────────────────┘
     │
     ▼
MITRE ATT&CK Report (technique ID, tactic, mitigations)
```

---

## Detected Attack Types → MITRE ATT&CK

| Attack Type          | MITRE ID   | Technique Name                               |
|----------------------|------------|----------------------------------------------|
| SQL Injection        | T1190      | Exploit Public-Facing Application            |
| Cross-Site Scripting | T1059.007  | Command and Scripting Interpreter: JavaScript|
| Command Injection    | T1059      | Command and Scripting Interpreter            |
| Path Traversal       | T1083      | File and Directory Discovery                 |
| Buffer Overflow      | T1203      | Exploitation for Client Execution            |
| LDAP Injection       | T1190      | Exploit Public-Facing Application            |
| CSRF                 | T1185      | Browser Session Hijacking                    |
| Parameter Tampering  | T1565.001  | Stored Data Manipulation                     |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Download the CSIC 2010 dataset

Download from Kaggle: https://www.kaggle.com/datasets/ispangler/csic-2010-web-application-attacks

Extract and place these files in the `data/` folder:
- `normalTrafficTraining.txt`
- `normalTrafficTest.txt`
- `anomalousTrafficTest.txt`

### 4. Train the classifier

```bash
python train.py --data-dir data/
```

This trains a Random Forest on CSIC 2010 features and saves the model to `models/classifier.joblib`.

> **Note:** The app works without a trained model using rule-based fallback detection.

### 5. Run the web app

```bash
python run.py
```

Open http://localhost:5000

---

## Project Structure

```
cyber-attack-detection/
├── src/
│   ├── preprocessor.py   # Parse CSIC 2010 HTTP request logs
│   ├── features.py       # Feature extraction (SQL, XSS, cmd patterns, etc.)
│   ├── classifier.py     # Random Forest classifier (train + predict)
│   ├── mitre_mapper.py   # MITRE ATT&CK technique database + rule-based detection
│   ├── agent.py          # Claude API agent with tool use
│   └── app.py            # Flask web application
├── templates/
│   └── index.html        # Web UI
├── data/                 # Place CSIC 2010 .txt files here
├── models/               # Trained model saved here
├── results/              # Analysis reports
├── train.py              # Training script
├── run.py                # App entry point
└── requirements.txt
```

---

## Dataset

**CSIC 2010 Web Application Attacks** — Spanish National Research Council (CSIC)

~25,000 normal requests + ~25,000 attack requests targeting a simulated e-commerce application.
Attack categories include SQL injection, XSS, buffer overflow, LDAP injection, command injection,
path traversal, and parameter tampering.
