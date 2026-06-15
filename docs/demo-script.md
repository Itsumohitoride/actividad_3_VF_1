# Guion de video — Demostracion K8S Microservices

- **Duracion:** 8 minutos
- **Formato:** Screencast con voz en off
- **Herramientas:** Terminal, navegador (ArgoCD UI, GitHub Actions), Docker Desktop

---

## Timeline

| Min | Seccion | Contenido |
|-----|---------|-----------|
| 0:00 | Intro | Que vamos a mostrar |
| 0:30 | Local dev | Docker build + docker-compose + health check |
| 1:45 | Docker push | Taggear y push a registry |
| 2:45 | Helm | Chart structure + helm lint + template |
| 4:00 | ArgoCD | UI: aplicacion synced + healthy + GitOps flow |
| 5:30 | CI/CD | GitHub Actions: CI + CD workflows running |
| 6:45 | Deploy verify | Pod ready + health endpoint + rollback |
| 7:30 | Outro | Resumen + repo link |

---

## 0:00 — Intro (30s)

**Dialogo:**
"Hola, hoy les voy a mostrar el pipeline completo de esta arquitectura de microservicios con Spring Boot, Docker, Helm, ArgoCD y CI/CD automatizado en GitHub Actions. Vamos desde el codigo fuente hasta el despliegue en Kubernetes."

**Capturas:**
- Pantalla inicial con logo del proyecto
- Split: terminal + browser tabs

---

## 0:30 — Seccion 1: Demo local (1min 15s)

**Dialogo:**
"Empezamos con el build local. Con un solo comando construimos la imagen Docker. Gradle corre dentro del contenedor, no necesitamos Java instalado en la maquina."

**Comandos a ejecutar:**
```bash
docker build -t microservice:latest .
docker compose up --build -d
curl http://localhost:8080/actuator/health
```

**Dialogo:**
"Usamos Docker Compose para orquestar. Verificamos la salud del microservicio con el endpoint de Actuator — responde con un 200 OK y status UP. Esto confirma que el contexto Spring Boot cargo correctamente."

**Capturas sugeridas:**
1. Terminal: `docker build` exitoso
2. Terminal: `curl` response `{"status":"UP"}`
3. Docker Desktop dashboard mostrando container running

---

## 1:45 — Seccion 2: Docker push (1min)

**Dialogo:**
"La imagen se etiqueta y se sube a GitHub Container Registry. En produccion esto lo hace automaticamente el pipeline CD, pero aqui lo hacemos manual para mostrar el proceso."

**Comandos:**
```bash
docker tag microservice:latest ghcr.io/itsumohitoride/actividad-3-vf-1-microservice:demo
docker push ghcr.io/itsumohitoride/actividad-3-vf-1-microservice:demo
```

**Dialogo:**
"La imagen queda disponible en ghcr.io con el tag 'demo'. El pipeline CD usa el commit SHA como tag para trazabilidad."

**Capturas sugeridas:**
1. Terminal: docker push output
2. Navegador: ghcr.io package page con tags

---

## 2:45 — Seccion 3: Helm (1min 15s)

**Dialogo:**
"Ahora veamos la configuracion declarativa con Helm. El chart del microservicio tiene templates para deployment, service, ingress, configmap y HPA."

**Comandos:**
```bash
helm lint ./charts/microservice
helm template ./charts/microservice --values ./charts/microservice/values-dev.yaml
```

**Dialogo:**
"Ejecutamos helm lint para verificar que el chart es valido — cero errores. Luego helm template para ver los manifiestos K8s generados. Los values por entorno permiten configurar desarrollo, staging y produccion con diferentes replicas, recursos y dominios."

**Capturas sugeridas:**
1. Terminal: `helm lint` output con 0 errors
2. Editor: values-dev.yaml mostrando estructura
3. Terminal: `helm template` output parcial (deployment)

---

## 4:00 — Seccion 4: ArgoCD (1min 30s)

**Dialogo:**
"ArgoCD es el corazon del GitOps. Aqui vemos la aplicacion microservice-dev desplegada en el namespace dev. El estado es Synced y Healthy."

**Comandos:**
```bash
argocd login localhost:8080 --username admin
argocd app list
argocd app get microservice-dev
```

**Dialogo:**
"La aplicacion se configura con auto-sync, self-heal y pruning. Cuando hay cambios en el repositorio Git, ArgoCD detecta el drift y sincroniza automaticamente. Veamos los parametros: source apunta al Helm chart en GitHub, destination es el namespace dev, y la politica de sync permite auto-sync con prune."

**Capturas sugeridas:**
1. Navegador: ArgoCD UI app list con microservice-dev
2. Navegador: ArgoCD UI app details — synced + healthy
3. Navegador: ArgoCD UI app tree — pod running

**Comandos adicionales:**
```bash
argocd app sync microservice-dev
argocd app wait microservice-dev --health
kubectl get pods -n dev
```

---

## 5:30 — Seccion 5: CI/CD (1min 15s)

**Dialogo:**
"Los pipelines de GitHub Actions automatizan todo. El workflow CI se ejecuta en cada push y pull request a develop: compila con Gradle, corre los tests, ejecuta quality gates y sube los reportes."

**Dialogo:**
"El workflow CD va mas alla: construye la imagen Docker, la sube a ghcr.io, actualiza el archivo values-dev.yaml con el nuevo tag SHA, y hace commit. ArgoCD detecta el cambio y despliega automaticamente."

**Capturas sugeridas:**
1. Navegador: GitHub Actions — CI workflow running/passed
2. Navegador: GitHub Actions — CD workflow steps
3. Navegador: GitHub commit mostrando values-dev.yaml actualizado

---

## 6:45 — Seccion 6: Deploy + rollback (45s)

**Dialogo:**
"Verificamos que el despliegue fue exitoso. El pod esta corriendo en el namespace dev, la health check pasa, y el endpoint de productos responde."

**Comandos:**
```bash
kubectl get pods -n dev
curl http://localhost:8080/actuator/health
curl http://localhost:8080/api/v1/products
```

**Dialogo:**
"Si algo sale mal, podemos hacer rollback con ArgoCD a una revision anterior, o con kubectl rollout undo. La salud post-rollback se verifica con el mismo health endpoint."

**Comandos rollback:**
```bash
argocd app rollback microservice-dev 1
kubectl rollout status deployment/microservice-dev -n dev
```

**Capturas sugeridas:**
1. Terminal: `kubectl get pods` con pod Ready
2. Terminal: curl products response (JSON array)
3. Terminal: rollback command + status

---

## 7:30 — Outro (30s)

**Dialogo:**
"Eso fue todo. Hemos visto el ciclo completo: build local, Docker, Helm, ArgoCD y CI/CD automatizado. Todo el codigo y configuracion estan en GitHub."

**Dialogo:**
"Gracias por ver."

**Capturas sugeridas:**
- Pantalla final con repo URL: https://github.com/Itsumohitoride/actividad_3_VF_1

---

## Resumen de comandos

```bash
# Local
docker build -t microservice:latest .
docker compose up --build -d
curl localhost:8080/actuator/health

# Docker push
docker tag microservice:latest ghcr.io/itsumohitoride/actividad-3-vf-1-microservice:demo
docker push ghcr.io/itsumohitoride/actividad-3-vf-1-microservice:demo

# Helm
helm lint ./charts/microservice
helm template ./charts/microservice --values ./charts/microservice/values-dev.yaml

# ArgoCD
argocd login localhost:8080 --username admin
argocd app get microservice-dev
argocd app sync microservice-dev

# K8s
kubectl get pods -n dev
kubectl rollout undo deployment/microservice-dev -n dev
```

## Recursos para edicion

- **Resolucion:** 1920x1080 (16:9)
- **Terminal:** Windows Terminal con tema oscuro, fuente Cascadia Code
- **Editor:** VS Code con tema oscuro
- **Zoom:** 4x en terminal para comandos, cursor visible
- **Transiciones:** Cortes directos (sin efectos)
- **Musica:** Ninguna o instrumental suave durante timelapses
