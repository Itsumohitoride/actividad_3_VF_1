# Convenciones de Codigo — K8S Microservices (Spring Boot + Gradle Containerized)

## Stack: Java / Spring Boot / Gradle / Docker / Kubernetes / Helm

### Java / Spring Boot

| Aspecto | Convencion |
|---------|-----------|
| Java version | 21 LTS (dentro del contenedor) |
| Spring Boot | 3.x |
| Build tool | Gradle 8+ (build.gradle o build.gradle.kts) |
| Packaging | JAR (no WAR) |
| Application config | application.yml (YAML) |
| Profile config | application-{profile}.yml (dev, staging, prod) |
| Puerto default | 8080 |
| Health endpoint | /actuator/health (Spring Boot Actuator) |
| Base path API | /api/v1/ |

### Estilo de Codigo Java

| Aspecto | Convencion |
|---------|-----------|
| Package naming | com.ecommify.{module} (ej: com.ecommify.product) |
| Clases | PascalCase: ProductController, OrderService |
| Metodos | camelCase: getProductById(), createOrder() |
| Variables | camelCase: productId, customerName |
| Constantes | UPPER_SNAKE: MAX_RETRY_COUNT |
| Controller | @RestController, @RequestMapping("/api/v1/...") |
| Service | @Service, inyeccion por constructor |
| Repository | @Repository o Spring Data JPA |
| DTO | sufijo DTO: ProductRequest, OrderResponse |
| Exceptions | @RestControllerAdvice + ErrorResponse DTO |
| Tests | JUnit 5 + Mockito |

### Containerized Build (no Java/Gradle local)

| Aspecto | Convencion |
|---------|-----------|
| Build local | `docker build --no-cache -t microservice:latest .` |
| Dev local | `docker compose up --build -d` |
| CI/CD build | `docker build .` (GitHub Actions) |
| Gradle cache | Cache layer en Dockerfile (COPY gradle/ primero) |
| Gradle wrapper | NO necesario (usamos imagen oficial gradle:8) |

### Dockerfile

| Aspecto | Convencion |
|---------|-----------|
| Builder image | gradle:8-jdk21-alpine |
| Runtime image | eclipse-temurin:21-jre-alpine |
| Gradle build | RUN gradle clean build --no-daemon |
| Usuario runtime | USER 1001 (non-root) |
| HEALTHCHECK | CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health |
| EXPOSE | 8080 |
| JAR copia | COPY --from=builder /home/gradle/src/build/libs/*.jar app.jar |
| Entrypoint | java -jar /app.jar |

### Docker Compose

| Aspecto | Convencion |
|---------|-----------|
| Build | context: ., dockerfile: Dockerfile |
| Puertos | 8080:8080 |
| Volumenes | Opcional: gradle cache persistente |
| Profiles | SPRING_PROFILES_ACTIVE=dev via env |

### Kubernetes Manifests

| Aspecto | Convencion |
|---------|-----------|
| API version | apps/v1, v1, networking.k8s.io/v1 |
| Nombres | kebab-case: product-service, app-config |
| Labels | app, version, tier, environment |
| Namespaces | dev, staging, production |
| Resources | requests + limits CPU/memory siempre |
| Probes | liveness: /actuator/health, readiness: /actuator/health |
| Pull policy | Always en dev, IfNotPresent en prod |

### Helm

| Aspecto | Convencion |
|---------|-----------|
| Chart name | kebab-case |
| Templates | deployment.yaml, service.yaml, ingress.yaml, configmap.yaml, hpa.yaml |
| Helpers | _helpers.tpl con labels, selectors, names |
| Values | values.yaml (defaults), values-{env}.yaml (overrides) |
| Version | SemVer en Chart.yaml |
| App version | Coincide con appVersion (tag de imagen) |

### GitHub Actions

| Aspecto | Convencion |
|---------|-----------|
| Workflow name | PascalCase: CI Pipeline, CD Deploy |
| Triggers | push, pull_request en ramas especificas |
| Jobs | build (docker build), test, lint, scan, push, deploy |
| JDK setup | NO necesario — build dentro del contenedor |
| Steps | Nombres descriptivos |
| Secrets | ${{ secrets.X }} nunca valores hardcodeados |

### Nombres

| Recurso | Convencion | Ejemplo |
|---------|-----------|---------|
| Microservicio | kebab-case | product-service, order-api |
| Docker image | lowercase | product-service:1.0.0 |
| K8s deployment | kebab-case | product-service-deployment |
| K8s service | kebab-case | product-service-svc |
| ConfigMap | kebab-case | app-config |
| Helm chart | kebab-case | product-service-chart |
| Namespace | lowercase | dev, staging, production |
| Git branch | feature/<id>-<name> | feature/19-spring-boot-microservice |

### Buenas Practicas

1. **Containerized build** — nunca instalar Java/Gradle local, todo via Docker
2. **Cache eficiente** — COPY gradle/ y build.gradle primero para cachear layers
3. **Stateless** — microservicio sin estado local (usar DB externa)
4. **Actuator** — health, info, metrics endpoints habilitados
5. **Recursos** — definir siempre requests y limits en K8s
6. **Seguridad** — non-root en Docker, no secrets en imagenes, .dockerignore
7. **Rollback** — documentar procedimiento antes de deploy
8. **GitOps** — nunca modificar cluster manualmente, solo via Git
9. **Testing** — JUnit 5 tests unitarios ejecutados dentro del contenedor
