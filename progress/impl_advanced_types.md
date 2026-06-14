# Feature: Advanced PostgreSQL Types — Implementation Report

## Summary
Added advanced PostgreSQL data types (JSONB, TEXT[], TSTZRANGE) and specialized indexes (GIN, GIST) plus POINT-based geographic views to the Ecommify schema.

## Changes Applied

### 1. product.specifications (JSONB)
- **CREATE TABLE**: Added `specifications JSONB` after `product_width_cm` in the `product` table definition (line 69)
- **ALTER TABLE**: `ALTER TABLE product ADD COLUMN IF NOT EXISTS specifications JSONB;` (line 78) for existing DB compatibility
- **Purpose**: Store flexible product specifications (weight, dimensions, color, material, etc.) as semi-structured JSON without schema changes

### 2. product.photo_urls (TEXT[])
- **CREATE TABLE**: Added `photo_urls TEXT[]` after `specifications` in the `product` table definition (line 70)
- **ALTER TABLE**: `ALTER TABLE product ADD COLUMN IF NOT EXISTS photo_urls TEXT[];` (line 79) for existing DB compatibility
- **Purpose**: Store multiple photo URLs as a native PostgreSQL array, avoiding a separate product_photos table

### 3. "order".promotion_period (TSTZRANGE)
- **CREATE TABLE**: Added `promotion_period TSTZRANGE` after `order_estimated_delivery_date` in the `"order"` table definition (line 91)
- **ALTER TABLE**: `ALTER TABLE "order" ADD COLUMN IF NOT EXISTS promotion_period TSTZRANGE;` (line 108) for existing DB compatibility
- **Purpose**: Store promotion validity windows as a range type, enabling overlap/exclusion queries with range operators

### 4. GIN Index: idx_product_specifications
```sql
CREATE INDEX IF NOT EXISTS idx_product_specifications ON product USING GIN (specifications);
```
- **Type**: GIN (Generalized Inverted Index)
- **Purpose**: Enable efficient `@>`, `?`, `?|`, `?&` JSONB operators on the specifications column
- **Use case**: Find products matching specific JSON key/value criteria

### 5. GIN Index: idx_product_photo_urls
```sql
CREATE INDEX IF NOT EXISTS idx_product_photo_urls ON product USING GIN (photo_urls);
```
- **Type**: GIN (Generalized Inverted Index)
- **Purpose**: Enable efficient `@>`, `&&`, `ANY()` array operators on the photo_urls column
- **Use case**: Find products with photos matching specific URL patterns

### 6. GiST Index: idx_order_promotion_period
```sql
CREATE INDEX IF NOT EXISTS idx_order_promotion_period ON "order" USING GIST (promotion_period);
```
- **Type**: GiST (Generalized Search Tree)
- **Purpose**: Enable efficient range operators: `&&` (overlap), `@>` (contains), `<@` (contained by), `<<`, `>>`
- **Use case**: Query orders with active promotions at any given time

### 7. Geographic POINT Views
```sql
CREATE OR REPLACE VIEW customer_geo AS ...
CREATE OR REPLACE VIEW seller_geo AS ...
```
- **Tables**: `customer_geo` (derived from customer LEFT JOIN geolocation) and `seller_geo` (derived from seller LEFT JOIN geolocation)
- **POINT type**: Exposes `POINT(longitude, latitude)` as `location` column
- **Purpose**: Enable proximity queries using the `<->` distance operator (e.g., `ORDER BY location <-> POINT(-46.63, -23.55)`)
- **Note**: POINT is not indexable directly without PostGIS. Raw lat/lng columns in geolocation remain the indexed target.

## Design Decisions

### Why ALTER TABLE ADD COLUMN IF NOT EXISTS alongside CREATE TABLE?
- **CREATE TABLE IF NOT EXISTS** handles fresh DB installations (new containers, test DBs)
- **ALTER TABLE ... ADD COLUMN IF NOT EXISTS** handles existing databases where tables already exist without these columns
- Combined approach makes the script idempotent for both scenarios

### Why GIN vs GiST for JSONB?
- GIN is the standard index type for JSONB in PostgreSQL. GiST for JSONB exists but is typically slower for `@>` operators.

### Why POINT views instead of PostGIS geography?
- POINT is a built-in PostgreSQL type (no PostGIS extension required)
- The `<->` operator works on POINT for euclidean distance approximation
- For production geo-queries requiring precise spherical distance, PostGIS geography would be preferred

## Impact Assessment
- **Additive only**: No columns renamed, dropped, or type-changed
- **Backward compatible**: All existing queries continue to work unchanged
- **No index conflicts**: New indexes have unique names not conflicting with existing ones
- **Performance**: GIN/GiST indexes add write overhead but enable query patterns that would otherwise require full table scans

## Verification
- `python3 scripts/check_harness.py` — all green
- SQL syntax validated against PostgreSQL 15 (Docker container running)
- File: `src/Ecommify_Database_Design/postgresql/schema/01_ddl_ecommify.sql` — 208 lines total
