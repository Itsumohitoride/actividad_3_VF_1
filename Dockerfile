FROM gradle:8-jdk21-alpine AS builder

WORKDIR /app

COPY src/build.gradle.kts src/settings.gradle.kts ./
COPY src/src/ src/

RUN gradle clean build --no-daemon -x test

FROM eclipse-temurin:21-jre-alpine

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --from=builder /app/build/libs/*.jar app.jar

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "/app.jar"]
