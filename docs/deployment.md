# Despliegue — K8S Microservices (Spring Boot + Gradle Containerized)

## Prerrequisitos

Solo necesitas **Docker Desktop** (Kubernetes opcional por ahora).

| Herramienta | Version | Por que |
|------------|---------|---------|
| Docker Desktop | 4.x+ | Unico requisito. Build y runtime. |
| Kubernetes | 1.28+ | Opcional, habilitar en Docker Desktop para F21+ |
| kubectl | 1.28+ | Opcional, para K8s |
| Helm | 3.x+ | Opcional, para F20 |
| ArgoCD CLI | 2.x+ | Opcional, para F21 |

**No necesitas:** Java, Gradle, Maven, Node.js, Python, ni nada mas.

## 1. Build Local (100% containerizado)

```bash
# Build completo (Gradle build dentro del contenedor)
docker build --no-cache -t microservice:latest .

# Build con cache de capas (mas rapido)
docker build -t microservice:latest .
```

## 2. Desarrollo Local con Docker Compose

```bash
# Build + iniciar
docker compose up --build -d

# Verificar salud
curl http://localhost:8080/actuator/health

# Ver logs
docker compose logs -f

# Detener
docker compose down
```

## 3. Build y Push de Imagen Docker

```bash
# Taggear
docker tag microservice:latest ghcr.io/<user>/<service>:<tag>

# Push (requiere login)
docker push ghcr.io/<user>/<service>:<tag>
```

## 4. Despliegue Local con Helm

```bash
# Instalar chart
helm install <release> ./charts/<chart-name> --namespace dev --create-namespace

# Template preview
helm template ./charts/<chart-name> --values ./charts/<chart-name>/values-dev.yaml

# Upgrade
helm upgrade <release> ./charts/<chart-name> --values ./charts/<chart-name>/values-dev.yaml

# Rollback
helm rollback <release> <revision>

# Listar releases
helm list --namespace dev
```

## 5. Instalacion de ArgoCD (GitOps)

Los manifiestos de instalacion estan en `k8s/argocd/`:

| Archivo | Proposito |
|---------|-----------|
| `namespace.yaml` | Namespace `argocd` |
| `install.yaml` | Componentes minimos: server, controller, repo-server, redis |
| `project.yaml` | AppProject `microservice` con destinos dev/staging/prod |
| `application.yaml` | Application `microservice-dev` con auto-sync, self-heal, prune |
| `kustomization.yaml` | Kustomize overlay combinando todos los recursos |

### 5.1 Instalar ArgoCD en el cluster

```bash
# Opcion A: Kustomize
kubectl apply -k k8s/argocd/

# Opcion B: Directo
kubectl apply -f k8s/argocd/namespace.yaml
kubectl apply -f k8s/argocd/install.yaml
kubectl apply -f k8s/argocd/project.yaml
kubectl apply -f k8s/argocd/application.yaml
```

> **Nota:** Las CRDs de ArgoCD (Application, AppProject, etc.) deben instalarse primero.
> Descargar: `kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/crds.yaml`

### 5.2 Acceder a UI de ArgoCD

```bash
# Port-forward a la UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Obtener password inicial del admin
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Login via CLI
argocd login localhost:8080 --username admin

# Abrir en navegador: https://localhost:8080
```

### 5.3 Comandos CLI utiles

```bash
# Listar aplicaciones
argocd app list

# Ver estado de sincronizacion
argocd app get microservice-dev

# Sincronizar manualmente
argocd app sync microservice-dev

# Ver historial y hacer rollback
argocd app rollback microservice-dev --list
argocd app rollback microservice-dev <revision>

# Ver logs de sincronizacion
argocd app logs microservice-dev --follow

# Ver estado de health
argocd app wait microservice-dev --health

# Cambiar password admin
argocd account update-password
```

### 5.4 GitOps Flow

1. Developer hace commit + push a `develop`
2. CI pipeline corre: build + test + lint
3. CD pipeline corre: build Docker image + push a ghcr.io
4. CD pipeline actualiza `values-dev.yaml` con nuevo image tag y hace commit
5. ArgoCD detecta drift entre Git y cluster
6. Auto-sync aplica cambios con self-heal y prune
7. Rolling update del deployment
8. Health check via Actuator `/actuator/health`

## 6. CI/CD Pipeline (GitHub Actions)

Dos workflows en `.github/workflows/` automatizan CI y CD:

| Workflow | Archivo | Trigger | Accion |
|----------|---------|---------|--------|
| CI | `ci.yml` | Push/PR a `develop`, `feature/*` | Gradle build + test + lint + quality gates |
| CD | `cd.yml` | Push a `develop` | Docker build + push a ghcr.io + update Helm values + ArgoCD auto-sync |

**Pipeline completo:** Ver `docs/pipelines.md` para detalle de workflows, secretos requeridos y GitOps flow.

### CI Flow
1. Checkout codigo
2. Setup JDK 21 con cache Gradle
3. `gradle build` (compila, excluye tests por velocidad)
4. `gradle test` (unit tests con JUnit 5)
5. `gradle check` (lint, calidad)
6. Upload test reports como artifact

### CD Flow (GitOps)
1. Checkout con token de escritura
2. Login a GitHub Container Registry
3. Build multi-plataforma con Docker Buildx
4. Push imagen con tag = short commit SHA (ej: `a1b2c3d`) + `latest` en `develop`
5. Actualizar `charts/microservice/values-dev.yaml` con nuevo tag
6. Commit + push del cambio al repositorio
7. ArgoCD detecta drift, auto-sincroniza, despliega nuevo pod

## Procedimiento de Rollback

```bash
# ArgoCD: rollback a revision anterior
argocd app rollback <app-name> <revision>

# Kubernetes manual
kubectl rollout undo deployment/<deployment-name> -n <namespace>
kubectl rollout status deployment/<deployment-name> -n <namespace>

# Verificar salud post-rollback
curl -f http://<service-url>/actuator/health
```

## Troubleshooting

| Problema | Causa | Solucion |
|----------|-------|----------|
| docker build falla | Gradle no descarga dependencias | Verificar conexion a internet, Gradle cache |
| JAR no encontrado | build.gradle mal configurado | Verificar Gradle build dentro del contenedor |
| Container exitoso pero no responde | Puerto incorrecto | Verificar server.port y EXPOSE |
| Docker build lento | Sin cache de capas | Ordenar COPY para cachear dependencias |
| ArgoCD no sincroniza | Credenciales Git invalidas | Verificar repo config en argocd |
