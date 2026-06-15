# Sesion actual — Actividad 3: K8S Microservices

## Estado

| # | Feature | Status |
|---|---------|--------|
| 19 | basic_microservice | done |
| 20 | helm_charts | done |
| 21 | argocd_gitops | done |
| 22 | ci_cd_pipelines | in_progress |
| 23 | documentation | pending |
| 24 | video_demo_script | pending |

## Feature activa

**F22: Pipelines CI/CD automatizados (GitHub Actions)**
- Branch: feature/22-ci-cd-pipelines (pendiente de crear)
- Inicio: 2026-06-15T18:35
- Plan: Crear workflows CI (build+test+lint) y CD (docker build+push+deploy via ArgoCD), quality gates, notificaciones, documentacion

## Acceptance criteria

- Workflow CI: build + test + lint en push/PR a rama configurada
- Workflow CD: build Docker image, push a container registry
- Deploy automático via ArgoCD (o kubectl con manifests actualizados)
- Quality gates: tests deben pasar antes de deploy
- Notificaciones de exito/fallo del pipeline
- Documentacion del pipeline (estructura, secretos necesarios)

## Siguiente paso

1. Crear branch feature/22-ci-cd-pipelines desde develop
2. Cargar skill devops-engineer (ya cargada)
3. Lanzar implementer para crear workflows en `.github/workflows/`
4. Verificar con check_harness.py
5. Commit, push, PR
