# Configuracion — K8S Microservices (Spring Boot + Gradle)

## application.yml

```yaml
server:
  port: ${PORT:8080}

spring:
  application:
    name: ${APP_NAME:product-service}
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: ${HEALTH_SHOW_DETAILS:always}
```

## application-dev.yml

```yaml
server:
  port: 8080
logging:
  level:
    com.ecommify: DEBUG
```

## Variables de Entorno del Microservicio

| Variable | Descripcion | Default | Ejemplo |
|----------|-------------|---------|---------|
| PORT | Puerto del servidor HTTP | 8080 | 8080 |
| SPRING_PROFILES_ACTIVE | Perfil activo | dev | dev, staging, production |
| APP_NAME | Nombre de la aplicacion | product-service | product-service |
| HEALTH_SHOW_DETAILS | Detalles del health check | always | always, never, when-authorized |

## Helm Values (values.yaml)

### values.yaml — defaults

```yaml
global:
  environment: development

image:
  repository: ghcr.io/namespace/microservice
  tag: latest
  pullPolicy: IfNotPresent

replicaCount: 1

resources:
  requests:
    cpu: 250m
    memory: 512Mi
  limits:
    cpu: 1
    memory: 1Gi

livenessProbe:
  httpGet:
    path: /actuator/health
    port: http
  initialDelaySeconds: 30
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /actuator/health
    port: http
  initialDelaySeconds: 15
  periodSeconds: 10

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: false
  host: microservice.local
  tls: false
  tlsSecret: ""

config:
  springProfilesActive: dev
  healthShowDetails: always

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

### values-dev.yaml

```yaml
global:
  environment: development
replicaCount: 1
image:
  tag: latest
  pullPolicy: Always
service:
  type: NodePort
ingress:
  enabled: false
config:
  springProfilesActive: dev
```

### values-prod.yaml

```yaml
global:
  environment: production
replicaCount: 3
image:
  tag: latest
  pullPolicy: IfNotPresent
ingress:
  enabled: true
  host: api.microservice.com
  tls: true
  tlsSecret: microservice-tls
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
config:
  springProfilesActive: prod
```

## Estructura de Archivos de Configuracion

| Archivo | Formato | Proposito |
|---------|---------|-----------|
| src/main/resources/application.yml | YAML | Config Spring Boot base |
| src/main/resources/application-dev.yml | YAML | Config desarrollo |
| src/main/resources/application-prod.yml | YAML | Config produccion |
| build.gradle o build.gradle.kts | Groovy/Kotlin | Build tool config |
| Dockerfile | Dockerfile | Multi-stage build |
| docker-compose.yml | YAML | Orquestacion local |
| charts/values.yaml | YAML | Helm defaults |
| charts/values-{env}.yaml | YAML | Overrides por ambiente |
| .github/workflows/ | YAML | CI/CD pipelines |
