# Feature 1 — Configuracion del harness como experto en bases de datos

## Resumen

Se implementó la configuración completa del harness como experto en bases de datos PostgreSQL para el proyecto Ecommify.

## Archivos creados/modificados

### Creados
- `docker-compose.yml` — Docker Compose para PostgreSQL 15 con healthcheck, volumen de schema y credenciales dev
- `src/Ecommify_Database_Design/notebooks/U4_Etapa1_Investigacion.ipynb` — Notebook template con 34 celdas (markdown + código) para Etapa 1
- `src/Ecommify_Database_Design/notebooks/U4_Etapa2_Implementacion.ipynb` — Notebook template con 41 celdas (markdown + código) para Etapa 2

### Modificados
- `docs/deployment.md` — Instrucciones completas de Docker: iniciar, detener, conectar, resetear DB
- `docs/configuration.md` — Parámetros de conexión, connection strings (psycopg2, SQLAlchemy, psql)
- `scripts/verify_env.py` — Nuevas funciones `check_docker()` y `check_postgres_container()` para verificar Docker + contenedor PostgreSQL

## Criterios de aceptación cumplidos

| # | Criterio | Estado |
|---|----------|--------|
| 1 | docker-compose.yml levanta PostgreSQL 15 con schema Ecommify precargado | OK |
| 2 | docs/deployment.md documenta cómo iniciar/detener/conectarse a PostgreSQL via Docker | OK |
| 3 | docs/configuration.md documenta credenciales, puerto, conexión | OK |
| 4 | notebooks/U4_Etapa1_Investigacion.ipynb creado como notebook template para Etapa 1 | OK |
| 5 | notebooks/U4_Etapa2_Implementacion.ipynb creado como notebook template para Etapa 2 | OK |
| 6 | scripts/verify_env.py verifica Docker y conexión básica a PostgreSQL | OK |
| 7 | python scripts/check_harness.py termina sin errores | OK |

## Detalles técnicos

### docker-compose.yml
- Imagen: `postgres:15`
- Puerto: `5432:5432`
- Volumen: `./src/Ecommify_Database_Design/postgresql/schema:/docker-entrypoint-initdb.d`
- Healthcheck con pg_isready (10s intervalo, 5 retries, 30s start period)
- Restart: unless-stopped

### verify_env.py
- `check_docker()`: Verifica docker --version y docker compose version
- `check_postgres_container()`: Verifica Docker engine reachable + docker compose ps. No es fatal si Docker engine no está corriendo (warning)
- Se ejecuta en la sección "Docker" de la verificación

### Notebooks
- Ambos notebooks tienen conexión psycopg2 a PostgreSQL, funciones helper (run_query, run_explain), y celdas placeholder para las secciones de cada etapa
- Celdas SQL ejecutables (comentadas como placeholder) para completar durante las etapas
