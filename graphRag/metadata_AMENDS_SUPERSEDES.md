Dưới đây là **metadata tối thiểu (đủ dùng, dễ mở rộng)** cho `AMENDS` và `SUPERSEDES` (để bạn hardlink manual mà vẫn “đúng logic”, nhất là khi sau này bạn muốn hỏi “hiện hành/đang áp dụng”).

Mình giả định `graph_edges.metadata` là `jsonb` (đúng kiểu hay dùng), và bạn đang insert theo pattern `WITH s,t ... INSERT ...`.

---

## 1) Schema metadata tối thiểu

### A) `AMENDS` (A sửa đổi B)

**Ý nghĩa cạnh (khuyến nghị):** `A (văn bản sửa đổi) -> B (văn bản bị sửa)`

**metadata tối thiểu (jsonb):**

```json
{
  "effective_date": "YYYY-MM-DD",
  "scope": "partial|all",
  "amends": [
    {
      "target_ref": "Điều 3 Khoản 2|Phụ lục I|Mục 1.2",
      "action": "replace|add|delete",
      "note": "mô tả ngắn (tùy chọn)"
    }
  ],
  "source": {
    "method": "manual_sql",
    "evidence": "trích yếu/ngữ cảnh ngắn hoặc số trang"
  }
}
```

**Giải thích ngắn:**

* `effective_date`: ngày hiệu lực của “sửa đổi”
* `scope`: `"all"` nếu sửa/đính chính toàn văn; `"partial"` nếu chỉ vài điều/khoản
* `amends[]`: danh sách phần bị tác động (tối thiểu chỉ cần `target_ref` + `action`)
* `source`: lưu dấu vết “manual” + chút evidence để debug

---

### B) `SUPERSEDES` (A thay thế B)

**Ý nghĩa cạnh (khuyến nghị):** `A (văn bản thay thế) -> B (văn bản bị thay thế)`

**metadata tối thiểu (jsonb):**

```json
{
  "effective_date": "YYYY-MM-DD",
  "scope": "all|partial",
  "supersedes": {
    "mode": "repeal_and_replace|replace_in_force|partial_replace",
    "target_ref": "toàn văn|Điều 5|Phụ lục II"
  },
  "source": {
    "method": "manual_sql",
    "evidence": "trích yếu/ngữ cảnh ngắn hoặc số trang"
  }
}
```

**Giải thích ngắn:**

* `mode` giúp sau này bạn phân biệt: “bãi bỏ & thay thế”, “thay thế đang hiệu lực”, hay “thay thế một phần”
* `target_ref` dùng khi `scope=partial` (còn `scope=all` thì có thể ghi `"toàn văn"`)

---

## 2) SQL insert mẫu cho `AMENDS`

> Placeholder: thay `<AMENDING_DOC_UUID>` là doc A, `<AMENDED_DOC_UUID>` là doc B.

```sql
BEGIN;

WITH
s AS (
  SELECT graph_doc_id, law_id, hierarchy_level
  FROM graph_documents
  WHERE source_document_id = '<AMENDING_DOC_UUID>'::uuid
),
t AS (
  SELECT graph_doc_id, law_id, hierarchy_level
  FROM graph_documents
  WHERE source_document_id = '<AMENDED_DOC_UUID>'::uuid
)
INSERT INTO graph_edges (
  source_graph_doc_id,
  target_graph_doc_id,
  source_law_id,
  target_law_id,
  relation_type,
  source_level,
  target_level,
  level_diff,
  confidence,
  context_snippet,
  verified,
  verified_by,
  verified_at,
  is_suggested,
  is_auto_created,
  notes,
  metadata
)
SELECT
  s.graph_doc_id,
  t.graph_doc_id,
  s.law_id,
  t.law_id,
  'AMENDS',
  s.hierarchy_level,
  t.hierarchy_level,
  (s.hierarchy_level - t.hierarchy_level),
  1.00,
  'Manual: A sửa đổi B theo ...',
  true,
  'manual_sql',
  NOW(),
  false,
  false,
  'manual AMENDS link',
  jsonb_build_object(
    'effective_date', '2025-01-01',                 -- đổi theo thực tế
    'scope', 'partial',                             -- 'partial' hoặc 'all'
    'amends', jsonb_build_array(
      jsonb_build_object(
        'target_ref', 'Điều 3 Khoản 2',
        'action', 'replace',
        'note', 'Sửa nội dung khoản 2'
      )
    ),
    'source', jsonb_build_object(
      'method', 'manual_sql',
      'evidence', 'dựa theo trích yếu/điều khoản trong A'
    )
  )
FROM s, t
ON CONFLICT (source_graph_doc_id, target_graph_doc_id, relation_type)
DO UPDATE SET
  confidence      = EXCLUDED.confidence,
  context_snippet = EXCLUDED.context_snippet,
  verified        = EXCLUDED.verified,
  verified_by     = EXCLUDED.verified_by,
  verified_at     = EXCLUDED.verified_at,
  notes           = EXCLUDED.notes,
  metadata        = EXCLUDED.metadata,
  updated_at      = NOW();

COMMIT;
```

---

## 3) SQL insert mẫu cho `SUPERSEDES`

> Placeholder: `<NEW_DOC_UUID>` là A, `<OLD_DOC_UUID>` là B.

```sql
BEGIN;

WITH
s AS (
  SELECT graph_doc_id, law_id, hierarchy_level
  FROM graph_documents
  WHERE source_document_id = '<NEW_DOC_UUID>'::uuid
),
t AS (
  SELECT graph_doc_id, law_id, hierarchy_level
  FROM graph_documents
  WHERE source_document_id = '<OLD_DOC_UUID>'::uuid
)
INSERT INTO graph_edges (
  source_graph_doc_id,
  target_graph_doc_id,
  source_law_id,
  target_law_id,
  relation_type,
  source_level,
  target_level,
  level_diff,
  confidence,
  context_snippet,
  verified,
  verified_by,
  verified_at,
  is_suggested,
  is_auto_created,
  notes,
  metadata
)
SELECT
  s.graph_doc_id,
  t.graph_doc_id,
  s.law_id,
  t.law_id,
  'SUPERSEDES',
  s.hierarchy_level,
  t.hierarchy_level,
  (s.hierarchy_level - t.hierarchy_level),
  1.00,
  'Manual: A thay thế B theo ...',
  true,
  'manual_sql',
  NOW(),
  false,
  false,
  'manual SUPERSEDES link',
  jsonb_build_object(
    'effective_date', '2025-03-15',                 -- đổi theo thực tế
    'scope', 'all',                                 -- 'all' hoặc 'partial'
    'supersedes', jsonb_build_object(
      'mode', 'repeal_and_replace',                 -- gợi ý: repeal_and_replace|replace_in_force|partial_replace
      'target_ref', 'toàn văn'                      -- nếu partial: 'Điều 5', 'Phụ lục II', ...
    ),
    'source', jsonb_build_object(
      'method', 'manual_sql',
      'evidence', 'căn cứ điều khoản hiệu lực trong A'
    )
  )
FROM s, t
ON CONFLICT (source_graph_doc_id, target_graph_doc_id, relation_type)
DO UPDATE SET
  confidence      = EXCLUDED.confidence,
  context_snippet = EXCLUDED.context_snippet,
  verified        = EXCLUDED.verified,
  verified_by     = EXCLUDED.verified_by,
  verified_at     = EXCLUDED.verified_at,
  notes           = EXCLUDED.notes,
  metadata        = EXCLUDED.metadata,
  updated_at      = NOW();

COMMIT;
```

---

## 4) Query debug nhanh (đọc metadata)

```sql
SELECT
  e.edge_id,
  e.relation_type,
  s.source_document_id AS src_doc,
  t.source_document_id AS tgt_doc,
  e.metadata->>'effective_date' AS effective_date,
  e.metadata->>'scope' AS scope,
  e.metadata
FROM graph_edges e
JOIN graph_documents s ON s.graph_doc_id = e.source_graph_doc_id
JOIN graph_documents t ON t.graph_doc_id = e.target_graph_doc_id
WHERE e.relation_type IN ('AMENDS','SUPERSEDES')
ORDER BY e.verified_at DESC
LIMIT 50;
```

---

Nếu bạn muốn “tối thiểu hơn nữa” để insert nhanh: với `AMENDS`/`SUPERSEDES` bạn chỉ cần `effective_date` + `scope` + (`amends[]` hoặc `supersedes{}`) là đủ. Phần `source` là để bạn debug sướng hơn khi test manual.
