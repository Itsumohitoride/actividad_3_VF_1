# Review — Feature 14: sharding_replica_design

**Veredicto:** CHANGES_REQUESTED

## Checkpoints

### C1 — El arnés está completo
- [ ] No aplica (archivo de documentación, no código)

### C2 — El estado es coherente
- [x] Feature 14 en in_progress, única feature activa
- [x] No hay features 	esting con transiciones inconsistentes
- [x] progress/current.md refleja estado actual

### C3 — El código respeta la arquitectura
- [x] Documentación en docs/ como especifica docs/architecture.md
- [x] No hay código modificado
- [x] No hay dependencias externas no declaradas

### C4 — La verificación es real
- [x] python scripts/check_harness.py termina OK (49 tests, todos verdes)
- [x] Feature 14 es documentación teórica; no requiere tests unitarios

### C5–C7 — No evaluados (sesión activa, aún no se cierra)

## Evaluación por criterio de aceptación

### ✅ 1. Shard key definida y justificada basada en patrones de query
Sección 1 completa:
- Shard key {event_type: "hashed", timestamp: 1} definida en 1.2
- Tabla de patrones de consulta en 1.3 (find, sort, aggregate)
- Cardinalidad analizada en 1.4 (9 valores enum, hot spot mitigado con hash)
- 4 alternativas consideradas con razones de rechazo en 1.5

### ✅ 2. Simulación de distribución de datos across shards (hash/range)
Sección 2 completa:
- Topología 3 shards multi-región en 2.1
- Distribución 10M docs ~33% cada shard en 2.2
- Desglose por tipo de evento en 2.3 (9 tipos, 400K–4M docs c/u)
- Enrutamiento targeted vs broadcast en 2.4

### ✅ 3. Configuración de replica set documentada (3 nodos, prioridad, tags)
Sección 3 completa:
- 3 nodos: Primary (priority 10, readwrite), Secondary 1 (priority 5, analytics), Secondary 2 (priority 3, reporting)
- Failover diagrama y estrategia en 3.2 y 3.3
- Código s.initiate() con tags concretos en 3.4

### ❌ 4. Estrategias Read Concern diferenciadas (local, majority, linearizable)
**Problema:** La matriz cubre local y majority, pero **no menciona ni diferencia linearizable read concern** en ninguna parte del documento. El criterio exige explícitamente cubrir estos 3 niveles. Incluso si la decisión es no usar linearizable, debe documentarse por qué y en qué caso aplicaría.

Afecta: Sección 4 (tabla 4.1) y Sección 6 (matriz completa). Todas las operaciones usan local o majority. Ninguna celda menciona linearizable.

**Corrección requerida:** Añadir en Sección 4 una entrada o nota sobre eadConcern: "linearizable", explicando su costo (espera a majority + escritura en primary) y cuándo sería apropiado (ej. operaciones financieras que requieren linearizability completo). Alternativamente, añadir una fila en la matriz 6.0 con readConcern linearizable para una operación de alta criticidad, o una nota "No recomendado para este caso de uso por latencia multi-región".

### ✅ 5. Estrategias Write Concern diferenciadas (acknowledged, majority, journaled)
Cubierto:
- w: 1 = acknowledged (carrito, sesiones)
- w: majority = majority (checkout, pagos)
- w: 0 = unacknowledged (logs)
- journal: true = journaled (checkout, pagos)
- Matriz 6.0 incluye columna journal explícita

### ✅ 6. Diagrama de topología incluido en documentación
Sección 5: diagrama ASCII completo con clientes, mongos, 3 shards (cada uno con primary + 2 secondaries etiquetados por región y propósito), config servers, y flujo de consulta targeted.

### ✅ 7. Documentación en docs/sharding_replica_design.md
Archivo existe en la ruta correcta. 329 líneas. Formato Markdown. Estructura Diátaxis (Referencia + Explicación).

## Cambios requeridos

1. **Añadir linearizable read concern** — Incluir en Sección 4.1 o 6 una fila/nota que diferencie eadConcern: "linearizable". Sugerencia: añadir una operación hipotética (ej. "confirmacion_pago_critica") que use linearizable, o una nota técnica explicando por qué no se recomienda para este cluster multi-región (latencia WAN, overhead de espera).
2. **Actualizar CHECKPOINTS.md** (opcional pero recomendado) para reflejar que C3 y C4 aplican parcialmente a features de documentación pura.
3. **Sin cambios en código** — No hay código modificado, no se requieren tests.
4. **Harness ya verde** — No requiere cambios.
