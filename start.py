#!/usr/bin/env python3
"""
FedHeal Platform CLI — Local Development Runner (No Docker Required)

Usage:
  python start.py backend        # Start all 4 backend microservices (Auth, Validation, Admin, Synthesis)
  python start.py frontend       # Start the React Vite dashboard on http://localhost:5173
  python start.py all            # Start both backend services and React frontend
  python start.py ml             # Start Flower federated learning server (:8080)
  python start.py ml simulate    # Run local federated training simulation
  python start.py bootstrap      # Create initial platform super-admin user
  python start.py status         # Check status and health of all running services
  python start.py test           # Run integration and unit test suite
"""
import os
import sys
import time
import shutil
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def ensure_frontend_deps():
    frontend_dir = ROOT / "frontend"
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("Frontend dependencies (node_modules) not found. Installing with npm install...")
        subprocess.run(["npm", "install"], cwd=str(frontend_dir), check=True, shell=True)

def start_backend():
    runner = ROOT / "backend" / "run_all.py"
    subprocess.run([sys.executable, str(runner)])

def start_frontend():
    ensure_frontend_deps()
    frontend_dir = ROOT / "frontend"
    print("\nStarting React + Vite Frontend on http://localhost:5173...")
    subprocess.run(["npm", "run", "dev"], cwd=str(frontend_dir), shell=True)

def start_all():
    ensure_frontend_deps()
    backend_script = ROOT / "backend" / "run_all.py"
    frontend_dir = ROOT / "frontend"

    print("=" * 60)
    print("Starting FedHeal Full Stack (Backend + Frontend)")
    print("=" * 60)

    p_backend = subprocess.Popen([sys.executable, str(backend_script)])
    time.sleep(2)
    p_frontend = subprocess.Popen(["npm", "run", "dev"], cwd=str(frontend_dir), shell=True)

    try:
        p_backend.wait()
    except KeyboardInterrupt:
        print("\nStopping full stack...")
        p_frontend.terminate()
        p_backend.terminate()

def run_ml(args):
    sub = args.subcommand or "server"
    runner = ROOT / "ml" / "run_federated.py"
    subprocess.run([sys.executable, str(runner), sub])

def bootstrap_admin(args):
    email = args.email or "admin@demo.local"
    password = args.password or "demo-bootstrap-password-1"
    auth_dir = ROOT / "backend" / "auth"
    env = {
        **os.environ,
        "FEDHEAL_ENV": "development",
        "FEDHEAL_DB_BACKEND": "local",
        "FEDHEAL_LOCAL_STORE_PATH": str(ROOT / "backend" / "auth_store.json"),
        "FEDHEAL_BOOTSTRAP_ADMIN_PASSWORD": password,
    }
    print(f"Creating super admin: {email} ...")
    cmd = [sys.executable, "create_super_admin.py", "--email", email]
    res = subprocess.run(cmd, cwd=str(auth_dir), env=env)
    if res.returncode == 0:
        print(f"\n[OK] Super admin ready: {email}")
        print(f"Password: {password}\n")

def check_status():
    import urllib.request
    services = [
        ("Auth Service", "http://127.0.0.1:8001/health"),
        ("Validation Service", "http://127.0.0.1:8002/health"),
        ("Admin Service", "http://127.0.0.1:8005/health"),
        ("Synthesis Service", "http://127.0.0.1:8006/health"),
        ("React Frontend", "http://localhost:5173"),
    ]
    print("\n--- FedHeal Service Status Check ---")
    for name, url in services:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "FedHeal-CLI"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                print(f"  [ONLINE]  {name:<22} -> {url} (HTTP {resp.status})")
        except Exception:
            print(f"  [OFFLINE] {name:<22} -> {url}")
    print("------------------------------------\n")

def run_tests():
    cmd = [sys.executable, "-m", "pytest", "tests", "-v"]
    subprocess.run(cmd, cwd=str(ROOT))

def main():
    parser = argparse.ArgumentParser(
        description="FedHeal Local Development CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("backend", help="Start all 4 backend microservices")
    subparsers.add_parser("frontend", help="Start the React Vite dashboard")
    subparsers.add_parser("all", help="Start backend services and frontend together")

    ml_parser = subparsers.add_parser("ml", help="Run machine learning / federated tasks")
    ml_parser.add_argument("subcommand", nargs="?", default="server", choices=["server", "simulate", "seed"])

    boot_parser = subparsers.add_parser("bootstrap", help="Create initial platform super-admin user")
    boot_parser.add_argument("--email", default="admin@demo.local")
    boot_parser.add_argument("--password", default="demo-bootstrap-password-1")

    subparsers.add_parser("status", help="Check health and status of running services")
    subparsers.add_parser("test", help="Run pytest test suite")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    if args.command == "backend":
        start_backend()
    elif args.command == "frontend":
        start_frontend()
    elif args.command == "all":
        start_all()
    elif args.command == "ml":
        run_ml(args)
    elif args.command == "bootstrap":
        bootstrap_admin(args)
    elif args.command == "status":
        check_status()
    elif args.command == "test":
        run_tests()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
