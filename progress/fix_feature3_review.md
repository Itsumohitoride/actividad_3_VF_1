# fix_feature3_review — Fix Cells 55 and 56

## Summary

Fixed 2 review issues in Feature 3 (Section 2 — Indexing analysis) in `U4_Etapa1_Investigacion.ipynb`.

## Issue 1: Cell 55 (now cell 56) — pg_stat_user_indexes

**Before:** Only queried `pg_indexes` (index definitions).
**After:** Queries BOTH `pg_indexes` AND `pg_stat_user_indexes` for real usage statistics (idx_scan, idx_tup_read, idx_tup_fetch).

## Issue 2: Cell 56 (now cell 57) — seq_scan and idx_scan

**Before:** Queried `n_live_tup` and `pg_total_relation_size` only.
**After:** Added `seq_scan`, `seq_tup_read`, `idx_scan`, `idx_tup_fetch` columns from `pg_stat_user_tables`.

## Files modified

- `src/Ecommify_Database_Design/notebooks/U4_Etapa1_Investigacion.ipynb`
  - Cell 55 (0-indexed 55, 1-indexed 56): Replaced source with dual query (pg_indexes + pg_stat_user_indexes)
  - Cell 56 (0-indexed 56, 1-indexed 57): Replaced source with extended query (added seq_scan, idx_scan columns)

## Verification

- JSON valid: confirmed via `json.load()`
- Other cells unchanged (73 total cells)
- Only the 2 target code cells were modified
