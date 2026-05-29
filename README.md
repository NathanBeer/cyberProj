# CyberProj Workspace

## Overview

This workspace contains two main areas:

- `Final_Project/` — a final cyber attack detection solution built around the MITRE ATT&CK framework, Kafka streaming, and a Flask web app.
- `Labs/` — a series of cybersecurity and AI lab exercises covering MITRE ATT&CK mapping, LLM agent development, workflow design, and anomaly detection pipelines.

---

## Final Project: Cyber Attack Detection

### Purpose

The `Final_Project` directory implements an intelligent cyber attack detection system that analyzes HTTP traffic, detects suspicious activity, and maps findings to MITRE ATT&CK techniques.

### Key Features

- Random Forest classifier trained on the CSIC 2010 web application attacks dataset
- Mapping from detected attack types to MITRE ATT&CK technique IDs, tactics, and URLs
- Kafka-based producer/consumer streaming pipeline with end-to-end tracing
- Attack chain detection across related session requests
- Flask web app for single-request interactive analysis
- Jupyter notebooks for retraining, production, classification, and statistics

### Project Structure

`Final_Project/cyber-attack-detection/`

- `src/` — core Python modules (`agent.py`, `app.py`, `classifier.py`, `features.py`, `mitre_mapper.py`, `preprocessor.py`)
- `templates/` — web UI assets
- `data/csic_database.csv` — dataset file used for training and evaluation
- `models/classifier.joblib` — trained classifier artifact
- `pipeline/` — Docker Compose, Jupyter Docker image, and notebooks
- `results/` — output directory for reports and pipeline artifacts
- `start_pipeline.bat` — launches the Docker-based pipeline environment on Windows
- `run.bat` — starts the Flask app on Windows
- `train.py` — standalone training script
- `generate_data.py` — synthetic request generator fallback
- `requirements.txt` — Python dependencies for the Flask app and classifier

### How to Run

#### Kafka Streaming Pipeline

1. Place `csic_database.csv` into `Final_Project/cyber-attack-detection/data/`.
2. Run `Final_Project/cyber-attack-detection/start_pipeline.bat` on Windows.
3. Open JupyterLab and execute notebooks in order:
   - `0_retrain.ipynb`
   - `1_producer.ipynb`
   - `2_consumer_classifier.ipynb`
   - `3_statistics.ipynb`
4. View traces in Jaeger and live messages in Redpanda.

#### Flask Web App

1. Install requirements:
   - `pip install -r Final_Project/cyber-attack-detection/requirements.txt`
2. Train the model:
   - `python Final_Project/cyber-attack-detection/train.py`
3. Run the app:
   - `python Final_Project/cyber-attack-detection/run.py`

---

## Labs Overview

### Lab1 — MITRE ATT&CK Mapping

Located at `Labs/Lab1 - Mittre Attack/`, this lab contains a threat intelligence mapping exercise that:

- analyzes a real-world cryptojacking campaign
- maps the attack sequence to MITRE ATT&CK techniques and tactics
- documents the attack workflow and defensive insights

### Lab2 — Anomaly Detection

Located at `Labs/Lab2 Anomaly Detection/`, this lab includes an anomaly detection exploration using QR phishing telemetry and containerization. The lab is primarily notebook-driven.

### Lab3 — LLM Agent Introduction

Located at `Labs/lab3 LLM Agent/`, this lab teaches the basics of LLM agents and tool usage.

Key contents:

- `compose.yml` and `Dockerfile` for a containerized agent environment
- `app/agent/app.py` as the core agent implementation
- `chainlit.md` for the Chainlit welcome guide
- README with agent concepts, environment setup, and tool integration instructions

### Lab4 — LLM Agent Workflow

Located at `Labs/lab4 LLM Agent Workflow/`, this lab focuses on workflow design in agent-based systems.

Key lessons:

- defensive and adversarial workflow architecture
- policy gating and request routing between agents
- explicit intermediate decision points before final responses
- containerized Chainlit / AG2 environment

### Lab5 — Accelerated AI Anomaly Detection

Located at `Labs/lab5 Accelerated AI/`, this lab implements an event-driven anomaly detection pipeline for QR code scan telemetry.

Highlights:

- synthetic QR scan data generation
- Isolation Forest anomaly detection
- Kafka-based producer and consumer pipeline
- Jaeger distributed tracing
- analysis notebooks for metrics and visualization

### Labs2

Located at `Labs/Labs2/`, this directory contains additional Docker Compose and lab materials for advanced containerized experimentation.

---

## Navigation

- `Final_Project/` — final deliverable and main detection system
- `Final_Project/cyber-attack-detection/` — full implementation of the MITRE ATT&CK classification pipeline
- `Labs/` — course lab exercises organized by topic

## Notes

- The `Final_Project` pipeline depends on the CSIC 2010 dataset. Download it separately if the CSV is not already present.
- Most lab exercises are designed to run inside Docker containers, so install Docker Desktop if you want to run them locally.
- This root README is intended as a central entry point for the workspace and links to the full project and lab folders.
