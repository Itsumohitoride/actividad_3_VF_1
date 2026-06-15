"""Verifica que existen los archivos base del harness y directorios del proyecto."""

import os
import sys

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
NC = "\033[0m"

HARNESS_FILES = [
    "AGENTS.md",
    "feature_list.json",
    "progress/current.md",
    "docs/architecture.md",
    "docs/conventions.md",
    "docs/deployment.md",
    "docs/configuration.md",
    "docs/verification.md",
    "CHECKPOINTS.md",
]

PROJECT_DIRS = [
    "src/",
    "tests/",
    "charts/",
    ".github/workflows/",
    "k8s/argocd/",
]


def run():
    all_ok = True

    print(f"--- Archivos base del harness ---")
    for path in HARNESS_FILES:
        if os.path.exists(path):
            print(f"{GREEN}[OK]{NC}    Existe {path}")
        else:
            print(f"{RED}[FAIL]  Falta archivo base: {path}{NC}")
            all_ok = False

    print(f"\n--- Directorios del proyecto (opcionales, se crean con features) ---")
    for path in PROJECT_DIRS:
        if os.path.isdir(path):
            print(f"{GREEN}[OK]{NC}    Existe {path}")
        else:
            print(f"{YELLOW}[WARN]{NC}  No existe {path} (se creara cuando se implemente la feature correspondiente)")

    return all_ok


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
