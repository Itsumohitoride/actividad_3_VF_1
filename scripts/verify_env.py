#!/usr/bin/env python3
"""Verifica el entorno para K8S Microservices Project."""

import importlib
import os
import shutil
import subprocess
import sys

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
NC = "\033[0m"

REQUIRED_PYTHON = (3, 11)
REQUIRED_PACKAGES = [
    "requests",
]

OPTIONAL_PACKAGES = [
    "pyyaml",
    "python_dotenv",
]


def check_python_version() -> bool:
    if sys.version_info < REQUIRED_PYTHON:
        ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(f"{RED}[FAIL]  Python >= 3.11 required (actual: {ver}){NC}")
        return False
    ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"{GREEN}[OK]{NC}    Python {ver}")
    return True


def check_package(name: str, optional: bool = False) -> bool:
    try:
        mod = importlib.import_module(name)
        ver = getattr(mod, "__version__", "unknown")
        tag = f"{YELLOW}[WARN]{NC}" if optional else f"{GREEN}[OK]{NC}"
        status = f"({ver})" if ver != "unknown" else ""
        print(f"{tag}    {name} {status}")
        return True
    except ImportError:
        tag = f"{YELLOW}[WARN]{NC}" if optional else f"{RED}[FAIL]{NC}"
        msg = "opcional" if optional else "obligatorio"
        print(f"{tag}  {name} no instalado ({msg})")
        return optional


def check_docker() -> bool:
    """Verifica que Docker y docker compose esten disponibles."""
    docker_path = shutil.which("docker")
    if not docker_path:
        print(f"{RED}[FAIL]  docker no encontrado en PATH (instala Docker Desktop){NC}")
        return False

    try:
        result = subprocess.run([docker_path, "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            ver = result.stdout.strip()
            print(f"{GREEN}[OK]{NC}    Docker: {ver}")
        else:
            print(f"{YELLOW}[WARN]{NC}  docker encontrado pero no responde")
            return False
    except Exception as e:
        print(f"{RED}[FAIL]  Error al ejecutar docker: {e}{NC}")
        return False

    # docker compose v2
    try:
        result = subprocess.run(
            [docker_path, "compose", "version"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            ver = result.stdout.strip()
            print(f"{GREEN}[OK]{NC}    Docker Compose: {ver}")
        else:
            print(f"{YELLOW}[WARN]{NC}  docker compose no disponible")
            return False
    except Exception as e:
        print(f"{YELLOW}[WARN]{NC}  docker compose check fallo: {e}")
        return False

    return True


def check_kubectl() -> bool:
    """Verifica que kubectl este disponible."""
    kubectl_path = shutil.which("kubectl")
    if not kubectl_path:
        print(f"{YELLOW}[WARN]{NC}  kubectl no encontrado en PATH (instala kubectl)")
        return True  # not fatal, can install later

    try:
        result = subprocess.run([kubectl_path, "version", "--client"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            ver = result.stdout.strip().split("\n")[0]
            print(f"{GREEN}[OK]{NC}    kubectl: {ver}")
        else:
            print(f"{YELLOW}[WARN]{NC}  kubectl encontrado pero no responde")
            return True
    except Exception as e:
        print(f"{YELLOW}[WARN]{NC}  Error al ejecutar kubectl: {e}")
        return True

    # Check cluster connectivity
    try:
        result = subprocess.run(
            [kubectl_path, "cluster-info", "--request-timeout=5s"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"{GREEN}[OK]{NC}    Cluster Kubernetes accesible")
        else:
            print(f"{YELLOW}[WARN]{NC}  Cluster Kubernetes no accesible (Docker Desktop K8s no activo?)")
    except Exception as e:
        print(f"{YELLOW}[WARN]{NC}  No se pudo verificar cluster: {e}")

    return True


def check_helm() -> bool:
    """Verifica que Helm este disponible."""
    helm_path = shutil.which("helm")
    if not helm_path:
        print(f"{YELLOW}[WARN]{NC}  helm no encontrado en PATH (instala Helm)")
        return True

    try:
        result = subprocess.run([helm_path, "version", "--short"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            ver = result.stdout.strip()
            print(f"{GREEN}[OK]{NC}    Helm: {ver}")
        else:
            print(f"{YELLOW}[WARN]{NC}  helm encontrado pero no responde")
            return True
    except Exception as e:
        print(f"{YELLOW}[WARN]{NC}  Error al ejecutar helm: {e}")

    return True


def check_argocd_cli() -> bool:
    """Verifica que ArgoCD CLI este disponible (opcional)."""
    argocd_path = shutil.which("argocd")
    if not argocd_path:
        print(f"{YELLOW}[WARN]{NC}  argocd CLI no encontrado en PATH (opcional)")
        return True

    try:
        result = subprocess.run([argocd_path, "version", "--client"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            ver = result.stdout.strip().split("\n")[0]
            print(f"{GREEN}[OK]{NC}    ArgoCD CLI: {ver}")
        else:
            print(f"{YELLOW}[WARN]{NC}  argocd CLI encontrado pero no responde")
    except Exception as e:
        print(f"{YELLOW}[WARN]{NC}  Error al ejecutar argocd: {e}")

    return True


def check_git() -> bool:
    """Verifica que git este disponible."""
    git_path = shutil.which("git")
    if not git_path:
        print(f"{RED}[FAIL]  git no encontrado en PATH (instala Git){NC}")
        return False

    try:
        result = subprocess.run([git_path, "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            ver = result.stdout.strip()
            print(f"{GREEN}[OK]{NC}    Git: {ver}")
        else:
            print(f"{YELLOW}[WARN]{NC}  git encontrado pero no responde")
    except Exception as e:
        print(f"{RED}[FAIL]  Error al ejecutar git: {e}{NC}")
        return False

    return True


def check_gh() -> bool:
    """Verifica que GitHub CLI este disponible (opcional)."""
    gh_path = shutil.which("gh")
    if not gh_path:
        print(f"{YELLOW}[WARN]{NC}  gh (GitHub CLI) no encontrado en PATH (opcional)")
        return True

    try:
        result = subprocess.run([gh_path, "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            ver = result.stdout.strip().split("\n")[0]
            print(f"{GREEN}[OK]{NC}    GitHub CLI: {ver}")
    except Exception as e:
        print(f"{YELLOW}[WARN]{NC}  Error al ejecutar gh: {e}")

    return True


def run() -> bool:
    print(f"{'='*50}")
    print(f"  K8S Microservices Project -- Verificacion de Entorno")
    print(f"{'='*50}\n")

    checks = [
        ("Python version", check_python_version()),
    ]

    print(f"\n--- Paquetes Python ---")
    for pkg in REQUIRED_PACKAGES:
        checks.append((pkg, check_package(pkg)))

    print(f"\n--- Paquetes opcionales ---")
    for pkg in OPTIONAL_PACKAGES:
        check_package(pkg, optional=True)

    print(f"\n--- Herramientas Docker ---")
    checks.append(("Docker", check_docker()))

    print(f"\n--- Kubernetes ---")
    checks.append(("kubectl", check_kubectl()))
    checks.append(("Helm", check_helm()))
    check_argocd_cli()

    print(f"\n--- Git ---")
    checks.append(("Git", check_git()))
    check_gh()

    all_ok = all(result for _, result in checks)

    print(f"\n{'='*50}")
    if all_ok:
        print(f"{GREEN}RESULTADO: Entorno listo para trabajar con K8S Microservices{NC}")
    else:
        print(f"{RED}RESULTADO: Hay problemas que resolver (revisa los FAIL arriba){NC}")
    print(f"{'='*50}")

    return all_ok


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
