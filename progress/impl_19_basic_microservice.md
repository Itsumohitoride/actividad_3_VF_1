# F19: Microservicio Spring Boot + Gradle (containerized build)

## Estado: implementada

## Archivos creados

| Archivo | Descripcion |
|---------|-------------|
| `src/build.gradle.kts` | Gradle build: Spring Boot 3.2.5, Java 21, web + actuator + test |
| `src/settings.gradle.kts` | Root project name: product-service |
| `src/src/main/java/com/ecommify/product/ProductServiceApplication.java` | @SpringBootApplication main |
| `src/src/main/java/com/ecommify/product/controller/HealthController.java` | GET /actuator/health returns {"status":"UP"} |
| `src/src/main/java/com/ecommify/product/controller/ProductController.java` | GET /api/v1/products, dummy list |
| `src/src/main/resources/application.yml` | server.port=8080, actuator, app name |
| `src/src/main/resources/application-dev.yml` | logging DEBUG for com.ecommify |
| `src/src/test/java/com/ecommify/product/ProductServiceApplicationTests.java` | Context load test |
| `Dockerfile` | Multi-stage: gradle:8-jdk21-alpine (builder) + eclipse-temurin:21-jre-alpine (runtime) |
| `docker-compose.yml` | product-service: build ., ports 8080:8080, SPRING_PROFILES_ACTIVE=dev |
| `.dockerignore` | .git, .gradle, build, .dockerignore, *.md, .gitignore |

## Detalles del Dockerfile

- **Builder:** gradle:8-jdk21-alpine, WORKDIR /app, COPY build.gradle.kts + settings.gradle.kts + src/, RUN gradle clean build --no-daemon -x test
- **Runtime:** eclipse-temurin:21-jre-alpine, non-root user (appuser), HEALTHCHECK via wget /actuator/health, EXPOSE 8080
- **JAR path:** /app/build/libs/*.jar

## Verification plan

1. `docker build --no-cache -t product-service:latest .`
2. `docker compose up --build -d`
3. `curl http://localhost:8080/actuator/health`
4. `curl http://localhost:8080/api/v1/products`
5. `docker compose down`

## Issues

- Ninguno detectado hasta ahora.
