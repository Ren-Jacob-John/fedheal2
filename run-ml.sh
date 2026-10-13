#!/usr/bin/env bash
set -e
MODE="${1:-server}"
echo "Starting FedHeal ML ($MODE)..."
python3 ml/run_federated.py "$MODE"
