#!/usr/bin/env python3
"""
Run all FedHeal backend microservices concurrently in one terminal.
Ports:
  - Auth Service:       http://localhost:8001
  - Validation Service: http://localhost:8002
  - Admin Service:      http://localhost:8005
  - Synthesis Service:  http://localhost:8006

Usage:
  python backend/run_all.py
"""
import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ANSI Colors
COLORS = {
    "auth": "\033[36m",       # Cyan
    "validation": "\033[33m", # Yellow
    "admin": "\033[35m",      # Magenta
    "synthesis": "\033[32m",  # Green
    "reset": "\033[0m",
    "bold": "\033[1m",
}

SERVICES = [
    {
        "name": "auth",
        "port": 8001,
        "dir": ROOT / "backend" / "auth",
        "env": {
            "FEDHEAL_ENV": "development",
            "FEDHEAL_DB_BACKEND": "local",
            "FEDHEAL_LOCAL_STORE_PATH": str(ROOT / "backend" / "auth_store.json"),
            "FEDHEAL_VALIDATION_API_URL": "http://127.0.0.1:8002",
            "FEDHEAL_DASHBOARD_ORIGIN": "http://localhost:5173",
        },
    },
    {
        "name": "validation",
        "port": 8002,
        "dir": ROOT / "backend" / "validation",
        "env": {
            "FEDHEAL_ENV": "development",
            "FEDHEAL_ADMIN_API_URL": "http://127.0.0.1:8005",
        },
    },
    {
        "name": "admin",
        "port": 8005,
        "dir": ROOT / "backend" / "admin",
        "env": {
            "FEDHEAL_ENV": "development",
            "FEDHEAL_DB_BACKEND": "local",
            "FEDHEAL_LOCAL_STORE_PATH": str(ROOT / "backend" / "admin_store.json"),
            "FEDMED_AUTH_API_URL": "http://127.0.0.1:8001",
            "FEDHEAL_DASHBOARD_ORIGIN": "http://localhost:5173",
        },
    },
    {
        "name": "synthesis",
        "port": 8006,
        "dir": ROOT / "backend" / "synthesis",
        "env": {
            "FEDHEAL_ENV": "development",
            "FEDHEAL_AUTH_API_URL": "http://127.0.0.1:8001",
            "FEDHEAL_ADMIN_API_URL": "http://127.0.0.1:8005",
            "FEDHEAL_ALLOW_DEMO_MODEL": "true",
            "FEDHEAL_DASHBOARD_ORIGIN": "http://localhost:5173",
        },
    },
]

processes = []

def stream_output(proc, name, color):
    tag = f"{color}[{name.upper():<10}]{COLORS['reset']} "
    for line in iter(proc.stdout.readline, ""):
        if not line:
            break
        print(f"{tag}{line.rstrip()}", flush=True)

def shutdown():
    print(f"\n{COLORS['bold']}Shutting down backend services...{COLORS['reset']}")
    for p in processes:
        try:
            if p.poll() is None:
                p.terminate()
                p.wait(timeout=3)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    print(f"{COLORS['bold']}All backend services stopped.{COLORS['reset']}")

def signal_handler(sig, frame):
    shutdown()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 60)
    print(f"{COLORS['bold']}Starting FedHeal Backend Services (No Docker){COLORS['reset']}")
    print("=" * 60)
    for s in SERVICES:
        print(f"  • {s['name']:<12} -> http://localhost:{s['port']}")
    print("=" * 60)
    print("Press Ctrl+C to stop all services\n")

    base_env = dict(os.environ)

    for s in SERVICES:
        env = {**base_env, **s["env"], "PYTHONUNBUFFERED": "1"}
        cmd = [
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "127.0.0.1",
            "--port", str(s["port"]),
            "--log-level", "info",
        ]
        proc = subprocess.Popen(
            cmd,
            cwd=str(s["dir"]),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        processes.append(proc)
        t = threading.Thread(
            target=stream_output,
            args=(proc, s["name"], COLORS.get(s["name"], "")),
            daemon=True,
        )
        t.start()
        time.sleep(0.5)

    try:
        while True:
            for p, s in zip(processes, SERVICES):
                if p.poll() is not None:
                    print(f"\n[ERROR] Service {s['name']} exited unexpectedly with code {p.returncode}.")
                    shutdown()
                    sys.exit(p.returncode)
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()

if __name__ == "__main__":
    main()
