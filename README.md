Cloud Forensic Readiness Using Logs, Metrics, and Distributed Traces
📌 Project Overview
This project is a working prototype of a Cloud Forensic Readiness Framework. It demonstrates how distributed cloud-native applications can collect, correlate, and preserve evidence (Logs, Metrics, and Traces) to support post-incident investigations.

The project simulates an online payment system and uses a unified investigation workflow to reconstruct incident timelines and verify evidence integrity using SHA-256 hashing.

🏗️ System Architecture
The system consists of the following components:

API Gateway (Port 8000): Acts as the entry point. It receives requests, propagates trace context, and forwards requests to the Payment Service.

Payment Service (Port 8001): Simulates payment processing. It supports fault injection (timeouts and internal errors) and generates telemetry (logs and traces).

Forensic Backend (Port 8002): The core research contribution. It stores incident metadata, correlates evidence, reconstructs timelines, and handles evidence preservation (hashing and verification).

Data Flow
Client ➔ API Gateway ➔ Payment Service ➔ Forensic Backend ➔ Database & Evidence Storage

🛠️ Technology Stack
Backend: Python 3.12, FastAPI, Uvicorn, HTTPX

Telemetry & Tracing: OpenTelemetry (API, SDK, FastAPI Instrumentation, HTTPX Instrumentation)

Database: SQLite with SQLAlchemy (for local prototype)

Security & Integrity: SHA-256 Hashing (via Python's hashlib)

🚀 Key Features Implemented
1. Distributed Tracing & Correlation
Requests are assigned a unique Trace ID at the Gateway.

The Trace ID is propagated to the Payment Service (using W3C Trace Context headers).

Logs from both services are enriched with the same trace_id, enabling cross-service correlation.

2. Automated Incident Generation
When an error occurs (e.g., simulated timeout or internal failure), the Payment Service automatically sends the incident details to the Forensic Backend.

This ensures that evidence is captured immediately without manual intervention.

3. Timeline Reconstruction
The Forensic Backend provides an endpoint (/incidents/{incident_id}/timeline) to reconstruct a chronological timeline of events for a specific incident.

4. Evidence Preservation & Integrity
Investigators can export an evidence package (/incidents/{incident_id}/collect).

A SHA-256 hash and a separate Manifest file are generated to ensure integrity.

The /evidence/{incident_id}/verify endpoint recalculates the hash and compares it against the manifest to detect tampering.

📂 Project Structure
text
Cloud-Forensic-Readiness-Using-Logs-Metrics-and-Distributed-Traces/
│
├── app/
│   ├── common/            # Shared logging and tracing configurations
│   ├── gateway/           # API Gateway microservice
│   └── payment_service/   # Payment Service microservice
│
├── forensic_backend/      # Forensic Investigation API & Database
│   ├── database.py        # SQLAlchemy models
│   └── main.py            # Forensic endpoints
│
├── evidence/              # Exported evidence files and manifests
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
💻 How to Run Locally
Prerequisites
Python 3.11 or 3.12

Git

Installation
Clone the repository:

bash
git clone https://github.com/saniaasiddiqui/Cloud-Forensic-Readiness-Using-Logs-Metrics-and-Distributed-Traces.git
cd Cloud-Forensic-Readiness-Using-Logs-Metrics-and-Distributed-Traces
Create and activate a virtual environment:

bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install dependencies:

bash
pip install -r requirements.txt
Starting the Services (Open 3 separate terminals)
Terminal 1 (Payment Service):

bash
uvicorn app.payment_service.main:app --host 0.0.0.0 --port 8001 --reload
Terminal 2 (API Gateway):

bash
uvicorn app.gateway.main:app --host 0.0.0.0 --port 8000 --reload
Terminal 3 (Forensic Backend):

bash
uvicorn forensic_backend.main:app --host 0.0.0.0 --port 8002 --reload
🧪 Testing and Demonstration
Scenario 1: Triggering an Incident
Send a request to trigger an error:

bash
curl -X POST "http://localhost:8000/payments?fail=error"
Check the Forensic Backend (/incidents) to see the automatically generated incident.

Scenario 2: Viewing the Timeline
Access http://localhost:8002/docs via Swagger UI.
Execute GET /incidents/{incident_id}/timeline using the Incident ID from Scenario 1.

Scenario 3: Evidence Integrity & Tamper Detection
Export evidence: POST /incidents/{incident_id}/collect

Modify the exported JSON file in the evidence/ folder.

Verify evidence: POST /evidence/{incident_id}/verify

Result: The system will detect the modification and return "verification_result": "FAILED" with a warning message.

🎯 Research Contribution
This prototype demonstrates that by treating operational telemetry (logs, metrics, traces) as forensic evidence, we can reconstruct incidents and prove data integrity using cryptographic hashing. The separation of evidence collection and verification controls is a critical step toward robust cloud forensic readiness.

