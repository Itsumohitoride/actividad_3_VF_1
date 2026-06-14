# Sesion actual — Actividad 3: K8S Microservices

## Feature activa

| # | Feature | Status |
|---|---------|--------|
| 19 | basic_microservice | in_progress |
| 20 | helm_charts | pending |
| 21 | argocd_gitops | pending |
| 22 | ci_cd_pipelines | pending |
| 23 | documentation | pending |
| 24 | video_demo_script | pending |

## F19: Microservicio Spring Boot + Gradle (containerized build)

- Branch: feature/19-spring-boot-microservice
- Inicio: 2026-06-14
- Build 100% containerizado (solo Docker Desktop necesario)
- Stack: Java 21, Spring Boot 3, Gradle 8
- Plan:
  1. Crear proyecto Spring Boot con Gradle (build.gradle.kts)
  2. MainApplication, HealthController, ApiController
  3. application.yml con Actuator
  4. Dockerfile multi-stage
  5. docker-compose.yml
  6. .dockerignore + .gitignore
  7. Verificar: docker build + docker compose up
