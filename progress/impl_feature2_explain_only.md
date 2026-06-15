# Feature 2 — Etapa 1.1: Análisis con EXPLAIN (solo planes estimados)

**Fecha:** 2026-06-06
**Fuente:** `progress/impl_feature2.md` — datos extraídos de EXPLAIN (ANALYZE, BUFFERS, TIMING) sobre 10 consultas

---

## Part A — Introducción a los planes EXPLAIN

`EXPLAIN` muestra el plan de ejecución estimado que el planner de PostgreSQL generaría para una consulta, **sin ejecutarla realmente**. El plan incluye:

- **Tipo de nodo**: Seq Scan, Index Scan, Hash Join, Nested Loop, etc.
- **Costo estimado de startup**: costo antes de empezar a retornar la primera fila.
- **Costo total estimado**: costo acumulado hasta retornar toda la salida.
- **Filas estimadas**: cardinalidad que el planner predice para cada nodo.
- **Ancho (width)**: estimación del tamaño promedio de fila en bytes.

Los costos están expresados en **unidades arbitrarias** basadas en la configuración de `seq_page_cost` (por defecto 1.0) y `cpu_tuple_cost` (por defecto 0.01). No son milisegundos, sino una medida relativa que el optimizer usa para comparar planes alternativos.

A diferencia de `EXPLAIN ANALYZE`, los planes con solo `EXPLAIN` **no ejecutan la consulta**, por lo que no incluyen tiempos reales ni estadísticas de buffers. Son útiles para inspección rápida sin impacto en la base de datos.

---

## Part B — Tabla resumen de estimaciones EXPLAIN

| # | Query | Scan type(s) | JOIN method(s) | Est. startup cost | Est. total cost | Est. rows | Most costly node |
|---|---|---|---|---|---|---|---|
| 1 | Order detail | Index Scan (7) | Nested Loop (5 niveles) | 2.08 | 76.59 | 4 | Append (33.34) |
| 2 | Sales by category | Parallel Seq Scan (4) | Parallel Hash Join + Hash Join | 11,924.85 | 14,665.55 | 71 | GroupAggregate (14,663) |
| 3 | Seller performance | Seq Scan + Parallel Seq Scan | Nested Loop + Parallel Hash + Hash | 8,468.82 | 12,937.16 | 1 | Nested Loop (12,937) |
| 4 | Customer history | Index Scan (4 via Append) | Nested Loop | 1.11 | 67.66 | 1 | Append (33.34) |
| 5 | Late deliveries | Parallel Seq Scan + Index Scan | Parallel Hash Join + Nested Loop | 5,053.90 | 8,292.41 | 1 | Parallel Hash Join (7,292) |
| 6 | Payment analysis | Parallel Seq Scan (2) | Parallel Hash Join | 3,708.73 | 8,376.01 | 1 | Sort (8,376) |
| 7 | Product review | Index Scan (3) + Parallel Seq Scan | Nested Loop (3 niveles) + Parallel Hash | 3,416.18 | 7,374.63 | 1 | Nested Loop (6,374) |
| 8 | Monthly trend | Parallel Seq Scan | Parallel Hash Join | 5,053.62 | 9,688.91 | 1 | Sort (9,689) |
| 9 | Top customers | Index Scan + Parallel Seq Scan | Nested Loop + Parallel Hash Join | 5,054.04 | 9,419.82 | 1 | Nested Loop (9,419) |
| 10 | Geographic dist. | Index Scan + Parallel Seq Scan (3) | Nested Loop + Parallel Hash + Hash Left Join | 8,469.52 | 12,835.34 | 1 | Nested Loop (12,835) |

**Observaciones:**
- 8 de 10 consultas tienen estimación de 1 fila (subestimación grave del planner)
- Q1 (order detail) es la única con estimación precisa (4 filas estimadas vs 0 reales por error de JOIN)
- Q2 (sales by category) tiene la estimación más alta (71 filas) y el mayor costo total (14,665)
- Las consultas Q1 y Q4 tienen los costos más bajos (<100) por ser búsquedas puntuales con índice
- Q3, Q7, Q9, Q10 tienen los costos más altos (>7,000) por procesar grandes volúmenes con Nested Loops

---

## Part C — Interpretación de tipos de Scan

Los siguientes tipos de escaneo se identificaron en los planes de las 10 consultas:

### Seq Scan (Full Table Scan)
- **Qué es**: Lee todas las páginas de la tabla secuencialmente.
- **Cuándo se usa**: Cuando no hay índice disponible, o el planner estima que se leerá un porcentaje alto de filas (>5-10%).
- **Dónde aparece**: En order_2017, order_2018, order_item, review, payment, product, product_category.
- **Impacto**: Es el escaneo más costoso para tablas grandes. En Q2, `order_2017` descarta 13,910 filas (62%) después de aplicar filtros. En Q3, `order_2018` escanea 52,783 filas para filtrar por `order_status = 'delivered'`.

### Index Scan (B-tree)
- **Qué es**: Navega por un índice B-tree para localizar filas específicas, luego accede al heap.
- **Cuándo se usa**: Consultas selectivas con condiciones de igualdad o rango en columnas indexadas.
- **Dónde aparece**: En tablas con PK/FK (order_item, product, product_category, payment) y en índices secundarios (customer_id_idx en particiones de order).
- **Impacto**: Muy eficiente para consultas puntuales (Q1: 0.292ms, Q4: 0.206ms). Sin embargo, cuando se ejecuta decenas de miles de veces dentro de un Nested Loop (Q7: 95,604 loops, Q9: 110,197 loops), el acumulado de buffers es masivo.

### Index Only Scan
- **Qué es**: Similar a Index Scan, pero todas las columnas necesarias están en el índice mismo. No requiere acceso al heap.
- **Cuándo se usa**: Cuando el índice cubre todas las columnas referenciadas.
- **Dónde aparece**: En `customer` en Q1 (idx_customer_unique_id) y en `seller` en Q10 (pk_seller).
- **Impacto**: Más eficiente que Index Scan porque evita lecturas del heap.

### Parallel Seq Scan
- **Qué es**: Un Seq Scan distribuido entre múltiples workers paralelos.
- **Cuándo se usa**: Tablas grandes cuando `parallel_tuple_cost` y `parallel_setup_cost` lo justifican.
- **Dónde aparece**: En order_2017, order_2018, order_item, review, payment — la mayoría de consultas con paralelismo activan 1-2 workers.
- **Impacto**: Reduce el tiempo de ejecución al dividir el trabajo, pero sigue siendo un escaneo completo de la tabla.

### Append
- **Qué es**: Combina resultados de múltiples particiones o subconsultas.
- **Cuándo se usa**: Tablas particionadas — cada partición se escanea y los resultados se concatenan.
- **Dónde aparece**: En todas las consultas que acceden a `order` (particionado por fecha en 4 sub-tablas).
- **Impacto**: Ineficiente cuando el partition pruning no filtra particiones. Q1 y Q4 escanean las 4 particiones aunque solo 1 tenga datos relevantes.

---

## Part D — Interpretación de métodos de JOIN

### Nested Loop
- **Cómo funciona**: Para cada fila del conjunto externo, escanea el conjunto interno en busca de coincidencias.
- **Cuándo es eficiente**: Cuando el conjunto externo es pequeño y el interno tiene un índice (Index Nested Loop).
- **Dónde aparece**: Q1 (5 niveles), Q3 (con Join Filter catastrófico), Q4, Q7 (3 niveles), Q9, Q10.
- **Problemas identificados**:
  - **Q3**: El Nested Loop con Join Filter `oi.seller_id = s.seller_id` (en vez de Hash Cond) causa que el lado externo (110,559 filas) se combine con el interno (3,095 filas de seller), resultando en **168 millones de evaluaciones** descartadas.
  - **Q7**: 3 niveles de anidamiento generan >1 millón de buffers compartidos.
  - **Q9-Q10**: Nested Loop con 0 filas reales por JOIN condition incorrecta.

### Hash Join
- **Cómo funciona**: Construye una tabla hash en memoria para el conjunto interno, luego recorre el externo y hace probing.
- **Cuándo es eficiente**: Tablas grandes sin orden previo, especialmente cuando una cabe en memoria (`work_mem`).
- **Dónde aparece**: Q2 (múltiples Hash Joins), Q3-Q10.
- **Uso de memoria observado**:
  - Q2: Hash table de order_item: 13MB + review: 8MB + product: 3MB = ~24MB combinados
  - Q7: Hash table de review: 11.8MB
  - Q5, Q9, Q10: Hash table de order_item: 14.3MB + review: 8.7MB

### Parallel Hash Join
- **Cómo funciona**: Hash Join distribuido entre workers paralelos.
- **Cuándo se usa**: Tablas grandes donde el costo de construir la hash table se amortiza entre workers.
- **Dónde aparece**: Q2, Q3, Q5, Q6, Q7, Q8, Q9, Q10 — la mayoría de consultas analizadas.
- **Impacto**: Acelera significativamente las operaciones (7 de 10 consultas usan paralelismo), pero las hash tables grandes (8-14MB) pueden causar contención de memoria.

### Hash Left Join
- **Cómo funciona**: Variante de Hash Join que preserva todas las filas del lado izquierdo.
- **Dónde aparece**: Q3 (LEFT JOIN con review), Q10 (LEFT JOIN con review y seller).
- **Impacto**: Similar a Hash Join pero puede requerir más memoria para rastrear filas no coincidentes.

### Resumen de métodos JOIN por consulta:
- **Solo Nested Loop**: Q1, Q4
- **Solo Hash Join / Parallel Hash Join**: Q2, Q6, Q8
- **Combinación Nested Loop + Hash Join**: Q3, Q5, Q7, Q9, Q10

---

## Part E — Operaciones costosas identificadas

### 1. ⚠️ Q3 (seller_performance): Costo total 12,937 — Nested Loop catastrófico
- **Nodo más costoso**: Nested Loop (12,937)
- **Problema**: El planner eligió Nested Loop con Join Filter en vez de Hash Join. La estimación de 1 fila (vs 110,559 reales) hizo que el planner subestimara el costo.
- **Impacto real**: 168 millones de filas descartadas, 13 segundos de ejecución, 1.8M de buffers.
- **Lección**: Una subestimación de cardinalidad puede llevar a elegir el plan equivocado, con impacto desproporcionado.

### 2. ⚠️ Q10 (geographic_distribution): Costo total 12,835 — Complejidad de 5 JOINs
- **Nodo más costoso**: Nested Loop (12,835)
- **Problema**: 5 JOINs (incluyendo 2 LEFT JOINs) con agregación por estado. El Nested Loop con Index Scan en `customer` ejecutado 110,559 veces.
- **Agravante**: JOIN condition incorrecta (`customer_unique_id = customer_id`) hace que todo el trabajo sea en vano — 0 filas retornadas.
- **Hash tables**: Parallel Hash Join con order_item (14.3MB) + Parallel Hash Left Join con review (8.7MB).

### 3. ⚠️ Q2 (sales_by_category): Costo total 14,665 — El más alto del conjunto
- **Nodo más costoso**: GroupAggregate (14,663) sobre 68 categorías.
- **Problema**: Seq Scans masivos en order_2017 (22,550 filas escaneadas, 62% descartadas), order_item (56,325 filas) y review (49,205 filas).
- **Hash tables**: 3 hash tables simultáneas sumando ~24MB de memoria.
- **Paralelismo**: 1 worker — el menor nivel de paralelismo entre las queries con workers.

### 4. Costos por Sequential Scans
Los Seq Scans (incluyendo Parallel Seq Scan) son los principales contribuyentes al costo en las consultas 2, 3, 5, 6, 7, 8, 9, y 10:
- **order_2017/2018**: Sin índice compuesto en `(order_status, order_purchase_timestamp)`, cada consulta escanea secuencialmente entre 8,000 y 52,000 filas.
- **order_item**: 56,325 filas escaneadas en cada consulta que JOINea con esta tabla.
- **review**: 49,205 filas escaneadas en 6 consultas para LEFT JOIN.
- **payment**: 103,886 filas escaneadas en Q6 sin índice en `order_id`.

### 5. Hash Tables grandes y presión de memoria
- Q2: 3 hash tables paralelas = ~24MB (work_mem por defecto: 4MB)
- Q3: Hash table order_item 14.3MB + review 8.7MB = ~23MB
- Q5: Hash table order_item 14.3MB
- Q7: Hash table review 11.8MB
- Con `work_mem` en 4MB por defecto, estas hash tables fuerzan el uso de batches múltiples (spill a disco), aunque en este caso todas caben en 1 batch porque la memoria disponible (paralelismo mediante) es mayor.

### Resumen de costos totales estimados (orden descendente):
| # | Query | Costo total | Diferencia vs Q1 (más barata) |
|---|-------|:-----------:|:-----------------------------:|
| 2 | Sales by category | 14,665.55 | **191×** más caro |
| 3 | Seller performance | 12,937.16 | **169×** más caro |
| 10 | Geographic distribution | 12,835.34 | **168×** más caro |
| 9 | Top customers | 9,419.82 | **123×** más caro |
| 8 | Monthly trend | 9,688.91 | **126×** más caro |
| 6 | Payment analysis | 8,376.01 | **109×** más caro |
| 5 | Late deliveries | 8,292.41 | **108×** más caro |
| 7 | Product review | 7,374.63 | **96×** más caro |
| 1 | Order detail | 76.59 | — (base) |
| 4 | Customer history | 67.66 | — (base) |

---

## Part F — Per-query EXPLAIN highlights (top 3 críticas)

### Q3: Seller Performance — Nested Loop catastrófico

```text
Nested Loop  (cost=8468.82..12937.10 rows=1 width=94)
  Join Filter: (oi.seller_id = s.seller_id)
  Rows Removed by Join Filter: 168084820
  ->  Gather  (cost=8468.82..12834.46 rows=1 width=80)
        Workers Planned: 2
        Workers Launched: 2
        ->  Parallel Hash Left Join  (cost=7468.82..11834.36 rows=1 width=80)
              Hash Cond: ((o.order_id = r.order_id) AND (...))
              ->  Parallel Hash Join  (cost=4053.62..8419.14 rows=1 width=119)
                    Hash Cond: ((o.order_id = oi.order_id) AND (...))
                    ->  Parallel Append  (cost=0.00..2656.41 rows=40214 width=41)
                    ->  Parallel Hash  (cost=3059.65..3059.65 rows=66265)
              ->  Parallel Hash  (cost=2546.88..2546.88 rows=57888)
  ->  Seq Scan on seller s  (cost=0.00..63.95 rows=3095 width=47)
        (ejecutado 110,559 veces — 1,819,285 buffers)
```

**Análisis:**
- El Nested Loop externo tiene un **Join Filter** en vez de una condición de igualdad indexada.
- `seller` se escanea secuencialmente **110,559 veces** (una por cada fila del resultado de la subconsulta).
- 168 millones de filas se evalúan y descartan en el Join Filter.
- El planner estimó **1 fila** — la realidad fue **110,559 filas**. Esta subestimación de 5 órdenes de magnitud causó que el planner eligiera Nested Loop en vez de Hash Join.
- **Solución estructural**: Crear índice en `order_item.seller_id` y forzar Hash Join, o reescribir la consulta.

### Q7: Product Review Analysis — 3 niveles de Nested Loop

```text
Nested Loop  (cost=3416.18..6374.43 rows=1 width=91)          ← Nivel 1
  ->  Nested Loop  (cost=3416.03..6374.27 rows=1 width=89)    ← Nivel 2
        ->  Nested Loop  (cost=3415.62..6373.81 rows=1 width=74)  ← Nivel 3
              ->  Parallel Hash Join  (cost=3415.20..6373.23 rows=1 width=117)
                    Hash Cond: ((o.order_id = r.order_id) AND (...))
                    ->  Parallel Append  (cost=0.00..2656.41 rows=40214)
                    ->  Parallel Hash  (cost=2546.88..2546.88 rows=57888)
              ->  Index Scan using pk_order_item on order_item oi
                    (cost=0.42..0.57 rows=1)
                    (95,604 loops — 382,703 buffers)
        ->  Index Scan using pk_product on product p
              (cost=0.41..0.46 rows=1)
              (109,126 loops — 436,506 buffers)
  ->  Index Scan using pk_product_category on product_category pc
        (cost=0.14..0.16 rows=1)
        (109,126 loops — 215,178 buffers)
```

**Análisis:**
- **3 niveles de anidamiento**: La cadena de JOINs order → review → order_item → product → product_category genera un árbol de ejecución profundamente anidado.
- **95,604 iteraciones** en el nivel 3 (Index Scan en order_item) y **109,126** en los niveles 2 y 1.
- **Más de 1 millón de buffers** compartidos (1,038,232).
- Cada nivel agrega un Index Scan que se ejecuta tantas veces como filas produce el nivel inferior, multiplicando el trabajo.
- **Lección**: Aunque cada Index Scan individual es barato (costo ~0.42-0.57), ejecutarlo 100,000 veces convierte una operación trivial en un cuello de botella de 430ms.
- El plan usa 2 workers paralelos, pero el Nested Loop se ejecuta en cada worker, triplicando el impacto de buffers.

### Q10: Geographic Distribution — Complejidad de 5 JOINs

```text
Sort  (cost=12835.34..12835.35 rows=1 width=83)
  ->  GroupAggregate  (cost=12835.30..12835.33 rows=1 width=83)
        ->  Sort  (cost=12835.30..12835.30 rows=1 width=77)
              ->  Nested Loop Left Join  (cost=8469.52..12835.29 rows=1 width=77)   ← LEFT JOIN seller
                    ->  Nested Loop  (cost=8469.24..12834.99 rows=1 width=77)
                          ->  Gather  (cost=8468.82..12834.46 rows=1 width=107)
                                Workers Planned: 2
                                ->  Parallel Hash Left Join  (cost=7468.82..11834.36 rows=1 width=107)  ← LEFT JOIN review
                                      ->  Parallel Hash Join  (cost=4053.62..8419.14 rows=1 width=113)  ← JOIN order_item
                                            ->  Parallel Append  (cost=0.00..2656.41 rows=40214)
                                                  (4 particiones de order)
                                            ->  Parallel Hash  (cost=3059.65..3059.65 rows=66265)
                                                  ->  Parallel Seq Scan on order_item
                                      ->  Parallel Hash  (cost=2546.88..2546.88 rows=57888)
                                            ->  Parallel Seq Scan on review
                          ->  Index Scan using idx_customer_unique_id on customer c
                                (cost=0.42..0.53 rows=1)
                                (110,559 loops — 331,677 buffers)
                                Index Cond: (customer_unique_id = o.customer_id)
                    ->  Index Only Scan using pk_seller on seller s  (never executed)
                          Index Cond: (seller_id = oi.seller_id)
```

**Análisis:**
- **5 JOINs**: 1) customer → order, 2) order → order_item, 3) order → review (LEFT), 4) order_item → seller (LEFT), más el Append entre particiones de order.
- **Estructura jerárquica**: Parallel Hash Join base (order + order_item) → Parallel Hash Left Join (+ review) → Nested Loop externo con customer (110,559 iteraciones) → Nested Loop Left Join con seller.
- El Index Scan en `customer` se ejecuta **110,559 veces** pero siempre retorna 0 filas por la condición incorrecta `customer_unique_id = o.customer_id`.
- El LEFT JOIN a `seller` aparece como **"never executed"** — el planner lo incluye en el plan pero nunca llega a ejecutarlo porque el Nested Loop anterior ya produjo 0 filas.
- **Costo real desperdiciado**: 253ms de ejecución para retornar 0 filas, 337,892 buffers.
- **Impacto del error de JOIN**: Una sola columna incorrecta invalida completamente el análisis de esta consulta, que es la más compleja del conjunto.

---

## Resumen de hallazgos

1. **El Nested Loop es el método más riesgoso**: Cuando el planner subestima la cardinalidad (8 de 10 consultas estiman 1 fila), elegir Nested Loop sobre Hash Join puede multiplicar el costo por órdenes de magnitud (Q3: 168M filas descartadas).

2. **Seq Scans dominan el costo en consultas analíticas**: Las tablas `order_2017`, `order_2018`, `order_item`, `review` y `payment` carecen de índices compuestos para los filtros más frecuentes (`order_status`, `order_purchase_timestamp`).

3. **Parallelismo ayuda pero no es suficiente**: 7 de 10 consultas usan workers paralelos, pero los cuellos de botella de Nested Loop y Seq Scan persisten.

4. **Hash tables grandes (8-14MB) son comunes**: Con `work_mem` default de 4MB, múltiples consultas están al borde del spill a disco.

5. **Partition pruning inefectivo en búsquedas puntuales**: Q1 y Q4 revisan las 4 particiones aunque solo 1 contiene datos relevantes.

6. **Error de JOIN condition en 3 consultas**: Q1, Q9, Q10 usan `customer_unique_id` en vez de `customer_id`, resultado en 0 filas y ~490ms de ejecución desperdiciada.
