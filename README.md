\# Intelligent IT Incident Prediction, Root-Cause Analysis \& Resolution Platform



An intelligent IT incident analysis platform that combines Machine Learning, temporal telemetry analysis, service dependency analysis, Root-Cause Analysis (RCA), and Retrieval-Augmented Generation (RAG) to detect, investigate, and explain IT service failures.



\## Overview



The platform follows an end-to-end incident analysis pipeline:



\*\*Telemetry → Feature Engineering → Failure Classification → Incident Detection → Dependency Analysis → Root-Cause Analysis → RAG → Grounded Incident Report\*\*



The goal is to combine machine learning with LLM-based retrieval to support faster and more explainable IT incident investigation.



\## Key Features



\* Synthetic IT telemetry generation

\* Temporal feature engineering using lag and rolling statistics

\* Failure classification using Random Forest

\* Incident timeline detection

\* Service dependency graph analysis

\* Failure-specific evidence scoring

\* Dependency-aware root-cause analysis

\* Incident RAG integration

\* Source-grounded LLM incident reporting

\* Source validation to reduce hallucinated documents and evidence



\## Services



The simulated environment contains five services:



\* `api-gateway`

\* `user-service`

\* `payment-service`

\* `notification-service`

\* `database`



\## Failure Types



The platform currently analyzes:



\* Normal

\* CPU Overload

\* Memory Leak

\* Database Connection Saturation



\## System Architecture



```text

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Synthetic Telemetry │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Feature Engineering │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Failure Classifier  │

&#x20;                   │   Random Forest     │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Incident Timeline   │

&#x20;                   │     Detection       │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Dependency \&        │

&#x20;                   │ Evidence Analysis   │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Root-Cause Analysis │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │    Incident RAG     │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │ Grounded Incident   │

&#x20;                   │       Report        │

&#x20;                   └─────────────────────┘

```



\## Dataset



The project uses a synthetic telemetry dataset containing:



\* 7 days of telemetry

\* 5 services

\* 5-minute intervals

\* 10,080 telemetry records

\* 32 engineered features



The dataset contains incidents representing:



\* Database connection saturation

\* Memory leak

\* CPU overload



A causal database incident is also simulated where the database begins degrading before the dependent payment service shows failure symptoms.



\## Machine Learning



A Random Forest classifier is used for failure classification.



Configuration:



```text

n\_estimators = 300

class\_weight = balanced

random\_state = 42

n\_jobs = -1

```



Current evaluation on the synthetic test split:



```text

Macro F1-score: 0.93

```



The dataset is synthetic and is intended to demonstrate the end-to-end incident-analysis pipeline rather than represent production-level model performance.



\## Root-Cause Analysis



The platform combines:



\* Temporal evidence

\* Failure-specific evidence

\* Service dependency relationships

\* Incident impact information



Example dependency:



```text

payment-service → database

```



For the main database saturation incident, the system identified:



```text

Affected Service : payment-service

Detected Failure : db\_connection\_saturation

Root Cause       : database

RCA Score        : 10.0

Temporal Score   : 5.0

Evidence Score   : 2.0

Dependency Score : 1.0

```



The database degradation occurs before the payment-service incident, providing temporal and dependency evidence for the root-cause decision.



\## Incident RAG



The RAG component connects the machine-learning analysis with an IT incident knowledge base containing:



\* Incident reports

\* Runbooks

\* Deployment records

\* Application logs

\* Architecture documentation



For the payment-service incident, the system retrieves evidence from:



```text

INC-1001.txt

payment\_api\_503\_runbook.md

payment-api-v2.4.1.txt

payment\_api\_incident\_1001.log

payment\_api\_architecture.md

```



The LLM is instructed to use only retrieved sources and not invent filenames, incident IDs, or technical evidence.



\## Project Structure



```text

intelligent\_incident\_platform/

│

├── data/

│   ├── telemetry.csv

│   ├── engineered\_telemetry.csv

│   ├── failure\_predictions.csv

│   ├── incident\_evidence.csv

│   ├── incident\_timeline.csv

│   ├── failure\_specific\_evidence.csv

│   ├── root\_cause\_analysis.csv

│   └── dependency\_evidence.csv

│

├── reports/

│   ├── payment\_latency.png

│   └── service\_dependency\_graph.png

│

├── src/

│   ├── data\_generator.py

│   ├── data\_generator\_backup.py

│   ├── feature\_engineering.py

│   ├── failure\_classifier.py

│   ├── anomaly\_detector.py

│   ├── evidence\_analyzer.py

│   ├── incident\_timeline.py

│   ├── dependency\_graph.py

│   ├── dependency\_evidence\_analyzer.py

│   ├── failure\_specific\_evidence.py

│   ├── root\_cause\_analyzer.py

│   ├── rag\_integration.py

│   └── incident\_rag\_analyzer.py

│

├── .gitignore

├── README.md

└── requirements.txt

```



\## Technologies Used



\* Python

\* Pandas

\* NumPy

\* Scikit-learn

\* Matplotlib

\* Seaborn

\* NetworkX

\* Sentence Transformers

\* LangChain

\* ChromaDB

\* Ollama

\* Llama 3.2



\## Installation



Create a virtual environment:



```powershell

python -m venv .venv

```



Activate the environment:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



Install dependencies:



```powershell

pip install -r requirements.txt

```



\## Running the Pipeline



\### 1. Generate telemetry



```powershell

python src/data\_generator.py

```



\### 2. Perform feature engineering



```powershell

python src/feature\_engineering.py

```



\### 3. Train and evaluate the failure classifier



```powershell

python src/failure\_classifier.py

```



\### 4. Detect incident timelines



```powershell

python src/incident\_timeline.py

```



\### 5. Analyze failure-specific evidence



```powershell

python src/failure\_specific\_evidence.py

```



\### 6. Perform root-cause analysis



```powershell

python src/root\_cause\_analyzer.py

```



\### 7. Run the RAG-based incident analysis



```powershell

python src/incident\_rag\_analyzer.py

```



\## RAG Setup



The RAG component uses Ollama with Llama 3.2.



Pull the required model:



```powershell

ollama pull llama3.2

```



The RAG component also requires the supporting Incident RAG knowledge base and its documents.



\## Limitations



\* Telemetry is synthetically generated.

\* Failure patterns are simplified compared with real production environments.

\* The service dependency graph is currently predefined.

\* Incident episodes can occasionally be fragmented when predicted failure types change.

\* Root-cause analysis depends on the quality of temporal, dependency, and evidence signals.

\* LLM output depends on the quality and coverage of retrieved knowledge-base documents.



\## Future Improvements



\* Real-time telemetry ingestion

\* Streaming anomaly detection

\* Advanced temporal models

\* Automated service dependency discovery

\* Graph Neural Network-based root-cause analysis

\* Advanced RAG with reranking

\* LLM-based incident investigation agents

\* Automated remediation recommendations

\* Production monitoring integration

\* Evaluation using real-world incident datasets



\## Author



\*\*Vyshnavi Sukhavasi\*\*



M.Tech Computer Science \& Engineering



GitHub: https://github.com/sukhavasivyshnavi



