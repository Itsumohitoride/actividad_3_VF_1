# CI/CD Pipelines

## Overview

Two GitHub Actions workflows automate build, test, quality checks, and deployment:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI** (`ci.yml`) | Push/PR to `develop` or `feature/*` | Build, test, lint, quality gates |
| **CD** (`cd.yml`) | Push to `develop` | Docker build + push, Helm values update, auto-deploy via ArgoCD |

## CI Pipeline

### Trigger
- Push to `develop`, `feature/*`
- Pull request to `develop`

### Jobs
1. **Build & Test** — Gradle build, unit tests, test report artifact
2. **Quality Gates** — `gradle check`, dependency analysis

### Required Secrets
None (public repo, standard GitHub token).

---

## CD Pipeline

### Trigger
- Push to `develop` (merge or direct push)

### Steps
1. **Login** to GitHub Container Registry (`ghcr.io`)
2. **Build & Push** Docker image tagged with short commit SHA (e.g., `ghcr.io/itsumohitoride/actividad-3-vf-1-microservice:a1b2c3d`)
3. **Update Helm values** — replaces `tag` in `charts/microservice/values-dev.yaml` with new SHA
4. **Commit & Push** the updated values file back to `develop`
5. **ArgoCD auto-syncs** — detects the change in the Git repo and deploys the new image

### Required Secrets
| Secret | Description |
|--------|-------------|
| `GITHUB_TOKEN` | Automatically provided; needs `contents: write` and `packages: write` permissions |

### Permissions
The CD workflow requires:
- `contents: write` — to commit updated Helm values back to the repo
- `packages: write` — to push Docker images to GitHub Container Registry

## GitOps Flow

```
Developer push → CI (build + test) → CD (docker build + push + values update)
                                                          ↓
                                              Git commit (new tag)
                                                          ↓
                                              ArgoCD auto-syncs
                                                          ↓
                                              New pod with updated image
```

## Local Testing

To test the CD pipeline locally without pushing:
```bash
# Build image locally
docker build -t microservice:local .

# Update values file manually
sed -i 's/tag: .*/tag: local/' charts/microservice/values-dev.yaml

# Deploy with Helm
helm upgrade --install microservice-dev charts/microservice -f charts/microservice/values-dev.yaml --namespace dev
```
