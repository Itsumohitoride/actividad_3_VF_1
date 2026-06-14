# Feature: Revert heading numbering to hierarchical structure

**File:** `src/Ecommify_Database_Design/notebooks/U4_Etapa1_Investigacion.ipynb`

**Status:** done — all 12 changes applied and verified

## Changes applied

| # | Description | Status |
|---|---|---|
| 1 | Inserted new parent cell `## 1. Análisis de planes de ejecución con EXPLAIN y ANALYZE` before `## 1. Análisis con EXPLAIN` | ✅ |
| 2 | `## 1. Análisis con EXPLAIN` → `### 1.1 Análisis con EXPLAIN` | ✅ |
| 3 | `## 2. Análisis con EXPLAIN ANALYZE` → `### 1.2 Análisis con EXPLAIN ANALYZE` | ✅ |
| 4 | `## 3. Documentar hallazgos` → `### 1.3 Documentar hallazgos` | ✅ |
| 5 | `## 4. Estrategias de indexación especializada` → `## 2. Estrategias de indexación especializada` | ✅ |
| 6 | `### 4.1 Análisis de aplicabilidad` → `### 2.1 Análisis de aplicabilidad` | ✅ |
| 7 | `### 4.2 Diseño de estrategia de indexación` → `### 2.2 Diseño de estrategia de indexación` | ✅ |
| 8 | `## 5. Técnicas de particionamiento declarativo` → `## 3. Técnicas de particionamiento declarativo` | ✅ |
| 9 | `### 5.1 Análisis de candidatos` → `### 3.1 Análisis de candidatos` | ✅ |
| 10 | `### 5.2 Diseño de estrategia` → `### 3.2 Diseño de estrategia` | ✅ |
| 11 | `### 5.3 Planificación de mantenimiento` → `### 3.3 Planificación de mantenimiento` | ✅ |
| 12 | Updated Table of Contents with new hierarchical entries | ✅ |

## Resulting hierarchy

```
## 1. Análisis de planes de ejecución con EXPLAIN y ANALYZE
  ### 1.1 Análisis con EXPLAIN
  ### 1.2 Análisis con EXPLAIN ANALYZE
  ### 1.3 Documentar hallazgos
## 2. Estrategias de indexación especializada
  ### 2.1 Análisis de aplicabilidad
  ### 2.2 Diseño de estrategia de indexación
## 3. Técnicas de particionamiento declarativo
  ### 3.1 Análisis de candidatos
  ### 3.2 Diseño de estrategia
  ### 3.3 Planificación de mantenimiento
```

## Verification

- All `#### Consulta N:` headings untouched ✅
- All code cells untouched (validated JSON structure) ✅
- Notebook JSON is valid (nbformat 4, 73 cells) ✅

## Edge cases handled

- `## 4. Estrategias...` and `## 5. Técnicas...` headings were on line **2** of their source arrays (after `---\n`), not line 1. Script searches all lines.
- UTF-8 encoding preserved for accented characters (í, ó, ñ, etc.).
