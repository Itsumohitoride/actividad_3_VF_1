# Feature 12: text_indexes_search — Implementación

## Cambios realizados

### 1. Schema: `mongodb/schema/products_catalog_schema.json`

**a) Text index existente actualizado:**
- **Antes:** `{"name": "text", "description": "text", "product_category_name": "text"}`
- **Después:** `{"product_category_name": 1, "name": "text", "description": "text", "tags": "text"}`
- El campo `tags` reemplaza `product_category_name` como campo text (alineado con notebook)
- `product_category_name` ahora es un campo regular (1) para filtro de igualdad
- Descripción actualizada a compound text+field

**b) Nuevo compound index añadido: `idx_text_category_compound`**
- Key: `{"product_category_name": 1, "name": "text", "description": "text", "tags": "text"}`
- Options: `{"default_language": "none"}`
- Propósito: Equality filter por categoría + full-text search en nombre/descripción/tags

### 2. Notebook: `notebooks/U5_Etapa1_MongoDB_Optimizacion.ipynb`

**a) Markdown cell 7 — Section 1.3 title actualizado:**
- "Índice de Texto para Búsqueda Full-Text" → "Índice de Texto Compuesto con Filtro de Categoría"
- Documenta el compound index con `product_category_name: 1` como filtro
- Explica sorting por textScore con $meta

**b) Code cell 8 — Código de comparación actualizado:**
- Crea el compound index `idx_text_category_compound` (dropea cualquier text index previo)
- REGEX: filtro por categoría + regex search (sin uso de índice de texto)
- FULL-TEXT: filtro por categoría + $text search + sorting por textScore
- Muestra top 5 resultados con relevance score
- Compara COLLSCAN (regex) vs IXSCAN + textScore (full-text)

### Detalles del índice compound

```
db.products_catalog.create_index(
    [("product_category_name", 1), ("name", "text"), ("description", "text"), ("tags", "text")],
    name="idx_text_category_compound",
    default_language="none"
)
```

- `product_category_name: 1` → Equality filter (MongoDB usa este campo para IXSCAN primero)
- `name: "text"` → Full-text search
- `description: "text"` → Full-text search
- `tags: "text"` → Full-text search

Query optimizada:
```javascript
db.products_catalog.find(
    {product_category_name: "eletronicos", $text: {$search: "bluetooth"}},
    {name: 1, product_category_name: 1, score: {$meta: "textScore"}}
).sort([("score", {$meta: "textScore"})])
```
