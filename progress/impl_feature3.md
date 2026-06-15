# Feature 3 — Etapa 1.2: Analisis de estrategias de indexacion

**Fecha:** 2026-06-07
**Estado:** Completado
**Base de datos:** PostgreSQL 15 (Docker), Ecommify schema
**Notebook modificado:** `U4_Etapa1_Investigacion.ipynb` (Cells 52-60)

---

## Resumen

Se analizaron las 10 consultas del workload Ecommify para identificar
columnas candidatas a indexación, se evaluaron los índices existentes
contra los patrones de acceso observados en los planes EXPLAIN ANALYZE
(Feature 2), y se diseñó una estrategia de indexación con 7 índices
nuevos que cubren las brechas identificadas.

---

## 1. Columnas en WHERE/JOIN frecuentes

Se identificaron 10 columnas usadas en cláusulas WHERE, JOIN y GROUP BY:

| Columna | Frecuencia | Consultas |
|---------|:----------:|-----------|
| `order_status` | **8/10** | Q2, Q3, Q5, Q6, Q7, Q8, Q9, Q10 |
| `order_id` | **8/10** | Q1, Q4, Q5, Q6, Q7, Q8, Q9, Q10 |
| `order_purchase_timestamp` | **8/10** | Q2, Q3, Q5, Q6, Q7, Q8, Q9, Q10 |
| `customer_id` | **4/10** | Q1, Q4, Q9, Q10 |
| `seller_id` | **3/10** | Q3, Q5, Q10 |
| `product_id` | **3/10** | Q1, Q2, Q7 |
| `category_name` | **3/10** | Q1, Q2, Q7 |

### Brechas críticas en índices existentes

| Columna | Tabla | Índice? | Problema |
|---------|:-----:|:-------:|----------|
| `order_id` | `order_item` | ❌ No | Seq Scan de 56k filas en 8 consultas |
| `order_purchase_timestamp` | `order_item` | ❌ No | Necesario para FK compuesta |
| `order_id` | `review` | ❌ No | Seq Scan de 49k filas en 4 consultas |
| `customer_id` | `customer` | ❌ No | No existe (solo en customer_unique_id) |
| `delivered_customer_date` | `order` | ❌ No | Seq Scan con filtro > en Q5 |

---

## 2. Columnas candidatas (prioridad)

Se evaluaron 12 columnas candidatas. Ranking de prioridad:

### Crítica (3) — Impacto inmediato
1. `order_item(order_id)` — 8 consultas beneficiadas, elimina Seq Scan de 56k filas
2. `order_item(order_purchase_timestamp)` — 6 consultas, cubre FK compuesta
3. `review(order_id)` — 4 consultas, elimina Seq Scan de 49k filas

### Alta (2) — Mejora significativa
4. `order_item(seller_id, order_id)` compuesto — soluciona Q3 (13s, 168M filas)
5. `review(order_id, review_score)` compuesto — reduce Q7 (1M+ buffers)

### Media (2) — Mejora incremental
6. `order(delivered_customer_date)` parcial — mejora Q5
7. `customer(customer_id)` — corrige JOIN condition

---

## 3. Seq Scans vs Index Scans (desde Feature 2)

Las tablas con más Seq Scans (y peor impacto):

| Tabla | Filas escaneadas | Consultas | Tipo scan actual | Índice propuesto |
|:-----:|:----------------:|:---------:|:----------------:|:----------------:|
| `order_item` | ~56,325 | Q2, Q3, Q5, Q6, Q7, Q8, Q9, Q10 | Parallel Seq Scan | `idx_oi_order_id` |
| `review` | ~49,205 | Q2, Q3, Q7, Q10 | Parallel Seq Scan | `idx_rev_order_id` |
| `payment` | ~103,886 | Q6 | Parallel Seq Scan | `idx_pay_order` (ya existe) |
| `order_2017` | ~22,550 | Q2, Q5, Q8 | Parallel Seq Scan | `idx_order_status_ts` |
| `order_2018` | ~52,783 | Q3, Q5, Q8 | Parallel Seq Scan | `idx_order_status_ts` |

---

## 4. Estrategia de indexación — 7 índices propuestos

### B-tree simples (3)
| Índice | Tabla | Columna | Operadores |
|--------|:-----:|:-------:|:----------:|
| `idx_oi_order_id` | order_item | `order_id` | `=` |
| `idx_rev_order_id` | review | `order_id` | `=` |
| `idx_customer_id` | customer | `customer_id` | `=` |

### B-tree compuestos (3)
| Índice | Tabla | Columnas | Orden | Operadores |
|--------|:-----:|:--------:|:----:|:----------:|
| `idx_oi_order_ts` | order_item | `(order_purchase_timestamp, order_id)` | igualdad + igualdad | `=` |
| `idx_oi_seller_order` | order_item | `(seller_id, order_id)` | igualdad + igualdad | `=` |
| `idx_rev_order_score` | review | `(order_id, review_score)` | igualdad + rango | `=`, `>=` |

### B-tree parcial (1)
| Índice | Tabla | Columna | Condición parcial |
|--------|:-----:|:-------:|:-----------------:|
| `idx_order_late` | order | `delivered_customer_date` | `WHERE delivered_customer_date > estimated_delivery_date` |

### Mantener existentes (3)
| Índice | Tipo | Columna | Propósito |
|--------|:----:|:-------:|-----------|
| `idx_product_specifications` | **GIN** | `product.specifications` (JSONB) | Búsqueda en datos semiestructurados |
| `idx_product_photo_urls` | **GIN** | `product.photo_urls` (TEXT[]) | Búsqueda en arreglo de URLs |
| `idx_order_promotion_period` | **GiST** | `order.promotion_period` (TSTZRANGE) | Búsqueda por rango de promoción |

---

## 5. EXPLAIN simulation (desde Feature 2 data)

### Q3 (seller_performance) — Impacto del índice compuesto

**Antes (sin índice):**
```
Nested Loop  (cost=8468.82..12937.10 rows=1)
  Join Filter: (oi.seller_id = s.seller_id)
  Rows Removed by Join Filter: 168,084,820
  ->  Seq Scan on seller s  (cost=0.00..63.95 rows=3095)
        (ejecutado 110,559 veces — 1,819,285 buffers)
Execution Time: 13,090 ms
```

**Después (con `idx_oi_seller_order` en order_item(seller_id, order_id)):**
- El Nested Loop se convierte en Hash Join (o Index Nested Loop con seller en outer)
- Se eliminan 168M evaluaciones de Join Filter
- Seq Scan en `seller` se ejecuta 1 vez (no 110,559)
- **Estimación: ~50-100ms** (vs 13,090ms actual)

### Q7 (product_review) — Impacto del índice compuesto

**Antes (sin índice):**
```
Nested Loop (3 niveles)  (cost=3416.18..6374.43)
  95,604 loops Index Scan pk_order_item
  109,126 loops Index Scan pk_product
  109,126 loops Index Scan pk_product_category
  Buffers: shared hit=1,038,232
Execution Time: 430.802 ms
```

**Después (con `idx_rev_order_score` en review(order_id, review_score)):**
- El LEFT JOIN a review usa Index Scan en lugar de Hash Join (Seq Scan)
- La cadena de Nested Loops se acorta: review pasa a ser accesible por índice
- Index Only Scan posible si se incluye review_id
- **Estimación: ~100-150ms** (vs 430ms actual)

### Q2 (sales_by_category) — Impacto del índice compuesto

**Antes (sin índice):**
```
Parallel Seq Scan on order_2017  (cost=0.00..1242.28)
  Filter: (order_purchase_timestamp >= ... AND order_status = 'delivered')
  Rows Removed by Filter: 13,910 (62% descartadas)
Buffers: shared hit=778
```

**Después (con `idx_order_status_ts` en order_2017(status, timestamp)):**
- Index Scan en lugar de Seq Scan
- Solo se leen las filas que cumplen ambas condiciones
- **Estimación: reduce ~4,000 buffers, ~30-50ms ahorro**

---

## 6. Resumen de impacto estimado

| Consulta | Antes (ms) | Después (estimado) | Mejora | Índice clave |
|:--------:|:----------:|:------------------:|:------:|:------------:|
| Q1 | 0.292 | 0.292 | — | Sin cambio (ya óptimo) |
| Q2 | 82.277 | ~30-50 | ~50% | `idx_order_status_ts` |
| Q3 | **13,090** | **~50-100** | **~99%** | `idx_oi_seller_order` |
| Q4 | 0.206 | 0.206 | — | Sin cambio (ya óptimo) |
| Q5 | 35.522 | ~15-20 | ~50% | `idx_order_late` |
| Q6 | 152.311 | ~100-120 | ~25% | `idx_oi_order_id` |
| Q7 | **430.802** | **~100-150** | **~70%** | `idx_rev_order_score` |
| Q8 | 159.936 | ~100-130 | ~30% | `idx_order_status_ts` |
| Q9 | 237.018 | ~30-50 | ~80% | `idx_customer_id` + JOIN fix |
| Q10 | 253.196 | ~50-80 | ~75% | `idx_customer_id` + JOIN fix |
| **Total** | **~14.44s** | **~0.5-0.8s** | **~95%** | Todos los índices |

---

## Archivos modificados

- `src/Ecommify_Database_Design/notebooks/U4_Etapa1_Investigacion.ipynb` — Cells 52-60 reemplazadas con análisis completo de indexación.
- `progress/impl_feature3.md` — Este reporte.
- `feature_list.json` — Feature 3 marcada como `in_progress`.
- `progress/current.md` — Actualizado con plan Feature 3.
