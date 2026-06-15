# Review — Feature 3 (Etapa 1.2: Análisis de estrategias de indexación)

**Veredicto:** CHANGES_REQUESTED

## Resumen de verificación

- **Notebook:** U4_Etapa1_Investigacion.ipynb — Cells 52-60 (9 cells)
- **check_harness.py:** ✅ Pasa (verde, exit code 0)
- **JSON notebook:** ✅ Válido
- **Análisis técnico:** ✅ Sólido, detallado, referencias correctas a datos de Feature 2

## Checkpoints (CHECKPOINTS.md)

- C1: [x] — check_harness.py pasa (con python, no python3 pero funcionalmente ok)
- C2: [ ] — Feature 3 sigue in_progress en feature_list.json, sin transición a testing; current.md muestra Feature 4 activa (inconsistencia)
- C3: [x] — Código respeta arquitectura (notebooks/), sin dependencias no declaradas
- C4: [ ] — tests/ no existe; no aplica tests unitarios (proyecto notebook)
- C5: [x] — Sin archivos temporales sospechosos
- C6: [ ] — Sin entrada de costo para Feature 3
- C7: [x] — docs/deployment.md y configuration.md existen y tienen contenido

## Evaluación contra acceptance criteria

### 1. Análisis de pg_stat_user_indexes ❌
**Esperado:** Consultar pg_stat_user_indexes para medir uso de índices (idx_scan, idx_tup_read, idx_tup_fetch).

**Real:** Cell 55 consulta pg_indexes (definiciones), NO pg_stat_user_indexes. El análisis de uso se deriva de EXPLAIN ANALYZE de Feature 2, no de las estadísticas del sistema.

**Evidencia:** Line 1273-1282 del notebook:
`sql
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
`

**Falta:** La métrica idx_scan no se consulta en ningún lado. La búsqueda global de pg_stat_user_indexes devuelve 0 resultados en todo src/.

### 2. Identificación de ≥3 columnas candidatas ✅
7 columnas candidatas identificadas y priorizadas (3 críticas, 2 alta, 2 media). Correcto.

### 3. Análisis de seq_scans vs index_scans ❌
**Esperado:** Consultar pg_stat_user_tables columnas seq_scan/idx_scan.

**Real:** Cell 56 (line 1304) consulta 
_live_tup y pg_total_relation_size de pg_stat_user_tables. NO consulta seq_scan ni idx_scan.

**Falta:** No se usa pg_stat_user_tables para estadísticas de escaneo. El análisis de seq_scans vs index_scans está presente en markdown pero basado en EXPLAIN, no en pg_stat_user_tables.

### 4. Recomendaciones de ≥2 tipos de índice ✅
4 tipos recomendados: B-tree simple (3), B-tree compuesto (3), B-tree parcial (1), más mantenimiento de GIN/GiST existentes. Justificación detallada por tipo.

### 5. EXPLAIN antes/después ✅ (parcial)
Análisis detallado de before/after para Q3, Q7, Q2 en progress/impl_feature3.md (reporte externo).

**Nota:** El notebook (cells 52-60) solo contiene tablas con "Impacto esperado" estimado, no simulaciones EXPLAIN completas. El reporte independiente sí las tiene.

## Checklist de revisión

- [x] Markdown cells properly formatted — Correcto, tablas bien estructuradas
- [x] No broken JSON — OK, archivo JSON válido
- [x] Code cells valid Python — OK
- [ ] Analysis grounded in actual Feature 2 data — Sí, pero datos son de EXPLAIN no de pg_stat_*
- [x] All 10 queries referenced correctly — Matriz completa en cell 58
- [x] Index recommendations justified by observed query patterns — Detallado y justificado
- [x] Technical accuracy of index types and operators — Correcto
- [x] Spanish language quality — Bueno, tecnicismos en inglés correctos

## Cambios requeridos

1. **Cell 55 — Añadir consulta a pg_stat_user_indexes**: Agregar analysis de idx_scan, idx_tup_read, idx_tup_fetch para cada índice existente. Esto mide cuáles índices se usan realmente vs cuáles son sobrecarga muerta.

   `sql
   SELECT schemaname, tablename, indexrelname AS index_name,
          idx_scan, idx_tup_read, idx_tup_fetch
   FROM pg_stat_user_indexes
   WHERE schemaname = 'public'
   ORDER BY idx_scan DESC;
   `

2. **Cell 56 — Añadir columnas seq_scan e idx_scan**: Modificar la consulta existente para incluir seq_scan e idx_scan de pg_stat_user_tables.

3. **Feature 3 status**: Marcar Feature 3 como 	esting en eature_list.json y añadir transición. Si el review se aprueba, mover a done.

4. **Consistencia current.md**: Feature 3 no debe quedar como activa en current.md si Feature 4 ya se inició.

## Notas adicionales

- El análisis de indexación es cualitativamente correcto y exhaustivo. Las columnas candidatas, tipos de índice y justificaciones son técnicamente sólidas.
- Los cambios requeridos son principalmente formales (uso de las vistas del sistema especificadas en acceptance criteria) más que de contenido.
- Una vez añadidas las consultas a pg_stat_user_indexes y pg_stat_user_tables (seq_scan/idx_scan), el feature estaría completo para testing.
