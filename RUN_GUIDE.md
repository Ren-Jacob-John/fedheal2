# FedHeal — Local Terminal Run Guide (No Docker Required)

This guide walks you through running the entire FedHeal stack locally directly from your terminals, without needing Docker.

---

## 1. Project Architecture

The codebase is organized into three clean layers:

```
fedheal/
├── frontend/             # React 18 + Vite dashboard (:5173)
│   ├── src/              # React components, state, API clients, styles
│   ├── public/           # Static assets
│   ├── package.json      # Frontend dependencies & scripts
│   └── vite.config.js    # Vite configuration
│
├── backend/              # FastAPI Microservices (:8001, :8002, :8005, :8006)
│   ├── auth/             # Login, Doctor/Hospital management, Cases, Vitals (:8001)
│   ├── validation/       # 5-stage clinical data validation gate (:8002)
│   ├── admin/            # Model registry, promotion gate & platform administration (:8005)
│   ├── synthesis/        # Case analysis synthesis & clinician review packet (:8006)
│   ├── shared/           # Common utilities (service_auth, audit, config, docstore)
│   └── run_all.py        # Concurrent multi-service terminal runner
│
├── ml/                   # Machine Learning & Federated Learning
│   ├── federated/        # Flower FL server (:8080), FedAvg, client runner, simulation
│   ├── models/           # Specialist models, foundation stubs, tabular predictors
│   ├── routing/          # Condition router, SHAP explainers, condition registry
│   └── run_federated.py  # ML command runner
│
├── tests/                # End-to-end and integration test suite
├── start.py              # Root multi-platform development CLI
├── run-backend.ps1/.sh   # Backend terminal starter
├── run-frontend.ps1/.sh  # Frontend terminal starter
└── run-ml.ps1/.sh        # ML terminal starter
```

---

## 2. Prerequisites

1. **Python 3.11+**:
   Check with:
   ```bash
   python --version
   ```
2. **Node.js 18+ & npm**:
   Check with:
   ```bash
   node -v
   npm -v
   ```

---

## 3. One-Time Setup

### Step A: Set up Python Virtual Environment
Open a terminal at the repository root:

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step B: Set up Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 4. Running the Platform in Your Terminals

You have two convenient ways to run:

### Method 1: Using the Root CLI (`start.py`)

#### Terminal 1 — Start All Backend Microservices:
```powershell
# Windows
python start.py backend

# Or using script:
.\run-backend.ps1
```
This runs all 4 backend services simultaneously:
- **Auth & Cases API**: http://localhost:8001 (Docs: http://localhost:8001/docs)
- **Validation API**: http://localhost:8002 (Docs: http://localhost:8002/docs)
- **Admin & Registry API**: http://localhost:8005 (Docs: http://localhost:8005/docs)
- **Synthesis API**: http://localhost:8006 (Docs: http://localhost:8006/docs)

#### Terminal 2 — Start the React Frontend:
```powershell
# Windows
python start.py frontend

# Or using script:
.\run-frontend.ps1
```
Open **http://localhost:5173** in your browser.

#### Terminal 3 (Optional) — Start Federated Learning:
```powershell
# Start Flower aggregation server on port 8080:
python start.py ml server

# Or run federated simulation (FedAvg):
python start.py ml simulate
```

---

### Method 2: Running All in a Single Terminal
To launch backend services and frontend together in one command:
```bash
python start.py all
```

---

## 5. Bootstrapping Your First Admin & Logging In

There is **no public registration** in FedHeal (accounts are onboarded top-down). Run this one-time command to bootstrap the platform super-admin:

```bash
python start.py bootstrap
```

This creates:
- **Email:** `admin@demo.local`
- **Password:** `demo-bootstrap-password-1`

You can then log into the dashboard at **http://localhost:5173** using these credentials!

---

## 6. Running Individual Backend Services (Debugging Mode)

If you are developing or debugging a specific backend service, you can run it independently:

```bash
# Terminal: Auth Service
cd backend/auth
uvicorn main:app --port 8001 --reload

# Terminal: Validation Service
cd backend/validation
uvicorn main:app --port 8002 --reload

# Terminal: Admin Service
cd backend/admin
uvicorn main:app --port 8005 --reload

# Terminal: Synthesis Service
cd backend/synthesis
uvicorn main:app --port 8006 --reload
```

---

## 7. Status & Health Checks

Verify that all services are up and healthy at any time:
```bash
python start.py status
```

---

## 8. Running Tests

To verify the installation and tests across all modules:
```bash
pytest tests/
```
