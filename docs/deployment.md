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

## 5. Instalacion de ArgoCD

```bash
# Crear namespace
kubectl create namespace argocd

# Instalar ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Acceder a UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Obtener password inicial
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Login via CLI
argocd login localhost:8080 --username admin
```

## 6. CI/CD Pipeline (GitHub Actions)

El pipeline se activa automaticamente con push a la rama configurada.
**No requiere JDK en el runner** — Gradle build dentro del contenedor Docker.

```yaml
# workflow simplificado
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t ghcr.io/${{ github.repository }}:${{ github.sha }} .
      - name: Push to registry
        run: docker push ghcr.io/${{ github.repository }}:${{ github.sha }}
      # ArgoCD detecta nuevo tag y sincroniza
```

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
