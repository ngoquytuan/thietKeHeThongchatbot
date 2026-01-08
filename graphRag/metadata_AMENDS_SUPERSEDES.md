Đây là cấu trúc bảng `graph_edges` cực kỳ đầy đủ và chuyên nghiệp dành cho hệ thống **Enterprise GraphRAG**. Với cấu trúc này, bạn không chỉ làm RAG thông thường mà còn có thể quản lý được cả vòng đời dữ liệu (Data Governance) và độ tin cậy của tri thức.

### 1. Phân nhóm và Giải thích các trường dữ liệu

Tôi sẽ chia các cột của bạn thành 5 nhóm chức năng chính để dễ quản lý:

#### Nhóm 1: Định danh và Kết nối (Core Identity)

* **`edge_id`**: Khóa chính duy nhất cho mỗi quan hệ.
* **`source_graph_doc_id` & `target_graph_doc_id**`: ID nội bộ của 2 node trong bảng `graph_documents`.
* **`source_law_id` & `target_law_id**`: Số hiệu văn bản (Ví dụ: `265/2025/NĐ-CP`). Dùng để đối chiếu nhanh mà không cần JOIN sang bảng document.
* **`source_task_code` & `target_task_code**`: Mã công việc/dự án (Ví dụ: `ĐTCT.2024.05`). Dùng để tạo quan hệ giữa các tài liệu cùng thuộc một dự án như bạn đã đề cập ở câu hỏi trước.

#### Nhóm 2: Logic Đồ thị (Graph Logic & Hierarchy)

* **`relation_type`**: Loại quan hệ chính (BASED_ON, PROPOSED_BY...).
* **`relation_subtype`**: Chi tiết hơn (Ví dụ: `relation_type` là `AMENDS` thì `subtype` có thể là `REPLACE_ARTICLE` - Thay thế điều khoản).
* **`source_level` & `target_level**`: Cấp bậc của 2 tài liệu (0: Luật, 1: Nghị định...).
* **`level_diff`**: Độ chênh lệch cấp bậc. Giúp truy vấn nhanh các quan hệ "vượt cấp" (Ví dụ: Từ Quyết định nhảy thẳng lên Luật).
* **`edge_weight`**: Trọng số liên kết (0.0 - 1.0). AI sẽ ưu tiên đi theo các link có weight cao khi tìm kiếm context.

#### Nhóm 3: Nguồn gốc và Trích xuất (Provenance & Extraction)

* **`extraction_method`**: Cách tạo link (`manual`, `ai_regex`, `llm_extraction`).
* **`extraction_context`**: **Cực kỳ quan trọng**. Chứa đoạn văn bản gốc chứng minh cho sự liên kết này (Ví dụ: "Xét tờ trình số...").
* **`page_number` & `paragraph_number**`: Vị trí chính xác trong file PDF/Docx nơi tìm thấy liên kết.
* **`confidence`**: Độ tin cậy của AI khi bóc tách link này.

#### Nhóm 4: Kiểm soát và Xác thực (Governance & Verification)

* **`verified`**: `true` nếu con người đã check, `false` nếu AI mới tự tạo.
* **`verified_by` & `verified_at**`: Ai là người duyệt link này và vào lúc nào.
* **`is_suggested`**: Nếu AI thấy có khả năng liên quan nhưng chưa chắc chắn, nó sẽ đánh dấu là `true` để chờ bạn duyệt.
* **`is_active`**: Dùng để "xóa mềm". Khi văn bản hết hiệu lực, bạn set `false` thay vì xóa để giữ lịch sử.

#### Nhóm 5: Metadata và Audit

* **`edge_metadata`**: Lưu trữ các trường linh hoạt phát sinh thêm dưới dạng JSONB.
* **`created_by` & `updated_by**`: Hệ thống hoặc User thực hiện thao tác.

---

### 2. Ví dụ một dòng dữ liệu (Sample Data)

Giả sử bạn có **Quyết định 456** được ban hành dựa trên **Tờ trình 123**:

| Cột | Giá trị | Giải thích |
| --- | --- | --- |
| **source_law_id** | 456/QĐ-UBND | Văn bản nguồn (đi trích dẫn) |
| **target_law_id** | 123/TTr-VP | Văn bản đích (được trích dẫn) |
| **relation_type** | `PROPOSED_BY` | Quyết định được đề xuất bởi Tờ trình |
| **source_level** | 3 | Cấp Quyết định |
| **target_level** | 4 | Cấp Tờ trình (thấp hơn) |
| **extraction_method** | `manual` | Bạn tự nhập tay |
| **extraction_context** | "Căn cứ Tờ trình số 123/TTr-VP ngày 01/01/2024 của Văn phòng..." | Ngữ cảnh trích dẫn |
| **verified** | `true` | Đã xác thực |
| **edge_weight** | 1.0000 | Liên kết tuyệt đối |

---

### 3. Tại sao các Index bạn nêu lại quan trọng?

Hệ thống Index này được thiết kế để phục vụ các kiểu truy vấn "khó" của GraphRAG:

1. **`INDEX source_graph_doc_id, target_graph_doc_id, relation_type WHERE is_active = true`**: Đây là index quan trọng nhất. Nó giúp tìm kiếm nhanh các quan hệ đang còn hiệu lực giữa 2 tài liệu bất kỳ.
2. **`INDEX level_diff`**: Dùng khi bạn muốn hỏi AI: "Tìm tất cả các văn bản dưới cấp của Luật này mà đang vi phạm quy định".
3. **`INDEX source_task_code, target_task_code WHERE is_active = true AND verified = true`**: Giúp gom nhóm toàn bộ tài liệu theo dự án cực nhanh cho các câu hỏi dạng: "Tóm tắt toàn bộ hồ sơ dự án ĐTCT.2024.05".
4. **`INDEX edge_weight WHERE edge_weight > 0.5`**: Khi hệ thống có hàng triệu link, AI chỉ nên "đi bộ" trên những link có trọng số cao để tránh bị nhiễu thông tin (Noise).

**Lời khuyên:** Với bảng này, khi làm **Hardlink manual**, bạn hãy cố gắng điền ít nhất là `relation_type`, `extraction_context` và `verified = true`. Những trường này sẽ giúp câu trả lời của RAG đạt chất lượng "Expert" (Chuyên gia).

Để xây dựng một GraphRAG linh hoạt cho các dự án chứa nhiều loại tài liệu như tờ trình, báo cáo, và quyết định, bạn cần mở rộng bộ nhãn `relation_type` trong bảng `graph_edges`. Việc chỉ sử dụng các nhãn pháp lý thuần túy (như `BASED_ON`) sẽ làm mất đi ngữ cảnh vận hành của dự án,.

Dưới đây là các nhãn gợi ý để bạn phân loại chính xác mối quan hệ giữa các tài liệu trong một dự án:

### 1. Nhãn cho quy trình nghiệp vụ (Functional Relations)
Các nhãn này giúp LLM hiểu được luồng công việc (workflow) từ khi đề xuất đến khi kết thúc:
*   **`PROPOSES` (Trình/Đề xuất cho):** Dùng cho các **Tờ trình**. Tờ trình A `PROPOSES` Quyết định B. Đây là quan hệ tiền đề nhưng không phải là "căn cứ pháp lý",.
*   **`IMPLEMENTS` (Thực hiện/Triển khai):** Dùng khi một văn bản cụ thể hóa việc thực hiện một kế hoạch hoặc quyết định trước đó,. Ví dụ: Quyết định triển khai dự án `IMPLEMENTS` Kế hoạch năm.
*   **`REPORTS_ON` (Báo cáo về):** Dùng cho các **Báo cáo**. Báo cáo tình hình tháng 5 `REPORTS_ON` tiến độ của Quyết định dự án X. Nhãn này giúp hệ thống truy xuất được kết quả thực hiện của một nút (node) cụ thể.

### 2. Nhãn cho mối quan hệ ngang hàng và liên kết (Horizontal Relations)
Trong một dự án, nhiều tài liệu có cùng **`task_code`** hoặc **`project_code`** nhưng không có quan hệ cha-con trực tiếp:
*   **`RELATED_TO` (Liên quan đến):** Nhãn chung nhất cho các tài liệu cùng thuộc một mã nhiệm vụ hoặc dự án nhưng không xác định được hướng tác động cụ thể.
*   **`REFERENCES` (Tham chiếu):** Sử dụng khi một tài liệu nhắc đến một tài liệu khác để cung cấp thông tin bổ sung, không mang tính bắt buộc hoặc căn cứ.
*   **`ATTACHED_TO` (Đính kèm cùng):** Dùng cho các phụ lục, danh mục hoặc tài liệu đi kèm không thể tách rời của một văn bản chính.

### 3. Nhãn cho logic thời gian và phiên bản
*   **`FOLLOWS` (Tiếp nối):** Dùng khi một tài liệu ra đời sau tài liệu khác trong cùng một chuỗi sự kiện mà không sửa đổi tài liệu trước đó.
*   **`SUPPLEMENTS` (Bổ sung cho):** Khác với `AMENDS` (sửa đổi nội dung cũ), nhãn này dùng khi tài liệu mới bổ sung thêm các điều khoản hoặc nội dung mà tài liệu cũ chưa có.

### Cách tối ưu hóa việc gắn nhãn
Để không làm phức tạp bảng `graph_edges`, bạn có thể kết hợp sử dụng cột **`edge_metadata`** (JSONB) mà bạn đã thiết kế sẵn,:
*   **Dùng nhãn chính:** Giữ `relation_type` ở mức khái quát (ví dụ: `PROCESS_FLOW`).
*   **Dùng nhãn chi tiết trong metadata:** Lưu thông tin cụ thể như `{"sub_type": "proposal_to_decision", "step": 1}` vào cột `edge_metadata`.

**Gợi ý áp dụng:** Khi thực hiện **Strategy 1 (Hard Linking)** dựa trên mã dự án (`project_code`), nếu hệ thống thấy hai tài liệu có chung mã nhưng không có từ khóa "Căn cứ", nó nên tự động gán nhãn `RELATED_TO` với độ tin cậy (`confidence`) khoảng 0.9,. Việc này giúp bạn bao phủ được 95% tài liệu hiện đang thiếu metadata chặt chẽ mà vẫn duy trì được mạng lưới liên kết trong dự án,.

***

**Ví von để dễ hình dung:** Nếu coi các tài liệu trong dự án là các thành viên trong một đội bóng, thì `BASED_ON` giống như quan hệ giữa Huấn luyện viên và Cầu thủ (mệnh lệnh - thực thi), còn `RELATED_TO` hay `REPORTS_ON` giống như quan hệ giữa các cầu thủ trên sân; họ không ra lệnh cho nhau nhưng mọi hành động của người này đều liên quan trực tiếp đến vị trí và kết quả của người kia.

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

Cấu trúc `edge_metadata` bạn đưa ra **rất ổn** và chuyên nghiệp. Nó biến một "đường kẻ" vô hồn giữa hai tài liệu thành một "kết nối có tri thức".

Trong GraphRAG, cột `metadata` này cực kỳ quan trọng vì AI sẽ sử dụng nó để giải thích **tại sao** hai tài liệu lại liên quan đến nhau. Tuy nhiên, để tối ưu cho việc truy vấn bằng SQL (JSONB) và xử lý ngôn ngữ tự nhiên (RAG), tôi có một vài góp ý điều chỉnh như sau:

---

### 1. Phân tích cấu trúc bạn đưa ra

* **`effective_date`**: Rất cần thiết. Giúp AI biết link này có còn giá trị tại thời điểm người dùng hỏi hay không.
* **`scope`**: Tốt. Phân biệt giữa "toàn bộ văn bản" hay chỉ "một phần".
* **`amends` (Mảng đối tượng)**: Đây là phần "đắt giá" nhất. Nó cho phép bạn thực hiện **Granular RAG** (RAG đến cấp độ điều khoản). Việc lưu `target_ref` và `action` giúp AI trả lời được câu hỏi: *"Điều 3 của quy chế cũ đã bị thay đổi như thế nào?"*.
* **`source`**: Bạn nên cân nhắc chuyển `source` ra các cột chính (như `extraction_method`, `extraction_context` mà chúng ta đã thảo luận ở bảng trước) để tạo Index tốt hơn. Nếu vẫn để trong JSONB, hãy giữ nó gọn nhẹ.

### 2. Gợi ý bổ sung để "hoàn hảo" hơn

Để biến `edge_metadata` thành "vũ khí" lợi hại cho hệ thống RAG, bạn nên cân nhắc thêm 2 trường này:

1. **`semantic_reason` (Text)**: Một câu tóm tắt bằng ngôn ngữ tự nhiên về quan hệ này.
* *VD: "Tờ trình này đề xuất chi tiết phương án tài chính cho mục 4 của Quyết định."*
* *Lý do:* Khi RAG tìm thấy cạnh này, nó có thể đọc thẳng câu này vào Prompt của LLM.


2. **`strength_score` (0-1)**: Độ mạnh của mối quan hệ trong ngữ cảnh cụ thể.
3. **`dependency_type`**: `hard` (Bắt buộc phải có A mới hiểu được B) hoặc `soft` (Chỉ là thông tin tham khảo thêm).

### 3. Ví dụ cấu trúc "Expert" đề xuất

```json
{
  "effective_date": "2025-01-01",
  "expiry_date": null, 
  "scope": "partial",
  "granularity": {
    "level": "article",
    "value": "Điều 5"
  },
  "amendments": [
    {
      "target_section": "Khoản 1 Điều 5",
      "action": "replace",
      "reason": "Cập nhật đơn giá mới theo thị trường"
    }
  ],
  "tags": ["tài chính", "định mức", "năm 2025"],
  "ai_summary": "Quyết định này thay thế đơn giá tại Khoản 1 Điều 5 của quy chế cũ do biến động giá thị trường."
}

```

---

### 4. Cách khai thác `edge_metadata` trong RAG

Khi bạn truy vấn, bạn có thể lọc trực tiếp bằng SQL JSONB để tăng độ chính xác:

* **Lọc theo hiệu lực:**
```sql
SELECT * FROM graph_edges 
WHERE edge_metadata->>'effective_date' <= '2025-01-08'
AND (edge_metadata->>'expiry_date' IS NULL OR edge_metadata->>'expiry_date' > '2025-01-08');

```


* **Lọc theo hành động cụ thể:**
```sql
-- Tìm tất cả các link liên quan đến việc "Xóa bỏ" (delete) nội dung
SELECT * FROM graph_edges 
WHERE edge_metadata @> '{"amends": [{"action": "delete"}]}';

```



### Một lưu ý nhỏ:

Nếu bạn dự định có hàng triệu `edges`, hãy tránh để `edge_metadata` quá lớn (vượt quá vài KB). Nếu dữ liệu quá lớn, hãy tách phần "nội dung chi tiết" sang một bảng khác và chỉ để lại các "flag" (cờ hiệu) quan trọng trong JSONB để tối ưu tốc độ scan của PostgreSQL.

**Bạn đã có dữ liệu mẫu cho các trường `amends` này chưa, hay cần tôi gợi ý một Prompt để AI tự động trích xuất thông tin này từ văn bản gốc?**


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

