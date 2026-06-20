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

`ash
# 1. Clonar
git clone https://github.com/Itsumohitoride/actividad_3_VF_1.git
cd actividad_3_VF_1

# 2. Build e iniciar (Gradle build dentro del contenedor)
docker compose up --build -d

# 3. Verificar
curl http://localhost:8080/actuator/health

# 4. Ver logs
docker compose logs -f

# 5. Detener
docker compose down
`

Respuesta esperada: {"status":"UP","groups":["liveness","readiness"]}

---

## Build de imagen Docker

`ash
# Build completo (sin cache)
docker build --no-cache -t microservice:latest .

# Build con cache de capas (mas rapido)
docker build -t microservice:latest .

# Push a registry (GitHub Container Registry)
docker login ghcr.io -u SU_USUARIO --password-stdin
docker tag microservice:latest ghcr.io/SU_USUARIO/actividad-3-vf-1-microservice:TAG
docker push ghcr.io/SU_USUARIO/actividad-3-vf-1-microservice:TAG
`

El Dockerfile es multi-stage:
1. **Builder:** gradle:8-jdk21-alpine — compila el JAR
2. **Runtime:** eclipse-temurin:21-jre-alpine — solo JRE, usuario no-root

---

## Despliegue con Helm

### Prerequisitos

- Docker Desktop con Kubernetes habilitado
- kubectl configurado para usar el contexto de Docker Desktop
- Imagen Docker disponible en un registry accesible desde el cluster

  > **Importante:** El valor image.repository en alues.yaml (y por entorno) debe apuntar a un registry real. Por defecto usa ghcr.io/namespace/microservice como placeholder. Ajustalo antes de instalar, ej: ghcr.io/tu-usuario/microservice.

### Push de imagen a registry

Antes de instalar el chart, buildear y pushear la imagen a un registry accesible por el cluster:

`ash
# Buildear
docker build -t microservice:latest .

# Taggear para GHCR
docker tag microservice:latest ghcr.io/Itsumohitoride/actividad-3-vf-1-microservice:latest

# Login y push
echo \ | docker login ghcr.io -u Itsumohitoride --password-stdin
docker push ghcr.io/Itsumohitoride/actividad-3-vf-1-microservice:latest
`

La imagen se configura en charts/microservice/values.yaml:
`yaml
image:
  repository: ghcr.io/Itsumohitoride/actividad-3-vf-1-microservice
  tag: latest
`

### Instalar el chart

`ash
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
`

### Actualizar

`ash
helm upgrade microservice-dev ./charts/microservice \
  --values ./charts/microservice/values-dev.yaml \
  --namespace dev
`

### Rollback

`ash
helm rollback microservice-dev 1 --namespace dev
`

### Valores por entorno

| Archivo | Entorno | Replicas | Service Type |
|---------|---------|----------|--------------|
| alues-dev.yaml | Desarrollo | 1 | NodePort |
| alues-staging.yaml | Pre-produccion | 2 | ClusterIP |
| alues-prod.yaml | Produccion | 3+ | ClusterIP + Ingress |

---

## Despliegue con ArgoCD (GitOps)

### 1. Instalar ArgoCD en el cluster

`ash
# 1. Crear namespace argocd (con apply para tener annotation)
kubectl apply -f k8s/argocd/namespace.yaml

# 2. Instalar ArgoCD desde el manifest oficial (directo, no via kustomize)
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.10.0/manifests/install.yaml

# 3. Aplicar recursos custom (AppProject, Application) via kustomize
kubectl apply -k k8s/argocd/
`

Paso 1 crea el namespace con kubectl apply (no create) para que tenga la annotation last-applied-configuration y evitar warnings. Paso 2 instala ArgoCD directamente (sin kustomize) porque los labels transforms de kustomize rompen los informers internos de ArgoCD (CrashLoopBackOff con "configmap argocd-cm not found"). Paso 3 aplica solo nuestros recursos custom (project, application).

Esto crea: namespace rgocd, server, controller, repo-server, redis, dex, applicationset-controller, notifications-controller.

> Si ya hay recursos previos y falla, borra el namespace y reaplica:
> `ash
> kubectl delete namespace argocd
> kubectl delete crd applications.argoproj.io applicationsets.argoproj.io appprojects.argoproj.io --ignore-not-found
> kubectl apply --server-side --force-conflicts -k https://github.com/argoproj/argo-cd/manifests/crds?ref=stable
> kubectl apply --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
> kubectl create namespace argocd
> kubectl apply -k k8s/argocd/
> `

### 2. Acceder a la UI

`ash
# Port-forward
kubectl port-forward svc/argocd-server -n argocd 9090:443

# Password del admin
# Linux/Mac:
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d

# Windows PowerShell:
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | %{ [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(\)) }

# Login
argocd login localhost:9090 --username admin

# Abrir en navegador: https://localhost:9090
`

### 3. Verificar la aplicacion

`ash
argocd app list
argocd app get microservice-dev
argocd app wait microservice-dev --health
`

Estado esperado: **Synced** + **Healthy**.

### 4. GitOps flow

`
Developer push → CI (build+test) → CD (docker build+push+values update)
                                         ↓
                                  Git commit (nuevo tag)
                                         ↓
                                  ArgoCD auto-sync
                                         ↓
                                  Nuevo pod con imagen actualizada
`

ArgoCD sincroniza automaticamente cuando detecta cambios en el repositorio Git (auto-sync, self-heal, prune).

### Comandos utiles

`ash
argocd app sync microservice-dev          # Sincronizar manual
argocd app logs microservice-dev --follow  # Logs de sync
argocd app rollback microservice-dev 1     # Rollback a revision anterior
kubectl rollout undo deployment/microservice-dev -n dev  # Rollback K8s directo
`

---

## CI/CD con GitHub Actions

### Workflows

| Workflow | Archivo | Trigger | Que hace |
|----------|---------|---------|----------|
| **CI** | .github/workflows/ci.yml | Push/PR a develop, eature/* | Build, test, lint, quality gates |
| **CD** | .github/workflows/cd.yml | Push a develop | Docker build+push a ghcr.io, actualiza Helm values, ArgoCD auto-sync |

### CI pipeline

`yaml
jobs:
  build:    # gradle build + test + upload reports
  quality:  # gradle check + dependencies
`

### CD pipeline

`yaml
jobs:
  deploy:   # docker login → buildx → build+push → update values → commit
`

El CD construye la imagen con tag = short commit SHA (ej: 1b2c3d), la sube a ghcr.io, actualiza charts/microservice/values-dev.yaml con el nuevo tag, y hace commit. ArgoCD detecta el cambio y sincroniza.

### Secretos requeridos

| Secreto | Provee |
|---------|--------|
| GITHUB_TOKEN | Automatico — permisos contents: write y packages: write |

Ver docs/pipelines.md para detalle completo.

---

## Estructura del proyecto

`
├── .github/workflows/       # CI/CD pipelines
│   ├── ci.yml               # Build + test + lint + quality gates
│   └── cd.yml               # Docker build+push + Helm values update + commit
├── charts/microservice/      # Helm chart
│   ├── templates/            # K8s templates
│   │   ├── configmap.yaml    # Configuracion Spring Boot
│   │   ├── deployment.yaml   # Deployment con probes y resources
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
│       │       └── ProductController.java
│       └── test/java/.../
│           └── ProductServiceApplicationTests.java
├── docker-compose.yml        # Orquestacion local
├── Dockerfile                # Multi-stage build (Gradle 8 + JDK 21)
└── .gitignore                # Ignora todo excepto lo necesario
`

---

## Troubleshooting

| Problema | Causa | Solucion |
|----------|-------|----------|
| docker build falla | Sin conexion o cache corrupto | docker build --no-cache |
| Container no responde | Puerto incorrecto | Verificar server.port=8080 en Spring |
| helm install falla | Namespace no existe | Agregar --create-namespace |
| ConfigMap/Service "exists and cannot be imported" | Recursos de instalacion previa sin anotaciones Helm | kubectl delete namespace dev y reintentar |
| Pod ImagePullBackOff | image.repository placeholder sin cambiar o registry inaccesible | Verificar alues-dev.yaml apunte a un registry real; crear imagePullSecrets si es privado |
| Pod CrashLoopBackOff | Read-only filesystem impide escritura en /tmp | Agregar emptyDir volume mount en /tmp al deployment |
| kubectl apply -f install.yaml falla con CRD annotation too long | Mezcla de client-side y server-side apply | Usar --server-side --force-conflicts siempre |
| kubectl apply -k k8s/argocd/ dice namespace not found | El upstream install.yaml ya no incluye el namespace | Ejecutar kubectl create namespace argocd antes |
| ArgoCD no sincroniza: "unable to resolve branch" | 	argetRevision en pplication.yaml apunta a rama inexistente | Verificar que la rama exista en el repo remoto |
| ArgoCD repo-server: connection refused | El servicio tarda en iniciar | Esperar 10-15s y reintentar rgocd app sync |
| Navegador redirige a HTTPS en localhost | Puerto 8080 ya se uso antes con HTTPS (cache del navegador) | Usar otro puerto (9090) para el microservicio |
| ase64 -d no funciona en Windows | Comando no existe en PowerShell | Usar %{ [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(\)) } |
| ./gradlew permission denied | Permisos de ejecucion | git update-index --chmod=+x src/gradlew |

---

## Referencia rapida de comandos

### Docker

| Comando | Explicacion |
|---------|-------------|
| docker build -t microservice:latest . | Construye la imagen desde el Dockerfile en el directorio actual (.). -t asigna nombre:tag. |
| docker build --no-cache -t microservice:latest . | Construye ignorando cache de capas (build desde cero). Usar si hay problemas de cache. |
| docker tag microservice:latest ghcr.io/user/repo:tag | Crea un alias de la imagen local apuntando a un registry remoto. |
| docker push ghcr.io/user/repo:tag | Sube la imagen al registry remoto. |
| docker login ghcr.io -u user --password-stdin | Autentica en GitHub Container Registry. --password-stdin lee el token desde stdin. |
| docker compose up --build -d | Inicia servicios del compose. --build reconstruye antes de iniciar. -d corre en segundo plano. |
| docker compose logs -f | Muestra logs de los servicios. -f sigue escribiendo (follow). |
| docker compose down | Detiene y elimina contenedores, redes y volumenes del compose. |

### kubectl

| Comando | Explicacion |
|---------|-------------|
| kubectl get pods -n dev | Lista pods en el namespace dev. -n especifica namespace. |
| kubectl logs deployment/microservice-dev -n dev | Muestra logs del Deployment. |
| kubectl port-forward deployment/microservice-dev -n dev 8080:8080 | Redirige puerto local 8080 al puerto 8080 del pod. Acceder en http://localhost:8080. |
| kubectl port-forward svc/argocd-server -n argocd 9090:443 | Redirige puerto local 9090 al puerto 443 del servicio ArgoCD. Acceder en https://localhost:9090. |
| kubectl apply -f <archivo.yml> | Aplica recursos K8s desde un archivo o URL. Crea o actualiza. |
| kubectl apply -k <directorio/> | Aplica recursos usando Kustomize (combina YAMLs). |
| kubectl rollout undo deployment/<name> -n <ns> | Revierte un Deployment a la revision anterior (rollback directo). |
| kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d | Obtiene y decodifica el password inicial del admin de ArgoCD. |

### Helm

| Comando | Explicacion |
|---------|-------------|
| helm lint ./charts/microservice | Valida que el chart este bien formado (YAML valido, valores obligatorios). |
| helm template ./charts/microservice --values ./charts/microservice/values-dev.yaml | Renderiza templates Go a YAML K8s sin instalar. Util para debug. |
| helm install microservice-dev ./charts/microservice --namespace dev --create-namespace --values ./charts/microservice/values-dev.yaml | Instala el chart como release microservice-dev en namespace dev. --create-namespace lo crea si no existe. |
| helm upgrade microservice-dev ./charts/microservice --namespace dev --values ./charts/microservice/values-dev.yaml | Actualiza un release existente (rolling update). |
| helm rollback microservice-dev 1 --namespace dev | Revierte a la revision 1. Ver revisiones con helm list --namespace dev. |
| helm uninstall microservice-dev --namespace dev | Elimina el release y sus recursos K8s. |

### ArgoCD CLI

| Comando | Explicacion |
|---------|-------------|
| rgocd login localhost:9090 --username admin | Autentica en el servidor ArgoCD via port-forward. |
| rgocd app list | Lista todas las apps (sync status, health). |
| rgocd app get microservice-dev | Detalle de la app: recursos K8s, parametros, eventos. |
| rgocd app sync microservice-dev | Sincroniza manual: aplica Git -> cluster inmediatamente. |
| rgocd app wait microservice-dev --health | Bloquea hasta que la app este Healthy. |
| rgocd app logs microservice-dev --follow | Logs del sync. --follow como tail -f. |
| rgocd app rollback microservice-dev 1 | Revierte a revision de deploy anterior. |

### curl

| Comando | Explicacion |
|---------|-------------|
| curl http://localhost:8080/actuator/health | Health check del microservicio. Responde {"status":"UP"} si funciona. |
| curl http://localhost:8080/api/v1/products | Endpoint REST del microservicio. Retorna lista de productos JSON. |

---

## Documentacion adicional

| Documento | Contenido |
|-----------|-----------|
| docs/architecture.md | Diagramas de arquitectura K8s, flujo CI/CD, stack tecnologico |
| docs/configuration.md | Variables de entorno, Spring Boot config, Helm values, secretos |
| docs/deployment.md | Instructivo completo de deploy y rollback |
| docs/pipelines.md | Detalle de workflows CI/CD, secretos, GitOps flow |
