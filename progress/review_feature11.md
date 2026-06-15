# Review — Feature 11: compound_partial_indexes

**Veredicto:** CHANGES_REQUESTED

## Checkpoints
- C1: [x]
- C2: [x]
- C3: [x]
- C4: [ ]  ← Razón: Falta validación .explain() para índices de event_logs y user_sessions
- C5: [x]
- C6: [x]
- C7: [x]

## Acceptance Criteria

### 1. Al menos 3 índices compuestos siguiendo regla ESR → ✅ PASS
- `products_catalog`: idx_esr_category_score_id — {product_category_name:1, avg_review_score:-1, product_id:1}
  - E=product_category_name (equality), S=avg_review_score -1 (sort), R=product_id (covering)
- `event_logs`: idx_esr_type_time_session — {event_type:1, timestamp:-1, session_id:1}
  - E=event_type (equality), S=timestamp -1 (sort), R=session_id (range for session grouping)
- `user_sessions`: idx_esr_customer_created — {customer_unique_id:1, created_at:-1}
  - E=customer_unique_id (equality), S=created_at -1 (sort), no range needed

### 2. Al menos 2 índices parciales → ✅ PASS
- `products_catalog`: idx_partial_high_rated — partialFilterExpression: {avg_review_score: { $gte: 4.0 }}
- `event_logs`: idx_partial_product_view — partialFilterExpression: {event_type: "product_view"}

### 3. Cada índice documentado con justificación ESR → ✅ PASS
- Los 5 índices tienen campo `description` con justificación ESR y uso esperado.

### 4. DDL de índices guardado en mongodb/schema/ → ✅ PASS
- Archivos modificados en src/Ecommify_Database_Design/mongodb/schema/
- products_catalog_schema.json: líneas 40-41 (2 índices nuevos)
- event_logs_schema.json: líneas 33-34 (2 índices nuevos)
- user_sessions_schema.json: línea 33 (1 índice nuevo)

### 5. Validación con .explain("executionStats") antes/después → ❌ FAIL
- **products_catalog ESR**: Section 1.1 del notebook — BEFORE/AFTER explain presente ✅
- **products_catalog partial**: Section 1.2 del notebook — BEFORE/AFTER explain presente ✅
- **event_logs ESR**: Sin celda explain en el notebook ❌
- **event_logs partial**: Sin celda explain en el notebook ❌
- **user_sessions ESR**: Sin celda explain en el notebook ❌

Solo 2 de 5 índices tienen validación explain() antes/después.

## Issues

### 🔴 Issue 1 (CRITICAL): Falta explain() para event_logs y user_sessions
El archivo notebooks/U5_Etapa1_MongoDB_Optimizacion.ipynb solo tiene celdas explain() para products_catalog (sección 1.1 y 1.2). Faltan:
- Antes/después de crear idx_esr_type_time_session en event_logs
- Antes/después de crear idx_partial_product_view en event_logs
- Antes/después de crear idx_esr_customer_created en user_sessions

**Fix**: Agregar celdas en el notebook que:
1. Hagan query sin índice (dropearlo si existe)
2. Ejecuten explain("executionStats")
3. Creen el índice
4. Re-ejecuten explain("executionStats")
5. Comparen métricas (nReturned, totalDocsExamined, executionTimeMillis)

### 🟡 Issue 2 (MODERATE): Nombre de campo inconsistente en products_catalog
Los índices ESR y parcial usan `product_category_name` en su key, pero:
- El schema define `category_name` (línea 11 de products_catalog_schema.json)
- El índice existente en línea 35 usa `category_name`
- El campo `product_category_name` no está definido en las propiedades del schema

**Fix**: Cambiar `product_category_name` a `category_name` en:
- products_catalog_schema.json línea 40 (key del ESR index)
- products_catalog_schema.json línea 41 (key del partial index)
- O actualizar el schema si el campo real en la colección se llama distinto

### 🔵 Issue 3 (MINOR): Nombres de índices inconsistentes entre DDL y notebook
- DDL: `idx_esr_category_score_id` / `idx_partial_high_rated`
- Notebook: `esr_category_score_id` / `partial_high_rated`
(sin prefijo `idx_`)

### 🔵 Issue 4 (MINOR): session_id como "range" en ESR justification
En idx_esr_type_time_session, session_id se lista como campo de rango, pero el patrón más común es equality. La justificación ESR sería más clara si se documentara como equality scan para agrupación por sesión en vez de "range scan".

## Resumen

| Criterio | Estado |
|----------|--------|
| 1. 3+ ESR indexes | ✅ |
| 2. 2+ partial indexes | ✅ |
| 3. Documentación ESR | ✅ |
| 4. DDL en mongodb/schema/ | ✅ |
| 5. explain() BEFORE/AFTER | ❌ |

**Se requiere agregar celdas de validación explain() para event_logs y user_sessions antes de aprobar.**
