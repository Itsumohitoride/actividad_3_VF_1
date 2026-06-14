# Feature 2 — Fix heading structure in U4_Etapa1_Investigacion.ipynb

**Status:** done
**Date:** 2026-06-06

## Changes applied

### Change 1 — Split combined EXPLAIN heading
- Replaced cell with `## 1.1 Análisis de planes de ejecución con EXPLAIN y ANALYZE`
- Two new cells inserted:
  - `### Análisis con EXPLAIN` — instruction on running EXPLAIN for estimated plan
  - `### Análisis con EXPLAIN ANALYZE` — instruction + metrics list + "Consultas analizadas" reference

### Change 2 — Add "Documentar hallazgos" heading
- Inserted `### Documentar hallazgos` before `### Tabla comparativa de métricas — TODAS LAS 10 CONSULTAS`
- Positions between Q10 analysis cell and metrics table heading

### Change 3 — Subtitles under 1.2 Indexación
- `### Análisis de aplicabilidad` before "Consultar índices existentes" code cell
- `### Diseño de estrategia de indexación` before "Matriz: tipo de consulta >> tipo de índice" cell

### Change 4 — Subtitles under 1.3 Particionamiento
- `### Análisis de candidatos` before "Identificar tablas con mas registros" code
- `### Diseño de estrategia` before "Análisis de tabla candidata" markdown
- `### Planificación de mantenimiento` before "Estrategia de creacion automatica" markdown

## Verification
- All 4 changes applied correctly (7 cells added: 64→71)
- No code cells modified
- `python scripts/check_harness.py` — all green
- Side fix: `verify_features.py` encoding changed from `utf-8` to `utf-8-sig` to handle BOM in feature_list.json
