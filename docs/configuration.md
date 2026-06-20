# Configuracion — K8S Microservices

## Variables de entorno

El microservicio acepta las siguientes variables de entorno:

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `SERVER_PORT` | `8080` | Puerto del servidor HTTP |
| `SPRING_PROFILES_ACTIVE` | `dev` | Perfil activo de Spring Boot |
| `MANAGEMENT_HEALTH_SHOW_DETAILS` | `always` | Nivel de detalle del health endpoint |

## Configuracion Spring Boot

### application.properties / application.yml

El microservicio usa la configuracion por defecto de Spring Boot con Actuador:

```properties
server.port=${SERVER_PORT:8080}
spring.application.name=microservice
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=${MANAGEMENT_HEALTH_SHOW_DETAILS:always}
```

### Perfiles

Los perfiles se configuran via `SPRING_PROFILES_ACTIVE` o el chart de Helm:

| Perfil | Uso |
|--------|-----|
| `dev` | Desarrollo local (default) |
| `staging` | Entorno de pre-produccion |
| `prod` | Produccion |

## Configuracion via Helm

### values.yaml (base)

```yaml
image:
  repository: ghcr.io/namespace/microservice
  tag: latest
  pullPolicy: IfNotPresent

replicaCount: 1

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

config:
  springProfilesActive: dev
  healthShowDetails: always
```

### values-dev.yaml (desarrollo)

```yaml
environment: development

image:
  tag: latest
  pullPolicy: Always

service:
  type: NodePort

config:
  springProfilesActive: dev
```

### values-staging.yaml

```yaml
environment: staging

replicaCount: 2

image:
  tag: staging
  pullPolicy: IfNotPresent

service:
  type: ClusterIP

config:
  springProfilesActive: staging
```

### values-prod.yaml

```yaml
environment: production

replicaCount: 3

image:
  tag: stable
  pullPolicy: IfNotPresent

service:
  type: ClusterIP

ingress:
  enabled: true
  host: microservice.example.com

config:
  springProfilesActive: prod
```

## Configuracion ArgoCD

La Application de ArgoCD se configura en `k8s/argocd/application.yaml`:

| Campo | Valor | Descripcion |
|-------|-------|-------------|
| `spec.source.repoURL` | `https://github.com/Itsumohitoride/actividad_3_VF_1.git` | Repositorio Git |
| `spec.source.path` | `charts/microservice` | Path del Helm chart |
| `spec.source.targetRevision` | `develop` | Rama Git |
| `spec.source.helm.valueFiles` | `[values-dev.yaml]` | Valores por entorno |
| `spec.destination.namespace` | `dev` | Namespace destino |

## Configuracion CI/CD

Los workflows de GitHub Actions usan:

- **GitHub Container Registry** (`ghcr.io`) para imagenes Docker
- **GITHUB_TOKEN** con permisos `contents: write` y `packages: write`
- **Docker Buildx** para build multi-plataforma
- **Gradle cache** via `actions/setup-java` con `cache: gradle`

## Secretos requeridos

| Secreto | Donde se usa | Descripcion |
|---------|-------------|-------------|
| `GITHUB_TOKEN` | CD workflow | Automático, permisos: contents+packages write |

> Para entornos on-premises, configurar credenciales de registry Docker
> via `imagePullSecrets` en el Deployment de Kubernetes.

