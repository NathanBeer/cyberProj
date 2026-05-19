# Cyber Attack Detection Agent using MITRE ATT&CK

## Overview
This project was developed as part of a Cyber Security course.

The system is an intelligent agent designed to analyze suspicious behavior on a target website and identify which cyber attack technique is being performed.  
To classify attacks, the agent relies on the **MITRE ATT&CK framework**, a widely used knowledge base of adversary tactics, techniques, and procedures (TTPs).

The goal of the project is to automate attack detection and provide a structured mapping between observed malicious activity and known attack techniques from the MITRE database.

---

## Features
- Detects suspicious activity patterns on websites
- Identifies potential cyber attacks
- Maps detected behaviors to MITRE ATT&CK techniques
- Provides attack classification results
- Modular architecture for future extension

---

## Technologies Used
- Python
- MITRE ATT&CK Database
- Web analysis / traffic inspection tools
- Machine learning / rule-based detection (depending on your implementation)

---

## Project Structure
```bash
project/
│
├── src/                 # Main source code
├── data/                # Input data / attack samples
├── models/              # Detection models or rules
├── results/             # Output reports and logs
└── README.md
