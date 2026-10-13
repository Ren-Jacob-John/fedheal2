# FedHeal Backend Services

FastAPI microservices delivering authentication, hospital isolation, data validation gates, model registry governance, and clinical case analysis.

## Structure

```
backend/
├── auth/           # Port 8001: Authentication, Tenant Isolation, Cases, Vitals & Scans
├── validation/     # Port 8002: 5-Stage Clinical Validation Gate & Outlier Detection
├── admin/          # Port 8005: Model Registry, Super Admin Governance & Promotion Gate
├── synthesis/      # Port 8006: Diagnostic Aggregation, Inference & Clinician Review Packet
├── shared/         # Shared backend modules (audit, service_auth, config, docstore, database)
├── run_all.py      # Concurrent terminal runner for all 4 backend services
└── requirements.txt # Backend dependencies
```

## Microservices Overview

| Service | Port | Endpoint Documentation | Purpose |
|---|---|---|---|
| **Auth & Data** | `8001` | http://localhost:8001/docs | User sessions, hospitals, cases, history, scan links, tenant isolation |
| **Validation** | `8002` | http://localhost:8002/docs | 5-stage validation gate: de-id, schema, plausible ranges, cross-field, IsolationForest |
| **Admin & Registry** | `8005` | http://localhost:8005/docs | Model candidates, gate evaluation, promotion, rollback, retraining queues |
| **Synthesis** | `8006` | http://localhost:8006/docs | `POST /cases/{id}/analyze`: loads promoted federated model, computes feature attributions |

## Running Locally

### Option 1: Run All Services Together (Single Terminal)
```bash
python backend/run_all.py
```

### Option 2: Run Any Service Individually
```bash
cd backend/auth && uvicorn main:app --port 8001 --reload
cd backend/validation && uvicorn main:app --port 8002 --reload
cd backend/admin && uvicorn main:app --port 8005 --reload
cd backend/synthesis && uvicorn main:app --port 8006 --reload
```

## Database Storage
- In local development (`FEDHEAL_ENV=development`), services default to high-performance JSON document stores (`FEDHEAL_DB_BACKEND=local`, saving to `backend/*_store.json`).
- Staging/production can connect to Google Cloud Firestore by setting `FEDHEAL_DB_BACKEND=firestore`.
