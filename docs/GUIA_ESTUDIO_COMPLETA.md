# GUIA DE ESTUDIO COMPLETA - K8S Microservices (Actividad 3 VF)

> **Proposito:** Entender que hace cada archivo del proyecto, por que existe, y como responde a cada punto de la guia.
> **Archivo personal de estudio** - no se sube al repositorio.

---

## 1. MAPA GUIA -> PROYECTO

### Punto A: Microservicio + Docker
| Archivo | Que hace |
|---------|----------|
| src/main/java/.../ProductServiceApplication.java | Entry point Spring Boot |
| src/main/java/.../ProductController.java | API REST /api/v1/products |
| src/build.gradle.kts | Build: plugins, dependencias, JDK 21 |
| Dockerfile | Multi-stage: compila JAR + runtime JRE |
| docker-compose.yml | Orquestacion local sin K8s |

### Punto B: Helm Charts
| Archivo | Que hace |
|---------|----------|
| charts/microservice/Chart.yaml | Metadata del chart |
| charts/microservice/values.yaml | Valores por defecto |
| charts/microservice/values-dev.yaml | Override desarrollo |
| charts/microservice/values-staging.yaml | Override staging |
| charts/microservice/values-prod.yaml | Override produccion |
| charts/microservice/templates/deployment.yaml | Template Deployment |
| charts/microservice/templates/service.yaml | Template Service |
| charts/microservice/templates/ingress.yaml | Template Ingress |
| charts/microservice/templates/configmap.yaml | Template ConfigMap |

### Punto C: ArgoCD
| Archivo | Que hace |
|---------|----------|
| k8s/argocd/namespace.yaml | Crea namespace argocd |
| k8s/argocd/project.yaml | AppProject que agrupa aplicaciones |
| k8s/argocd/application.yaml | Application GitOps: apunta al repo + chart + auto-sync |
| k8s/argocd/kustomization.yaml | Kustomize para aplicar todo junto |

### Punto D: CI/CD Pipelines
| Archivo | Que hace |
|---------|----------|
| .github/workflows/ci.yml | CI: build + test + lint en push a develop/feature |
| .github/workflows/cd.yml | CD: Docker build+push + update Helm values + commit |

### Punto E: Tecnologias
- **Docker** -> Dockerfile, docker-compose.yml, cd.yml
- **Kubernetes** -> charts/microservice/templates/
- **CI** -> .github/workflows/ci.yml
- **ArgoCD** -> k8s/argocd/
- **Helm** -> charts/microservice/

---

## 2. ESTRUCTURA DEL PROYECTO

`
actividad_3_VF_1/
  .github/workflows/      - CI/CD pipelines (ci.yml, cd.yml)
  charts/microservice/    - Helm chart (templates + values)
  docs/                   - Documentacion adicional
  k8s/argocd/             - Manifiestos ArgoCD
  src/                    - Codigo fuente Java Spring Boot
  Dockerfile              - Multi-stage build
  docker-compose.yml      - Orquestacion local
  README.md               - Documentacion principal
`

---

## 3. MICROSERVICIO SPRING BOOT

### 3.1 build.gradle.kts

Define como se compila el proyecto:

- **plugins { java }**: compila .java a .class, genera JAR
- **spring-boot 3.2.5**: empaqueta fat-JAR ejecutable
- **dependency-management 1.1.4**: importa BOM de Spring Boot (versiones consistentes)
- **group/version**: identifican el artefacto
- **JavaLanguageVersion.of(21)**: JDK 21 (Spring Boot 3.2 requiere >= 17)
- **mavenCentral()**: repositorio publico de dependencias
- **spring-boot-starter-web**: Tomcat + Spring MVC (para REST)
- **spring-boot-starter-actuator**: health checks, metrics (esencial para K8s)
- **spring-boot-starter-test**: JUnit 5, Mockito
- **useJUnitPlatform()**: Configura JUnit 5

### 3.2 ProductServiceApplication.java

Entry point. Anotacion @SpringBootApplication combina:
1. @Configuration: fuente de beans
2. @EnableAutoConfiguration: Spring configura automaticamente segun classpath
3. @ComponentScan: escanea paquete en busca de componentes

SpringApplication.run() inicia Tomcat en puerto 8080.

### 3.3 ProductController.java

API REST con un solo endpoint GET /api/v1/products. Retorna lista quemada de productos (Laptop, Mouse, Keyboard) como JSON.

- @RestController: retorna JSON directamente
- @RequestMapping("/api/v1/products"): prefijo de ruta (versionado)
- @GetMapping: maneja HTTP GET
- ResponseEntity.ok(products): HTTP 200 + body

Datos hardcoded para demostracion. En produccion se conectaria a BD.

### 3.4 application.yml

Configuracion Spring Boot:
- server.port: 8080 (Tomcat)
- spring.application.name: product-service
- management: expone solo health e info (seguridad), detalles siempre visibles, probes habilitadas

Las probes (/actuator/health/liveness y /readiness) son usadas por K8s.

### 3.5 application-dev.yml

Activa logging DEBUG para com.ecommify via SPRING_PROFILES_ACTIVE=dev.

### 3.6 ProductServiceApplicationTests.java

Test de integracion: @SpringBootTest arranca el contexto completo. Si falla, hay error de configuracion.

---

## 4. DOCKERIZACION

### 4.1 Dockerfile - Multi-stage

Stage 1 - Builder:
- FROM gradle:8-jdk21-alpine (Gradle + JDK 21, ~300MB)
- COPY build.gradle.kts + settings.gradle.kts primero (caching)
- COPY src/ (codigo fuente)
- RUN gradle clean build --no-daemon -x test (compila JAR, salta tests)

Stage 2 - Runtime:
- FROM eclipse-temurin:21-jre-alpine (solo JRE, ~50MB)
- Crea usuario no-root (appuser) por seguridad
- COPY --from=builder /app/build/libs/*.jar app.jar
- USER appuser (no se ejecuta como root)
- EXPOSE 8080 (documenta puerto)
- HEALTHCHECK via wget /actuator/health cada 30s
- ENTRYPOINT ["java", "-jar", "/app.jar"]

Beneficio multi-stage: imagen final ~50MB vs ~300MB. Mas segura (sin herramientas de build).

### 4.2 docker-compose.yml

Orquestacion local: build . , puerto 8080:8080, SPRING_PROFILES_ACTIVE=dev.

### 4.3 .dockerignore

Excluye .git, .gradle, build/ del contexto Docker (imagen mas pequena, build mas rapido).

---

## 5. HELM CHARTS

Helm es el gestor de paquetes de K8s. Charts = templates YAML parametrizables.

### 5.1 Chart.yaml

apiVersion v2, name microservice, type application, version 0.1.0, appVersion 1.0.0.

### 5.2 values.yaml - Valores default

- environment: development
- replicaCount: 1 (pods)
- image: repository, tag, pullPolicy (IfNotPresent)
- resources: requests 250m CPU/512Mi RAM, limits 1 CPU/1Gi RAM
- service: ClusterIP, port 80, targetPort 8080
- ingress: disabled
- config: springProfilesActive dev, healthShowDetails always

### 5.3 Overrides por entorno

values-dev.yaml: 1 replica, tag latest, pullPolicy Always (siempre descarga), NodePort (accesible desde host).

values-staging.yaml: 2 replicas, ingress habilitado (staging.microservice.com), sin TLS.

values-prod.yaml: 3 replicas, ingress habilitado (api.microservice.com).

### 5.4 Templates

deployment.yaml: Define Deployment con:
- image desde values
- envFrom ConfigMap (variables de entorno)
- liveness/readiness probes
- resources requests/limits

service.yaml: Service tipo ClusterIP/NodePort. Selector por labels para encontrar pods.

ingress.yaml: Solo se genera si ingress.enabled=true.

configmap.yaml: SPRING_PROFILES_ACTIVE y HEALTH_SHOW_DETAILS como env vars.

Las labels se definen inline en cada template (app.kubernetes.io/name, instance, environment, etc.). Sin helpers externos para mantener cada template autocontenido.

### 5.5 Como funciona Helm

1. helm install -> Lee Chart.yaml -> Carga values.yaml + override -> Procesa templates Go -> Envia YAML a K8s -> K8s crea recursos.


---

## 6. ARGOCD - GITOPS

ArgoCD implementa GitOps: el estado deseado del cluster esta en Git, ArgoCD sincroniza automaticamente.

### 6.1 Componentes de ArgoCD

| Componente | Funcion |
|-----------|---------|
| argocd-server (Deployment+Service) | API + UI. Puertos 8080 (HTTP), 8083 (gRPC) |
| argocd-application-controller (StatefulSet) | Monitorea apps, corrige desviaciones (self-heal) |
| argocd-repo-server (Deployment) | Clona repos Git, cachea charts |
| argocd-redis (Deployment+Service) | Cache para repo-server |

### 6.2 project.yaml (AppProject)

Agrupa aplicaciones ArgoCD. Define destinos (dev, staging, prod) y repos permitidos.

### 6.3 application.yaml (EL CORAZON DE GITOPS)

- source.repoURL: repositorio Git del chart
- source.path: charts/microservice
- source.helm.valueFiles: [values-dev.yaml]
- destination: cluster local, namespace dev
- syncPolicy.automated:
  - prune: true (elimina recursos que ya no estan en Git)
  - selfHeal: true (revierte cambios manuales)
  - CreateNamespace=true
  - retry: 5 reintentos con backoff

### 6.4 Flujo GitOps

Developer push -> CI/CD (build+push+commit) -> ArgoCD detecta cambio -> Auto-sync -> Rolling update

### 6.5 kustomization.yaml

1. Crear namespace: kubectl apply -f k8s/argocd/namespace.yaml
2. Instalar ArgoCD directamente: kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.10.0/manifests/install.yaml
3. Aplicar recursos custom: kubectl apply -k k8s/argocd/

---

## 7. CI/CD - GITHUB ACTIONS

### 7.1 CI Pipeline (ci.yml)

Triggers: push a develop/feature/*, PR a develop.

Jobs:
1. Build & Test: checkout, JDK 21, gradle build, gradle test, upload reports
2. Quality Gates: gradle check, gradle dependencies

### 7.2 CD Pipeline (cd.yml)

Trigger: SOLO push a develop.

Pasos:
1. Checkout con GITHUB_TOKEN (contents:write + packages:write)
2. Login a GHCR
3. Docker Buildx (cache de capas)
4. Metadata: tags = SHA corto + latest
5. Build + push imagen a ghcr.io
6. Update Helm values: reemplaza tag con nuevo SHA
7. Commit + push con [skip ci]

### 7.3 Flujo completo

git push develop -> CI (build+test) -> CD (build+push+update) -> ArgoCD auto-sync -> nuevo pod

---

## 8. GLOSARIO

| Concepto | Explicacion |
|----------|-------------|
| Microservicio | App dividida en servicios independientes |
| Spring Boot | Framework Java con Tomcat embebido |
| Gradle | Build tool: compila, dependencias, tests |
| Docker | Contenerizacion |
| Multi-stage | 2 etapas: builder (pesado) + runtime (ligero) |
| Kubernetes (K8s) | Orquestador de contenedores |
| Pod | Unidad minima de K8s |
| Deployment | Gestiona replicas, updates, rollbacks |
| Service | IP/DNS estable para pods |
| Ingress | Exponer servicios fuera del cluster |
| ConfigMap | Config no sensible como env vars |
| Helm | Gestor de paquetes K8s |
| ArgoCD | GitOps: Git como fuente de verdad |
| Auto-sync | Aplica cambios de Git automaticamente |
| Self-heal | Revierte cambios manuales |
| Prune | Elimina recursos que ya no existen en Git |
| Liveness | Sonda: esta vivo? Si no, reinicia |
| Readiness | Sonda: acepta trafico? Si no, no envia |
| Rolling update | Actualiza pods sin downtime |
| GHCR | GitHub Container Registry |

---

## 9. RESPUESTAS A PREGUNTAS FRECUENTES

**Q: Que pasa si cambio el codigo?**
R: Con CI/CD es automatico: push a develop -> CI build+test -> CD build+push+update -> ArgoCD auto-sync.

**Q: Por que CI y CD separados?**
R: CI verifica calidad en todo el codigo. CD solo deploya desde develop. Si feature branch falla, no bloquea CD.

**Q: Ventaja de Helm?**
R: Parametrizacion, multiples entornos, versionado, reusabilidad.

**Q: Como sabe ArgoCD que hay cambio?**
R: Polling cada 3 min o webhook de GitHub.

**Q: Que pasa si elimino recurso manualmente en K8s?**
R: ArgoCD lo recrea (self-heal). Sigue en Git.

**Q: Que pasa si elimino recurso de Git?**
R: ArgoCD lo elimina del cluster (prune).

**Q: Liveness vs Readiness?**
R: Liveness = esta vivo? Reinicia si no. Readiness = acepta trafico? No envia peticiones si no.

**Q: Por que non-root?**
R: Seguridad: si el contenedor es comprometido, el atacante no tiene permisos de root.

**Q: Rolling update?**
R: K8s actualiza pods uno por uno sin downtime.

**Q: [skip ci]?**
R: Evita que el commit del CD dispare otro CI (loop infinito).

---

> **Fin de la guia de estudio.**
> Creada para entender el proyecto K8S Microservices y como responde a cada punto de la Guia de Actividad 3 VF 1.
