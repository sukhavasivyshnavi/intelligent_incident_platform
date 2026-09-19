# Intelligent IT Incident Prediction, Root-Cause Analysis & Resolution Platform

> An end-to-end ML + RAG platform for detecting IT service failures, tracing dependency-aware root causes, and generating source-grounded incident reports.

## Overview

Modern IT incidents rarely originate where the first visible symptom appears. This project simulates that problem by combining telemetry-driven machine learning, temporal evidence, service dependency analysis, root-cause scoring, and Retrieval-Augmented Generation (RAG).

The platform follows this pipeline:

```
Telemetry
   ↓
Temporal Feature Engineering
   ↓
Failure Classification
   ↓
Incident Timeline Detection
   ↓
Failure-Specific Evidence
   ↓
Service Dependency Analysis
   ↓
Root-Cause Analysis
   ↓
Incident RAG
   ↓
Grounded Incident Report
```

The main objective is **explainable incident analysis**: instead of only predicting a failure type, the system uses *when* a failure occurred, *which service depends on which*, and *what supporting evidence exists* to identify a plausible upstream root cause.

---

## What the Project Does

### 1. Generates IT telemetry
Creates a synthetic 7-day telemetry stream for five interconnected services at 5-minute intervals.

### 2. Builds temporal features
Creates lag, change, rolling mean, and rolling standard-deviation features so the model can capture degradation patterns rather than relying only on absolute metric values.

### 3. Classifies failures
A Random Forest classifier identifies:

- Normal
- CPU overload
- Memory leak
- Database connection saturation

### 4. Detects incident episodes
Groups consecutive abnormal predictions into incident timelines and measures duration, peak severity, latency, and error behavior.

### 5. Traces dependencies
Uses a service dependency graph to distinguish an affected service from a possible upstream cause.

### 6. Performs root-cause analysis
Combines:

- Temporal evidence
- Failure-specific evidence
- Dependency relationships
- Impact information

### 7. Grounds the investigation with RAG
Retrieves relevant incident reports, runbooks, deployment records, logs, and architecture documentation.

### 8. Generates a source-grounded report
The LLM is explicitly constrained to use retrieved evidence and avoid inventing filenames, incident IDs, or technical facts.

---

## Architecture

```
┌──────────────────────┐
│ Synthetic Telemetry  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Feature Engineering  │
│ Lag + Rolling Stats  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Failure Classifier   │
│    Random Forest     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Incident Timeline    │
│      Detection       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Evidence + Dependency│
│      Analysis        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Root-Cause Analysis  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│     Incident RAG     │
│ Chroma + Embeddings  │
│      + Llama 3.2     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Grounded Incident    │
│       Report         │
└──────────────────────┘
```

---

## Simulated Environment

The project models five services:

| Service | Role |
|---|---|
| `api-gateway` | Entry point for application requests |
| `user-service` | User-related application operations |
| `payment-service` | Payment processing |
| `notification-service` | Notification handling |
| `database` | Shared database dependency |

### Dependency graph

```
api-gateway
 ├── user-service ──────┐
 ├── payment-service ───┼──> database
 └── notification-service
```

---

## Dataset

The synthetic dataset contains:

- **7 days** of telemetry
- **5 services**
- **5-minute intervals**
- **10,080 telemetry records**
- **32 engineered features**

The simulated incidents include:

- Database connection saturation
- Memory leak
- CPU overload

A dedicated causal scenario is included where the **database begins degrading before the dependent payment service exhibits failure symptoms**. This provides a controlled case for testing temporal and dependency-aware root-cause analysis.

---

## Machine Learning

### Failure classifier

The failure classification model uses a Random Forest with:

```
n_estimators = 300
class_weight = balanced
random_state = 42
n_jobs = -1
```

### Evaluation

On the synthetic time-based test split:

**Macro F1-score: 0.93**

The dataset is intentionally synthetic, so this metric demonstrates the behavior of the implemented pipeline rather than production-level model performance.

---

## Root-Cause Analysis

The RCA layer does not simply assume that the affected service is the root cause.

It evaluates candidate upstream dependencies using temporal and technical evidence.

### Example

For the simulated database saturation incident:

```
Affected Service : payment-service
Detected Failure : db_connection_saturation
Root Cause       : database

RCA Score        : 10.0
Temporal Score   : 5.0
Evidence Score   : 2.0
Dependency Score : 1.0
Impact Score     : 2.0
```

The key causal relationship is:

```
database degradation
        ↓
payment-service degradation
```

This allows the platform to separate a **symptom** from a likely **upstream source** when the available evidence supports that relationship.

---

## Incident RAG

The RAG layer connects ML findings with a structured IT incident knowledge base.

### Knowledge sources

- Incident reports
- Troubleshooting runbooks
- Deployment records
- Application logs
- Architecture documentation

For the payment-service investigation, the retrieved sources include:

```
INC-1001.txt
payment_api_503_runbook.md
payment-api-v2.4.1.txt
payment_api_incident_1001.log
payment_api_architecture.md
```

The RAG pipeline uses:

- Sentence Transformers embeddings
- ChromaDB
- LangChain
- Ollama
- Llama 3.2

The report-generation prompt is designed to:

1. Use only retrieved sources.
2. Distinguish ML findings from documentary evidence.
3. Avoid inventing filenames or incident IDs.
4. Explicitly identify unavailable evidence instead of fabricating it.
5. Validate generated source filenames against the retrieved source set.

---

## Example Investigation Flow

```
Payment API starts showing failures
              ↓
Telemetry detects abnormal latency/errors
              ↓
Failure classifier identifies
database connection saturation
              ↓
Timeline analysis identifies the incident episode
              ↓
Dependency analysis finds:
payment-service → database
              ↓
Earlier database degradation is detected
              ↓
RCA identifies database as the upstream root cause
              ↓
RAG retrieves:
incident + runbook + deployment + logs + architecture
              ↓
LLM generates a grounded incident report
```

---

## Project Structure

```
intelligent_incident_platform/
│
├── data/
│   ├── telemetry.csv
│   ├── engineered_telemetry.csv
│   ├── failure_predictions.csv
│   ├── incident_evidence.csv
│   ├── incident_timeline.csv
│   ├── failure_specific_evidence.csv
│   ├── root_cause_analysis.csv
│   └── dependency_evidence.csv
│
├── reports/
│   ├── payment_latency.png
│   └── service_dependency_graph.png
│
├── src/
│   ├── data_generator.py
│   ├── feature_engineering.py
│   ├── failure_classifier.py
│   ├── anomaly_detector.py
│   ├── evidence_analyzer.py
│   ├── incident_timeline.py
│   ├── dependency_graph.py
│   ├── dependency_evidence_analyzer.py
│   ├── failure_specific_evidence.py
│   ├── root_cause_analyzer.py
│   ├── rag_integration.py
│   └── incident_rag_analyzer.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Tech Stack

**Programming & Data**
- Python
- Pandas
- NumPy

**Machine Learning**
- Scikit-learn
- Random Forest

**Visualization & Graph Analysis**
- Matplotlib
- Seaborn
- NetworkX

**RAG / GenAI**
- LangChain
- Sentence Transformers
- ChromaDB
- Ollama
- Llama 3.2

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/sukhavasivyshnavi/intelligent_incident_platform.git
cd intelligent_incident_platform
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## Running the ML Pipeline

Run the stages in order:

### Generate telemetry

```powershell
python src/data_generator.py
```

### Feature engineering

```powershell
python src/feature_engineering.py
```

### Failure classification

```powershell
python src/failure_classifier.py
```

### Incident timeline detection

```powershell
python src/incident_timeline.py
```

### Failure-specific evidence analysis

```powershell
python src/failure_specific_evidence.py
```

### Root-cause analysis

```powershell
python src/root_cause_analyzer.py
```

### RAG-based incident investigation

```powershell
python src/incident_rag_analyzer.py
```

---

## RAG Prerequisites

The incident RAG analyzer uses Ollama with Llama 3.2.

Install Ollama separately and pull the model:

```powershell
ollama pull llama3.2
```

The RAG analyzer also expects the supporting Incident RAG knowledge base to be available with the referenced incident, runbook, deployment, log, and architecture documents.

---

## Key Engineering Decisions

### Temporal reasoning
Current and historical telemetry are compared using lag and rolling features so that the system can detect degradation trends.

### Evidence-first RCA
Root-cause selection requires supporting evidence rather than relying only on dependency relationships.

### Dependency-aware reasoning
A service that fails first is not automatically treated as the root cause. Upstream dependencies are considered when their degradation precedes the observed incident.

### Grounded generation
The LLM receives retrieved technical sources and is instructed to stay within that evidence boundary.

### Synthetic-data transparency
All incident telemetry is synthetic. Results are presented as a demonstration of the architecture and reasoning pipeline, not as a benchmark on real production incidents.

---

## Limitations

- Telemetry is synthetically generated.
- Failure patterns are simplified.
- The dependency graph is currently predefined.
- Some incidents can be fragmented when the classifier changes predicted failure types during a degradation period.
- RCA quality depends on the temporal and evidence signals available.
- RAG quality depends on the coverage and relevance of the knowledge base.
- Real production telemetry, distributed tracing, alert streams, and deployment metadata are not yet connected.

---

## Future Work

- Real-time telemetry ingestion
- Streaming anomaly detection
- Automated dependency discovery
- Distributed-tracing integration
- Advanced temporal models
- Graph-based root-cause analysis
- Reranking for incident RAG
- LLM-based incident investigation agents
- Automated remediation workflows
- Integration with production observability platforms
- Evaluation on real-world incident datasets

---

## Author

**Vyshnavi Sukhavasi**  
M.Tech — Computer Science & Engineering

GitHub: https://github.com/sukhavasivyshnavi
