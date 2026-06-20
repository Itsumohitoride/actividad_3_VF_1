# K8S Microservices — Spring Boot + Gradle Containerized

Microservicio Spring Boot containerizado con Helm charts parametrizables, despliegue GitOps mediante ArgoCD, y pipelines CI/CD automatizados con GitHub Actions.

El stack completo: **Java 21 + Spring Boot 3.2 + Gradle 8 → Docker → Helm → ArgoCD → Kubernetes → GitHub Actions**.

## Descripcion del proyecto

Trabajo practico de arquitectura de software: disenar e implementar microservicios individualmente desplegables utilizando contenedores Docker, Kubernetes como orquestador, Helm para gestion de paquetes y configuraciones, ArgoCD para GitOps, y pipelines CI/CD para automatizar la construccion y despliegue del microservicio al detectar commits en la rama configurada.

### Entregables

- Microservicio Spring Boot funcional, dockerizado, con charts de Helm
- Despliegue en Kubernetes con ArgoCD (auto-sync, self-heal, prune)
- Pipelines CI/CD automatizados que detectan commits y despliegan sin errores
- Documentacion clara, completa y bien estructurada
- Codigo fuente comentado (Javadoc)

---

## Requisitos

| Herramienta | Version | Necesaria para |
|-------------|---------|----------------|
| **Docker Desktop** | 4.x+ | Build de imagen, docker-compose local, Kubernetes |
| Kubernetes en Docker Desktop | 1.28+ | Despliegue con Helm y ArgoCD |
| **kubectl** | 1.28+ | Interactuar con el cluster K8s |
| **Helm** | 3.x+ | Instalar charts K8s |
| **ArgoCD CLI** | 2.x+ | Gestionar aplicaciones ArgoCD |

**No necesitas:** Java, Gradle, Maven, Node.js, ni Python — todo corre dentro de contenedores.

---

## Inicio rapido (local, sin K8s)

```bash
# 1. Clonar
git clone https://github.com/Itsumohitoride/actividad_3_VF_1.git
cd actividad_3_VF_1

# 2. Build imagen (Gradle dentro del contenedor)
docker build -t microservice:latest .

# 3. Iniciar
docker compose up --build -d

# 4. Verificar
curl http://localhost:8080/actuator/health

# 5. Ver logs
docker compose logs -f

# 6. Detener
docker compose down
```

Respuesta esperada: `{"status":"UP","groups":["liveness","readiness"]}`

---

## Build de imagen Docker

```bash
# Build completo (sin cache)
docker build --no-cache -t microservice:latest .

# Build con cache de capas (mas rapido)
docker build -t microservice:latest .

# Push a registry (GitHub Container Registry)
docker tag microservice:latest ghcr.io/SU_USUARIO/actividad-3-vf-1-microservice:TAG
docker push ghcr.io/SU_USUARIO/actividad-3-vf-1-microservice:TAG
```

El Dockerfile es multi-stage:
1. **Builder:** `gradle:8-jdk21-alpine` — compila el JAR
2. **Runtime:** `eclipse-temurin:21-jre-alpine` — solo JRE, usuario no-root

---

## Despliegue con Helm

### Prerequisitos

- Docker Desktop con Kubernetes habilitado
- `kubectl` configurado para usar el contexto de Docker Desktop
- Imagen Docker disponible en un registry accesible desde el cluster

  > **Importante:** El valor `image.repository` en `values.yaml` (y por entorno) debe apuntar a un registry real. Por defecto usa `ghcr.io/namespace/microservice` como placeholder. Ajustalo antes de instalar, ej: `ghcr.io/tu-usuario/microservice`.

### Instalar el chart

```bash
# Verificar chart
helm lint ./charts/microservice

# Previsualizar manifiestos
helm template ./charts/microservice --values ./charts/microservice/values-dev.yaml

# Eliminar namespace si ya existe con anterioridad
kubectl delete namespace dev

# Instalar
helm install microservice-dev ./charts/microservice --namespace dev --create-namespace --values ./charts/microservice/values-dev.yaml

# Verificar
kubectl get pods -n dev

# Port-forward (terminal 1, usar 9090 si 8080 esta ocupado por ArgoCD)
kubectl port-forward deployment/microservice-dev -n dev 9090:8080

# Health check (terminal 2)
curl http://localhost:9090/actuator/health

# Endpoint de productos
curl http://localhost:9090/api/v1/products
```

### Actualizar

```bash
helm upgrade microservice-dev ./charts/microservice \
  --values ./charts/microservice/values-dev.yaml \
  --namespace dev
```

### Rollback

```bash
helm rollback microservice-dev 1 --namespace dev
```

### Valores por entorno

| Archivo | Entorno | Replicas | Service Type |
|---------|---------|----------|--------------|
| `values-dev.yaml` | Desarrollo | 1 | NodePort |
| `values-staging.yaml` | Pre-produccion | 2 | ClusterIP |
| `values-prod.yaml` | Produccion | 3+ | ClusterIP + Ingress |

---

## Despliegue con ArgoCD (GitOps)

### 1. Instalar ArgoCD en el cluster

```bash
# 1a. CRDs primero (server-side apply)
kubectl apply --server-side --force-conflicts -k https://github.com/argoproj/argo-cd/manifests/crds?ref=stable

# 1b. ArgoCD base (upstream oficial, server-side apply para evitar conflictos de anotaciones)
kubectl apply --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 1c. Crear namespace argocd (el upstream ya no lo incluye)
kubectl create namespace argocd

# 1d. Project + Application del microservicio
kubectl apply -k k8s/argocd/
```

Esto crea: namespace `argocd`, server, controller, repo-server, redis, dex, applicationset-controller, notifications-controller.

> Si ya hay recursos previos y falla, borra el namespace y reaplica:
> ```bash
> kubectl delete namespace argocd
> kubectl delete crd applications.argoproj.io applicationsets.argoproj.io appprojects.argoproj.io --ignore-not-found
> kubectl apply --server-side --force-conflicts -k https://github.com/argoproj/argo-cd/manifests/crds?ref=stable
> kubectl apply --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
> kubectl create namespace argocd
> kubectl apply -k k8s/argocd/
> ```

### 2. Acceder a la UI

```bash
# Port-forward (mantener esta terminal abierta)
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Password del admin — Linux/Mac
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Password del admin — Windows (PowerShell)
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | %{ [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }

# Login
argocd login localhost:8080 --username admin

# Abrir en navegador: https://localhost:8080
```

> **Nota sobre puertos:** ArgoCD UI y el microservicio usan el mismo puerto 8080. No pueden correr al mismo tiempo.
> - Para ArgoCD UI: `kubectl port-forward svc/argocd-server -n argocd 8080:443`
> - Para microservicio: `kubectl port-forward deployment/microservice-dev -n dev 9090:8080` (usar puerto distinto)
> - Si el navegador redirige a HTTPS, es porque ese puerto ya se uso antes con SSL. Cambia de puerto o borra cache del navegador.

### 3. Verificar la aplicacion

```bash
argocd app list
argocd app get microservice-dev
argocd app wait microservice-dev --health
```

Estado esperado: **Synced** + **Healthy**.

### 4. GitOps flow

```
Developer push → CI (build+test) → CD (docker build+push+values update)
                                         ↓
                                  Git commit (nuevo tag)
                                         ↓
                                  ArgoCD auto-sync
                                         ↓
                                  Nuevo pod con imagen actualizada
```

ArgoCD sincroniza automaticamente cuando detecta cambios en el repositorio Git (auto-sync, self-heal, prune).

### Comandos utiles

```bash
argocd app sync microservice-dev          # Sincronizar manual
argocd app logs microservice-dev --follow  # Logs de sync
argocd app rollback microservice-dev 1     # Rollback a revision anterior
kubectl rollout undo deployment/microservice-dev -n dev  # Rollback K8s directo
```

---

## CI/CD con GitHub Actions

### Workflows

| Workflow | Archivo | Trigger | Que hace |
|----------|---------|---------|----------|
| **CI** | `.github/workflows/ci.yml` | Push/PR a `develop`, `feature/*` | Build, test, lint, quality gates |
| **CD** | `.github/workflows/cd.yml` | Push a `develop` | Docker build+push a ghcr.io, actualiza Helm values, ArgoCD auto-sync |

### CI pipeline

```yaml
jobs:
  build:    # gradle build + test + upload reports
  quality:  # gradle check + dependencies
```

### CD pipeline

```yaml
jobs:
  deploy:   # docker login → buildx → build+push → update values → commit
```

El CD construye la imagen con tag = short commit SHA (ej: `a1b2c3d`), la sube a `ghcr.io`, actualiza `charts/microservice/values-dev.yaml` con el nuevo tag, y hace commit. ArgoCD detecta el cambio y sincroniza.

### Secretos requeridos

| Secreto | Provee |
|---------|--------|
| `GITHUB_TOKEN` | Automatico — permisos `contents: write` y `packages: write` |

Ver `docs/pipelines.md` para detalle completo.

---

## Estructura del proyecto

```
├── .github/workflows/       # CI/CD pipelines
│   ├── ci.yml               # Build + test + lint + quality gates
│   └── cd.yml               # Docker build+push + Helm values update + commit
├── charts/microservice/      # Helm chart
│   ├── templates/            # K8s templates
│   │   ├── _helpers.tpl      # Labels reutilizables
│   │   ├── configmap.yaml    # Configuracion Spring Boot
│   │   ├── deployment.yaml   # Deployment con probes, resources, emptyDir
│   │   ├── hpa.yaml          # Autoescalado
│   │   ├── ingress.yaml      # Ingress (opcional)
│   │   └── service.yaml      # Service ClusterIP/NodePort
│   ├── Chart.yaml            # Metadata del chart
│   ├── values.yaml           # Valores por defecto
│   ├── values-dev.yaml       # Desarrollo
│   ├── values-staging.yaml   # Staging
│   └── values-prod.yaml      # Produccion
├── docs/                     # Documentacion
│   ├── architecture.md       # Diagramas de arquitectura y flujo CI/CD
│   ├── configuration.md      # Variables de entorno y configuraciones
│   ├── deployment.md         # Instrucciones detalladas de deploy y rollback
│   └── pipelines.md          # Documentacion de pipelines CI/CD
├── k8s/argocd/               # Manifiestos ArgoCD
│   ├── namespace.yaml        # Namespace argocd
│   ├── install.yaml          # Componentes ArgoCD
│   ├── project.yaml          # AppProject microservice
│   ├── application.yaml      # Application con auto-sync, self-heal, prune
│   └── kustomization.yaml    # Kustomize overlay
├── src/                      # Codigo fuente
│   ├── build.gradle.kts      # Gradle + Spring Boot 3.2.5 + Actuator
│   ├── settings.gradle.kts   # Configuracion Gradle
│   ├── gradlew               # Gradle wrapper (Unix)
│   ├── gradlew.bat           # Gradle wrapper (Windows)
│   └── src/                  # Codigo Java
│       ├── main/java/.../
│       │   ├── ProductServiceApplication.java
│       │   └── controller/
│       │       ├── HealthController.java
│       │       └── ProductController.java
│       └── test/java/.../
│           └── ProductServiceApplicationTests.java
├── docker-compose.yml        # Orquestacion local
├── Dockerfile                # Multi-stage build (Gradle 8 + JDK 21)
└── .gitignore                # Ignora todo excepto lo necesario
```

---

## Troubleshooting

| Problema | Causa | Solucion |
|----------|-------|----------|
| `docker build` falla | Sin conexion o cache corrupto | `docker build --no-cache` |
| Container no responde | Puerto incorrecto | Verificar `server.port=8080` en Spring |
| `helm install` falla | Namespace no existe | Agregar `--create-namespace` |
| ConfigMap/Service "exists and cannot be imported" | Recursos de instalacion previa sin anotaciones Helm | `kubectl delete namespace dev` y reintentar |
| Pod ImagePullBackOff | `image.repository` placeholder sin cambiar o registry inaccesible | Verificar `values-dev.yaml` apunte a un registry real; crear `imagePullSecrets` si es privado |
| Pod CrashLoopBackOff | Read-only filesystem impide escritura en `/tmp` | Agregar `emptyDir` volume mount en `/tmp` al deployment |
| `kubectl apply -f install.yaml` falla con CRD annotation too long | Mezcla de client-side y server-side apply | Usar `--server-side --force-conflicts` siempre |
| `kubectl apply -k k8s/argocd/` dice namespace not found | El upstream `install.yaml` ya no incluye el namespace | Ejecutar `kubectl create namespace argocd` antes |
| ArgoCD no sincroniza: "unable to resolve branch" | `targetRevision` en `application.yaml` apunta a rama inexistente | Verificar que la rama exista en el repo remoto |
| ArgoCD repo-server: connection refused | El servicio tarda en iniciar | Esperar 10-15s y reintentar `argocd app sync` |
| Navegador redirige a HTTPS en localhost | Puerto 8080 ya se uso antes con HTTPS (cache del navegador) | Usar otro puerto (9090) para el microservicio |
| `base64 -d` no funciona en Windows | Comando no existe en PowerShell | Usar `%{ [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_)) }` |
| `./gradlew` permission denied | Permisos de ejecucion | `git update-index --chmod=+x src/gradlew` |

---

## Referencia rapida de comandos

```bash
# Build y local
docker build -t microservice:latest .
docker compose up --build -d
curl localhost:8080/actuator/health

# K8s
kubectl get pods -n dev
kubectl logs deployment/microservice-dev -n dev
kubectl port-forward deployment/microservice-dev -n dev 8080:8080   # si 8080 da conflicto con ArgoCD, usar 9090:8080

# Helm
helm lint ./charts/microservice
helm template ./charts/microservice --values ./charts/microservice/values-dev.yaml
helm install microservice-dev ./charts/microservice --namespace dev --create-namespace --values ./charts/microservice/values-dev.yaml
helm upgrade microservice-dev ./charts/microservice --namespace dev --values ./charts/microservice/values-dev.yaml
helm rollback microservice-dev 1 --namespace dev
helm uninstall microservice-dev --namespace dev

# ArgoCD — instalacion
kubectl apply --server-side --force-conflicts -k https://github.com/argoproj/argo-cd/manifests/crds?ref=stable
kubectl apply --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl create namespace argocd
kubectl apply -k k8s/argocd/

# ArgoCD — password (Windows)
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" ^
  | %{ [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_)) }

# ArgoCD — password (Linux/Mac)
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# ArgoCD — UI (terminal 1)
kubectl port-forward svc/argocd-server -n argocd 8080:443

# ArgoCD — CLI (terminal 2)
argocd login localhost:8080
argocd app list
argocd app get microservice-dev
argocd app sync microservice-dev
argocd app rollback microservice-dev 1

# Limpiar ArgoCD completamente y reiniciar
kubectl delete namespace argocd
kubectl delete crd applications.argoproj.io applicationsets.argoproj.io appprojects.argoproj.io
kubectl delete clusterrole argocd-application-controller argocd-applicationset-controller argocd-server
kubectl delete clusterrolebinding argocd-application-controller argocd-applicationset-controller argocd-server
```

---

## Documentacion adicional

| Documento | Contenido |
|-----------|-----------|
| `docs/architecture.md` | Diagramas de arquitectura K8s, flujo CI/CD, stack tecnologico |
| `docs/configuration.md` | Variables de entorno, Spring Boot config, Helm values, secretos |
| `docs/deployment.md` | Instructivo completo de deploy y rollback |
| `docs/pipelines.md` | Detalle de workflows CI/CD, secretos, GitOps flow |
