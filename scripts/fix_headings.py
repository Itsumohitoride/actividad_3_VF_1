"""Fix heading hierarchy in U4_Etapa1_Investigacion.ipynb.

Searches for heading text across ALL lines of source arrays (not just first line).
"""
import json
import copy

NB_PATH = "src/Ecommify_Database_Design/notebooks/U4_Etapa1_Investigacion.ipynb"

with open(NB_PATH, "r", encoding="utf-8") as f:
    nb = json.load(f)

cells = nb["cells"]
changes_log = []

def find_cell_by_heading(heading_text):
    """Find cell index and line index where heading_text appears in source array."""
    for i, cell in enumerate(cells):
        if cell["cell_type"] != "markdown" or not cell["source"]:
            continue
        for j, line in enumerate(cell["source"]):
            stripped = line.rstrip("\n").rstrip()
            if stripped == heading_text:
                return i, j
    return None, None

def replace_heading_in_cell(cell_idx, line_idx, new_text):
    """Replace the heading at given line in cell source."""
    cell = cells[cell_idx]
    new_source = list(cell["source"])
    new_source[line_idx] = new_text + "\n"
    cells[cell_idx] = copy.deepcopy(cell)
    cells[cell_idx]["source"] = new_source

# ============================================================
# Change 12: Update Table of Contents cell
# ============================================================
toc_new_source = [
    "## Tabla de Contenido\n",
    "\n",
    "1. [Análisis de planes de ejecución con EXPLAIN y ANALYZE](#1-analisis-de-planes-de-ejecucion-con-explain-y-analyze)\n",
    "   - [1.1 Análisis con EXPLAIN](#11-analisis-con-explain)\n",
    "   - [1.2 Análisis con EXPLAIN ANALYZE](#12-analisis-con-explain-analyze)\n",
    "   - [1.3 Documentar hallazgos](#13-documentar-hallazgos)\n",
    "2. [Estrategias de indexación especializada](#2-estrategias-de-indexacion-especializada)\n",
    "   - [2.1 Análisis de aplicabilidad](#21-analisis-de-aplicabilidad)\n",
    "   - [2.2 Diseño de estrategia de indexación](#22-diseno-de-estrategia-de-indexacion)\n",
    "3. [Técnicas de particionamiento declarativo](#3-tecnicas-de-particionamiento-declarativo)\n",
    "   - [3.1 Análisis de candidatos](#31-analisis-de-candidatos)\n",
    "   - [3.2 Diseño de estrategia](#32-diseno-de-estrategia)\n",
    "   - [3.3 Planificación de mantenimiento](#33-planificacion-de-mantenimiento)\n",
]
toc_found = False
for i, cell in enumerate(cells):
    if cell["cell_type"] == "markdown" and cell["source"]:
        first = cell["source"][0].strip()
        if first.startswith("## Tabla de Contenido"):
            cells[i] = copy.deepcopy(cell)
            cells[i]["source"] = toc_new_source
            changes_log.append("Change 12: Updated TOC cell at index %d" % i)
            toc_found = True
            break
if not toc_found:
    changes_log.append("WARNING: TOC cell not found!")

# ============================================================
# Change 1: Insert new parent cell before "## 1. Análisis con EXPLAIN"
# ============================================================
new_parent_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 1. Análisis de planes de ejecución con EXPLAIN y ANALYZE\n"
    ]
}

insert_idx, _ = find_cell_by_heading("## 1. Análisis con EXPLAIN")
if insert_idx is not None:
    cells.insert(insert_idx, new_parent_cell)
    changes_log.append("Change 1: Inserted new parent cell at index %d" % insert_idx)
else:
    changes_log.append("WARNING: Could not find '## 1. Análisis con EXPLAIN' for insertion!")

# ============================================================
# Changes 2-11: Replace heading texts (search all lines)
# ============================================================
heading_replacements = [
    ("## 1. Análisis con EXPLAIN",               "### 1.1 Análisis con EXPLAIN",                 "Change 2"),
    ("## 2. Análisis con EXPLAIN ANALYZE",        "### 1.2 Análisis con EXPLAIN ANALYZE",          "Change 3"),
    ("## 3. Documentar hallazgos",                "### 1.3 Documentar hallazgos",                  "Change 4"),
    ("## 4. Estrategias de indexación especializada", "## 2. Estrategias de indexación especializada", "Change 5"),
    ("### 4.1 Análisis de aplicabilidad",          "### 2.1 Análisis de aplicabilidad",             "Change 6"),
    ("### 4.2 Diseño de estrategia de indexación", "### 2.2 Diseño de estrategia de indexación",    "Change 7"),
    ("## 5. Técnicas de particionamiento declarativo", "## 3. Técnicas de particionamiento declarativo", "Change 8"),
    ("### 5.1 Análisis de candidatos",             "### 3.1 Análisis de candidatos",               "Change 9"),
    ("### 5.2 Diseño de estrategia",              "### 3.2 Diseño de estrategia",                  "Change 10"),
    ("### 5.3 Planificación de mantenimiento",    "### 3.3 Planificación de mantenimiento",         "Change 11"),
]

for search_heading, replace_heading, change_label in heading_replacements:
    cell_idx, line_idx = find_cell_by_heading(search_heading)
    if cell_idx is not None:
        replace_heading_in_cell(cell_idx, line_idx, replace_heading)
        changes_log.append("%s: Changed cell %d line %d '%s' -> '%s'" % (
            change_label, cell_idx, line_idx, search_heading, replace_heading))
    else:
        changes_log.append("WARNING: '%s' not found for %s!" % (search_heading, change_label))

# ============================================================
# Write back
# ============================================================
nb["cells"] = cells
with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("=== Changes applied ===")
for log in changes_log:
    print(log)
print("\nTotal cells after edit: %d" % len(cells))
