# Feature 11 — compound_partial_indexes

## Files Modified

| File | Action |
|------|--------|
| `mongodb/schema/products_catalog_schema.json` | Added 2 indexes (1 ESR, 1 Partial) |
| `mongodb/schema/event_logs_schema.json` | Added 2 indexes (1 ESR, 1 Partial) |
| `mongodb/schema/user_sessions_schema.json` | Added 1 index (1 ESR) |

## Indexes Added

### products_catalog_schema.json

| Name | Key | Type | ESR Justification |
|------|-----|------|-------------------|
| `idx_esr_category_score_id` | `{product_category_name: 1, avg_review_score: -1, product_id: 1}` | **ESR** | E=product_category_name (equality filter), S=avg_review_score -1 (sort desc), R=product_id (covering, no scan) |
| `idx_partial_high_rated` | `{avg_review_score: -1, product_category_name: 1}` | **Partial** | Filters `avg_review_score >= 4.0`. Smaller index, faster scans for top-rated queries |

### event_logs_schema.json

| Name | Key | Type | ESR Justification |
|------|-----|------|-------------------|
| `idx_esr_type_time_session` | `{event_type: 1, timestamp: -1, session_id: 1}` | **ESR** | E=event_type (equality), S=timestamp -1 (sort recent first), R=session_id (range for session grouping) |
| `idx_partial_product_view` | `{customer_unique_id: 1, timestamp: -1}` | **Partial** | Filters `event_type: "product_view"`. Drastically reduces index size vs full event_logs index |

### user_sessions_schema.json

| Name | Key | Type | ESR Justification |
|------|-----|------|-------------------|
| `idx_esr_customer_created` | `{customer_unique_id: 1, created_at: -1}` | **ESR** | E=customer_unique_id (equality), S=created_at -1 (sort newest first). No range component needed |

## Totals

- **ESR indexes**: 3
- **Partial indexes**: 2
- **Total added**: 5 indexes across 3 collections
