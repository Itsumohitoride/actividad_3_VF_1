# Feature 14: sharding_replica_design — Reporte de implementación

## Archivo creado

- **`docs/sharding_replica_design.md`** — Documento de diseño completo de sharding y replica sets para la colección `event_logs`

## Resumen de contenido

| Sección | Descripción |
|---------|-------------|
| **1. Shard Key Design** | Shard key `{event_type: "hashed", timestamp: 1}` con justificación por patrones de consulta, análisis de cardinalidad, alternativas rechazadas y estrategia de chunking |
| **2. Data Distribution Simulation** | Tabla de distribución de 10M documentos en 3 shards (us-east-1, us-west-2, eu-west-1) con tabla por tipo de evento y explicación de enrutamiento targeted vs broadcast |
| **3. Replica Set Configuration** | 3 nodos por shard con prioridades, tags, ubicaciones y propósito; estrategia de elección, failover y reincorporación |
| **4. Read/Write Concern Strategy** | Matriz por operación (checkout, carrito, búsqueda, reportes, logs) con árbol de decisión e impacto en rendimiento |
| **5. Topology Diagram (ASCII)** | Diagrama completo del cluster: clientes → mongos → shards (cada uno con primary + 2 secondaries) → config servers; flujo de consulta targeted |
| **6. Write/Read Concern Matrix** | Matriz detallada con writeConcern, wtimeout, journal, readConcern, readPreference, maxStalenessSeconds para 9 operaciones |

## Formato

- Markdown con tablas, diagrama ASCII, árbol de decisión y referencias
- Escrito en español
- Sigue marco Diátaxis (Referencia + Explicación)
- Práctico y accionable: incluye configuraciones concretas (`rs.initiate`, comandos de sharding)
