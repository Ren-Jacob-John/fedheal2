# FedHeal — Federated Learning Healthcare AI

Developed by a team of 4 members.

> **Status: research / MVP prototype. Nothing in this repository is clinically validated.**
> FedHeal is clinical *decision support*. Every result must be reviewed by a doctor. See
> [What works today and what is planned](#what-works-today-and-what-is-planned) before relying on any feature.

---

## 1. What FedHeal is

FedHeal is a healthcare AI platform that helps a doctor understand why a patient was admitted and what to
consider next. For each patient, the doctor provides:

- **vitals**,
- **medical history**,
- **the condition / problem the patient is admitted for**,
- **scans** done on the patient.

The AI analyses this information and returns a **result with the reasoning behind it**, for the doctor to
accept, override, or send back for more data.

The AI is trained with **federated learning**: every hospital trains on its own data, and only learned model
weights are combined. **One hospital's patient data is never shared with another hospital.** After the first
training, the shared model keeps improving through further federated rounds, and a new version only goes
live after it passes a validation gate.

### Who uses it

| User | Created by | What they can do |
|---|---|---|
| **Platform operator** (`super_admin`) | the developers | create hospitals and their hospital users, see platform-level status, validate / promote / roll back models. **No access to patient-level data.** |
| **Hospital user** (`hospital_admin`) | the platform operator | create and deactivate the hospital's doctors. Manages people, not patients. |
| **Doctor** (`clinician`) | the hospital user | create patient cases, enter vitals / history / condition, upload scans, run AI analysis, review results. Sees only their own hospital's cases. |

There is **no public registration**. Accounts are created top-down: developers → hospital user → doctors.

### Data isolation rule

A hospital's data stays inside that hospital:

- The hospital a request belongs to is read from the signed login token, never from anything the client sends.
- A doctor asking for another hospital's case gets `403`, and the attempt is written to the audit log.
- Training reads a hospital's data only through a token scoped to that one hospital.
- Training clients send back **only** weights, an example count and a hospital id.
- The model registry refuses anything that looks like patient data.

---

## 2. How it works (end to end)

1. The developers create a **hospital** and its **hospital user**. The hospital user creates **doctors**.
2. A doctor logs in and creates a **patient case** (admission reason, current condition, symptoms).
3. The doctor adds **medical history**, **vitals** and **scans**. Vitals pass a 5-stage validation gate
   (de-identification screen → schema → plausibility ranges → cross-field consistency → outlier detection);
   only validated records can be used for training.
4. The doctor runs **AI analysis** on the case. The analysis uses the **currently promoted federated model**
   and returns a clinician review packet: the model result, which inputs drove it, which inputs were missing,
   and the model's version and status.
5. The doctor records a **review**: Accepted, Overridden, or Needs more data.
6. **Federated retraining.** Each hospital trains locally on its own validated data; only weights are
   averaged (FedAvg) into a new global model, which is registered as a **candidate**.
7. **Validation gate → promotion.** A candidate is checked against the gate. Only a `super_admin` can promote
   it. The previous version is kept so it can be **rolled back**.
8. Promoted models are what step 4 uses, so the system improves as more validated data arrives.

New data never changes the live model by itself. Doctor review decisions are **never** used as training labels.

---

## 3. What works today and what is planned

Legend: **Done** = code and tests exist · **Partial** = works with gaps · **Planned** = not built yet.
Nothing was run in Docker/Compose yet; "Done" does not mean clinically validated.

| Capability from the concept | Status | Notes |
|---|---|---|
| Two-level user creation (developers → hospital user → doctors), no public sign-up | **Done** | |
| Hospital data isolation | **Done** | enforced from the token; cross-hospital access refused and audited |
| Doctor enters condition, history, vitals | **Done** | cases, structured history, case-linked validated vitals |
| Doctor uploads scans | **Partial** | scans are stored and linked; the authenticated analysis route reports unavailable because there is no validated imaging model |
| AI result for the patient | **Partial** | one runnable heart-risk model on vitals, trained on small public data; not clinically useful or validated |
| Reasoning behind the result | **Partial** | feature contributions, missing/unused inputs, and a clinician-review flag; history/symptoms remain context-only |
| Suggested next steps for the doctor | **Partial** | suggestions come only from versioned, provenance-tagged rules marked unvalidated for clinician review; no match means no suggestion |
| Doctor review (accept / override / needs more data) | **Done** | reviews may link to an analysis but are not training labels |
| Federated training across hospitals (FedAvg) | **Done** | 2-hospital flow tested through the real services |
| Model registry, validation gate, promotion, rollback | **Done** | no automatic deployment |
| Model improves over time | **Partial** | count-triggered retraining requests are off by default; candidates require validation and explicit super-admin promotion |
| Saved AI-analysis history per case | **Done** | append-only, hospital-scoped, structured identifiers/output only |
| Extra vitals (temperature, SpO2, respiratory rate) | **Partial** | nullable storage, validation and upload support exist; no promoted model consumes them yet |
| Imaging models (chest X-ray, retina, skin, CT) | **Planned** | stubs only; no validated models or weights in the repo |
| Federated-update privacy: TLS, clipping, differential privacy, secure aggregation | **Planned** | today the aggregation server sees each hospital's weight update, so it must run on a trusted network |
| Docker Compose run, browser E2E test | **Partial** | Compose and CI browser job are configured; neither runtime was executed in the current environment |

Honest model status, recorded numbers, and gate thresholds: [`docs/MODEL_STATUS.md`](docs/MODEL_STATUS.md).
What is deliberately not done: [`docs/MVP_SCOPE.md`](docs/MVP_SCOPE.md).
Privacy details: [`docs/FEDERATED_PRIVACY.md`](docs/FEDERATED_PRIVACY.md).

**Never claim:** accurate, clinically proven, hospital-ready, FDA approved, medically certified.

---

## 4. Architecture

Organized into a clean, intuitive full-stack structure:

```
Browser (React Frontend :5173) ──JWT──► Backend Auth/Cases/Vitals :8001 ──service token──► Backend Validation :8002
        │                                             ▲
        │                                             └── hospital-scoped service token ── ML Federated (Flower :8080)
        ├──JWT──► Backend Admin/Registry :8005 ◄─────── candidates & round reports ─────── ML Federated
        └──JWT──► Backend Synthesis/Analysis :8006 ─── reads promoted model from Admin
                         └─ uses ML Routing ─────────► ML Specialist Models
```

| Folder | Subsystem | Purpose & Port |
|---|---|---|
| `frontend/` | React 18 + Vite | Clinician, hospital admin & operator dashboard (**Port 5173**) |
| `backend/auth/` | FastAPI | Auth, hospital tenants, cases, vitals, history, scans (**Port 8001**) |
| `backend/validation/` | FastAPI | 5-stage data validation & anomaly gate (**Port 8002**) |
| `backend/admin/` | FastAPI | Platform oversight, model registry, validation gate & promotion (**Port 8005**) |
| `backend/synthesis/` | FastAPI | Diagnostic synthesis packet & `POST /cases/{id}/analyze` (**Port 8006**) |
| `backend/shared/` | Python library | Common utilities: `service_auth.py`, `audit.py`, `config.py`, `docstore.py` |
| `ml/federated/` | Flower / Scikit-Learn | Federated training (FedAvg), Flower server (**Port 8080**), client runner, simulation |
| `ml/models/` | ML Architectures | Specialist model zoo (TabPFN, XGBoost, Random Forest, stubs) |
| `ml/routing/` | Explainability | Condition router, SHAP explainers, condition registry |

More detail: [`RUN_GUIDE.md`](RUN_GUIDE.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/API.md`](docs/API.md).

---

## 5. Safety rules built into the design

- Every analysis is `requires_clinician_review`. The system never states a confirmed diagnosis.
- It does not output a treatment plan, medication or dose.
- Every result shows the model version, status (`DEPLOYED`, or `FALLBACK` for the non-clinical demo model) and whether it is federated.
- Missing inputs are reported as missing. Nothing is silently filled in.
- With no promoted model, analysis answers `MODEL_UNAVAILABLE`. The demo fallback only runs if `FEDHEAL_ALLOW_DEMO_MODEL=true`, and is labelled **NON-CLINICAL DEMO MODEL**.
- A scan without a validated imaging model is reported as `UPLOADED — analysis UNAVAILABLE`.
- Services refuse to start in production mode with missing or placeholder secrets.

---

## 6. Running FedHeal locally in Terminals (No Docker Required)

See the detailed [`RUN_GUIDE.md`](RUN_GUIDE.md) for full steps.

### Quickstart

```bash
# 1. Setup virtual environment & dependencies
python -m venv .venv && . .venv/Scripts/activate  # (on Windows) or: source .venv/bin/activate (macOS/Linux)
pip install -r requirements.txt

# 2. Setup frontend
cd frontend && npm install && cd ..

# 3. Create initial administrator
python start.py bootstrap

# 4. Start the stack in separate terminals:
# Terminal 1 (Backend - all 4 microservices on :8001, :8002, :8005, :8006):
python start.py backend
# (Or on Windows: .\run-backend.ps1)

# Terminal 2 (Frontend - React Vite on :5173):
python start.py frontend
# (Or on Windows: .\run-frontend.ps1)

# Terminal 3 (Optional - ML Federated Learning Server on :8080):
python start.py ml server
# (Or on Windows: .\run-ml.ps1)
```

You can also run both backend and frontend concurrently in one terminal:
```bash
python start.py all
```


### Demo walkthrough

The full step-by-step flow is in [`docs/DEMO_RUNBOOK.md`](docs/DEMO_RUNBOOK.md). In short:

1. Log in as the platform operator and create two hospitals and a hospital user for each.
2. As a hospital user, create a doctor.
3. As the doctor, create a case, then add vitals and history (and optionally a scan).
4. Run AI analysis. Before any model is promoted, the correct answer is `MODEL_UNAVAILABLE`.
5. To verify federated training, run `python -m pytest -q tests/integration/test_federation_flow.py`
   from the repository root. It seeds public UCI data, uses clearly named synthetic-only threshold
   records, and starts hospital-local networked clients. The candidate is registered but not deployed.
   Do not run `simulate_real.py`: central pooling is disabled by the privacy boundary.
6. Validate the candidate. With the default gate the recorded public-data run is **rejected**, which is the
   honest result. A relaxed test policy exists only to demonstrate the wiring.
7. Promote a passing model, run analysis again, then record a doctor review.
8. Try another hospital's case id as a doctor from a different hospital: you get `403`.
9. Roll back to the previous model version.

### Tests

```bash
# per module, for example:
(cd module1-auth && pytest)
pytest tests/        # cross-module and integration tests
```

See [`docs/TESTING.md`](docs/TESTING.md). Known gap: Module 3 tests are not in CI yet.

### Troubleshooting

- **401 between services:** a shared secret or signing key does not match. Check the table above.
- **CORS errors:** `FEDHEAL_DASHBOARD_ORIGIN` must exactly match the dashboard URL, including the port.
- **403 on training export:** the hospital token belongs to a different hospital.
- **Imaging/genomic specialists show `[STUB]`:** expected without torch, weights and data.
- **Security model and required configuration:** [`docs/SECURITY.md`](docs/SECURITY.md).

---

## 7. Technology

| Layer | Used |
|---|---|
| Federated learning | Flower (FedAvg), scikit-learn (SGD logistic regression for the vitals model) |
| Validation | rules plus Isolation Forest outlier detection |
| Model zoo (scaffolded) | XGBoost, TabPFN, LightGBM, PyTorch imaging and segmentation models. Most are stubs until weights and data exist |
| Explainability | linear feature contributions (promoted model), SHAP (demo model), Grad-CAM and knowledge graph (scaffolded) |
| APIs | FastAPI, Pydantic (Modules 1 and 7 store data through `docstore.py` / `repo.py`) |
| Auth | bcrypt password hashing, JWT for users, scoped signed tokens between services |
| Database | Firebase Firestore (the Firestore emulator in Compose, a local JSON-file store for development) |
| Frontend | React 18 + Vite |

---

## 8. Roadmap

Planned in this order (details and acceptance rules in the project docs):

1. Suggested next-step considerations from a reviewable, sourced rule file (no dosing, no invented advice).
2. Use history, symptoms, admission condition and extra vitals as model inputs. Missing values stay missing.
3. Save every AI analysis per case (append-only, hospital-scoped) and link reviews to it.
4. Automatic retraining trigger per hospital, with candidates still gated and promotion still manual.
5. Docker Compose and browser end-to-end run, Module 3 in CI.
6. Scan analysis through a validated imaging model, only when real weights and a licensed dataset exist.
7. Federated-update privacy: TLS, update clipping, differential privacy, evaluate secure aggregation.

---

## 9. Why this matters

Hospitals cannot pool raw patient records because of privacy law and data-governance policy, and a model
trained at one hospital often performs poorly at another. FedHeal keeps patient data where it was collected and
shares only learned weights, so small and rural hospitals can benefit from a model shaped by many hospitals
without handing over their patients' records. The validation gate, the human-review requirement and the
explicit model status exist because a silently wrong or unexplained result is dangerous in medicine.
