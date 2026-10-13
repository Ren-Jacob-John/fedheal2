# FedHeal Machine Learning & Federated Learning

Machine learning subsystem implementing privacy-preserving federated training across hospitals (using Flower / FedAvg), specialist model catalog, condition routing, and explainability.

## Structure

```
ml/
├── federated/          # Federated Learning Engine (Flower / FedAvg)
│   ├── server.py           # Flower aggregation server (:8080)
│   ├── client.py           # Local client model trainer
│   ├── client_runner.py    # Multi-tenant runner fetching hospital-scoped data
│   ├── simulate.py         # In-memory federated simulation
│   ├── seed_uci_heart.py   # Seeds public UCI Cleveland cohort through validation gate
│   ├── federation_registry.py # Submits candidates & round metrics to Model Registry
│   └── datasets/           # UCI Cleveland reference dataset
│
├── models/             # Specialist Model Zoo & Architectures
│   ├── base.py             # SpecialistModel contract & PredictionResult
│   ├── registry.py         # Modality-keyed specialist model catalog
│   ├── fusion.py           # Multi-modal late-fusion scoring
│   └── models/             # Tabular (XGBoost, TabPFN), imaging & genomic specialist stubs
│
├── routing/            # Condition Router & Explainability
│   ├── condition_router.py # Maps admission condition to specialists and explainers
│   ├── conditions.py       # Clinical condition definitions
│   └── explainers/         # SHAP, Grad-CAM, and knowledge graph reasoner
│
├── run_federated.py    # Terminal command runner for ML workflows
└── requirements.txt    # ML dependencies
```

## Running ML Locally

### Start Flower Federated Learning Server
```bash
python ml/run_federated.py server
```
Listens for federated hospital clients on `0.0.0.0:8080`.

### Run In-Memory Federated Simulation
```bash
python ml/run_federated.py simulate
```
Executes federated rounds across simulated hospital splits with FedAvg and pooled holdout evaluation.

### Seed Real Benchmark Data (UCI Cleveland)
```bash
python ml/run_federated.py seed
```
Uploads validated patient records through the backend validation gate to verify end-to-end retraining.
