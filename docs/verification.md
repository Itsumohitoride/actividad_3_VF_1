# Verificacion — K8S Microservices (Spring Boot + Gradle Containerized)

## Como verificar el trabajo

### Feature completada
1. Microservicio Spring Boot corre localmente con docker compose
2. Docker image se construye sin errores (Gradle build dentro del contenedor)
3. Helm lint pasa sin errores
4. Helm template genera manifiestos K8s validos
5. ArgoCD Application configurada y sincronizada
6. Pipeline CI/CD configurado en GitHub Actions
7. Documentacion actualizada (docs/)
8. `python3 scripts/check_harness.py` — todo verde

### Antes de marcar done
- [ ] `docker build --no-cache .` — exit 0 (Gradle build dentro del contenedor)
- [ ] `docker compose up --build -d` — servicio responde
- [ ] `curl localhost:8080/actuator/health` — 200 OK
- [ ] `helm lint ./charts/*` — 0 errors, 0 warnings
- [ ] `helm template ./charts/* --values values-dev.yaml` — manifiestos YAML validos
- [ ] `kubectl apply --dry-run=client -f <manifest>` — manifiestos K8s validos
- [ ] ArgoCD app status = Synced + Healthy
- [ ] Pipeline CI/CD configurado en .github/workflows/
- [ ] Todos los criterios de aceptacion cumplidos

### Checklist por Feature

#### F19: Microservicio Spring Boot + Gradle
- [ ] Dockerfile multi-stage (gradle:8-jdk21 builder + jre21 runtime)
- [ ] Gradle build ejecutado dentro del contenedor
- [ ] Non-root user en runtime
- [ ] HEALTHCHECK via wget /actuator/health
- [ ] Endpoints: /actuator/health y /api/v1/* funcionales
- [ ] docker build exit 0
- [ ] docker compose up sin errores
- [ ] No requiere Java/Gradle en host

#### F20: Helm Charts
- [ ] Chart.yaml completo
- [ ] Templates: deployment, service, ingress, configmap, hpa
- [ ] _helpers.tpl con labels reutilizables
- [ ] values.yaml + values-{env}.yaml
- [ ] helm lint exit 0
- [ ] helm template genera YAML validos

#### F21: ArgoCD + GitOps
- [ ] ArgoCD instalado en cluster
- [ ] Repositorio Git configurado
- [ ] Application con auto-sync, self-heal, prune
- [ ] Health checks (Actuator) funcionando
- [ ] Documentacion de UI y CLI

#### F22: CI/CD Pipelines
- [ ] CI workflow: docker build + test + lint en push
- [ ] CD workflow: push image + deploy
- [ ] Quality gates implementados
- [ ] Notificaciones configuradas
- [ ] Documentacion del pipeline

#### F23: Documentacion
- [ ] README.md completo
- [ ] docs/architecture.md actualizado
- [ ] docs/deployment.md con rollback
- [ ] docs/configuration.md completo
- [ ] docs/verification.md actualizado
- [ ] Codigo comentado (Javadoc)

#### F24: Video Demo Script
- [ ] Timeline minuto a minuto
- [ ] Dialogos sugeridos
- [ ] Capturas de pantalla listadas
- [ ] Duracion 5-10 min
