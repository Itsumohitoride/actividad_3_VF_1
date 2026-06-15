# Feature 13 — aggregation_pipeline_optimization

## What was changed

Updated **Section 2** (Optimización del Aggregation Pipeline) in `notebooks/U5_Etapa1_MongoDB_Optimizacion.ipynb`.

## Markdown cell changes (cell 13)

Updated stage description from 6 to 7 stages, adding **$project** as stage 2 and explaining the **$lookup** as auto-lookup for top 3 products per category.

## Code cell changes (cell 14)

### BEFORE pipeline
Kept as-is: simpler pipeline without $lookup, demonstrating suboptimal order ($group before $match, no early projection).

### AFTER pipeline — 7 stages with $lookup

| Stage | Operator | Purpose |
|-------|----------|---------|
| 1 | `$match` | Filter rating >= 4 and non-empty category |
| 2 | `$project` | Early projection — keep only needed fields (name included for lookup display) |
| 3 | `$group` | Group by category, count products, average rating |
| 4 | **`$lookup`** | Self-lookup on `products_catalog` — for each category, fetch top 3 products (rating >= 4, sorted desc, limited to 3) |
| 5 | `$addFields` | Weighted score = avgRating * log(count + 1) |
| 6 | `$sort` | Descending by weightedScore |
| 7 | `$limit` | Top 10 categories |

### $lookup details
- **Type**: Self-lookup (same collection `products_catalog`)
- **Method**: Sub-pipeline with `let` + `$expr` for joining on `product_category_name`
- **Sub-pipeline stages**: `$match` (same rating filter) → `$project` → `$sort` (desc) → `$limit` (3)
- **Output field**: `top_products` — array of up to 3 product names with ratings

### Additional output
Print section shows `top_products` for the top 3 categories to visually demonstrate $lookup enrichment.

## Verification

- Notebook remains valid JSON
- Pipeline has 7 stages including $lookup
- acceptance criteria met:
  - [x] Min 5 stages (7 implemented)
  - [x] Includes $match, $group, $project/$addFields, $sort
  - [x] Includes $lookup
  - [x] $match early + projection applied
  - [x] allowDiskUse configured
  - [x] explain() BEFORE/AFTER metrics
  - [x] Stage-by-stage documentation
