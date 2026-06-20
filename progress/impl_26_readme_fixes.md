# F26: Fix README inconsistencies and deployment blockers

## Estado: implementada

## Problemas corregidos

| # | Archivo | Problema | Fix |
|---|---------|----------|-----|
| 1 | `charts/microservice/values.yaml` | `image.repository: ghcr.io/namespace/microservice` (placeholder invalido) | `ghcr.io/YOUR_USERNAME/actividad-3-vf-1-microservice` |
| 2 | `charts/microservice/values-dev.yaml` | `image.tag: 07ab88c` (SHA stale) | `latest` |
| 3 | `k8s/argocd/application.yaml` | `targetRevision: feature/21-argocd-gitops` (branch no usada en CD) | `main` |
| 4 | `src/src/main/resources/application.yml` | Sin config para health probes K8s | Agregado `endpoint.health.show-details` y `probes.enabled` |
| 5 | `src/.../HealthController.java` | Custom controller sobreescribia Actuator | Eliminado - Actuator nativo maneja /actuator/health |
| 6 | `charts/microservice/templates/configmap.yaml` | `HEALTH_SHOW_DETAILS` no es env var Spring Boot valida | `MANAGEMENT_ENDPOINT_HEALTH_SHOW_DETAILS` |
| 7 | `README.md` | docker build redundante, base64 sin Windows, sin prerequisito push imagen | Multiples correcciones |

## Verification

- `grep HealthController` -> 0 resultados (archivo eliminado)
- `image.repository` actualizado a placeholder claro
- `targetRevision` apunta a `main`
- Health probes habilitadas en application.yml
- README refleja comandos correctos y multiplataforma
