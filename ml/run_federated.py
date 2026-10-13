#!/usr/bin/env python3
"""
FedHeal Machine Learning Runner.
Provides simple terminal options for Federated Learning:
  - Start Flower Federated Server (:8080)
  - Run Federated Simulation (FedAvg over UCI Heart Disease dataset)
  - Seed UCI Heart Disease Data

Usage:
  python ml/run_federated.py server        # Start Flower server on port 8080
  python ml/run_federated.py simulate      # Run local federated simulation
  python ml/run_federated.py seed          # Seed UCI Cleveland dataset
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ML_DIR = ROOT / "ml"

def run_server():
    print("Starting Flower Federated Learning Server on 0.0.0.0:8080...")
    cmd = [sys.executable, "server.py", "--address", "0.0.0.0:8080"]
    subprocess.run(cmd, cwd=str(ML_DIR / "federated"))

def run_simulate():
    print("Running Federated Learning Simulation (FedAvg)...")
    cmd = [sys.executable, "simulate.py"]
    subprocess.run(cmd, cwd=str(ML_DIR / "federated"))

def run_seed():
    print("Seeding UCI Heart dataset through local services...")
    cmd = [sys.executable, "seed_uci_heart.py"]
    subprocess.run(cmd, cwd=str(ML_DIR / "federated"))

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        return

    mode = sys.argv[1].lower()
    if mode == "server":
        run_server()
    elif mode == "simulate":
        run_simulate()
    elif mode == "seed":
        run_seed()
    else:
        print(f"Unknown ML command: {mode}")
        print("Available options: server, simulate, seed")
        sys.exit(1)

if __name__ == "__main__":
    main()
