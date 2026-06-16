## PENDING REVIEW

**Feature:** F26 — Fix README inconsistencies and deployment blockers
**Branch:** feature/26-readme-fixes
**PR:** https://github.com/Itsumohitoride/actividad_3_VF_1/pull/12
**Estado:** Pendiente de revision humana

## Cambios realizados

| Archivo | Cambio |
|---------|--------|
| `README.md` | docker build redundante eliminado, base64 multiplataforma, prerequisito push imagen |
| `charts/microservice/values.yaml` | image.repository -> ghcr.io/YOUR_USERNAME/... |
| `charts/microservice/values-dev.yaml` | image.tag stale -> latest |
| `charts/microservice/templates/configmap.yaml` | HEALTH_SHOW_DETAILS -> MANAGEMENT_ENDPOINT_HEALTH_SHOW_DETAILS |
| `k8s/argocd/application.yaml` | targetRevision feature/21 -> main |
| `src/src/main/resources/application.yml` | health probes configuradas |
| `src/.../HealthController.java` | ELIMINADO (Actuator nativo) |
| `docs/deployment.md` | base64 multiplataforma |
