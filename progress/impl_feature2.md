# Feature 2 — Etapa 1.1: Analisis de planes de ejecucion con EXPLAIN y ANALYZE

**Fecha:** 2026-06-06
**Estado:** Completado (ALL 10 queries)
**Base de datos:** PostgreSQL 15 (Docker), Ecommify schema

---

## Resumen

Se ejecutó `EXPLAIN (ANALYZE, BUFFERS, TIMING)` sobre las **10 consultas** existentes en `postgresql/queries/`. Se analizaron nodos de ejecución, costos, filas estimadas vs reales, uso de buffers, tiempos de planificación y ejecución, paralelismo, y spills a disco.

### Problemas de calidad de datos identificados

1. **Q1, Q9, Q10**: La columna `customer_unique_id` en `customer` NO coincide con `customer_id` en `order`. Las consultas usan `c.customer_unique_id = o.customer_id` que retorna 0 filas. La columna correcta sería `c.customer_id = o.customer_id` (96,096 coincidencias existen). 
2. **Q4**: El `customer_id` '8d7941984c29d3bd1e5c3e5b9c5e9c3e' original no existe. Se reemplazó con '00012a2ce6f8dcda20d059ce98491703' que sí tiene datos.

---

## Query 1: `01_order_detail.sql` — Detalle de orden

### Query
```sql
SELECT o.order_id, c.customer_unique_id, o.order_status,
       o.order_purchase_timestamp, oi.order_item_id, p.product_id,
       pc.name_english AS category, oi.price, oi.freight_value,
       pay.payment_type, pay.payment_installments, pay.payment_value
FROM "order" o
JOIN customer c ON o.customer_id = c.customer_unique_id
JOIN order_item oi ON o.order_id = oi.order_id
JOIN product p ON oi.product_id = p.product_id
JOIN product_category pc ON p.category_name = pc.category_name
JOIN payment pay ON o.order_id = pay.order_id
WHERE o.order_id = 'd3c8851a6651eeff2f73b0e011ac45d0';
```

### Fix aplicado
`WHERE` reemplazado con `order_id` real: `d3c8851a6651eeff2f73b0e011ac45d0`

### Filas retornadas: 0 (problema JOIN customer, ver nota datos)

### EXPLAIN ANALYZE output
```
Nested Loop  (cost=2.08..76.59 rows=4 width=179) (actual time=0.169..0.170 rows=0 loops=1)
  Buffers: shared hit=28
  ->  Nested Loop  (cost=1.67..58.85 rows=4 width=204) (actual time=0.108..0.157 rows=1 loops=1)
        Buffers: shared hit=25
        ->  Nested Loop  (cost=1.39..25.47 rows=1 width=142) (actual time=0.087..0.088 rows=1 loops=1)
              Buffers: shared hit=14
              ->  Nested Loop  (cost=0.98..17.03 rows=1 width=97) (actual time=0.052..0.053 rows=1 loops=1)
                    Buffers: shared hit=10
                    ->  Nested Loop  (cost=0.83..16.87 rows=1 width=95) (actual time=0.046..0.046 rows=1 loops=1)
                          Buffers: shared hit=8
                          ->  Index Scan using pk_order_item on order_item oi  (cost=0.42..8.44 rows=1 width=80) (actual time=0.028..0.029 rows=1 loops=1)
                                Index Cond: (order_id = 'd3c8851a6651eeff2f73b0e011ac45d0'::bpchar)
                                Buffers: shared hit=4
                          ->  Index Scan using pk_product on product p  (cost=0.41..8.43 rows=1 width=48) (actual time=0.015..0.015 rows=1 loops=1)
                                Index Cond: (product_id = oi.product_id)
                                Buffers: shared hit=4
                    ->  Index Scan using pk_product_category on product_category pc  (cost=0.14..0.16 rows=1 width=34) (actual time=0.006..0.006 rows=1 loops=1)
                          Index Cond: ((category_name)::text = (p.category_name)::text)
                          Buffers: shared hit=2
              ->  Index Scan using idx_pay_order on payment pay  (cost=0.42..8.44 rows=1 width=45) (actual time=0.035..0.035 rows=1 loops=1)
                    Index Cond: (order_id = 'd3c8851a6651eeff2f73b0e011ac45d0'::bpchar)
                    Buffers: shared hit=4
        ->  Append  (cost=0.27..33.34 rows=4 width=128) (actual time=0.020..0.067 rows=1 loops=1)
              Buffers: shared hit=11
              ->  Index Scan using order_2016_pkey on order_2016 o_1  (cost=0.27..8.29 rows=1 width=78) (actual time=0.020..0.020 rows=1 loops=1)
                    Index Cond: (order_id = 'd3c8851a6651eeff2f73b0e011ac45d0'::bpchar)
                    Buffers: shared hit=3
              ->  Index Scan using order_2017_pkey on order_2017 o_2  (cost=0.41..8.43 rows=1 width=78) (actual time=0.020..0.020 rows=0 loops=1)
                    Index Cond: (order_id = 'd3c8851a6651eeff2f73b0e011ac45d0'::bpchar)
                    Buffers: shared hit=3
              ->  Index Scan using order_2018_pkey on order_2018 o_3  (cost=0.41..8.43 rows=1 width=78) (actual time=0.023..0.023 rows=0 loops=1)
                    Index Cond: (order_id = 'd3c8851a6651eeff2f73b0e011ac45d0'::bpchar)
                    Buffers: shared hit=3
              ->  Index Scan using order_future_pkey on order_future o_4  (cost=0.14..8.16 rows=1 width=276) (actual time=0.004..0.004 rows=0 loops=1)
                    Index Cond: (order_id = 'd3c8851a6651eeff2f73b0e011ac45d0'::bpchar)
                    Buffers: shared hit=2
  ->  Index Only Scan using idx_customer_unique_id on customer c  (cost=0.42..4.44 rows=1 width=33) (actual time=0.012..0.012 rows=0 loops=1)
        Index Cond: (customer_unique_id = o.customer_id)
        Heap Fetches: 0
        Buffers: shared hit=3
Planning:
  Buffers: shared hit=1013
Planning Time: 2.137 ms
Execution Time: 0.292 ms
```

### Metricas

| Metrica | Valor |
|---------|-------|
| Planning Time | 2.137 ms |
| Execution Time | 0.292 ms |
| Costo total | 76.59 |
| Filas estimadas | 4 |
| Filas reales | 0 (customer JOIN mismatch) |
| Buffers shared hit | 28 |
| Nodos de ejecucion | 13 |
| Paralelismo | No |

### Nodos analizados en detalle

**1. Index Scan on `order_item` (pk_order_item):**
- Costo: 0.42..8.44, filas: 1 real
- Búsqueda eficiente por PK

**2. Append sobre particiones de `order`:**
- Revisa las 4 particiones (2016, 2017, 2018, future)
- Solo order_2016 retorna 1 fila
- Partition pruning inefectivo: revisa todas aunque el order_id solo existe en una

**3. Index Only Scan on `customer` (idx_customer_unique_id):**
- 0 filas reales — `customer_unique_id` no coincide con `order.customer_id`
- Causa raiz: las consultas usan columna incorrecta para el JOIN

### Bottlenecks (Q1)
1. **Partition pruning inefectivo**: 4 index scans innecesarios
2. **JOIN condicion incorrecta**: `customer_unique_id` vs `customer_id`
3. Tiempo total irrelevante (0.29ms) por ser query puntual con PK

---

## Query 2: `02_sales_by_category.sql` — Ventas por categoria

### Query
```sql
SELECT pc.name_english AS category,
       COUNT(DISTINCT o.order_id) AS total_orders,
       SUM(oi.price) AS gross_revenue,
       ROUND(AVG(r.review_score), 2) AS avg_score
FROM "order" o
JOIN order_item oi ON o.order_id = oi.order_id
JOIN product p ON oi.product_id = p.product_id
JOIN product_category pc ON p.category_name = pc.category_name
LEFT JOIN review r ON o.order_id = r.order_id
WHERE o.order_purchase_timestamp >= '2017-10-01'
  AND o.order_purchase_timestamp <  '2018-01-01'
  AND o.order_status = 'delivered'
GROUP BY pc.name_english
ORDER BY gross_revenue DESC;
```

### Filas retornadas: 68

### EXPLAIN ANALYZE output
```
Sort  (cost=14665.55..14665.73 rows=71 width=89) (actual time=78.566..82.085 rows=68 loops=1)
  Sort Key: (sum(oi.price)) DESC
  Sort Method: quicksort  Memory: 30kB
  Buffers: shared hit=6119
  ->  GroupAggregate  (cost=11924.85..14663.37 rows=71 width=89) (actual time=66.431..82.019 rows=68 loops=1)
        Group Key: pc.name_english
        Buffers: shared hit=6116
        ->  Gather Merge  (cost=11924.85..14441.32 rows=22080 width=58) (actual time=66.370..72.281 rows=19631 loops=1)
              Workers Planned: 1
              Workers Launched: 1
              Buffers: shared hit=6113
              ->  Sort  (cost=10924.84..10957.31 rows=12988 width=58) (actual time=64.456..64.987 rows=9816 loops=2)
                    Sort Key: pc.name_english
                    Sort Method: quicksort  Memory: 1329kB
                    Buffers: shared hit=6113
                    Worker 0:  Sort Method: quicksort  Memory: 1323kB
                    ->  Hash Join  (cost=8335.44..10037.44 rows=12988 width=58) (actual time=42.925..61.749 rows=9816 loops=2)
                          Hash Cond: ((p.category_name)::text = (pc.category_name)::text)
                          Buffers: shared hit=6076
                          ->  Hash Join  (cost=8332.84..9998.81 rows=12988 width=56) (actual time=42.853..60.344 rows=9978 loops=2)
                                Hash Cond: (oi.product_id = p.product_id)
                                Buffers: shared hit=6024
                                ->  Parallel Hash Join  (cost=7158.44..8790.32 rows=12988 width=74) (actual time=36.360..50.509 rows=9978 loops=2)
                                      Hash Cond: (o.order_id = oi.order_id)
                                      Buffers: shared hit=5143
                                      ->  Parallel Hash Left Join  (cost=3270.48..4610.31 rows=10148 width=35) (actual time=16.451..25.037 rows=8671 loops=2)
                                            Hash Cond: (o.order_id = r.order_id)
                                            Buffers: shared hit=2746
                                            ->  Parallel Seq Scan on order_2017 o  (cost=0.00..1242.28 rows=10097 width=33) (actual time=0.011..4.251 rows=8640 loops=2)
                                                  Filter: ((order_purchase_timestamp >= ...) AND (order_status = 'delivered'::order_status_enum))
                                                  Rows Removed by Filter: 13910
                                                  Buffers: shared hit=778
                                            ->  Parallel Hash  (cost=2546.88..2546.88 rows=57888 width=35) (actual time=16.178..16.179 rows=49205 loops=2)
                                                  Buckets: 131072  Batches: 1  Memory Usage: 8000kB
                                                  Buffers: shared hit=1968
                                                  ->  Parallel Seq Scan on review r  (cost=0.00..2546.88 rows=57888 width=35) (actual time=0.011..9.379 rows=49205 loops=2)
                                                        Buffers: shared hit=1968
                                      ->  Parallel Hash  (cost=3059.65..3059.65 rows=66265 width=72) (actual time=19.117..19.117 rows=56325 loops=2)
                                            Buckets: 131072  Batches: 1  Memory Usage: 13152kB
                                            Buffers: shared hit=2397
                                            ->  Parallel Seq Scan on order_item oi  (cost=0.00..3059.65 rows=66265 width=72) (actual time=0.007..5.767 rows=56325 loops=2)
                                                  Buffers: shared hit=2397
                                ->  Hash  (cost=762.51..762.51 rows=32951 width=48) (actual time=6.282..6.283 rows=32951 loops=2)
                                      Buckets: 65536  Batches: 1  Memory Usage: 3108kB
                                      Buffers: shared hit=866
                                      ->  Seq Scan on product p  (cost=0.00..762.51 rows=32951 width=48) (actual time=0.007..2.292 rows=32951 loops=2)
                                            Buffers: shared hit=866
                          ->  Hash  (cost=1.71..1.71 rows=71 width=34) (actual time=0.029..0.029 rows=71 loops=2)
                                Buckets: 1024  Batches: 1  Memory Usage: 13kB
                                Buffers: shared hit=2
                                ->  Seq Scan on product_category pc  (cost=0.00..1.71 rows=71 width=34) (actual time=0.010..0.014 rows=71 loops=2)
                                      Buffers: shared hit=2
Planning:
  Buffers: shared hit=635
Planning Time: 1.467 ms
Execution Time: 82.277 ms
```

### Metricas

| Metrica | Valor |
|---------|-------|
| Planning Time | 1.467 ms |
| Execution Time | 82.277 ms |
| Costo total | 14,665.55 |
| Filas estimadas | 71 |
| Filas reales | 68 |
| Buffers shared hit | 6,119 |
| Nodos de ejecucion | 18 |
| Paralelismo | 1 worker planificado, 1 lanzado |

### Nodos analizados

**1. Parallel Seq Scan on `order_2017`:**
- 8,640 filas reales, 13,910 filtradas
- Sin indice compuesto en (order_purchase_timestamp, order_status)

**2. Parallel Hash Join (order + order_item):**
- Hash table: 56,325 filas, 13MB de memoria
- Costo: 7,158..8,790

**3. Parallel Seq Scan on `review`:**
- 49,205 filas escaneadas sin indice en review.order_id

### Bottlenecks (Q2)
1. Seq Scan en order_2017 con filtro — 62% filas descartadas
2. Seq Scan en review (49k filas) para LEFT JOIN
3. Seq Scan en order_item (56k filas) para Hash Join
4. Hash tables combinadas: ~21MB de memoria

---

## Query 3: `03_seller_performance.sql` — Ranking de vendedores

### ⚠️ PEOR RENDIMIENTO: 13 SEGUNDOS

### Query
```sql
SELECT s.seller_id, s.seller_city, s.seller_state,
       COUNT(DISTINCT oi.order_id) AS total_orders,
       SUM(oi.price) AS total_revenue,
       ROUND(AVG(oi.freight_value), 2) AS avg_freight,
       ROUND(AVG(r.review_score), 2) AS avg_review
FROM seller s
JOIN order_item oi ON s.seller_id = oi.seller_id
JOIN "order" o ON oi.order_id = o.order_id AND oi.order_purchase_timestamp = o.order_purchase_timestamp
LEFT JOIN review r ON o.order_id = r.order_id AND o.order_purchase_timestamp = r.order_purchase_timestamp
WHERE o.order_status = 'delivered'
GROUP BY s.seller_id, s.seller_city, s.seller_state
ORDER BY total_revenue DESC
LIMIT 20;
```

### Filas retornadas: 20

### EXPLAIN ANALYZE output
```
Limit  (cost=12937.16..12937.16 rows=1 width=151) (actual time=13083.557..13087.856 rows=20 loops=1)
  Buffers: shared hit=1825500, temp read=1437 written=1441
  ->  Sort  (cost=12937.16..12937.16 rows=1 width=151) (actual time=13083.556..13087.853 rows=20 loops=1)
        Sort Key: (sum(oi.price)) DESC
        Sort Method: top-N heapsort  Memory: 29kB
        Buffers: shared hit=1825500, temp read=1437 written=1441
        ->  GroupAggregate  (cost=12937.11..12937.15 rows=1 width=151) (actual time=13025.869..13087.268 rows=2970 loops=1)
              Group Key: s.seller_id
              Buffers: shared hit=1825497, temp read=1437 written=1441
              ->  Sort  (cost=12937.11..12937.11 rows=1 width=94) (actual time=13025.843..13040.376 rows=110559 loops=1)
                    Sort Key: s.seller_id
                    Sort Method: external merge  Disk: 11496kB
                    Buffers: shared hit=1825497, temp read=1437 written=1441
                    ->  Nested Loop  (cost=8468.82..12937.10 rows=1 width=94) (actual time=34.456..12906.222 rows=110559 loops=1)
                          Join Filter: (oi.seller_id = s.seller_id)
                          Rows Removed by Join Filter: 168084820
                          Buffers: shared hit=1825494
                          ->  Gather  (cost=8468.82..12834.46 rows=1 width=80) (actual time=34.432..69.655 rows=110559 loops=1)
                                Workers Planned: 2
                                Workers Launched: 2
                                Buffers: shared hit=6209
                                ->  Parallel Hash Left Join  (cost=7468.82..11834.36 rows=1 width=80) (actual time=32.182..106.516 rows=36853 loops=3)
                                      Hash Cond: ((o.order_id = r.order_id) AND (o.order_purchase_timestamp = r.order_purchase_timestamp))
                                      Buffers: shared hit=6209
                                      ->  Parallel Hash Join  (cost=4053.62..8419.14 rows=1 width=119) (actual time=19.375..63.184 rows=36732 loops=3)
                                            Hash Cond: ((o.order_id = oi.order_id) AND (o.order_purchase_timestamp = oi.order_purchase_timestamp))
                                            Buffers: shared hit=4115
                                            ->  Parallel Append  (cost=0.00..2656.41 rows=40214 width=41) (actual time=0.016..10.765 rows=32159 loops=3)
                                                  Buffers: shared hit=1718
                                                  ->  Parallel Index Scan using order_future_order_status_order_purchase_timestamp_idx on order_future o_4  (cost=0.14..8.16 rows=1 width=140) (actual time=0.018..0.018 rows=0 loops=1)
                                                        Index Cond: (order_status = 'delivered'::order_status_enum)
                                                        Buffers: shared hit=2
                                                  ->  Parallel Seq Scan on order_2018 o_3  (cost=0.00..1329.14 rows=31044 width=41) (actual time=0.011..15.783 rows=52783 loops=1)
                                                        Filter: (order_status = 'delivered'::order_status_enum)
                                                        Rows Removed by Filter: 1228
                                                        Buffers: shared hit=932
                                                  ->  Parallel Seq Scan on order_2017 o_2  (cost=0.00..1109.62 rows=25571 width=41) (actual time=0.007..5.301 rows=21714 loops=2)
                                                        Filter: (order_status = 'delivered'::order_status_enum)
                                                        Rows Removed by Filter: 836
                                                        Buffers: shared hit=778
                                                  ->  Parallel Seq Scan on order_2016 o_1  (cost=0.00..8.42 rows=157 width=41) (actual time=0.008..0.036 rows=134 loops=2)
                                                        Filter: (order_status = 'delivered'::order_status_enum)
                                                        Rows Removed by Filter: 31
                                                        Buffers: shared hit=6
                                            ->  Parallel Hash  (cost=3059.65..3059.65 rows=66265 width=86) (actual time=18.798..18.799 rows=37550 loops=3)
                                                  Buckets: 131072  Batches: 1  Memory Usage: 14336kB
                                                  Buffers: shared hit=2397
                                                  ->  Parallel Seq Scan on order_item oi  (cost=0.00..3059.65 rows=66265 width=86) (actual time=0.008..5.169 rows=37550 loops=3)
                                                        Buffers: shared hit=2397
                                      ->  Parallel Hash  (cost=2546.88..2546.88 rows=57888 width=43) (actual time=12.251..12.252 rows=32803 loops=3)
                                            Buckets: 131072  Batches: 1  Memory Usage: 8768kB
                                            Buffers: shared hit=1968
                                            ->  Parallel Seq Scan on review r  (cost=0.00..2546.88 rows=57888 width=43) (actual time=0.007..5.639 rows=32803 loops=3)
                                                  Buffers: shared hit=1968
                          ->  Seq Scan on seller s  (cost=0.00..63.95 rows=3095 width=47) (actual time=0.000..0.048 rows=1521 loops=110559)
                                Buffers: shared hit=1819285
Planning:
  Buffers: shared hit=837
Planning Time: 1.785 ms
Execution Time: 13090.123 ms
```

### Metricas

| Metrica | Valor |
|---------|-------|
| Planning Time | 1.785 ms |
| Execution Time | **13,090 ms (13s)** |
| Costo total | 12,937.16 |
| Filas estimadas | 1 (erronea) |
| Filas reales (Nested Loop) | 110,559 |
| Filas descartadas por Join Filter | **168,084,820** |
| Buffers shared hit | **1,825,500** |
| Temp read/written | 1,437 / 1,441 bloques (~11.5MB) |
| Paralelismo | 2 workers |
| Spill a disco | Si — Sort external merge 11.5MB |

### Nodos analizados en detalle

**1. Nested Loop (seller s × subconsulta) — EL CULPABLE:**
- `Seq Scan on seller s` ejecutado **110,559 veces** (una por cada fila del lado izquierdo)
- `Rows Removed by Join Filter: 168,084,820` — **168 MILLONES de filas** procesadas y descartadas
- `shared hit=1,819,285` solo del lado seller
- Causa: El Nested Loop tiene `oi.seller_id = s.seller_id` como Join Filter (no Hash Cond), forzando un producto cartesiano filtrado

**2. Parallel Hash Left Join (order + review):**
- Ejecutado 3 veces (3 workers)
- 36,853 filas promedio
- Hash table de review: 8.7MB

**3. Parallel Append en order:**
- Seq Scans en order_2017 y order_2018 con filtro order_status
- order_2018: 52,783 filas (1,228 filtradas)
- order_2017: 21,714 filas (836 filtradas)

### Bottlenecks (Q3) — CRITICO
1. **⚠️ Nested Loop catastrófico**: 168M filas descartadas en Join Filter. La causa es que `seller` tiene 3,095 filas y la subconsulta 110k filas - el Nested Loop con Join Filter en `s.seller_id = oi.seller_id` produce 168M evaluaciones. **SOLUCION: Usar Hash Join entre seller y order_item, o agregar un indice en order_item.seller_id para permitir Index Nested Loop.**
2. **Spill a disco**: Sort externo de 11.5MB por la agregacion
3. **Seq Scans en order** (con filtro status) sin indices compuestos
4. **Estimacion de filas pesimista**: planner estima 1 fila, realidad 110k

---

## Query 4: `04_customer_order_history.sql` — Historial de ordenes

### Query
```sql
SELECT o.order_id, o.order_purchase_timestamp, o.order_status,
       oi.price, oi.freight_value,
       pay.payment_type, pay.payment_installments, pay.payment_value
FROM "order" o
JOIN order_item oi ON o.order_id = oi.order_id AND o.order_purchase_timestamp = oi.order_purchase_timestamp
JOIN payment pay ON o.order_id = pay.order_id AND o.order_purchase_timestamp = pay.order_purchase_timestamp
WHERE o.customer_id = '00012a2ce6f8dcda20d059ce98491703'
ORDER BY o.order_purchase_timestamp DESC;
```

### Fix aplicado
`customer_id` reemplazado con '00012a2ce6f8dcda20d059ce98491703' (existente en DB)

### Filas retornadas: 1

### EXPLAIN ANALYZE output
```
Sort  (cost=67.66..67.66 rows=1 width=94) (actual time=0.116..0.117 rows=1 loops=1)
  Sort Key: o.order_purchase_timestamp DESC
  Sort Method: quicksort  Memory: 25kB
  Buffers: shared hit=22
  ->  Nested Loop  (cost=1.11..67.65 rows=1 width=94) (actual time=0.076..0.100 rows=1 loops=1)
        Join Filter: ((o.order_id = pay.order_id) AND (o.order_purchase_timestamp = pay.order_purchase_timestamp))
        Buffers: shared hit=19
        ->  Nested Loop  (cost=0.69..67.13 rows=1 width=123) (actual time=0.061..0.084 rows=1 loops=1)
              Buffers: shared hit=15
              ->  Append  (cost=0.27..33.34 rows=4 width=70) (actual time=0.040..0.063 rows=1 loops=1)
                    Buffers: shared hit=11
                    ->  Index Scan using order_2016_customer_id_idx on order_2016 o_1  (cost=0.27..8.29 rows=1 width=45) (actual time=0.016..0.016 rows=0 loops=1)
                          Index Cond: (customer_id = '00012a2ce6f8dcda20d059ce98491703'::bpchar)
                          Buffers: shared hit=2
                    ->  Index Scan using order_2017_customer_id_idx on order_2017 o_2  (cost=0.41..8.43 rows=1 width=45) (actual time=0.024..0.025 rows=1 loops=1)
                          Index Cond: (customer_id = '00012a2ce6f8dcda20d059ce98491703'::bpchar)
                          Buffers: shared hit=4
                    ->  Index Scan using order_2018_customer_id_idx on order_2018 o_3  (cost=0.41..8.43 rows=1 width=45) (actual time=0.015..0.015 rows=0 loops=1)
                          Index Cond: (customer_id = '00012a2ce6f8dcda20d059ce98491703'::bpchar)
                          Buffers: shared hit=3
                    ->  Index Scan using order_future_customer_id_idx on order_future o_4  (cost=0.14..8.16 rows=1 width=144) (actual time=0.007..0.007 rows=0 loops=1)
                          Index Cond: (customer_id = '00012a2ce6f8dcda20d059ce98491703'::bpchar)
                          Buffers: shared hit=2
              ->  Index Scan using pk_order_item on order_item oi  (cost=0.42..8.44 rows=1 width=53) (actual time=0.019..0.019 rows=1 loops=1)
                    Index Cond: (order_id = o.order_id)
                    Filter: (o.order_purchase_timestamp = order_purchase_timestamp)
                    Buffers: shared hit=4
        ->  Index Scan using idx_pay_order on payment pay  (cost=0.42..0.51 rows=1 width=53) (actual time=0.013..0.013 rows=1 loops=1)
              Index Cond: (order_id = oi.order_id)
              Filter: (oi.order_purchase_timestamp = order_purchase_timestamp)
              Buffers: shared hit=4
Planning:
  Buffers: shared hit=778
Planning Time: 1.787 ms
Execution Time: 0.206 ms
```

### Metricas

| Metrica | Valor |
|---------|-------|
| Planning Time | 1.787 ms |
| Execution Time | **0.206 ms** |
| Costo total | 67.66 |
| Filas estimadas | 1 |
| Filas reales | 1 |
| Buffers shared hit | 22 |
| Nodos de ejecucion | 10 |
| Paralelismo | No |

### Analisis
- **Mejor rendimiento de las 10 consultas** (0.2ms)
- Usa indices existentes en order particionado (customer_id_idx en cada particion)
- Nested Loop con Index Scans — optimo para busqueda puntual
- Partition pruning inefectivo: revisa las 4 particiones aunque solo 1 contiene datos

---

## Query 5: `05_late_deliveries.sql` — Entregas tardias

### Query
```sql
SELECT o.order_id, o.order_purchase_timestamp, o.order_estimated_delivery_date,
       o.order_delivered_customer_date,
       (o.order_delivered_customer_date - o.order_estimated_delivery_date) AS days_late,
       s.seller_city, s.seller_state
FROM "order" o
JOIN order_item oi ON o.order_id = oi.order_id AND o.order_purchase_timestamp = oi.order_purchase_timestamp
JOIN seller s ON oi.seller_id = s.seller_id
WHERE o.order_delivered_customer_date > o.order_estimated_delivery_date
  AND o.order_status = 'delivered'
ORDER BY days_late DESC
LIMIT 50;
```

### Filas retornadas: 50

### EXPLAIN ANALYZE output
```
Limit  (cost=8292.41..8292.41 rows=1 width=87) (actual time=32.774..35.442 rows=50 loops=1)
  Buffers: shared hit=30388
  ->  Sort  (cost=8292.41..8292.41 rows=1 width=87) (actual time=32.773..35.439 rows=50 loops=1)
        Sort Key: ((o.order_delivered_customer_date - o.order_estimated_delivery_date)) DESC
        Sort Method: top-N heapsort  Memory: 36kB
        Buffers: shared hit=30388
        ->  Nested Loop  (cost=5053.90..8292.40 rows=1 width=87) (actual time=20.605..34.250 rows=8714 loops=1)
              Buffers: shared hit=30383
              ->  Gather  (cost=5053.62..8292.10 rows=1 width=90) (actual time=20.563..24.266 rows=8714 loops=1)
                    Workers Planned: 2
                    Workers Launched: 2
                    Buffers: shared hit=4241
                    ->  Parallel Hash Join  (cost=4053.62..7292.00 rows=1 width=90) (actual time=18.283..23.612 rows=2905 loops=3)
                          Hash Cond: ((o.order_id = oi.order_id) AND (o.order_purchase_timestamp = oi.order_purchase_timestamp))
                          Buffers: shared hit=4241
                          ->  Parallel Append  (cost=0.00..2668.61 rows=13406 width=57) (actual time=0.048..3.567 rows=2609 loops=3)
                                Buffers: shared hit=1718
                                ->  Parallel Index Scan using order_future_order_status_order_purchase_timestamp_idx on order_future o_4  (cost=0.14..8.16 rows=1 width=156) (actual time=0.024..0.025 rows=0 loops=1)
                                      Index Cond: (order_status = 'delivered'::order_status_enum)
                                      Filter: (order_delivered_customer_date > order_estimated_delivery_date)
                                      Buffers: shared hit=2
                                ->  Parallel Seq Scan on order_2018 o_3  (cost=0.00..1408.57 rows=10348 width=57) (actual time=0.026..5.061 rows=4944 loops=1)
                                      Filter: ((order_delivered_customer_date > order_estimated_delivery_date) AND (order_status = 'delivered'::order_status_enum))
                                      Rows Removed by Filter: 49067
                                      Buffers: shared hit=932
                                ->  Parallel Seq Scan on order_2017 o_2  (cost=0.00..1175.95 rows=8524 width=57) (actual time=0.017..1.707 rows=959 loops=3)
                                      Filter: ((order_delivered_customer_date > order_estimated_delivery_date) AND (order_status = 'delivered'::order_status_enum))
                                      Rows Removed by Filter: 14074
                                      Buffers: shared hit=778
                                ->  Parallel Seq Scan on order_2016 o_1  (cost=0.00..8.90 rows=52 width=57) (actual time=0.051..0.105 rows=4 loops=1)
                                      Filter: ((order_delivered_customer_date > order_estimated_delivery_date) AND (order_status = 'delivered'::order_status_enum))
                                      Rows Removed by Filter: 325
                                      Buffers: shared hit=6
                          ->  Parallel Hash  (cost=3059.65..3059.65 rows=66265 width=74) (actual time=17.664..17.665 rows=37550 loops=3)
                                Buckets: 131072  Batches: 1  Memory Usage: 14304kB
                                Buffers: shared hit=2397
                                ->  Parallel Seq Scan on order_item oi  (cost=0.00..3059.65 rows=66265 width=74) (actual time=0.007..4.665 rows=37550 loops=3)
                                      Buffers: shared hit=2397
              ->  Index Scan using pk_seller on seller s  (cost=0.28..0.30 rows=1 width=47) (actual time=0.001..0.001 rows=1 loops=8714)
                    Index Cond: (seller_id = oi.seller_id)
                    Buffers: shared hit=26142
Planning:
  Buffers: shared hit=826
Planning Time: 1.461 ms
Execution Time: 35.522 ms
```

### Metricas

| Metrica | Valor |
|---------|-------|
| Planning Time | 1.461 ms |
| Execution Time | 35.522 ms |
| Costo total | 8,292.41 |
| Filas estimadas | 1 |
| Filas reales (Nested Loop) | 8,714 |
| Buffers shared hit | 30,388 |
| Paralelismo | 2 workers |

### Analisis
- Parallel Hash Join entre order y order_item con Hash Cond compuesta (order_id + timestamp)
- Seq Scans en order_2017/2018 con filtros ineficientes (49,067 filas descartadas en 2018)
- Index Scan en seller (8,714 loops) — eficiente por PK
- Principal problema: Seq Scans en order_2017/2018 sin indice compuesto

---

## Query 6: `06_payment_method_analysis.sql` — Metodos de pago

### Query
```sql
SELECT pay.payment_type, COUNT(DISTINCT pay.order_id) AS total_orders,
       COUNT(*) AS total_payments, SUM(pay.payment_value) AS total_value,
       ROUND(AVG(pay.payment_value), 2) AS avg_payment,
       ROUND(AVG(pay.payment_installments), 1) AS avg_installments
FROM payment pay
JOIN "order" o ON pay.order_id = o.order_id AND pay.order_purchase_timestamp = o.order_purchase_timestamp
WHERE o.order_status = 'delivered'
GROUP BY pay.payment_type
ORDER BY total_value DESC;
```

### Filas retornadas: 4

### EXPLAIN ANALYZE output
```
Sort  (cost=8376.01..8376.02 rows=1 width=116) (actual time=148.630..150.766 rows=4 loops=1)
  Sort Key: (sum(pay.payment_value)) DESC
  Sort Method: quicksort  Memory: 25kB
  Buffers: shared hit=3040, temp read=1029 written=1032
  ->  GroupAggregate  (cost=8375.96..8376.00 rows=1 width=116) (actual time=127.942..150.728 rows=4 loops=1)
        Group Key: pay.payment_type
        Buffers: shared hit=3037, temp read=1029 written=1032
        ->  Sort  (cost=8375.96..8375.97 rows=1 width=45) (actual time=50.709..58.652 rows=100756 loops=1)
              Sort Key: pay.payment_type
              Sort Method: external merge  Disk: 5528kB
              Buffers: shared hit=3030, temp read=691 written=693
              ->  Gather  (cost=3708.73..8375.95 rows=1 width=45) (actual time=15.221..35.294 rows=100756 loops=1)
                    Workers Planned: 2
                    Workers Launched: 2
                    Buffers: shared hit=3025
                    ->  Parallel Hash Join  (cost=2708.73..7375.85 rows=1 width=45) (actual time=12.692..32.424 rows=33585 loops=3)
                          Hash Cond: ((o.order_id = pay.order_id) AND (o.order_purchase_timestamp = pay.order_purchase_timestamp))
                          Buffers: shared hit=3025
                          ->  Parallel Append  (cost=0.00..2656.41 rows=40214 width=41) (actual time=0.021..6.775 rows=32159 loops=3)
                                Buffers: shared hit=1718
                                ->  Parallel Index Scan using order_future_order_status_order_purchase_timestamp_idx on order_future o_4  (cost=0.14..8.16 rows=1 width=140) (actual time=0.022..0.022 rows=0 loops=1)
                                      Index Cond: (order_status = 'delivered'::order_status_enum)
                                      Buffers: shared hit=2
                                ->  Parallel Seq Scan on order_2018 o_3  (cost=0.00..1329.14 rows=31044 width=41) (actual time=0.010..2.775 rows=17594 loops=3)
                                      Filter: (order_status = 'delivered'::order_status_enum)
                                      Rows Removed by Filter: 409
                                      Buffers: shared hit=932
                                ->  Parallel Seq Scan on order_2017 o_2  (cost=0.00..1109.62 rows=25571 width=41) (actual time=0.008..3.712 rows=21714 loops=2)
                                      Filter: (order_status = 'delivered'::order_status_enum)
                                      Rows Removed by Filter: 836
                                      Buffers: shared hit=778
                                ->  Parallel Seq Scan on order_2016 o_1  (cost=0.00..8.42 rows=157 width=41) (actual time=0.006..0.071 rows=267 loops=1)
                                      Filter: (order_status = 'delivered'::order_status_enum)
                                      Rows Removed by Filter: 62
                                      Buffers: shared hit=6
                          ->  Parallel Hash  (cost=1792.09..1792.09 rows=61109 width=53) (actual time=12.088..12.089 rows=34629 loops=3)
                                Buckets: 131072  Batches: 1  Memory Usage: 10016kB
                                Buffers: shared hit=1181
                                ->  Parallel Seq Scan on payment pay  (cost=0.00..1792.09 rows=61109 width=53) (actual time=0.009..3.178 rows=34629 loops=3)
                                      Buffers: shared hit=1181
Planning:
  Buffers: shared hit=721
Planning Time: 1.297 ms
Execution Time: 152.311 ms
```

### Metricas

| Metrica | Valor |
|---------|-------|
| Planning Time | 1.297 ms |
| Execution Time | 152.311 ms |
| Costo total | 8,376.01 |
| Filas estimadas | 1 |
| Filas reales (GroupAgg) | 4 |
| Filas procesadas (Sort) | 100,756 |
| Buffers shared hit | 3,040 |
| Temp read/written | 691/693 bloques (~5.5MB) |
| Paralelismo | 2 workers |
| Spill a disco | Si — Sort external merge 5.5MB |

### Bottlenecks (Q6)
1. **Spill a disco**: Sort necesita external merge de 5.5MB para ordenar 100,756 filas de payment
2. **Seq Scan en payment** (103,886 filas) sin indice en payment.order_id
3. **Parallel Hash Join** entre order y payment usando Hash Cond compuesta (order_id + timestamp)
4. GroupAggregate con Group Key en payment_type (solo 4 grupos) despues de ordenar 100k filas — ineficiente

---

## Query 7: `07_product_review_analysis.sql` — Reviews de productos

### Query
```sql
SELECT p.product_id, pc.name_english AS category,
       COUNT(r.review_id) AS review_count,
       ROUND(AVG(r.review_score), 2) AS avg_score,
       SUM(oi.price) AS total_sales
FROM product p
JOIN product_category pc ON p.category_name = pc.category_name
JOIN order_item oi ON p.product_id = oi.product_id
JOIN "order" o ON oi.order_id = o.order_id AND oi.order_purchase_timestamp = o.order_purchase_timestamp
JOIN review r ON o.order_id = r.order_id AND o.order_purchase_timestamp = r.order_purchase_timestamp
WHERE o.order_status = 'delivered'
GROUP BY p.product_id, pc.name_english
HAVING COUNT(r.review_id) >= 5
ORDER BY avg_score ASC
LIMIT 20;
```

### Filas retornadas: 20

### EXPLAIN ANALYZE output
```
Limit  (cost=7374.63..7374.63 rows=1 width=122) (actual time=425.770..429.848 rows=20 loops=1)
  Buffers: shared hit=1038232, temp read=1305 written=1308
  ->  Sort  (cost=7374.63..7374.63 rows=1 width=122) (actual time=425.769..429.845 rows=20 loops=1)
        Sort Key: (round(avg(r.review_score), 2))
        Sort Method: top-N heapsort  Memory: 30kB
        Buffers: shared hit=1038232, temp read=1305 written=1308
        ->  GroupAggregate  (cost=7374.46..7374.62 rows=1 width=122) (actual time=375.016..428.858 rows=4640 loops=1)
              Group Key: p.product_id, pc.name_english
              Filter: (count(r.review_id) >= 5)
              Rows Removed by Filter: 26696
              Buffers: shared hit=1038229, temp read=1305 written=1308
              ->  Gather Merge  (cost=7374.46..7374.58 rows=1 width=91) (actual time=374.992..405.533 rows=107577 loops=1)
                    Workers Planned: 2
                    Workers Launched: 2
                    Buffers: shared hit=1038229, temp read=1305 written=1308
                    ->  Sort  (cost=6374.44..6374.45 rows=1 width=91) (actual time=370.642..374.335 rows=35859 loops=3)
                          Sort Key: p.product_id, pc.name_english
                          Sort Method: external merge  Disk: 3560kB
                          Buffers: shared hit=1038229, temp read=1305 written=1308
                          Worker 0:  Sort Method: external merge  Disk: 3352kB
                          Worker 1:  Sort Method: external merge  Disk: 3528kB
                          ->  Nested Loop  (cost=3416.18..6374.43 rows=1 width=91) (actual time=19.719..299.604 rows=35859 loops=3)
                                Buffers: shared hit=1038199
                                ->  Nested Loop  (cost=3416.03..6374.27 rows=1 width=89) (actual time=19.702..262.726 rows=36375 loops=3)
                                      Buffers: shared hit=823021
                                      ->  Nested Loop  (cost=3415.62..6373.81 rows=1 width=74) (actual time=19.674..172.462 rows=36375 loops=3)
                                            Buffers: shared hit=386515
                                            ->  Parallel Hash Join  (cost=3415.20..6373.23 rows=1 width=117) (actual time=19.638..54.408 rows=31868 loops=3)
                                                  Hash Cond: ((o.order_id = r.order_id) AND (o.order_purchase_timestamp = r.order_purchase_timestamp))
                                                  Buffers: shared hit=3812
                                                  ->  Parallel Append  (cost=0.00..2656.41 rows=40214 width=41) (actual time=0.015..11.305 rows=32159 loops=3)
                                                        Buffers: shared hit=1718
                                                        ->  Parallel Index Scan using order_future_order_status_order_purchase_timestamp_idx on order_future o_4  (cost=0.14..8.16 rows=1 width=140) (actual time=0.015..0.016 rows=0 loops=1)
                                                              Index Cond: (order_status = 'delivered'::order_status_enum)
                                                              Buffers: shared hit=2
                                                        ->  Parallel Seq Scan on order_2018 o_3  (cost=0.00..1329.14 rows=31044 width=41) (actual time=0.007..4.644 rows=17594 loops=3)
                                                              Filter: (order_status = 'delivered'::order_status_enum)
                                                              Rows Removed by Filter: 409
                                                              Buffers: shared hit=932
                                                        ->  Parallel Seq Scan on order_2017 o_2  (cost=0.00..1109.62 rows=25571 width=41) (actual time=0.008..6.871 rows=21714 loops=2)
                                                              Filter: (order_status = 'delivered'::order_status_enum)
                                                              Rows Removed by Filter: 836
                                                              Buffers: shared hit=778
                                                        ->  Parallel Seq Scan on order_2016 o_1  (cost=0.00..8.42 rows=157 width=41) (actual time=0.005..0.119 rows=267 loops=1)
                                                              Filter: (order_status = 'delivered'::order_status_enum)
                                                              Rows Removed by Filter: 62
                                                              Buffers: shared hit=6
                                                  ->  Parallel Hash  (cost=2546.88..2546.88 rows=57888 width=76) (actual time=19.088..19.089 rows=32803 loops=3)
                                                        Buckets: 131072  Batches: 1  Memory Usage: 11840kB
                                                        Buffers: shared hit=1968
                                                        ->  Parallel Seq Scan on review r  (cost=0.00..2546.88 rows=57888 width=76) (actual time=0.010..7.853 rows=32803 loops=3)
                                                              Buffers: shared hit=1968
                                            ->  Index Scan using pk_order_item on order_item oi  (cost=0.42..0.57 rows=1 width=80) (actual time=0.003..0.003 rows=1 loops=95604)
                                                  Index Cond: (order_id = o.order_id)
                                                  Filter: (o.order_purchase_timestamp = order_purchase_timestamp)
                                                  Buffers: shared hit=382703
                                      ->  Index Scan using pk_product on product p  (cost=0.41..0.46 rows=1 width=48) (actual time=0.002..0.002 rows=1 loops=109126)
                                            Index Cond: (product_id = oi.product_id)
                                            Buffers: shared hit=436506
                                ->  Index Scan using pk_product_category on product_category pc  (cost=0.14..0.16 rows=1 width=34) (actual time=0.001..0.001 rows=1 loops=109126)
                                      Index Cond: ((category_name)::text = (p.category_name)::text)
                                      Buffers: shared hit=215178
Planning:
  Buffers: shared hit=1015
Planning Time: 2.301 ms
Execution Time: 430.802 ms
```

### Metricas

| Metrica | Valor |
|---------|-------|
| Planning Time | 2.301 ms |
| Execution Time | **430.802 ms** |
| Costo total | 7,374.63 |
| Filas estimadas | 1 |
| Filas reales (Nested Loop interno) | 95,604 loops |
| Buffers shared hit | **1,038,232** |
| Temp read/written | 1,305/1,308 bloques |
| Paralelismo | 2 workers |
| Spill a disco | Si — Sort external merge ~3.5MB por worker |

### Nodos analizados en detalle

**1. Nested Loop con 3 niveles de anidamiento:**
- Nivel 3 (mas interno): Index Scan pk_order_item ejecutado **95,604 veces**
- Nivel 2: Index Scan pk_product ejecutado **109,126 veces**
- Nivel 1: Index Scan pk_product_category ejecutado **109,126 veces**
- `Buffers: shared hit=1,038,232` — MAS DE UN MILLON de buffers

**2. Parallel Hash Join (order + review):**
- 31,868 filas
- Hash table de review: 11.8MB

**3. GroupAggregate con HAVING:**
- 4,640 grupos, filtrados a 20
- 26,696 filas descartadas por HAVING (COUNT < 5)

### Bottlenecks (Q7)
1. **⚠️ Nested Loop profundo (3 niveles)**: 109k loops de Index Scan en product y product_category. Cada iteracion hace index lookups, resultando en 1M+ buffers. Causado por la cadena: order → review → order_item → product → product_category.
2. **Index Scan pk_order_item ejecutado 95k veces** con Filter adicional en timestamp (no solo Index Cond)
3. **Spill a disco**: Sort externo de ~10MB total combinado entre workers
4. **HAVING COUNT >= 5**: 26,696 filas descartadas despues de la agregacion — costoso

---

## Query 8: `08_monthly_sales_trend.sql` — Tendencia mensual

### Query
```sql
SELECT DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
       COUNT(DISTINCT o.order_id) AS total_orders,
       SUM(oi.price) AS gross_revenue,
       SUM(oi.freight_value) AS total_freight,
       ROUND(SUM(oi.price) / NULLIF(COUNT(DISTINCT o.order_id), 0), 2) AS avg_order_value
FROM "order" o
JOIN order_item oi ON o.order_id = oi.order_id AND o.order_purchase_timestamp = oi.order_purchase_timestamp
WHERE o.order_status = 'delivered'
  AND o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp <  '2019-01-01'
GROUP BY DATE_TRUNC('month', o.order_purchase_timestamp)
ORDER BY month;
```

### Filas retornadas: 20

### EXPLAIN ANALYZE output
```
GroupAggregate  (cost=9688.91..9688.95 rows=1 width=112) (actual time=63.766..158.642 rows=20 loops=1)
  Group Key: (date_trunc('month'::text, o.order_purchase_timestamp))
  Buffers: shared hit=4301, temp read=868 written=871
  ->  Sort  (cost=9688.91..9688.91 rows=1 width=53) (actual time=63.179..71.255 rows=109880 loops=1)
        Sort Key: (date_trunc('month'::text, o.order_purchase_timestamp))
        Sort Method: external merge  Disk: 6944kB
        Buffers: shared hit=4294, temp read=868 written=871
        ->  Gather  (cost=5053.62..9688.90 rows=1 width=53) (actual time=15.932..41.979 rows=109880 loops=1)
              Workers Planned: 2
              Workers Launched: 2
              Buffers: shared hit=4291
              ->  Parallel Hash Join  (cost=4053.62..8688.80 rows=1 width=53) (actual time=13.814..39.976 rows=36627 loops=3)
                    Hash Cond: ((o.order_id = oi.order_id) AND (o.order_purchase_timestamp = oi.order_purchase_timestamp))
                    Buffers: shared hit=4291
                    ->  Parallel Append  (cost=0.00..2930.79 rows=40103 width=41) (actual time=0.016..7.729 rows=32070 loops=3)
                          Buffers: shared hit=1710
                          ->  Parallel Seq Scan on order_2018 o_2  (cost=0.00..1488.00 rows=31044 width=41) (actual time=0.011..3.311 rows=17594 loops=3)
                                Filter: ((order_purchase_timestamp >= ...) AND (order_purchase_timestamp < ...) AND (order_status = 'delivered'::order_status_enum))
                                Rows Removed by Filter: 409
                                Buffers: shared hit=932
                          ->  Parallel Seq Scan on order_2017 o_1  (cost=0.00..1242.28 rows=25571 width=41) (actual time=0.011..4.269 rows=21714 loops=2)
                                Filter: ((order_purchase_timestamp >= ...) AND (order_purchase_timestamp < ...) AND (order_status = 'delivered'::order_status_enum))
                                Rows Removed by Filter: 836
                                Buffers: shared hit=778
                    ->  Parallel Hash  (cost=3059.65..3059.65 rows=66265 width=53) (actual time=13.238..13.239 rows=37550 loops=3)
                          Buckets: 131072  Batches: 1  Memory Usage: 10752kB
                          Buffers: shared hit=2397
                          ->  Parallel Seq Scan on order_item oi  (cost=0.00..3059.65 rows=66265 width=53) (actual time=0.006..4.641 rows=37550 loops=3)
                                Buffers: shared hit=2397
Planning:
  Buffers: shared hit=447
Planning Time: 1.007 ms
Execution Time: 159.936 ms
```

### Metricas

| Metrica | Valor |
|---------|-------|
| Planning Time | 1.007 ms |
| Execution Time | 159.936 ms |
| Costo total | 9,688.91 |
| Filas estimadas | 1 |
| Filas reales (Sort) | 109,880 |
| Buffers shared hit | 4,301 |
| Temp read/written | 868/871 (~7MB) |
| Paralelismo | 2 workers |
| Spill a disco | Si — Sort external merge 6.9MB |

### Bottlenecks (Q8)
1. **Spill a disco**: Sort de 109k filas por `DATE_TRUNC('month', ...)` requiere external merge de 6.9MB
2. **Parallel Seq Scan en order_2018**: solo 409 filas filtradas de 18,003 — buen filtro
3. **Parallel Hash Join** entre order y order_item: hash table de 10.7MB
4. GroupAggregate con group key funcional (DATE_TRUNC) — forzando Sort completo

---

## Query 9: `09_top_customers_by_spend.sql` — Top clientes

### Query
```sql
SELECT c.customer_unique_id, c.customer_city, c.customer_state,
       COUNT(DISTINCT o.order_id) AS total_orders,
       SUM(oi.price) AS total_spent,
       MAX(o.order_purchase_timestamp) AS last_order
FROM customer c
JOIN "order" o ON c.customer_unique_id = o.customer_id
JOIN order_item oi ON o.order_id = oi.order_id AND o.order_purchase_timestamp = oi.order_purchase_timestamp
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
ORDER BY total_spent DESC
LIMIT 20;
```

### Filas retornadas: 0 (customer JOIN mismatch)

### EXPLAIN ANALYZE output
```
Limit  (cost=9419.82..9419.82 rows=1 width=95) (actual time=234.991..236.903 rows=0 loops=1)
  Buffers: shared hit=334838
  ->  Sort  (cost=9419.82..9419.82 rows=1 width=95) (actual time=234.990..236.901 rows=0 loops=1)
        Sort Key: (sum(oi.price)) DESC
        Sort Method: quicksort  Memory: 25kB
        Buffers: shared hit=334838
        ->  GroupAggregate  (cost=9419.78..9419.81 rows=1 width=95) (actual time=234.960..236.872 rows=0 loops=1)
              Group Key: c.customer_unique_id
              Buffers: shared hit=334835
              ->  Sort  (cost=9419.78..9419.79 rows=1 width=94) (actual time=234.959..236.870 rows=0 loops=1)
                    Sort Key: c.customer_unique_id
                    Sort Method: quicksort  Memory: 25kB
                    Buffers: shared hit=334835
                    ->  Nested Loop  (cost=5054.04..9419.77 rows=1 width=94) (actual time=234.933..236.845 rows=0 loops=1)
                          Buffers: shared hit=334832
                          ->  Gather  (cost=5053.62..9419.24 rows=1 width=80) (actual time=18.427..35.330 rows=110197 loops=1)
                                Workers Planned: 2
                                Workers Launched: 2
                                Buffers: shared hit=4241
                                ->  Parallel Hash Join  (cost=4053.62..8419.14 rows=1 width=80) (actual time=15.472..38.923 rows=36732 loops=3)
                                      Hash Cond: ((o.order_id = oi.order_id) AND (o.order_purchase_timestamp = oi.order_purchase_timestamp))
                                      Buffers: shared hit=4241
                                      ->  Parallel Append  (cost=0.00..2656.41 rows=40214 width=74) (actual time=0.021..5.916 rows=32159 loops=3)
                                            Buffers: shared hit=1718
                                            ->  Parallel Index Scan using order_future_order_status_order_purchase_timestamp_idx on order_future o_4  (cost=0.14..8.16 rows=1 width=272) (actual time=0.024..0.024 rows=0 loops=1)
                                                  Index Cond: (order_status = 'delivered'::order_status_enum)
                                                  Buffers: shared hit=2
                                            ->  Parallel Seq Scan on order_2018 o_3  (cost=0.00..1329.14 rows=31044 width=74) (actual time=0.009..3.098 rows=26392 loops=2)
                                                  Filter: (order_status = 'delivered'::order_status_enum)
                                                  Rows Removed by Filter: 614
                                                  Buffers: shared hit=932
                                            ->  Parallel Seq Scan on order_2017 o_2  (cost=0.00..1109.62 rows=25571 width=74) (actual time=0.012..6.950 rows=43428 loops=1)
                                                  Filter: (order_status = 'delivered'::order_status_enum)
                                                  Rows Removed by Filter: 1673
                                                  Buffers: shared hit=778
                                            ->  Parallel Seq Scan on order_2016 o_1  (cost=0.00..8.42 rows=157 width=74) (actual time=0.006..0.026 rows=134 loops=2)
                                                  Filter: (order_status = 'delivered'::order_status_enum)
                                                  Rows Removed by Filter: 31
                                                  Buffers: shared hit=6
                                      ->  Parallel Hash  (cost=3059.65..3059.65 rows=66265 width=47) (actual time=14.718..14.718 rows=37550 loops=3)
                                            Buckets: 131072  Batches: 1  Memory Usage: 9920kB
                                            Buffers: shared hit=2397
                                            ->  Parallel Seq Scan on order_item oi  (cost=0.00..3059.65 rows=66265 width=47) (actual time=0.010..5.022 rows=37550 loops=3)
                                                  Buffers: shared hit=2397
                          ->  Index Scan using idx_customer_unique_id on customer c  (cost=0.42..0.53 rows=1 width=47) (actual time=0.002..0.002 rows=0 loops=110197)
                                Index Cond: (customer_unique_id = o.customer_id)
                                Buffers: shared hit=330591
Planning:
  Buffers: shared hit=781
Planning Time: 1.679 ms
Execution Time: 237.018 ms
```

### Metricas

| Metrica | Valor |
|---------|-------|
| Planning Time | 1.679 ms |
| Execution Time | 237.018 ms |
| Costo total | 9,419.82 |
| Filas estimadas | 1 |
| Filas reales (Gather) | 110,197 |
| Buffers shared hit | 334,838 |
| Paralelismo | 2 workers |

### Problema principal
El Index Scan `idx_customer_unique_id` se ejecuta **110,197 veces** pero siempre retorna 0 filas porque `customer_unique_id` no coincide con `order.customer_id`. Esto causa 237ms de ejecucion desperdiciados. **Con el JOIN correcto (`c.customer_id = o.customer_id`), la consulta seria mucho mas rapida y retornaria datos.**

---

## Query 10: `10_geographic_distribution.sql` — Distribucion geografica

### Query
```sql
SELECT c.customer_state,
       COUNT(DISTINCT o.order_id) AS total_orders,
       SUM(oi.price) AS total_revenue,
       ROUND(AVG(r.review_score), 2) AS avg_review,
       COUNT(DISTINCT s.seller_id) AS unique_sellers
FROM customer c
JOIN "order" o ON c.customer_unique_id = o.customer_id
JOIN order_item oi ON o.order_id = oi.order_id AND o.order_purchase_timestamp = oi.order_purchase_timestamp
LEFT JOIN review r ON o.order_id = r.order_id AND o.order_purchase_timestamp = r.order_purchase_timestamp
LEFT JOIN seller s ON oi.seller_id = s.seller_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY total_revenue DESC;
```

### Filas retornadas: 0 (customer JOIN mismatch)

### EXPLAIN ANALYZE output
```
Sort  (cost=12835.34..12835.35 rows=1 width=83) (actual time=249.202..253.061 rows=0 loops=1)
  Sort Key: (sum(oi.price)) DESC
  Sort Method: quicksort  Memory: 25kB
  Buffers: shared hit=337892
  ->  GroupAggregate  (cost=12835.30..12835.33 rows=1 width=83) (actual time=249.180..253.039 rows=0 loops=1)
        Group Key: c.customer_state
        Buffers: shared hit=337889
        ->  Sort  (cost=12835.30..12835.30 rows=1 width=77) (actual time=249.179..253.037 rows=0 loops=1)
              Sort Key: c.customer_state
              Sort Method: quicksort  Memory: 25kB
              Buffers: shared hit=337889
              ->  Nested Loop Left Join  (cost=8469.52..12835.29 rows=1 width=77) (actual time=249.164..253.022 rows=0 loops=1)
                    Buffers: shared hit=337886
                    ->  Nested Loop  (cost=8469.24..12834.99 rows=1 width=77) (actual time=249.164..253.021 rows=0 loops=1)
                          Buffers: shared hit=337886
                          ->  Gather  (cost=8468.82..12834.46 rows=1 width=107) (actual time=38.657..60.291 rows=110559 loops=1)
                                Workers Planned: 2
                                Workers Launched: 2
                                Buffers: shared hit=6209
                                ->  Parallel Hash Left Join  (cost=7468.82..11834.36 rows=1 width=107) (actual time=36.125..77.021 rows=36853 loops=3)
                                      Hash Cond: ((o.order_id = r.order_id) AND (o.order_purchase_timestamp = r.order_purchase_timestamp))
                                      Buffers: shared hit=6209
                                      ->  Parallel Hash Join  (cost=4053.62..8419.14 rows=1 width=113) (actual time=20.510..45.285 rows=36732 loops=3)
                                            Hash Cond: ((o.order_id = oi.order_id) AND (o.order_purchase_timestamp = oi.order_purchase_timestamp))
                                            Buffers: shared hit=4115
                                            ->  Parallel Append  (cost=0.00..2656.41 rows=40214 width=74) (actual time=0.018..6.573 rows=32159 loops=3)
                                                  Buffers: shared hit=1718
                                                  ->  Parallel Index Scan using order_future_order_status_order_purchase_timestamp_idx on order_future o_4  (cost=0.14..8.16 rows=1 width=272) (actual time=0.018..0.019 rows=0 loops=1)
                                                        Index Cond: (order_status = 'delivered'::order_status_enum)
                                                        Buffers: shared hit=2
                                                  ->  Parallel Seq Scan on order_2018 o_3  (cost=0.00..1329.14 rows=31044 width=74) (actual time=0.009..3.623 rows=26392 loops=2)
                                                        Filter: (order_status = 'delivered'::order_status_enum)
                                                        Rows Removed by Filter: 614
                                                        Buffers: shared hit=932
                                                  ->  Parallel Seq Scan on order_2017 o_2  (cost=0.00..1109.62 rows=25571 width=74) (actual time=0.010..7.948 rows=43428 loops=1)
                                                        Filter: (order_status = 'delivered'::order_status_enum)
                                                        Rows Removed by Filter: 1673
                                                        Buffers: shared hit=778
                                                  ->  Parallel Seq Scan on order_2016 o_1  (cost=0.00..8.42 rows=157 width=74) (actual time=0.006..0.024 rows=134 loops=2)
                                                        Filter: (order_status = 'delivered'::order_status_enum)
                                                        Rows Removed by Filter: 31
                                                        Buffers: shared hit=6
                                            ->  Parallel Hash  (cost=3059.65..3059.65 rows=66265 width=80) (actual time=19.783..19.783 rows=37550 loops=3)
                                                  Buckets: 131072  Batches: 1  Memory Usage: 14304kB
                                                  Buffers: shared hit=2397
                                                  ->  Parallel Seq Scan on order_item oi  (cost=0.00..3059.65 rows=66265 width=80) (actual time=0.009..5.558 rows=37550 loops=3)
                                                        Buffers: shared hit=2397
                                      ->  Parallel Hash  (cost=2546.88..2546.88 rows=57888 width=43) (actual time=15.011..15.012 rows=32803 loops=3)
                                            Buckets: 131072  Batches: 1  Memory Usage: 8768kB
                                            Buffers: shared hit=1968
                                            ->  Parallel Seq Scan on review r  (cost=0.00..2546.88 rows=57888 width=43) (actual time=0.008..6.919 rows=32803 loops=3)
                                                  Buffers: shared hit=1968
                          ->  Index Scan using idx_customer_unique_id on customer c  (cost=0.42..0.53 rows=1 width=36) (actual time=0.002..0.002 rows=0 loops=110559)
                                Index Cond: (customer_unique_id = o.customer_id)
                                Buffers: shared hit=331677
                    ->  Index Only Scan using pk_seller on seller s  (cost=0.28..0.30 rows=1 width=33) (never executed)
                          Index Cond: (seller_id = oi.seller_id)
                          Heap Fetches: 0
Planning:
  Buffers: shared hit=875
Planning Time: 2.365 ms
Execution Time: 253.196 ms
```

### Metricas

| Metrica | Valor |
|---------|-------|
| Planning Time | 2.365 ms |
| Execution Time | 253.196 ms |
| Costo total | 12,835.34 |
| Filas estimadas | 1 |
| Filas reales (Gather) | 110,559 |
| Buffers shared hit | 337,892 |
| Paralelismo | 2 workers |

### Problema principal
Mismo problema que Q9: Index Scan en `customer` ejecutado 110,559 veces con 0 filas. El LEFT JOIN a `seller` nunca se ejecuta (never executed) porque ya no hay filas en ese punto. La consulta es conceptualmente la mas compleja (5 JOINs con LEFT JOINs y agregacion por estado).

---

## Tabla comparativa cruzada — TODAS LAS 10 CONSULTAS

| # | Query | Planning (ms) | Execution (ms) | Costo total | Filas reales | Buffers hit | Paralelismo | Spill | Nodo mas costoso |
|---|-------|:------------:|:--------------:|:-----------:|:------------:|:-----------:|:-----------:|:-----:|:----------------|
| 1 | order_detail | 2.137 | **0.292** | 76.59 | 0* | 28 | No | No | Append (order partitions) 33.34 |
| 2 | sales_by_category | 1.467 | **82.277** | 14,665.55 | 68 | 6,119 | Si (1) | No | Parallel Hash Join 8,790 |
| 3 | seller_performance | 1.785 | **13,090.123** | 12,937.16 | 20 | 1,825,500 | Si (2) | **Si** | Nested Loop (168M filtradas) |
| 4 | customer_order_history | 1.787 | **0.206** | 67.66 | 1 | 22 | No | No | Append (order partitions) 33.34 |
| 5 | late_deliveries | 1.461 | **35.522** | 8,292.41 | 50 | 30,388 | Si (2) | No | Parallel Hash Join 7,292 |
| 6 | payment_method_analysis | 1.297 | **152.311** | 8,376.01 | 4 | 3,040 | Si (2) | **Si** | External Sort 5.5MB |
| 7 | product_review_analysis | 2.301 | **430.802** | 7,374.63 | 20 | **1,038,232** | Si (2) | **Si** | Nested Loop (3 niveles) |
| 8 | monthly_sales_trend | 1.007 | **159.936** | 9,688.91 | 20 | 4,301 | Si (2) | **Si** | External Sort 6.9MB |
| 9 | top_customers_by_spend | 1.679 | **237.018** | 9,419.82 | 0* | 334,838 | Si (2) | No | Index Scan customer (110k loops) |
| 10 | geographic_distribution | 2.365 | **253.196** | 12,835.34 | 0* | **337,892** | Si (2) | No | Index Scan customer (110k loops) |

*Q1, Q9, Q10 retornan 0 filas por error en JOIN condition (`customer_unique_id` vs `customer_id`).

### Resumen de metricas agregadas

| Metrica | Total |
|---------|-------|
| Tiempo de ejecucion combinado | ~14.44 segundos |
| Buffers totales | ~3.9 millones |
| Queries con paralelismo | 7 de 10 |
| Queries con spill a disco | 3 de 10 |
| Seq Scans en tablas grandes | 8 ocurrencias |

---

## Top 5 BOTTLENECKS priorizados

### 1. ⚠️ CRITICO: Nested Loop con Join Filter en Q3 (seller_performance) — 13s
**Problema:** La consulta Q3 usa un Nested Loop con `oi.seller_id = s.seller_id` como Join Filter (no Hash Cond), causando que `seller` (3,095 filas) se ejecute 110,559 veces. **168 millones de filas** son evaluadas y descartadas.
**Impacto:** 13 segundos de ejecucion, 1.8M de buffers.
**Solución:** Crear indice en `order_item.seller_id` y forzar Hash Join; o reescribir la consulta usando CTE materializado.

### 2. ⚠️ ALTO: Seq Scans en tablas grandes (Q2, Q3, Q5, Q6, Q7, Q8)
**Problema:** Las tablas `order_2017`, `order_2018`, `order_item`, `review`, `payment` se escanean secuencialmente en 6 de 10 consultas, filtrando por `order_status = 'delivered'` y rangos de fecha.
**Impacto:** Cientos de miles de filas leidas innecesariamente.
**Solución:** Indices compuestos:
   - `order(order_status, order_purchase_timestamp)` — cubre filtros en Q2, Q3, Q5, Q6, Q7, Q8
   - `order_item(order_id)` — permite Index Nested Loop en lugar de Hash Join
   - `review(order_id)` — permite Index Scan en LEFT JOINs
   - `payment(order_id)` — permite Index Scan en lugar de Seq Scan

### 3. ⚠️ ALTO: Spills a disco en Q3, Q6, Q7, Q8
**Problema:** 4 de 10 consultas hacen spill a disco (external sort), usando entre 3.5MB y 11.5MB.
**Impacto:** Degradacion de rendimiento por I/O de disco.
**Solución:** Aumentar `work_mem` de 4MB a 16-32MB; optimizar GROUP BY con indices cubrientes.

### 4. ⚠️ MEDIO: Partition pruning inefectivo (Q1, Q4)
**Problema:** Aunque `order` esta particionada por rango de fecha, las busquedas por `order_id` (Q1) y `customer_id` (Q4) revisan las 4 particiones secuencialmente.
**Impacto:** 3-4 index scans innecesarios por consulta.
**Solución:** Incluir condicion de particion en WHERE, o usar particionamiento HASH por order_id.

### 5. ⚠️ MEDIO: Estimacion de filas erronea del planner
**Problema:** El planner estima consistentemente 1 fila para Q3, Q5, Q6, Q7, Q8, Q9, Q10 cuando la realidad es de miles a cientos de miles.
**Impacto:** El planner elige planes suboptimos (Nested Loop en lugar de Hash Join).
**Solución:** Actualizar estadisticas con `ANALYZE`; aumentar `default_statistics_target`.

### Problema adicional: Calidad de datos en JOIN customer
Q1, Q9, Q10 usan `customer_unique_id` para JOIN con `order.customer_id`, pero la columna correcta es `customer.customer_id`. Esto causa 0 filas en 3 consultas y 490ms de ejecucion desperdiciada. **Corregir JOIN condition es prioritario antes de optimizar estas consultas.**

---

## Archivos modificados
- `progress/impl_feature2.md` — Este reporte completo (ALL 10 queries).
- `src/Ecommify_Database_Design/notebooks/U4_Etapa1_Investigacion.ipynb` — Seccion 1.1 actualizada con EXPLAIN ANALYZE outputs, análisis de nodos, tabla comparativa y bottlenecks.
- `scripts/_temp_explain.py` — Script temporal para ejecutar EXPLAIN ANALYZE (eliminar despues).
- `scripts/_investigate.py` — Script temporal de investigacion de datos (eliminar despues).
- `scripts/_investigate2.py` — Script temporal de investigacion de datos (eliminar despues).
- `scripts/_run_all_explain.py` — Script principal de EXPLAIN ANALYZE (eliminar despues).
