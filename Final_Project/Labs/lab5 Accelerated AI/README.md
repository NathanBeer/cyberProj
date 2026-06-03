# Event-driven Anomaly Detection Pipeline for QR Code Scans

This project implements an **event-driven anomaly detection system** for QR code scanning telemetry using Isolation Forest machine learning. The solution demonstrates modern cybersecurity pipeline architecture with asynchronous processing, distributed tracing, and real-time ML inference.

## Architecture Overview

The pipeline consists of four main components that work together to detect anomalous QR code scans in real-time:

### 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   QR Scan       │    │   Apache     │    │   Anomaly        │    │   Results       │
│   Producer      │───▶│   Kafka      │───▶│   Detector       │───▶│   Storage       │
│   (Synthetic)   │    │   (Queue)    │    │   (ML Model)     │    │   (TSV File)    │
└─────────────────┘    └──────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
    ┌──────────────┐        ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
    │  Jaeger      │        │  Jaeger      │        │  Jaeger      │        │   Jupyter    │
    │  Tracing     │        │  Tracing     │        │  Tracing     │        │   Analysis   │
    │  (Start)     │        │  (Queue)     │        │  (Inference) │        │   & Viz      │
    └──────────────┘        └──────────────┘        └──────────────┘        └──────────────┘
```

## Components

### 1. Model Training (`notebooks/2. Anomaly Detection/1. Model Training.ipynb`)

**Purpose**: Offline training phase for the anomaly detection model.

**What it does**:
- Generates synthetic QR scan data with realistic features
- Creates both normal and anomalous patterns (phishing attempts)
- Trains an Isolation Forest model for unsupervised anomaly detection
- Saves the trained model and preprocessing objects for inference

**Key Features**:
- Synthetic dataset with 10,000 samples (3% anomalies in training)
- Features: scan hour, URL length, dot count, protocol (HTTP/HTTPS)
- Model evaluation with classification metrics
- Persistent model storage (`isolation_forest_model.pkl`, `scaler.pkl`, `encoder.pkl`)

### 2. QR Scan Producer (`notebooks/2. Anomaly Detection/2. Producer.ipynb`)

**Purpose**: Simulates real-world QR scanning events as data source.

**What it does**:
- Generates synthetic QR scan events with realistic telemetry
- Produces events to Kafka topic `qr-events` (different from classification pipeline)
- Implements distributed tracing from event inception
- Includes ground truth labels for evaluation

**Key Features**:
- Event structure: `event_id`, `timestamp`, `user`, `device_id`, `url`, `url_length`, `dot_count`, `protocol`, `hour`
- 8% anomaly rate (higher than training for realistic detection scenarios)
- Anomalies: late-night scans, very long URLs, many dots, HTTP protocol
- OpenTelemetry tracing with Jaeger integration
- Service name: `qr-scan-producer`

### 3. Anomaly Detector Consumer (`notebooks/2. Anomaly Detection/3. Consumer.ipynb`)

**Purpose**: Real-time anomaly detection using the trained ML model.

**What it does**:
- Consumes QR scan events from Kafka topic `qr-events`
- Applies trained Isolation Forest model for anomaly scoring
- Persists detection results to TSV file
- Continues distributed traces across the pipeline

**Key Features**:
- Loads pre-trained model and preprocessing objects
- Real-time feature preprocessing (scaling, encoding)
- Anomaly score computation and binary classification
- TSV output: `anomaly_detection_results.tsv`
- Consumer group: `qr-anomaly-detector`
- Service name: `qr-anomaly-detector`
- Traces: `consume_qr_event`, `preprocess_features`, `detect_anomaly`, `write_tsv`

### 4. Results Visualizer (`notebooks/2. Anomaly Detection/4. Visualizer.ipynb`)

**Purpose**: Post-processing analysis and performance evaluation.

**What it does**:
- Loads detection results from TSV file
- Performs temporal aggregation and trend analysis
- Evaluates model performance against ground truth
- Generates comprehensive visualizations

**Key Features**:
- Time-series analysis of anomaly patterns
- Confusion matrix and classification metrics
- Feature distribution comparisons
- Performance tracking over time
- Anomaly score distributions
- Summary statistics and insights

## Technology Stack

- **Data Processing**: Python, Pandas, NumPy
- **Machine Learning**: Scikit-learn (Isolation Forest)
- **Message Queue**: Apache Kafka
- **Distributed Tracing**: Jaeger, OpenTelemetry
- **Visualization**: Matplotlib, Seaborn
- **Data Storage**: TSV files (for simplicity)
- **Containerization**: Docker Compose (infrastructure)

## Data Flow

1. **Training Phase** (Offline):
   - Generate synthetic QR scan data
   - Train Isolation Forest model
   - Save model artifacts

2. **Real-time Pipeline**:
   - Producer generates QR scan events → Kafka (`qr-events` topic)
   - Consumer processes events with ML model → TSV results
   - All components emit traces to Jaeger

3. **Analysis Phase** (Offline):
   - Load results from TSV
   - Generate visualizations and metrics
   - Evaluate detection performance

## Key Design Decisions

### Event-Driven Architecture
- **Decoupling**: Producer and consumer are independent
- **Scalability**: Multiple consumers can process in parallel
- **Fault Tolerance**: Kafka provides message persistence and replay

### Machine Learning Integration
- **Unsupervised Learning**: Isolation Forest doesn't require labeled anomalies
- **Real-time Inference**: Model processes events individually
- **Preprocessing**: Consistent feature scaling and encoding

### Observability
- **End-to-End Tracing**: Single trace per event across all components
- **Trace Context**: Event ID becomes trace ID for correlation
- **Rich Metadata**: Spans include relevant attributes (scores, predictions, features)

### Data Persistence
- **Simple Storage**: TSV files for easy inspection and analysis
- **Structured Output**: All relevant fields preserved for post-processing
- **Append-Only**: Results accumulate over time

## Running the Solution

### Prerequisites
- Docker and Docker Compose (for Kafka and Jaeger infrastructure)
- Python environment with required packages

### Execution Order

1. **Start Infrastructure**:
   ```bash
   docker compose up -d
   ```

2. **Train Model**:
   - Run `notebooks/2. Anomaly Detection/1. Model Training.ipynb`
   - This creates the model files needed by the consumer

3. **Start Pipeline**:
   - Run `notebooks/2. Anomaly Detection/2. Producer.ipynb` (in one notebook/tab)
   - Run `notebooks/2. Anomaly Detection/3. Consumer.ipynb` (in another notebook/tab)

4. **Analyze Results**:
   - Run `notebooks/2. Anomaly Detection/4. Visualizer.ipynb`
   - View traces in Jaeger UI (localhost:16686)

### Expected Output

- **Kafka**: Events flowing through `qr-events` topic
- **Jaeger**: Complete traces showing producer → consumer pipeline
- **TSV File**: Accumulating detection results with anomaly scores
- **Visualizations**: Performance metrics, time-series analysis, feature distributions

## Performance Characteristics

- **Throughput**: ~1-2 events/second (configurable)
- **Latency**: Sub-second end-to-end processing
- **Accuracy**: Configurable via contamination parameter in Isolation Forest
- **Scalability**: Horizontal scaling via Kafka consumer groups

## Comparison to Classification Pipeline

This anomaly detection pipeline differs from the MITRE ATT&CK classification solution:

| Aspect | Classification Pipeline | Anomaly Detection Pipeline |
|--------|------------------------|---------------------------|
| **Topic** | `raw-events` | `qr-events` |
| **Data Type** | Windows security logs | QR scan telemetry |
| **Detection Method** | Rule-based MITRE mapping | ML-based anomaly scoring |
| **Output Format** | CSV with tactic/technique | TSV with anomaly scores |
| **Service Names** | `windows-log-producer`, `packet-classifier` | `qr-scan-producer`, `qr-anomaly-detector` |
| **ML Approach** | None (rule-based) | Unsupervised Isolation Forest |

## Educational Value

This solution demonstrates:

- **Real-time ML pipelines** in cybersecurity
- **Event-driven system design** principles
- **Distributed tracing** for observability
- **Unsupervised anomaly detection** techniques
- **Pipeline architecture** best practices
- **Performance evaluation** of ML systems

## Future Enhancements

- GPU acceleration for high-throughput scenarios
- Model retraining pipelines
- Alert generation and notification systems
- Integration with SIEM platforms
- A/B testing frameworks for model comparison
- Feature engineering and model improvement