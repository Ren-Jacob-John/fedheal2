"""
config.py / service_auth.py / audit.py / limits.py / docstore.py are copied into each
module that needs them (modules deploy independently). The copies must stay
byte-identical; this fails loudly if someone edits only one.

Run from the repo root:  pytest tests/test_shared_files_in_sync.py
"""
import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

COPIES = {
    "config.py": ["backend/auth", "backend/validation", "ml/federated", "backend/admin", "backend/synthesis"],
    "service_auth.py": ["backend/auth", "backend/validation", "ml/federated", "backend/admin", "backend/synthesis"],
    "audit.py": ["backend/auth", "backend/validation", "backend/admin", "backend/synthesis"],
    "limits.py": ["backend/auth", "backend/validation"],
    "docstore.py": ["backend/auth", "backend/admin"],
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_copies_are_identical():
    problems = []
    for name, modules in COPIES.items():
        digests = {m: digest(ROOT / m / name) for m in modules}
        if len(set(digests.values())) != 1:
            problems.append(f"{name} differs across: {digests}")
    assert not problems, "\n".join(problems)
