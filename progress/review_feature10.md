# Review — feature 10 (setup_mongodb_u5)

**Veredicto:** CHANGES_REQUESTED

## Checkpoints
- C1: [x] — Arnés completo, harness verde (30/30 tests)
- C2: [x] — Estado coherente, una feature in_progress
- C3: [x] — Código respeta arquitectura y convenciones
- C4: [ ] — Feature F10 no tiene tests dedicados; verify_env.py no actualizado
- C5: [ ] — Feature in_progress, sesión no cerrada
- C6: [ ] — Feature in_progress, costo no registrado
- C7: [x] — Docs de despliegue/conf existentes (no afectados aún)

## Archivos validados

### 1. mongodb/schema/geolocation_schema.json ✅
- Existe, JSON válido ✓
- Schema validation con 5 campos requeridos: zip_code_prefix (string), lat (double), lng (double), city (string), state (string) ✓
- 2 índices: compuesto {state:1, city:1} y {zip_code_prefix:1} ✓
- Ubicación correcta en mongodb/schema/ ✓

### 2. mongodb/schema/products_schema.json ✅
- Modificado con 7 campos CSV añadidos (product_name_lenght, product_description_lenght, product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm) ✓
- Todos los 6 índices originales preservados (product_id unique, category_name, tags, avg_review_score, created_at, full-text) ✓

### 3. mongodb/seed_data/02_load_from_csv.py ✅
- Existe, Python válido ✓
- Usa pymongo + python-dotenv ✓
- Carga .env con MONGO_USER/MONGO_PASSWORD ✓
- load_geolocation(): batch inserts de 1000 docs, crea índices, muestra top 5 estados ✓
- load_products(): carga traducción, upsert de productos con campos CSV ✓
- verify_all(): verifica las 4 colecciones con conteos ✓
- Manejo de errores (BulkWriteError, ConnectionFailure) ✓

### 4. notebooks/U5_Etapa1_MongoDB_Optimizacion.ipynb ✅
- JSON válido, nbformat 4, 57 celdas ✓
- Celda 1.3: carga MONGO_USER/MONGO_PASSWORD desde .env, construye URI ✓
- Celda 1.9.1: carga geolocation_schema.json, crea GEOLOCATION con validación e índices ✓
- Celda 1.9.2: lee CSV, batch inserts 1000 docs ✓
- Celda 1.9.3: lee traducciones + products CSV, upsert con campos CSV ✓
- Celda 1.9.4: verifica 4 colecciones (GEOLOCATION, products, event_logs, user_sessions) con conteos ✓
- Celda 1.9.5: consultas de validación (muestras GEOLOCATION, top estados, traducciones, campos CSV, resumen eventos/sesiones) ✓

### Harness check ✅
- 30 tests, todos verdes ✓
- Exit code 0 ✓

## Cambios requeridos

1. **scripts/verify_env.py no actualizado** — La acceptance criteria de F10 exige: "scripts/verify_env.py actualizado para verificar conexion MongoDB". No se modificó. El implementador alegó una regla "NEVER modify scripts/" que **no existe** en AGENTS.md, docs/conventions.md ni ningún documento del proyecto. Esta es una regla auto-declarada, no una restricción real del proyecto.

   **Acción requerida:** Actualizar scripts/verify_env.py para incluir verificación de conexión MongoDB (pymongo ping test).

2. **Feature en in_progress sin avanzar** — F10 debería pasar a "testing" o "done" después de resolver el punto 1. Actualmente está bloqueada por una restricción inexistente.
