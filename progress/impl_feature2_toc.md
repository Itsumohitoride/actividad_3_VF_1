# Feature 2 — TOC + numbering: implementation findings

## Summary

Added Table of Contents and renumbered headings in `U4_Etapa1_Investigacion.ipynb`.

## Changes made

### Part 1 — Table of Contents inserted
- Inserted new markdown cell at index 1 with `## Tabla de Contenido` and links to all 3 sections + subsections
- Position: after title cell (cell 0), before code cells

### Part 2 — Heading renumbering

| Cell | Old text | New text |
|------|----------|----------|
| 5 | `### Análisis con EXPLAIN` | `## 1. Análisis de planes de ejecución con EXPLAIN y ANALYZE` |
| 6 | *(new)* | `### 1.1 Análisis con EXPLAIN` |
| 7 | `### Análisis con EXPLAIN ANALYZE` | `### 1.2 Análisis con EXPLAIN ANALYZE` |
| 48 | `### Documentar hallazgos` | `### 1.3 Documentar hallazgos` |
| 52 | `## 1.2 Estrategias de indexacion especializada` | `## 2. Estrategias de indexación especializada` |
| 54 | `### Análisis de aplicabilidad` | `### 2.1 Análisis de aplicabilidad` |
| 57 | `### Diseño de estrategia de indexación` | `### 2.2 Diseño de estrategia de indexación` |
| 61 | `## 1.3 Tecnicas de particionamiento declarativo` | `## 3. Técnicas de particionamiento declarativo` |
| 62 | `### Análisis de candidatos` | `### 3.1 Análisis de candidatos` |
| 64 | `### Diseño de estrategia` | `### 3.2 Diseño de estrategia` |
| 69 | `### Planificación de mantenimiento` | `### 3.3 Planificación de mantenimiento` |

### Edge cases encountered
- Cells 52 and 61 have `---` (horizontal rule) as first line before heading — had to search all source lines, not just `source[0]`
- Title and `## Configuracion inicial` are in the same cell (cell 0) — TOC inserted at index 1, not between them
- No code cells modified
- No `#### Consulta N:` heading cells touched

## Verification
- Total cells: 73 (was 71, +1 TOC +1 `### 1.1` subsection)
- `python scripts/check_harness.py` — all green
- All heading changes confirmed by reading back notebook
