# Diseño de Sharding y Replica Sets para Ecommify — Colección event_logs

> **Tipo:** Referencia + Explicación (Diátaxis)  
> **Audiencia:** Arquitectos de datos, administradores de MongoDB, equipo de plataforma  
> **Propósito:** Documentar el diseño de escalabilidad horizontal y alta disponibilidad para la colección analítica de alto volumen event_logs  
> **Alcance:** Shard key design, distribución de datos, configuración de replica sets, estrategia de read/write concern, topología del cluster

---

## 1. Diseño de Shard Key

### 1.1 Colección objetivo

| Propiedad | Valor |
|-----------|-------|
| Colección | `event_logs` |
| Volumen estimado | 10M documentos / mes |
| Crecimiento | ~330k documentos/día |
| TTL | 90 días (índice TTL sobre `ttl_expire`) |
| Patrón de acceso principal | Consultas por tipo de evento + rango temporal |

### 1.2 Shard Key propuesta

```
shard_key = { event_type: "hashed", timestamp: 1 }
```

**Estructura:**

| Componente | Tipo | Función |
|-----------|------|---------|
| `event_type` (hashed) | `hashed` | Distribuye escrituras uniformemente entre shards. El hash evita hot spots en tipos populares como `product_view`. |
| `timestamp` | `1` (ascendente) | Permite range queries eficientes dentro de cada shard para análisis temporales. |

### 1.3 Justificación por patrones de consulta

| Patrón de consulta | Cómo lo sirve la shard key |
|-------------------|---------------------------|
| `find({event_type: "product_view", timestamp: {$gte: ISODate(...)}})` | El hash dirige al shard correcto por event_type; timestamp en orden ascendente permite range scan local. |
| `find({event_type: "checkout_start"}).sort({timestamp: -1})` | Misma lógica: filtro por event_type va al shard, sort por timestamp es local. |
| `aggregate([{$match: {event_type: ...}}, {$group: {timestamp bucket}}])` | Pipeline entero ejecuta en un solo shard (targeted query), sin scatter-gather. |

### 1.4 Cardinalidad y distribución del hash

El dominio de `event_type` tiene **9 valores** en un enum cerrado:

```
product_view, product_click, search, cart_add, cart_remove,
cart_abandon, checkout_start, category_view, seller_view
```

**Problema:** Con sharding ranged por `event_type`, los tipos populares (`product_view`) crearían un hot shard.  
**Solución:** `hashed` sobre `event_type` distribuye los 9 valores + sus ocurrencias a través de los chunks del cluster. El hash de MongoDB divide el espacio en 2^64 intervalos y asigna chunks de forma uniforme.

### 1.5 Alternativas consideradas

| Alternativa | Razón de rechazo |
|------------|-----------------|
| Ranged sharding por `timestamp` | Write skew: todas las escrituras nuevas caen en el mismo rango temporal, creando un hot shard (último chunk). |
| Ranged sharding por `event_type` | Hot spots: `product_view` representa ~40% de los eventos; su chunk recibiría tráfico desbalanceado. |
| Shard key solo `event_type` (hashed) | Distribuye escrituras pero no permite range queries locales por timestamp; toda consulta temporal haría broadcast. |
| Shard key compuesta `{event_type: 1, timestamp: 1}` sin hash | Sigue sufriendo hot spots en tipos populares; el timestamp solo diversifica dentro del tipo, no entre shards. |

### 1.6 Estrategia de chunking

- Tamaño de chunk recomendado: **64 MB** (default de MongoDB)
- Número inicial de chunks: **12** (4 chunks por shard × 3 shards)
- `shardCollection` con `numInitialChunks: 12` para evitar migraciones tempranas

---

## 2. Simulación de Distribución de Datos

### 2.1 Topología del cluster

| Shard | Región | Proveedor | Propósito |
|-------|--------|-----------|-----------|
| Shard A | us-east-1 | AWS N. Virginia | Tráfico principal Norteamérica |
| Shard B | us-west-2 | AWS Oregón | Tráfico Oeste USA + failover |
| Shard C | eu-west-1 | AWS Irlanda | Tráfico Europa |

### 2.2 Distribución de 10M documentos

Con hashed sharding sobre `event_type`, la distribución es estadísticamente uniforme:

```
Shard A (us-east-1)  →  ~3,300,000 docs  (33%)
Shard B (us-west-2)  →  ~3,300,000 docs  (33%)
Shard C (eu-west-1)  →  ~3,400,000 docs  (34%)
```

### 2.3 Distribución por tipo de evento (simulada)

| event_type | Total | Shard A | Shard B | Shard C |
|-----------|-------|---------|---------|---------|
| product_view | 4,000,000 | ~1,320,000 | ~1,320,000 | ~1,360,000 |
| product_click | 1,500,000 | ~495,000 | ~495,000 | ~510,000 |
| search | 1,200,000 | ~396,000 | ~396,000 | ~408,000 |
| cart_add | 900,000 | ~297,000 | ~297,000 | ~306,000 |
| cart_remove | 600,000 | ~198,000 | ~198,000 | ~204,000 |
| cart_abandon | 500,000 | ~165,000 | ~165,000 | ~170,000 |
| checkout_start | 400,000 | ~132,000 | ~132,000 | ~136,000 |
| category_view | 500,000 | ~165,000 | ~165,000 | ~170,000 |
| seller_view | 400,000 | ~132,000 | ~132,000 | ~136,000 |

### 2.4 Enrutamiento de consultas

| Tipo de consulta | Enrutamiento | Explicación |
|-----------------|-------------|-------------|
| `find({event_type: "product_view", timestamp: ...})` | **Targeted** → 1 shard | mongos calcula el hash de `product_view` y dirige al shard correspondiente. |
| `find({session_id: "sess_abc"})` | **Broadcast** → todos los shards | No incluye event_type; mongos debe consultar los 3 shards (scatter-gather). |
| `aggregate([{$match: {event_type: ...}}, {$sort: {timestamp: -1}}])` | **Targeted** → 1 shard | El $match por event_type permite enrutamiento preciso. |
| `aggregate([{$group: {_id: "$event_type"}}])` | **Broadcast** → merge en mongos | Pipeline sin shard key obliga a merge en el router (o allowDiskUse). |

**Nota:** Las consultas sin filtro por `event_type` hacen scatter-gather. Para mitigar, crear índices secundarios locales en cada shard y confiar en el parallel query execution de mongos.

---

## 3. Configuración de Replica Sets

Cada shard es un **replica set de 3 nodos** con la misma topología multi-región para asegurar alta disponibilidad y aislamiento de cargas de trabajo.

### 3.1 Nodos por replica set

| Nodo | Prioridad | Tags | Ubicación | Propósito |
|------|-----------|------|-----------|-----------|
| **Primary** | 10 | `purpose:readwrite` | us-east-1 | Recibe todas las escrituras. Sirve lecturas consistentes (checkout, escritura inmediata). |
| **Secondary 1** | 5 | `purpose:analytics` | us-west-2 | Sirve consultas analíticas pesadas (reportes agregados). No afecta rendimiento del primary. |
| **Secondary 2** | 3 | `purpose:reporting` | eu-west-1 | Sirve dashboards y reportes programados. Aislado del tráfico transaccional. |

### 3.2 Estrategia de elección y failover

| Aspecto | Configuración |
|---------|--------------|
| **Priority primary** | Miembro con priority más alta (10). Si cae, el secondary con priority 5 en us-west-2 asume. |
| **Failover target** | Secondary 1 (priority 5) es el candidato natural. Secondary 2 (priority 3) solo si ambos caen. |
| **Election timeout** | 10 segundos (default). Ajustable a 15s para entornos multi-región con latencia WAN. |
| **Voting** | Los 3 nodos votan. Sin arbiters (3 nodos impares evita empates). |
| **Rollback** | Si el primary reconecta después de una elección, MongoDB hace rollback de escrituras no replicadas. |

### 3.3 Diagrama de failover

```
Estado normal:
  Shard A Primary (us-east-1) ← replica → Secondary 1 (us-west-2)
                                      ← replica → Secondary 2 (eu-west-1)

Failover (cae us-east-1):
  Shard A Secondary 1 (us-west-2) → se convierte en Primary (priority 5)
  Shard A Secondary 2 (eu-west-1) → replica del nuevo primary
  
Reincorporación:
  Cuando us-east-1 vuelve, se reincorpora como Secondary hasta que su
  priority 10 lo devuelva a Primary (elección automática).
```

### 3.4 Configuración de tags y read preferences

```javascript
// Ejemplo de configuración de tags para un replica set
rs.initiate({
  _id: "shardA",
  members: [
    { _id: 0, host: "shardA-primary:27018", priority: 10, tags: { purpose: "readwrite", location: "us-east-1" } },
    { _id: 1, host: "shardA-secondary1:27018", priority: 5, tags: { purpose: "analytics", location: "us-west-2" } },
    { _id: 2, host: "shardA-secondary2:27018", priority: 3, tags: { purpose: "reporting", location: "eu-west-1" } },
  ]
})
```

---

## 4. Estrategia de Read/Write Concern

### 4.1 Matriz por operación

| Operación | Write Concern | Read Concern | readPreference | Justificación |
|-----------|--------------|-------------|----------------|---------------|
| **Checkout** | `w: majority` | `majority` | `primary` | Consistencia fuerte: el cliente debe ver su orden confirmada. Pérdida de datos = pérdida de ingresos. |
| **Carrito** | `w: 1` | `local` | `primary` | Balance: el carrito puede tolerar lecturas eventuales. w:1 es más rápido que majority. |
| **Búsqueda de productos** | — | `local` | `secondaryPreferred` | Rendimiento: los resultados de búsqueda no necesican ser líder. secondaryPreferred descarga al primary. |
| **Reportes analíticos** | — | `local` | `secondary` | Aislamiento: reportes pesados se ejecutan en secondary con tag `purpose:reporting`. No afectan tráfico transaccional. |
| **Log de eventos** | `w: 0` | — | `primary` | Máximo rendimiento: los logs no requieren confirmación de escritura. w:0 (fire-and-forget). |

### 4.2 Árbol de decisión

```
¿La operación requiere consistencia inmediata?
  ├── Sí → Write Concern: majority, Read Concern: majority, readPreference: primary
  │      └── Ej: Checkout, pagos
  ├── No → ¿Es una operación de escritura?
  │      ├── Sí → ¿Es crítica?
  │      │     ├── Sí → w: majority
  │      │     │      └── Ej: actualización de carrito con stock
  │      │     └── No → w: 1
  │      │            └── Ej: carrito, sesiones
  │      └── No → ¿Es una consulta analítica?
  │           ├── Sí → readPreference: secondary (tag: reporting)
  │           └── No → readPreference: secondaryPreferred
  │                  └── Ej: búsqueda de productos, catálogo
```

### 4.3 Impacto en rendimiento

| Operación | Write Concern | Latencia de escritura estimada | Riesgo de consistencia |
|-----------|--------------|-------------------------------|----------------------|
| Checkout | `w: majority` | ~50-100 ms (2 confirmaciones cruzando regiones) | Cero — escritura confirmada por mayoría |
| Carrito | `w: 1` | ~5-15 ms (solo primary) | Mínimo — si primary falla antes de replicar, se pierde esa operación |
| Log eventos | `w: 0` | ~1-5 ms (sin espera) | Alto — se pueden perder logs si primary falla inmediatamente |

---

## 5. Diagrama de Topología (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENTES                                    │
│  (aplicación web, workers, jobs programados, dashboards)                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │        mongos (routers)        │
                    │  (1 o más instancias)          │
                    │  - Enruta queries por shard    │
                    │  - Merge de resultados         │
                    └───────────────────────────────┘
                    │               │               │
        ┌───────────┘               │               └───────────┐
        ▼                           ▼                           ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│   Shard A         │   │   Shard B         │   │   Shard C         │
│   us-east-1       │   │   us-west-2       │   │   eu-west-1       │
│                   │   │                   │   │                   │
│  ┌─────────────┐  │   │  ┌─────────────┐  │   │  ┌─────────────┐  │
│  │ Primary      │  │   │  │ Primary      │  │   │  │ Primary      │  │
│  │ priority: 10 │  │   │  │ priority: 10 │  │   │  │ priority: 10 │  │
│  │ purpose:     │  │   │  │ purpose:     │  │   │  │ purpose:     │  │
│  │ readwrite    │  │   │  │ readwrite    │  │   │  │ readwrite    │  │
│  └──────┬───────┘  │   │  └──────┬───────┘  │   │  └──────┬───────┘  │
│         │          │   │         │          │   │         │          │
│         ▼          │   │         ▼          │   │         ▼          │
│  ┌─────────────┐  │   │  ┌─────────────┐  │   │  ┌─────────────┐  │
│  │ Secondary 1  │  │   │  │ Secondary 1  │  │   │  │ Secondary 1  │  │
│  │ priority: 5  │  │   │  │ priority: 5  │  │   │  │ priority: 5  │  │
│  │ purpose:     │  │   │  │ purpose:     │  │   │  │ purpose:     │  │
│  │ analytics    │  │   │  │ analytics    │  │   │  │ analytics    │  │
│  │ us-west-2    │  │   │  │ eu-west-1    │  │   │  │ us-east-1    │  │
│  └─────────────┘  │   │  └─────────────┘  │   │  └─────────────┘  │
│         │          │   │         │          │   │         │          │
│         ▼          │   │         ▼          │   │         ▼          │
│  ┌─────────────┐  │   │  ┌─────────────┐  │   │  ┌─────────────┐  │
│  │ Secondary 2  │  │   │  │ Secondary 2  │  │   │  │ Secondary 2  │  │
│  │ priority: 3  │  │   │  │ priority: 3  │  │   │  │ priority: 3  │  │
│  │ purpose:     │  │   │  │ purpose:     │  │   │  │ purpose:     │  │
│  │ reporting    │  │   │  │ reporting    │  │   │  │ reporting    │  │
│  │ eu-west-1    │  │   │  │ us-east-1    │  │   │  │ us-west-2    │  │
│  └─────────────┘  │   │  └─────────────┘  │   │  └─────────────┘  │
└───────────────────┘   └───────────────────┘   └───────────────────┘
           │                       │                       │
           └───────────┬───────────┴───────────┬───────────┘
                       ▼                       ▼
        ┌─────────────────────────────────────────────┐
        │          Config Servers (replica set)        │
        │  3 nodos: cs1, cs2, cs3                     │
        │  Almacenan metadatos del cluster:           │
        │  - qué datos están en cada shard            │
        │  - configuración de chunks                  │
        │  - balanceo y migraciones                   │
        └─────────────────────────────────────────────┘
```

### 5.1 Flujo de una consulta targeted

```
1. Cliente → mongos: db.event_logs.find({event_type: "product_view", timestamp: ...})
2. mongos:
   a. Calcula hash("product_view") → determina rango de chunk
   b. Consulta Config Servers → ¿qué shard tiene ese chunk?
   c. Resuelve: Shard B
3. mongos → Shard B: ejecuta find secundario en el secondary con tag analytics
4. Shard B Secondary 1: IXSCAN sobre idx_esr_type_time_session
5. Shard B → mongos: cursor con resultados
6. mongos → Cliente: stream de documentos
```

---

## 6. Matriz Completa de Write/Read Concern

| Operación | writeConcern | wtimeout | journal | readConcern | readPreference | maxStalenessSeconds | Consistencia |
|-----------|-------------|----------|---------|-------------|----------------|---------------------|--------------|
| Checkout | `majority` | 5000ms | `true` | `majority` | `primary` | — | Fuerte (linealizable) |
| Confirmación pago | `majority` | 5000ms | `true` | `majority` | `primary` | — | Fuerte (linealizable) |
| Agregar al carrito | `1` | — | `false` | `local` | `primary` | — | Eventual |
| Eliminar del carrito | `1` | — | `false` | `local` | `primary` | — | Eventual |
| Búsqueda de productos | — | — | — | `local` | `secondaryPreferred` | 90s | Eventual |
| Ver catálogo | — | — | — | `local` | `secondaryPreferred` | 90s | Eventual |
| Dashboard reportes | — | — | — | `local` | `secondary` (tag: reporting) | 120s | Eventual (aislado) |
| Analytics batch | — | — | — | `local` | `secondary` (tag: analytics) | 120s | Eventual (aislado) |
| Log de eventos | `0` | — | `false` | — | `primary` | — | Sin garantía |
| Sesiones de usuario | `1` | — | `false` | `local` | `primary` | — | Eventual |

### 6.1 Notas sobre la matriz

- **w:majority con journal:true** asegura que la escritura sobrevive incluso a una caída del proceso mongod.
- **w:0** (fire-and-forget) no espera confirmación. Usar solo para datos prescindibles (logs).
- **maxStalenessSeconds** en lecturas secondary evita que un secondary muy atrasado sirva datos obsoletos. 90s es el default sensato; 120s para cargas analíticas pesadas.
- **readConcern "local"** devuelve los datos más recientes en ese nodo, sin garantía de replicación. Es el default y el de menor latencia.
- **readConcern "majority"** devuelve datos confirmados por la mayoría del replica set. Requiere habilitar el cache de majority en el replica set.

---

## Referencias

| Recurso | Enlace |
|---------|--------|
| MongoDB Sharding Documentation | https://www.mongodb.com/docs/manual/sharding/ |
| MongoDB Hashed Sharding | https://www.mongodb.com/docs/manual/core/hashed-sharding/ |
| MongoDB Replica Sets | https://www.mongodb.com/docs/manual/replication/ |
| MongoDB Read/Write Concern | https://www.mongodb.com/docs/manual/reference/read-concern/ |
| Ecommify event_logs Schema | `mongodb/schema/event_logs_schema.json` |
| Notebook de optimización | `notebooks/U5_Etapa1_MongoDB_Optimizacion.ipynb` (Sección 3) |

---

> **Documento mantenido por:** Equipo de plataforma Ecommify  
> **Última actualización:** 2026-06-13  
> **Próxima revisión sugerida:** Post-implementación del sharding en producción

