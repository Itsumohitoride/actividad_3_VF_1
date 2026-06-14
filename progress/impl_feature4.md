# Feature 4 — Etapa 1.3: Analisis de particionamiento

**Fecha:** 2026-06-07
**Estado:** Completado (Cells 61-72 del notebook)
**Base de datos:** PostgreSQL 15 (Docker), Ecommify schema

---

## Resumen

Se analizó el particionamiento actual de la tabla `order`, particionada por RANGE en
`order_purchase_timestamp` con 4 particiones. Se evaluó la distribución de datos,
efectividad del partition pruning en las 10 consultas, y se diseñó una estrategia
de mantenimiento automático y archivado.

---

## 1. Distribución de datos en cada partición

Basado en los EXPLAIN ANALYZE de Feature 2 (Q3, Q9 principalmente):

| Partición | Rango | Filas estimadas | % del total |
|-----------|-------|:---------------:|:-----------:|
| order_2016 | 2016-01-01 → 2017-01-01 | ~300 | ~0.3% |
| order_2017 | 2017-01-01 → 2018-01-01 | ~44,000 | ~45.8% |
| order_2018 | 2018-01-01 → 2019-01-01 | ~52,000 | ~54.1% |
| order_future | 2019-01-01 → MAXVALUE | ~0 | ~0% |
| **Total** | | **~96,096** | **100%** |

### Observaciones
- order_2016 tiene muy pocos datos (<1%), posiblemente datos de prueba
- order_2017 y order_2018 concentran ~99.9% de los datos
- order_future no tiene datos actualmente pero absorberá todo crecimiento futuro
- **Problema**: order_future no tiene límite superior (MAXVALUE), creará desbalance

---

## 2. EXPLAIN ANALYZE: consultas multi-particion vs single-particion

### Consultas que acceden a múltiples particiones (TODAS las consultas)

De las 10 consultas analizadas en Feature 2, **ninguna** accede a una sola partición
gracias al partition pruning. La tabla `order` es accedida vía `Append` en todas las
consultas, que escanea las 4 particiones.

| Consulta | Particiones escaneadas | ¿Pruning? | Filas totales |
|----------|----------------------|:---------:|:-------------:|
| Q1 (order_detail) | 4 | ❌ No (busca por order_id) | 0* |
| Q2 (sales_by_category) | 1 (order_2017) | ✅ Sí (rango Oct-Dic 2017) | 68 |
| Q3 (seller_performance) | 4 | ❌ No (solo filtro status) | 20 |
| Q4 (customer_history) | 4 | ❌ No (busca por customer_id) | 1 |
| Q5 (late_deliveries) | 4 | ❌ No (solo filtro status) | 50 |
| Q6 (payment_analysis) | 4 | ❌ No (solo filtro status) | 4 |
| Q7 (review_analysis) | 4 | ❌ No (solo filtro status) | 20 |
| Q8 (monthly_trend) | 2 (order_2017, 2018) | ✅ Sí (rango 2017-2018) | 20 |
| Q9 (top_customers) | 4 | ❌ No (solo filtro status) | 0* |
| Q10 (geo_distribution) | 4 | ❌ No (solo filtro status) | 0* |

*Q1, Q9, Q10: 0 filas por JOIN condition incorrecta.

### Análisis de pruning
- **Q2**: El filtro `WHERE order_purchase_timestamp >= '2017-10-01' AND < '2018-01-01'`
  permite al planner excluir order_2016, order_2018 y order_future → solo escanea order_2017
- **Q8**: El filtro `WHERE order_purchase_timestamp >= '2017-01-01' AND < '2019-01-01'`
  permite excluir order_2016 y order_future → escanea order_2017 y order_2018
- **Las demás consultas**: No filtran por `order_purchase_timestamp` → NO hay pruning,
  el Append escanea las 4 particiones

---

## 3. Pruning effectiveness analysis

### ¿Qué es partition pruning?
PostgreSQL examina las condiciones WHERE de una consulta y, si la clave de partición
está presente, puede **saltarse** (prune) las particiones que no contienen datos
relevantes. Esto reduce el número de escaneos y mejora el rendimiento.

### Efectividad por consulta

| Nivel | Consultas | Condición |
|-------|-----------|-----------|
| ✅ **Pruning total** | Q2, Q8 | WHERE con rango en order_purchase_timestamp |
| ❌ **Sin pruning** | Q1, Q3, Q4, Q5, Q6, Q7, Q9, Q10 | Sin filtro en columna de partición |

### Impacto medido (de EXPLAIN ANALYZE)
- Q1: Append escanea 4 particiones para encontrar 1 fila → 3 index scans innecesarios
- Q4: Append escanea 4 particiones para encontrar 1 fila → 3 index scans innecesarios
- Q8: Append escanea 2 particiones en vez de 4 → **50% menos de escaneos**

### ¿Por qué tan poco pruning?
1. 8 de 10 consultas filtran por `order_status` o `customer_id` u `order_id`, no por timestamp
2. La columna de partición (`order_purchase_timestamp`) solo aparece en WHERE de Q2 y Q8
3. Las búsquedas puntuales por PK (Q1, Q4) no pueden usar pruning porque la PK incluye
   `order_id` como primer componente, no el timestamp

### Recomendación
- Para mejorar pruning en Q1 y Q4: incluir condición de rango de fecha en el WHERE
  (ej. `WHERE order_id = '...' AND order_purchase_timestamp >= '2017-01-01'`)
- Considerar partición HASH por order_id para búsquedas puntuales (trade-off: pierde
  pruning para consultas temporales)

---

## 4. Recomendaciones de ajustes

### 4.1 Dividir order_future en particiones anuales

**Problema:** `order_future` usa `FOR VALUES FROM ('2019-01-01') TO (MAXVALUE)`,
atrapando todos los datos de 2019 en adelante sin particionar.

**Solución:** Crear particiones anuales específicas:

```sql
CREATE TABLE IF NOT EXISTS order_2019 PARTITION OF "order"
    FOR VALUES FROM ('2019-01-01') TO ('2020-01-01');
CREATE TABLE IF NOT EXISTS order_2020 PARTITION OF "order"
    FOR VALUES FROM ('2020-01-01') TO ('2021-01-01');
CREATE TABLE IF NOT EXISTS order_2021 PARTITION OF "order"
    FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
```

### 4.2 Automatizar creación de particiones

- **Recomendado:** pg_partman con intervalo anual y pre-creación de 2 años
- **Alternativa:** pg_cron + función PL/pgSQL `create_year_partition()`
- **Frecuencia:** Ejecutar cada enero

### 4.3 Política de retención

| Horizonte | Acción | Detalle |
|-----------|--------|---------|
| 0-5 años | Activo | Datos en tabla particionada principal |
| 5-15 años | Archivado | DETACH + mover a schema archive |
| >15 años | Eliminación | DROP partition segura |

### 4.4 Pros/Cons de enfoques alternativos

| Enfoque | Pro | Contra |
|---------|-----|--------|
| **RANGE anual (actual)** | Pruning en consultas temporales. Balance tamaño/partición | Sin pruning en búsquedas por ID. order_future sin límite |
| **RANGE mensual** | Mejor granularidad. Pruning más fino | Demasiadas particiones (12+ por año). Overhead de gestión |
| **LIST por status** | Pruning por estado. Útil si filtran por status | No beneficia consultas temporales. Solo 8 valores |
| **HASH por order_id** | Distribución uniforme. Pruning en búsquedas por ID | Sin pruning temporal. Consultas agregadas escanean todo |
| **Sub-particionamiento** | Pruning por año + mes o año + status | Complejidad alta. Soporte limitado en PostgreSQL |

### Recomendación final
**Mantener RANGE anual** como estrategia principal, pero:
1. Dividir order_future en particiones anuales específicas
2. Agregar índices compuestos en `(order_purchase_timestamp, order_status)` en cada partición
3. Implementar pg_partman para auto-creación
4. Establecer política de archivado a 5 años

---

## 5. Resumen de cambios en el notebook (Cells 61-72)

| Cell | Tipo | Cambio |
|------|------|--------|
| 61 | markdown | Reemplazadas instrucciones placeholder con overview del particionamiento actual |
| 62 | markdown | Tabla de candidatos con 9 tablas, justificación de order como única candidata |
| 63 | code | Conservada query. Agregado comentario con resultados esperados |
| 64 | markdown | Diseño de estrategia: tabla con tipo, columna, granularidad, justificación RANGE vs LIST/HASH |
| 65 | markdown | Tabla candidata con datos reales: ~96k registros, distribución por partición, pruning analysis |
| 66 | markdown | Estado actual: distribución detallada y pruning effectiveness por consulta |
| 67 | code | Conservada query de listado de particiones. Comentario con resultados esperados |
| 68 | code | Conservada query de rangos. Comentario con rangos esperados y recomendación |
| 69 | markdown | Plan de mantenimiento: problemas identificados y 4 recomendaciones |
| 70 | markdown | 3 opciones de auto-creación: pg_partman, pg_cron + PL/pgSQL, script externo |
| 71 | markdown | Política de retención 5/15 años, estrategia DETACH + archive, consideraciones legales |
| 72 | code | Script Python de simulación de archivado con lógica de retención |

---

## Archivos modificados
- `progress/impl_feature4.md` — Este reporte.
- `progress/current.md` — Estado de sesión actual.
- `feature_list.json` — Feature 4 marcada como in_progress.
- `src/Ecommify_Database_Design/notebooks/U4_Etapa1_Investigacion.ipynb` — Cells 61-72 actualizadas.
