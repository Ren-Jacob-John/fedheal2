#!/usr/bin/env python3
"""
FedHeal Dependency & Environment Checker
Checks whether required Python packages from requirements.txt are installed in the currently active environment.

Usage:
  python check_packages.py
"""
import sys
import re
from pathlib import Path

# Use standard library importlib.metadata (Python 3.8+)
try:
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata

ROOT = Path(__file__).resolve().parent
REQUIREMENTS_FILE = ROOT / "requirements.txt"

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Normalization mapping for packages where import name / metadata name differ
NAME_MAP = {
    "python-multipart": "multipart",
    "google-cloud-firestore": "google-cloud-firestore",
    "python-jose": "jose",
}

def clean_pkg_name(raw_name: str) -> str:
    # Strip extras like [standard], [bcrypt], [cryptography]
    name = re.split(r"[=<>~!]", raw_name)[0].strip()
    name = re.sub(r"\[.*?\]", "", name).strip()
    return name

def parse_requirements(filepath: Path):
    if not filepath.exists():
        print(f"{RED}Error: {filepath} not found.{RESET}")
        return []

    pkgs = []
    for line in filepath.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        clean_name = clean_pkg_name(line)
        spec = line[len(clean_name):].strip()
        # Clean off any extras for spec comparison
        if "[" in clean_name:
            clean_name = re.sub(r"\[.*?\]", "", clean_name)
        pkgs.append((clean_name, spec, line))
    return pkgs

def get_installed_version(pkg_name: str):
    # Try direct name
    for name_variant in [pkg_name, pkg_name.replace("-", "_"), pkg_name.replace("_", "-")]:
        try:
            return importlib_metadata.version(name_variant)
        except importlib_metadata.PackageNotFoundError:
            pass
    return None

def main():
    print("=" * 65)
    print(f"{BOLD}FedHeal Environment & Package Checker{RESET}")
    print("=" * 65)

    # 1. Environment Info
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    venv_status = f"{GREEN}ACTIVE (.venv){RESET}" if in_venv else f"{YELLOW}NOT ACTIVE (Using Global/System Python){RESET}"
    
    print(f"  • Python Interpreter: {CYAN}{sys.executable}{RESET}")
    print(f"  • Python Version:     {sys.version.split()[0]}")
    print(f"  • Virtual Environment: {venv_status}")
    print("=" * 65)

    requirements = parse_requirements(REQUIREMENTS_FILE)
    if not requirements:
        return

    installed_count = 0
    missing_count = 0
    missing_names = []

    print(f"{'STATUS':<12} {'PACKAGE':<28} {'INSTALLED':<12} {'REQUIREMENT':<12}")
    print("-" * 65)

    for pkg_name, spec, full_spec in requirements:
        version = get_installed_version(pkg_name)
        if version:
            installed_count += 1
            status_str = f"{GREEN}[INSTALLED]{RESET}"
            req_display = spec if spec else "(any)"
            print(f"{status_str:<21} {pkg_name:<28} {version:<12} {req_display:<12}")
        else:
            missing_count += 1
            missing_names.append(full_spec)
            status_str = f"{RED}[MISSING]{RESET}"
            req_display = spec if spec else "(any)"
            print(f"{status_str:<21} {pkg_name:<28} {'-':<12} {req_display:<12}")

    print("=" * 65)
    print(f"{BOLD}Summary:{RESET} {installed_count} installed, {missing_count} missing (Total: {len(requirements)})")

    if missing_count == 0:
        print(f"\n{GREEN}{BOLD}[OK] All required packages are installed! Your environment is ready.{RESET}\n")
    else:
        print(f"\n{YELLOW}{BOLD}[ACTION REQUIRED] To install missing packages in this environment, run:{RESET}")
        if not in_venv:
            print(f"{CYAN}  1. Activate your venv: .venv\\Scripts\\activate{RESET}")
        print(f"{CYAN}  2. Run: pip install -r requirements.txt{RESET}\n")

if __name__ == "__main__":
    main()
