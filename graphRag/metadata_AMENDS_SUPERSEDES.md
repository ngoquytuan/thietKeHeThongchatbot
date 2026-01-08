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

Có — với hệ “tờ trình / quyết định / báo cáo / công văn / phụ lục” thì chỉ 3 nhãn `BASED_ON/AMENDS/SUPERSEDES` thường **không đủ**. Bạn nên có thêm một nhóm nhãn “liên quan nhưng không mang ngữ nghĩa pháp lý mạnh”, để GraphRAG vẫn traverse được mà không làm sai logic hiệu lực.

Dưới đây là bộ nhãn mình hay khuyến nghị (chia nhóm rõ để bạn dễ kiểm soát ranking và tránh suy luận sai):

## 1) Nhóm “tham chiếu / liên quan” (an toàn, dùng nhiều nhất)

### `REFERENCES`

Dùng khi A **nhắc tới** B (trích dẫn, dẫn số hiệu, dẫn đoạn) nhưng chưa chắc “là căn cứ”.

* Ví dụ: báo cáo có đoạn “theo Quyết định …” (nhưng không phải căn cứ pháp lý chính thức).

**metadata tối thiểu gợi ý**

* `ref_type`: `"citation|mention"`
* `ref_text`: đoạn trích ngắn hoặc vị trí

---

### `RELATED_TO`

Quan hệ “có liên quan” chung chung để nối graph (dùng khi bạn chưa phân loại được).

* Ví dụ: nhiều tài liệu trong cùng một case/hồ sơ dự án.

**Lưu ý**: nhãn này nên để `confidence` thấp hơn và thường `verified=false` nếu auto.

---

### `SAME_CASE` / `SAME_DOSSIER`

Cùng hồ sơ/cùng vụ việc/cùng mã dự án.

* Rất hợp với “tờ trình–báo cáo–quyết định–phụ lục” cùng một hồ sơ.

**metadata tối thiểu**

* `case_id` hoặc `dossier_id`

---

## 2) Nhóm “quy trình văn bản” (workflow / hành chính)

### `PROPOSES`

Tờ trình / đề xuất **đề nghị ban hành** quyết định/đề án.

* Hướng khuyến nghị: `Tờ trình -> Quyết định/Dự thảo`

**metadata**

* `proposal_type`: `"submission|draft|recommendation"`

---

### `APPROVES`

Quyết định **phê duyệt** một tờ trình/đề án/kế hoạch.

* Hướng: `Quyết định -> Đề án/Kế hoạch/Tờ trình`

---

### `ATTACHES` / `HAS_ATTACHMENT`

Tài liệu A **đính kèm** tài liệu B (phụ lục, danh mục, bảng biểu).

* Hướng: `Tài liệu chính -> Phụ lục`

**metadata**

* `attachment_kind`: `"appendix|annex|table|map"`

---

### `RESPONDS_TO`

Công văn trả lời / phản hồi văn bản trước đó.

* Hướng: `Văn bản trả lời -> Văn bản được hỏi/được yêu cầu`

---

### `REQUESTS`

Văn bản A yêu cầu văn bản B hoặc yêu cầu thực hiện/giải trình.

* Hướng: `Văn bản yêu cầu -> Văn bản phản hồi (hoặc task)`

---

## 3) Nhóm “phiên bản / biến thể” (không hẳn sửa đổi pháp lý)

### `REVISES`

Bản dự thảo v2/v3 **chỉnh sửa** bản dự thảo trước (không nhất thiết là “AMENDS” theo hiệu lực pháp lý).

* Hướng: `v2 -> v1`

### `DERIVED_FROM`

Báo cáo/tổng hợp được lập **từ dữ liệu** hoặc **từ báo cáo khác**.

* Hướng: `Bản tổng hợp -> Nguồn`

---

## 4) Nhóm “đối tượng / phạm vi áp dụng”

### `IMPLEMENTS`

Văn bản A **triển khai** văn bản B (kế hoạch triển khai, hướng dẫn thực hiện).

* Hướng: `Kế hoạch/Hướng dẫn -> Quyết định/Chủ trương`

### `EVALUATES`

Báo cáo A **đánh giá** quyết định/kế hoạch B.

* Hướng: `Báo cáo -> Quyết định/Kế hoạch`

---

# Bộ nhãn tối thiểu mình khuyên dùng cho project kiểu “hồ sơ dự án”

Nếu bạn muốn gọn mà vẫn đủ bao phủ:

* Nhóm pháp lý mạnh: `BASED_ON`, `AMENDS`, `SUPERSEDES`
* Nhóm liên quan an toàn: `REFERENCES`, `RELATED_TO`, `SAME_DOSSIER`
* Nhóm workflow: `PROPOSES`, `APPROVES`, `ATTACHES`, `RESPONDS_TO`
* Nhóm phiên bản: `REVISES` (dự thảo)

=> Tổng ~10 nhãn là đã rất “đã tay” để test GraphRAG.

---

## Gợi ý quan trọng để GraphRAG “không trả lời sai”

* Chỉ coi **hiệu lực** khi relation_type nằm trong: `AMENDS`, `SUPERSEDES` (và có `effective_date`)
* Các nhãn mềm (`RELATED_TO`, `SAME_DOSSIER`, `REFERENCES`) dùng để **mở rộng ngữ cảnh** và **gợi ý nguồn** chứ không dùng để “kết luận pháp lý”
* Khi build ranking: ưu tiên đường đi qua `BASED_ON/AMENDS/SUPERSEDES` hơn `RELATED_TO`

---

Nếu bạn cho mình danh sách **loại tài liệu** bạn có (ví dụ: tờ trình, quyết định, báo cáo, công văn, kế hoạch, phụ lục, biên bản…) mình sẽ map ra một **bảng “loại A → loại B dùng nhãn gì”** + SQL insert mẫu cho 3–4 nhãn bạn dùng nhiều nhất (PROPOSES/APPROVES/ATTACHES/REFERENCES) để bạn chạy manual test luôn.


Câu hỏi của bạn rất thực tế. Trong một hệ thống quản lý hồ sơ dự án hoặc doanh nghiệp, mối quan hệ giữa các tài liệu thường phong phú hơn nhiều so với logic "cha-con" của văn bản pháp luật.

Dựa trên các loại tài liệu bạn nêu (Tờ trình, Quyết định, Báo cáo), tôi gợi ý bạn bổ sung các nhãn `relation_type` sau để GraphRAG có thể truy xuất ngữ cảnh chính xác hơn:

### 1. Nhóm Quan hệ Tiến trình (Workflow/Sequence)

Nhóm này giúp AI hiểu được tài liệu nào "đẻ" ra tài liệu nào trong một quy trình:

* **`PROPOSED_BY` (Được đề xuất bởi):** Dùng cho Quyết định nối ngược về Tờ trình. (Ví dụ: *Quyết định A được ban hành dựa trên nội dung Tờ trình B*).
* **`RESULTED_IN` (Dẫn đến):** Ngược lại với nhãn trên, dùng từ Tờ trình trỏ đến Quyết định.
* **`REPORTED_IN` (Được báo cáo tại):** Dùng để nối các dữ liệu, sự kiện hoặc các Quyết định vào một Báo cáo tổng hợp/Báo cáo định kỳ.

### 2. Nhóm Quan hệ Thực thi & Chi tiết (Implementation)

Nhóm này giúp AI đào sâu vào chi tiết:

* **`IMPLEMENTS` (Thực hiện):** Dùng cho Kế hoạch hoặc Báo cáo thực hiện trỏ về Quyết định chủ trương.
* **`DETAILED_BY` (Được chi tiết hóa bởi):** Dùng từ một văn bản khung (Quy chế) trỏ đến các hướng dẫn cụ thể.
* **`ATTACHED_TO` (Đính kèm):** Dùng cho các phụ lục, bảng biểu đi kèm một báo cáo hoặc tờ trình chính.

### 3. Nhóm Quan hệ Tham chiếu Ngang (Associative)

Dùng cho các tài liệu cùng thuộc một thực thể nhưng không có quan hệ thứ bậc:

* **`CO-REFERENCED` (Tham chiếu chéo):** Hai tài liệu nhắc đến nhau hoặc cùng nhắc đến một sự kiện/dự án mà không cái nào là cha của cái nào.
* **`PART_OF_PROJECT` (Thuộc dự án):** Nhãn quan trọng nhất để gom nhóm tất cả Tờ trình, Báo cáo, Quyết định vào một "cụm" (Project Cluster).
* **`EVIDENCE_FOR` (Bằng chứng cho):** Dùng cho các Báo cáo, Biên bản nghiệm thu trỏ về một xác nhận hoặc kết luận nào đó.

---

### Bảng tổng hợp gợi ý cho hệ thống của bạn:

| Relation Type | Source (Doc A) | Target (Doc B) | Ý nghĩa cho RAG |
| --- | --- | --- | --- |
| **`PROPOSED_BY`** | Quyết định | Tờ trình | Tìm lý do tại sao Quyết định này ra đời. |
| **`REPORTED_IN`** | Quyết định/Sự kiện | Báo cáo | Tìm xem kết quả của Quyết định này được ghi nhận ở đâu. |
| **`PART_OF`** | Tờ trình/Báo cáo | Dự án/Hồ sơ lớn | Gom tất cả tài liệu liên quan đến một dự án để trả lời câu hỏi tổng quát. |
| **`VERSION_OF`** | Báo cáo (V2) | Báo cáo (V1) | Tránh lấy nhầm dữ liệu cũ, AI sẽ biết đâu là bản mới nhất. |

---

### Cách "Hardlink" thủ công các nhãn này hiệu quả:

Nếu bạn nhập tay, hãy đưa thêm trường **`context_snippet`** vào bảng `graph_edges`.

* *Ví dụ:* Nếu chọn nhãn `PROPOSED_BY`, hãy copy dòng chữ trong Quyết định: *"Xét Tờ trình số 123/TT-ABC ngày..."* vào cột này.
* **Lợi ích:** Khi RAG hoạt động, nó không chỉ biết A nối với B, mà còn biết **tại sao** chúng nối với nhau, giúp câu trả lời của AI cực kỳ thuyết phục.

**Gợi ý bước tiếp theo:** Bạn có muốn tôi bổ sung các nhãn này vào bảng `graph_templates` để khi bạn verify metadata, hệ thống sẽ tự động gợi ý nhãn phù hợp dựa trên `document_type` không?

