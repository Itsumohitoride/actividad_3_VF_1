# Arquitectura — K8S Microservices

## Diagrama de arquitectura K8S

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                          │
│                                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   Namespace  │    │   Namespace  │    │   Namespace  │          │
│  │     dev      │    │   staging    │    │     prod     │          │
│  │              │    │              │    │              │          │
│  │  ┌────────┐  │    │  ┌────────┐  │    │  ┌────────┐  │          │
│  │  │Micro-  │  │    │  │Micro-  │  │    │  │Micro-  │  │          │
│  │  │service │  │    │  │service │  │    │  │service │  │          │
│  │  │ Pod    │  │    │  │ Pod    │  │    │  │ Pod    │  │          │
│  │  │ :8080  │  │    │  │ :8080  │  │    │  │ :8080  │  │          │
│  │  └────────┘  │    │  └────────┘  │    │  └────────┘  │          │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘          │
│         │                   │                   │                  │
│         └───────────────────┼───────────────────┘                  │
│                             │                                      │
│                    ┌────────┴────────┐                             │
│                    │  ArgoCD         │                             │
│                    │  (argocd ns)    │                             │
│                    │  auto-sync      │                             │
│                    │  self-heal      │                             │
│                    │  prune          │                             │
│                    └────────┬────────┘                             │
│                             │                                      │
│                    ┌────────┴────────┐                             │
│                    │  GitHub Repo    │                             │
│                    │  Helm charts/   │                             │
│                    │  K8s manifests  │                             │
│                    └─────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

## Flujo CI/CD (GitOps)

```
                    ┌──────────────┐
                    │  Developer   │
                    │  git push    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  GitHub      │
                    │  Actions     │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼                         ▼
     ┌────────────────┐       ┌────────────────┐
     │  CI Pipeline   │       │  CD Pipeline   │
     │  - gradle build│       │  - docker build│
     │  - gradle test │       │  - push ghcr.io│
     │  - gradle check│       │  - update Helm │
     │  - quality gate│       │    values tag   │
     └────────────────┘       └───────┬────────┘
                                      │
                                      ▼
                             ┌────────────────┐
                             │  Git commit    │
                             │  (new tag)     │
                             └───────┬────────┘
                                     │
                                     ▼
                             ┌────────────────┐
                             │  ArgoCD        │
                             │  auto-sync     │
                             └───────┬────────┘
                                     │
                                     ▼
                             ┌────────────────┐
                             │  K8s Pod       │
                             │  rolling update│
                             └────────────────┘
```

## Componentes

### Microservicio (Spring Boot)
- **Framework:** Spring Boot 3.2.5 + JDK 21
- **Build:** Gradle (multi-stage Docker)
- **Endpoints:** `/actuator/health`, `/api/v1/products`
- **Health:** Liveness + Readiness probes via Actuator

### Helm Charts
- **Chart:** `charts/microservice/`
- **Templates:** deployment, service, ingress, configmap, hpa
- **Entornos:** dev, staging, prod (values-{env}.yaml)

### ArgoCD (GitOps)
- **Namespace:** `argocd`
- **Project:** `microservice` (AppProject CRD)
- **Application:** `microservice-dev` con auto-sync, self-heal, prune
- **Source:** GitHub repo → Helm chart con values-dev.yaml

### CI/CD (GitHub Actions)
- **CI:** Build, test, lint, quality gates en push/PR
- **CD:** Docker build+push a ghcr.io, actualiza Helm values, commit
- **Auto-deploy:** ArgoCD detecta cambio en Git y sincroniza

## Stack tecnologico

| Capa | Tecnologia |
|------|-----------|
| Lenguaje | Java 21 |
| Framework | Spring Boot 3.2.5 |
| Build | Gradle 8.x |
| Container | Docker (multi-stage) |
| Orquestacion | Docker Compose (local), Kubernetes (produccion) |
| Paqueteria | Helm 3.x |
| GitOps | ArgoCD 2.10 |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry (ghcr.io) |

## Flujo de datos

```
Cliente HTTP
    │
    ▼
┌────────────────┐
│  Service       │  ClusterIP:80 → Pod:8080
│  (K8s Service) │
└────────┬───────┘
         │
         ▼
┌────────────────┐
│  Ingress       │  (opcional, deshabilitado en dev)
│  (K8s Ingress) │
└────────┬───────┘
         │
         ▼
┌────────────────┐
│  Microservice  │  Spring Boot → /api/v1/products
│  Pod :8080     │             → /actuator/health
└────────────────┘
```
