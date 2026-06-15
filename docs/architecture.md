# K8S Microservices — Arquitectura

## Proposito

Proyecto educativo para implementar un microservicio Java Spring Boot desplegable individualmente utilizando contenedores Docker, orquestador Kubernetes, Helm para gestion de paquetes/configuraciones, ArgoCD para GitOps, y pipelines CI/CD automatizados.

Build 100% containerizado — no requiere Java ni Gradle en el host.

## Arquitectura del Sistema

```
┌──────────────────────────────────────────────────────────┐
│                    Git Repository                         │
│  src/ (Spring Boot + Gradle), charts/, .github/workflows │
└──────────────┬───────────────────────────────────────────┘
               │ push/PR
               ▼
┌──────────────────────────────────────────────────────────┐
│                 CI/CD Pipeline (GitHub Actions)           │
│  docker build → test → lint → scan → push → deploy      │
│  (todo dentro de contenedores, no requiere JDK en runner) │
└──────────────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│                 Container Registry                        │
│  ghcr.io/namespace/microservice:sha                      │
└──────────────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Spring Boot  │  │   ArgoCD    │  │   Ingress       │  │
│  │ Deployment   │  │ Application │  │   Controller    │  │
│  │ Service      │  │ Controller  │  │                 │  │
│  │ HPA          │  │             │  │                 │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
│  Namespaces: dev, staging, production                    │
└──────────────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│                    GitOps (ArgoCD)                        │
│  Auto-sync desde Git repo → estado cluster              │
│  Self-heal: corrige desviaciones                         │
│  Prune: elimina recursos no declarados                   │
└──────────────────────────────────────────────────────────┘
```

## Componentes

### 1. Microservicio Spring Boot
- API REST con Java 21+, Spring Boot 3.x
- Build: Gradle (build.gradle) — **ejecutado dentro del contenedor Docker**
- Endpoints: /actuator/health, /api/v1/*
- JAR ejecutable construido en builder stage
- Sin Java/Gradle en el host

### 2. Docker (Containerized Build)
- Multi-stage: builder (gradle:8-jdk21) + runtime (eclipse-temurin:21-jre-alpine)
- Gradle build dentro del contenedor: `RUN gradle clean build`
- Non-root user en stage final
- HEALTHCHECK via wget al endpoint /actuator/health
- .dockerignore para build eficiente

### 3. Helm Charts
- Chart.yaml con metadatos
- Templates: deployment, service, ingress, configmap, hpa
- values.yaml con defaults + overrides por ambiente

### 4. Kubernetes
- Cluster local (Docker Desktop K8s, Minikube, kind)
- Namespaces por ambiente (dev, staging, prod)
- Deployments con replicas, resource limits, probes
- Services (ClusterIP, NodePort)
- Ingress para routing externo
- HPA para auto-escalado

### 5. ArgoCD
- GitOps: Git como fuente unica de verdad
- Application CRD con source Helm y destination K8s
- Auto-sync con self-heal y prune
- UI para visualizar estado del cluster

### 6. CI/CD (GitHub Actions)
- Workflow CI: build imagen Docker, test, lint en cada push/PR
- Workflow CD: push imagen + deploy automatico
- Quality gates: tests pasan dentro del contenedor
- Sin JDK en runner — todo via Docker

## Flujo de Despliegue

```
Developer commit → GitHub push → GitHub Actions
    → docker build (Gradle build dentro del contenedor)
    → docker push a ghcr.io
    → ArgoCD detects drift → sync cluster
    → rolling update deployment → health check via Actuator
```

## Stack Tecnologico

| Componente | Tecnologia |
|------------|-----------|
| Microservicio | Java 21+, Spring Boot 3.x |
| Build | Gradle 8+ (ejecutado en contenedor Docker) |
| Contenedor build | gradle:8-jdk21-alpine |
| Contenedor runtime | eclipse-temurin:21-jre-alpine |
| Orquestador | Kubernetes (Docker Desktop / Minikube) |
| Paquetes | Helm 3+ |
| GitOps | ArgoCD |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry (ghcr.io) |
| Health Check | Spring Boot Actuator (/actuator/health) |
