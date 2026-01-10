Việc triển khai GraphRAG trên PostgreSQL là một hướng đi tối ưu vì bạn có thể tận dụng sức mạnh của Recursive CTE và tính nhất quán của dữ liệu mà không cần thêm hạ tầng phức tạp như Neo4j. Để giải quyết khó khăn trong việc tạo linking (liên kết), trước hết bạn cần hiểu rõ cấu trúc các bảng chuyên dụng cho đồ thị.
Dưới đây là chi tiết về 6 bảng mà bạn đang quan tâm và vai trò của chúng trong hệ thống:
1. Giải thích các bảng trong Schema Graph
Hệ thống này được thiết kế theo nguyên tắc cô lập kiến trúc (Architectural Isolation), tức là các bảng đồ thị hoạt động độc lập để không làm ảnh hưởng đến hiệu năng của hệ thống tìm kiếm chính.
• graph_documents: Là bản sao (mirror) của bảng tài liệu chính nhưng được bổ sung các thông tin về phân cấp (hierarchy level) từ L0 đến L5. Nó giúp hệ thống biết tài liệu nào là văn bản nền tảng (L0 - ví dụ: Luật, Điều lệ) và tài liệu nào là quyết định cụ thể (L3-L5).
• graph_edges: Đây là bảng quan trọng nhất, lưu trữ các mối quan hệ (cạnh) giữa các tài liệu. Nó chứa thông tin về điểm đầu (source), điểm cuối (target) và loại quan hệ như BASED_ON (căn cứ theo), IMPLEMENTS (thực hiện), hay SUPERSEDES (thay thế).
• graph_validation_rules: Chứa các quy tắc định nghĩa tính hợp lệ của đồ thị. Ví dụ: quy tắc "không được có vòng lặp" (No Cycles) hoặc "văn bản cấp thấp phải tham chiếu đến văn bản cấp cao hơn".
• graph_validation_log: Là nơi ghi lại các vi phạm (violations) khi dữ liệu không thỏa mãn các quy tắc trong bảng graph_validation_rules. Ví dụ: nếu một văn bản cấp 5 không có tham chiếu đến cấp 0, hệ thống sẽ log lại để bạn kiểm tra.
• graph_changelog: Lưu trữ nhật ký thay đổi (audit trail). Bất kỳ hành động thêm, sửa, xóa nào trên đồ thị đều được ghi lại để biết ai đã thực hiện, vào lúc nào, giúp bảo vệ tính toàn vẹn của dữ liệu.
• graph_templates: Chứa các mẫu cấu trúc đồ thị chuẩn. Ví dụ: một "Standard Project Hierarchy" (Phân cấp dự án chuẩn) giúp hệ thống tự động gợi ý cấu trúc khi bạn import tài liệu mới của một dự án tương tự.
--------------------------------------------------------------------------------
2. Gợi ý để tạo Linking giữa các tài liệu hiệu quả
Nếu bạn đang gặp khó khăn khi nối dây giữa các tài liệu, đặc biệt khi metadata hiện tại có thể bị thiếu (thường chỉ khoảng 5% tài liệu có metadata đầy đủ), bạn có thể áp dụng 3 chiến lược sau:
Chiến lược 1: Hard Linking (Độ tin cậy 90-100%)
Dựa trên các mã định danh có độ chính xác tuyệt đối để tự động tạo liên kết:
• Mã nhiệm vụ/Dự án (Task/Project Code): Nếu hai tài liệu cùng chứa mã ĐTCT.2024.05, chúng chắc chắn có liên quan.
• Số hiệu văn bản (Law ID): Sử dụng Regex để bóc tách số hiệu (ví dụ: 265/2025/NĐ-CP) từ nội dung.
• Trường "Căn cứ": Đây là "mỏ vàng" để trích xuất quan hệ BASED_ON. Bạn có thể dùng citation_service.py để bóc tách các tham chiếu này.
Chiến lược 2: Semantic & Inferred Linking (Độ tin cậy 40-80%)
Khi không có mã định danh khớp hoàn toàn, hãy dùng trọng số để gợi ý liên kết:
• Overlap từ khóa: Nếu hai tài liệu có chung >70% từ khóa chuyên môn, hãy gắn nhãn is_suggested để con người duyệt.
• Thứ tự thời gian: Một văn bản "Báo cáo" thường sẽ là con của một văn bản "Quyết định" nếu chúng cùng phòng ban và báo cáo ra đời sau.
Chiến lược 3: Quy trình 2 bước để tối ưu hiệu năng
Thay vì tạo liên kết trực tiếp, hãy làm theo quy trình:
1. Bước 1: Cập nhật thông tin quan hệ vào cột JSONB metadata của tài liệu. Điều này giúp dữ liệu linh hoạt và dễ chỉnh sửa.
2. Bước 2: Chạy script Extract để đẩy các quan hệ từ JSONB vào bảng graph_edges. Bảng này sẽ giúp các truy vấn tìm kiếm đồ thị (như tìm cây phả hệ văn bản) chạy nhanh hơn gấp nhiều lần so với việc quét JSON.
Lời khuyên: Bạn nên bắt đầu bằng việc chạy một script kiểm tra (Enrichment) để tự động phân cấp tài liệu dựa trên tiêu đề và nội dung, sau đó mới tiến hành tạo các liên kết tự động.
Sơ đồ tư duy về Linking: Hãy tưởng tượng graph_documents là các nút thắt, và graph_edges chính là những sợi dây nối chúng lại. Việc tạo linking giống như việc bạn tìm các đầu dây tương ứng thông qua các "nhãn" (Task code, Law ID) để dệt thành một tấm lưới kiến thức bền chặt..

Dựa trên tài liệu thiết kế hệ thống GraphRAG cho PostgreSQL mà bạn đang triển khai, đây là giải thích chi tiết về mục đích và nội dung của từng bảng. Hệ thống này được thiết kế theo mô hình **Sandbox (cô lập hoàn toàn)** để bạn có thể thử nghiệm mà không làm ảnh hưởng đến dữ liệu tìm kiếm hiện tại.

### 1. Ý nghĩa và nội dung các bảng

| Tên bảng | Nội dung chứa gì? | Dùng làm gì? |
| --- | --- | --- |
| **`graph_documents`** | Bản sao (mirror) của `documents_metadata_v2` cộng với các trường phân cấp: `hierarchy_level` (0-3), `is_root_node`, `is_leaf_node`, `parent_count`, `child_count`. | Quản lý định danh tài liệu trong đồ thị, lưu trữ các chỉ số thống kê của node (như độ quan trọng, độ sâu) để truy vấn nhanh mà không cần scan bảng metadata gốc. |
| **`graph_edges`** | Thông tin về các liên kết giữa các node: `source_graph_doc_id`, `target_graph_doc_id`, `relation_type` (BASED_ON, AMENDS, SUPERSEDES), `confidence`, `context_snippet` (đoạn text trích dẫn). | Đây là xương sống của đồ thị, dùng để thực hiện các truy vấn đệ quy (Recursive CTE) để tìm các tài liệu liên quan, cấp trên hoặc cấp dưới. |
| **`graph_templates`** | Các khuôn mẫu quan hệ chuẩn (ví dụ: Quyết định cấp 3 luôn phải căn cứ vào Quy chế cấp 1). | Dùng để định nghĩa các cấu trúc đồ thị chuẩn cho từng loại nghiệp vụ, giúp tự động hóa việc tạo link khi import tài liệu mới. |
| **`graph_validation_rules`** | Các quy tắc logic: "Tài liệu cấp 3 không được tham chiếu trực tiếp cấp 0", "Không được có vòng lặp (A link B, B link A)". | Chứa các câu lệnh SQL kiểm tra tính nhất quán và toàn vẹn của dữ liệu trong đồ thị. |
| **`graph_validation_log`** | Nhật ký lỗi khi chạy các quy tắc validation: ID tài liệu vi phạm, ID rule, thông báo lỗi, trạng thái xử lý. | Theo dõi và giám sát chất lượng đồ thị, giúp Admin biết cần sửa tay những liên kết nào đang bị sai logic. |
| **`graph_changelog`** | Lịch sử thay đổi: loại thay đổi (thêm edge, đổi level), giá trị cũ, giá trị mới, người thực hiện. | Dùng để Audit (kiểm toán) dữ liệu, cho phép khôi phục lại trạng thái cũ nếu việc tạo link tự động hoặc thủ công bị sai. |

---

### 2. Hướng dẫn Hardlink Manual (Tạo liên kết thủ công)

Nếu bạn muốn tạo các liên kết "cứng" một cách thủ công, bạn cần thực hiện theo các bước sau với dữ liệu tương ứng:

#### Bước 1: Đồng bộ tài liệu vào `graph_documents`

Bạn không tạo trực tiếp link từ bảng cũ. Hãy chạy hàm đồng bộ để đưa tài liệu vào hệ thống đồ thị:

```sql
SELECT sync_document_to_graph('ID_CỦA_TÀI_LIỆU_GỐC');

```

* **Dữ liệu cần đưa vào:** Chỉ cần `source_document_id`. Các trường `law_id`, `title` sẽ tự động được lấy từ bảng metadata cũ sang.

#### Bước 2: Tạo liên kết trong `graph_edges`

Đây là bước quan trọng nhất để tạo "Hardlink". Bạn cần insert dữ liệu sau:

* **`source_graph_doc_id`**: ID của văn bản cấp thấp hơn (văn bản đi trích dẫn).
* **`target_graph_doc_id`**: ID của văn bản cấp cao hơn (văn bản được trích dẫn).
* **`relation_type`**: Đặt là `'BASED_ON'` (Căn cứ vào), `'AMENDS'` (Sửa đổi) hoặc `'SUPERSEDES'` (Thay thế).
* **`extraction_method`**: Đặt là `'manual'` để phân biệt với link tự động bằng AI/Regex.
* **`verified`**: Đặt là `true` vì bạn đang làm thủ công, độ tin cậy tuyệt đối.

```bash
LUAT_KHCN_2013 (Rank 0) ━━━━━━━━━━━━━━━━━┓
│                                        ┃
│                                        ▼
└─→ 654/TT-BKH (Rank 1)                 governing_laws
    │                                    
    └─→ QC-HDQLQ (Rank 2)               
        │
        ├─→ 654/QĐ-CTCT (Rank 3) ━━━━━━┳━━━ task_code: DTCT.2024.05
        │   │                          ┃
        │   └─→ QT-DTCT (Rank 4) ━━━━━━┫
        │       │                      ┃
        │       └─→ DA-DTCT-2024-05 ━━━┫
        │           │           (Rank 5)┃
        │           └─→ BC-DTCT-Q1 ━━━━┛
        │               (Rank 6)
        │
        └─→ 888/QĐ-KTQLB (Rank 3) ━━━━┳━━━ task_code: GPS-2025
            │                         ┃
            └─→ QT-NCPT (Rank 4) ━━━━┫
                │                     ┃
                └─→ DA-GPS-2025 ━━━━━┫
                    │         (Rank 5)┃
                    └─→ BC-GPS-TEST ━┛
                        (Rank 6)
```

theo sơ đồ này thì link phải có sẽ là QC-HDQLQ(source_graph_doc_id) base_on 654/TT-BKH(target_graph_doc_id), và 654/TT-BKH base_on LUAT_KHCN_2013 đúng không? các tài liệu còn lại cũng tương tự, dưới base_on trên, có đúng không? trả lời ngắn gọn trong chat
**Đúng 100%!** 

Đây chính xác là cấu trúc GraphRAG relationships:

### **1. Vertical Hierarchy (base_on):**
```
QC-HDQLQ.base_on → 654/TT-BKH
654/TT-BKH.base_on → LUAT_KHCN_2013
654/QĐ-CTCT.base_on → QC-HDQLQ
...
BC-DTCT-Q1.base_on → DA-DTCT-2024-05
```

**Rule:** `child.base_on = parent_id` (từ dưới lên trên)

---

### **2. Legal Governance (governing_laws):**
```
Tất cả docs Rank 3-6 → governing_laws = ["LUAT_KHCN_2013"]
```
**Rule:** Documents cấp thấp luôn reference về luật gốc (nét đứt trong sơ đồ)

---

### **3. Project Clustering (task_code):**
```
654/QĐ-CTCT, QT-DTCT, DA-DTCT-2024-05, BC-DTCT-Q1
→ Cùng task_code: "DTCT.2024.05"
```
**Rule:** Nhóm documents thuộc cùng dự án/nhiệm vụ

---

### **Metadata Implementation:**

```json
// BC-DTCT-Q1 (Rank 6)
"hierarchy": {
  "parent_id": "DA-DTCT-2024-05",      // base_on relationship
  "root_id": "LUAT_KHCN_2013",         // trace to top
  "path": "0/1/2/3/5/6"
}

"governance": {
  "governing_laws": ["LUAT_KHCN_2013"], // Legal reference
  "implements": "DA-DTCT-2024-05"       // Direct parent
}

"graph_context": {
  "related_projects": ["DTCT.2024.05"], // Project cluster
  "related_documents": [                // Siblings
    "654/QĐ-CTCT",
    "QT-DTCT", 
    "DA-DTCT-2024-05"
  ]
}
```

**Bạn hiểu hoàn toàn đúng cấu trúc!** 👍


#### Bước 3: Cập nhật Level trong `graph_documents` (Quan trọng)

Để graph hoạt động hiệu quả, bạn nên gán cấp bậc cho tài liệu:

* **Level 0**: Điều lệ, Luật (Gốc).
* **Level 1**: Quy chế, Quy định.
* **Level 2**: Kế hoạch năm.
* **Level 3**: Quyết định thực thi cụ thể.

#### Bước 4: Chạy kiểm tra (Validation)

Sau khi tạo link, hãy chạy các rule trong `graph_validation_rules` để đảm bảo link bạn vừa tạo không tạo ra vòng lặp vô tận (circular reference) hoặc vi phạm logic cấp bậc.

Dưới đây là “vai trò chuẩn” của 6 bảng bạn nêu trong một **GraphRAG chạy trên PostgreSQL** (kiểu “GraphRAG lite”/module graph tách riêng), đặc biệt phù hợp cho bài toán **linking giữa các tài liệu** (legal docs / SOP / dự án…). 

---

## 1) `graph_documents` — “node table” (mỗi tài liệu = 1 node)

**Nên chứa gì**

* **Khóa chính**: `graph_doc_id` (UUID)
* **Liên kết về bảng gốc**: `source_document_id` (UUID) trỏ về `documents_metadata_v2(document_id)` hoặc bảng documents gốc của bạn
* **Các field cache để query nhanh** (đỡ phải join/parse JSONB liên tục):

  * `law_id` / `doc_number`, `title`, `doc_type`, `department`, `issue_date`
  * `task_code`/`project_code` (nếu có)
* **Hierarchy / phân cấp** (nếu bạn dùng):

  * `hierarchy_level`, `hierarchy_level_name`
  * `auto_classified_level`, `auto_classification_confidence`
* **Trạng thái biên tập**:

  * `manual_review_status` (`pending/reviewed/approved`)
  * `reviewed_by`, `reviewed_at`
* **Metadata mở rộng**: `metadata JSONB`

**Dùng làm gì**

* Là “sổ hộ khẩu” cho tất cả node trong graph.
* Là điểm neo để **resolve** mọi thứ: từ `task_code/law_id` ra `graph_doc_id`.
* Hỗ trợ thống kê (parent_count/child_count), lọc theo level, department, tags.

---

## 2) `graph_edges` — “edge table” (mỗi quan hệ = 1 cạnh)

**Nên chứa gì**

* **Khóa chính**: `edge_id` (UUID)
* **FK**: `source_graph_doc_id`, `target_graph_doc_id` (trỏ `graph_documents`)
* **Quan hệ**:

  * `relation_type` (vd: `BASED_ON`, `IMPLEMENTS`, `AMENDS`, `SUPERSEDES`, `REFERS_TO`, `RELATES_TO`, `CONFLICTS`)
* **Bằng chứng & độ tin cậy** (cực quan trọng để tránh link “ảo”):

  * `context_snippet` (đoạn text chứa reference)
  * `page_number`/`chunk_id` (nếu biết)
  * `confidence` (0–1)
  * `extraction_method` (`manual/regex/ml/suggested`)
  * `is_suggested`, `verified`, `verified_by`, `verified_at`
* **Chống trùng**: unique `(source_graph_doc_id, target_graph_doc_id, relation_type)`
* (Tuỳ chọn) cache: `source_law_id`, `target_law_id` để debug/query nhanh

**Dùng làm gì**

* Đây là bảng “ăn tiền” cho **linking** + **graph traversal** (Recursive CTE).
* Cho phép tách bạch:

  * edge tự động tạo (regex/ML) nhưng **chưa chắc đúng** → `is_suggested=true`
  * edge đã được người duyệt → `verified=true`
* Cho phép audit, scoring, và “đảo chiều” (incoming/outgoing).

---

## 3) `graph_templates` — “mẫu cấu trúc graph / pattern”

**Nên chứa gì**

* `template_id`, `template_name`, `description`
* `pattern_type` (vd: `hierarchy`, `workflow`, `regulatory`)
* `template_structure JSONB` mô tả:

  * các level / loại doc mong đợi
  * các cạnh bắt buộc (vd level 3 phải `BASED_ON` level 0/1/2)
* `usage_count`, `created_by`, timestamps

**Dùng làm gì**

* Là “khuôn” để:

  * gợi ý parent/edge cho tài liệu mới
  * validate completeness theo template
  * tạo UI “wizard”: chọn template → hệ thống gợi ý các link cần có

---

## 4) `graph_validation_rules` — “rule definitions”

**Nên chứa gì**

* `rule_id`, `rule_name`, `rule_type` (`hierarchy/completeness/consistency`)
* `rule_query` (SQL trả về các vi phạm) **hoặc** một “rule DSL” (nhưng SQL thường đủ)
* `severity` (`error/warning/info`)
* `auto_fix_available`, `auto_fix_query` (nếu có thể tự sửa)
* `is_active`, `created_at`

**Dùng làm gì**

* Chuẩn hoá chất lượng graph:

  * **No cycles** (không vòng lặp)
  * **Level constraints** (cấp thấp không được “căn cứ” cấp thấp hơn, tuỳ logic)
  * **Completeness** (vd “Level 3 phải tham chiếu ít nhất 1 Level 0”)
* Dùng để chạy batch validation sau mỗi lần import/extract edges.

---

## 5) `graph_validation_log` — “rule violations / kết quả kiểm tra”

**Nên chứa gì**

* `log_id`, `rule_id`
* “đối tượng bị lỗi”:

  * `affected_graph_doc_id` hoặc `affected_edge_id`
* `violation_type`, `violation_message`
* `status` (`open/fixed/ignored`)
* `resolved_by`, `resolved_at`, `resolution_notes`
* `created_at`

**Dùng làm gì**

* Là **backlog** cho người curate:

  * lọc `open` để xử lý
  * track ai sửa, sửa khi nào
* Cực hữu ích nếu bạn có UI: “Validation inbox”.

---

## 6) `graph_changelog` — “audit trail mọi thay đổi”

**Nên chứa gì**

* `change_id`
* `change_type` (`doc_added`, `edge_created`, `edge_deleted`, `edge_updated`, `level_changed`, …)
* `entity_type` (`document/edge`), `entity_id`
* `old_value JSONB`, `new_value JSONB` (snapshot trước/sau)
* `changed_by`, `change_reason`
* `created_at`

**Dùng làm gì**

* Debug “vì sao graph sai”: ai tạo edge này, từ đâu, lúc nào.
* Hỗ trợ rollback logic (ít nhất là rollback “bằng tay” dựa trên old/new).

---

# Gợi ý thực dụng để bạn “linking được ngay” (tránh đau đầu)

1. **Tách “suggested edges” và “verified edges”** ngay từ đầu
   → `is_suggested` + `verified` trong `graph_edges` giúp bạn không bị nhiễu khi traverse.

2. **Luôn lưu evidence** (context_snippet + pointer chunk/page)
   → sau này bạn sẽ cảm ơn mình khi cần duyệt link.

3. **Index tối thiểu cho traversal**

* `graph_edges(source_graph_doc_id)`
* `graph_edges(target_graph_doc_id)`
* `graph_edges(relation_type)`
* (nếu hay query theo type+source) index composite `(source_graph_doc_id, relation_type)`

---

Nếu bạn nói rõ “khó khăn khi tạo linking” là:

* **khó resolve target** (ví dụ chỉ có `265/2025/NĐ-CP` nhưng chưa map ra doc_id), hay
* **bị trùng edge / nổ vòng lặp / traverse chậm**,

mình sẽ đưa luôn chiến lược cụ thể (schema + SQL/CTE) tương ứng.
Nếu bạn muốn **hardlink manual** (tức là “tôi chọn A ↔ B, lưu thẳng vào graph và coi như đúng”), thì bạn chỉ cần ghi **tối thiểu** vào 2 bảng: **`graph_documents`** (đảm bảo A/B tồn tại như node) và **`graph_edges`** (tạo cạnh). Các bảng còn lại (`graph_changelog`, `graph_validation_*`, `graph_templates`) là “hạ tầng” để audit/kiểm tra/quy chuẩn—không bắt buộc để link chạy, nhưng nên ghi để về sau không mù thông tin.

Dưới đây là checklist “bạn cần đưa gì” cho từng bảng khi làm hardlink manual.

---

## 1) `graph_documents` — bạn phải có node cho cả 2 tài liệu

### Bạn cần insert gì?

**Tối thiểu**

* `graph_doc_id` (UUID)
* `source_document_id` (id của tài liệu trong hệ thống/bảng gốc)
* (tuỳ schema) `title` hoặc `doc_number` để debug

**Nên có**

* `doc_type`, `law_id`/`doc_number`, `issue_date`
* `hierarchy_level` (nếu bạn có phân cấp)
* `manual_review_status='approved'` hoặc tương đương

👉 Nếu tài liệu đã tồn tại trong `graph_documents` thì **không insert nữa**, chỉ dùng lại `graph_doc_id`.

---

## 2) `graph_edges` — đây là “hardlink” thật sự

### Bạn cần insert gì?

**Tối thiểu**

* `edge_id` (UUID)
* `source_graph_doc_id` (graph_doc_id của tài liệu A)
* `target_graph_doc_id` (graph_doc_id của tài liệu B)
* `relation_type` (loại quan hệ bạn chọn)

**Nên có (rất nên để khỏi hối hận)**

* `extraction_method='manual'`
* `verified=true` (vì bạn hardlink)
* `is_suggested=false`
* `confidence=1.0`
* `context_snippet` (lý do/ngữ cảnh: “Theo mục 2.1 SOP-23, tài liệu này căn cứ…”)
* `created_by` / `verified_by`, `verified_at`
* unique constraint để tránh trùng:

  * `(source_graph_doc_id, target_graph_doc_id, relation_type)`

> Thực tế vận hành: nhiều đội còn thêm `note`/`justification` để reviewer sau đọc là hiểu ngay.

---

## 3) `graph_changelog` — log lại thao tác hardlink (khuyến nghị)

### Bạn cần insert gì?

**Tối thiểu (để audit)**

* `change_id`
* `change_type='edge_created'`
* `entity_type='edge'`
* `entity_id=edge_id`
* `new_value` (JSONB chứa source/target/relation_type + metadata manual)
* `changed_by`
* `created_at`

**Dùng để làm gì khi manual?**

* Sau này có tranh cãi “ai link cái này”, “link từ lúc nào”, “vì sao”.

---

## 4) `graph_validation_rules` — không cần đụng khi manual (trừ khi bạn tự định nghĩa rule)

Nếu bạn mới hardlink, bạn **không cần insert gì** vào đây.

* Bảng này chỉ lưu “luật kiểm tra” kiểu: cấm cycle, bắt buộc có parent, v.v.

---

## 5) `graph_validation_log` — chỉ ghi khi bạn chạy validation và phát hiện lỗi

Manual link xong, nếu bạn chạy validation mà phát hiện vi phạm:

* cycle
* link sai level
* thiếu edge bắt buộc
  …thì mới insert log.

**Tối thiểu khi có vi phạm**

* `log_id`, `rule_id`
* `affected_edge_id` (hoặc `affected_graph_doc_id`)
* `violation_message`
* `status='open'`
* `created_at`

---

## 6) `graph_templates` — không cần đụng khi manual (trừ khi bạn dùng template để gợi ý/validate)

Manual hardlink “tay đôi” thì thường **không insert gì** vào đây.

---

# Bộ dữ liệu tối thiểu để “manual hardlink chạy được ngay”

Bạn chỉ cần đảm bảo:

1. `graph_documents` có 2 dòng (A và B)

* có `graph_doc_id_A`, `graph_doc_id_B`

2. `graph_edges` có 1 dòng

* `source_graph_doc_id=graph_doc_id_A`
* `target_graph_doc_id=graph_doc_id_B`
* `relation_type='...'`
* gợi ý set: `verified=true, extraction_method='manual', confidence=1.0`

(Optional nhưng nên) 3) `graph_changelog` ghi 1 dòng “edge_created”.

---

# Một “mẫu” hardlink bạn có thể follow (không phụ thuộc schema chi tiết)

**Ví dụ bạn muốn:** A *BASED_ON* B

* A = “Quy trình xử lý sự cố”
* B = “Nghị định/Policy gốc”

Bạn sẽ ghi:

* `graph_documents`: đảm bảo A/B tồn tại
* `graph_edges`: `{A_id, B_id, relation_type='BASED_ON', verified=true, extraction_method='manual', context_snippet='Hardlink by reviewer: ...'}`
* `graph_changelog`: snapshot new_value

---

Nếu bạn paste nhanh **schema hiện tại** (cột của `graph_documents` và `graph_edges` của bạn), mình sẽ viết luôn **SQL INSERT/UPSERT chuẩn** đúng cột của bạn (kèm constraint + index để tránh trùng và để traverse nhanh).


Nếu chỉ nhìn theo **6 bảng bạn liệt kê** (`graph_changelog`, `graph_documents`, `graph_edges`, `graph_templates`, `graph_validation_log`, `graph_validation_rules`) thì:

* ✅ **Bạn đã đủ để “vận hành graph layer”**: lưu node, lưu edge, audit thay đổi, có rule + log để kiểm tra chất lượng.
* ❌ Nhưng để **“vận hành GraphRAG end-to-end”** (truy hồi + mở rộng theo graph + trả lời có citation) thì còn phụ thuộc bạn đã có (hoặc cần bổ sung) vài mảnh ghép khác ngoài 6 bảng này.

Mình đánh giá theo 3 mức:

---

## A) Bạn đã vận hành được “Graph” ở mức nào?

### 1) Manual hardlink & traverse cơ bản: **CÓ** (nếu đáp ứng các điều kiện dưới)

Bạn **vận hành graph** được nếu:

* `graph_documents` có đủ node cho các tài liệu cần liên kết (ít nhất có `graph_doc_id` + tham chiếu về doc gốc).
* `graph_edges` có edge với:

  * `source_graph_doc_id`, `target_graph_doc_id`, `relation_type`
  * có index theo `source`, `target` (rất quan trọng để CTE chạy nhanh)
  * có unique chống trùng cạnh theo `(source, target, relation_type)` (khuyến nghị mạnh)
* Có thể chạy được recursive query kiểu:

  * “lấy tất cả văn bản căn cứ của A trong N hops”
  * “lấy tất cả văn bản bị sửa đổi bởi A”

=> Với đúng 2 bảng `graph_documents` + `graph_edges` là bạn đã **link được và đi graph được**.

### 2) Graph “đáng tin” để dùng trong RAG: **CÓ / CHƯA** tuỳ bạn có các cột/logic này chưa

Để graph không làm RAG “ảo giác”, bạn cần thêm/đảm bảo trong `graph_edges`:

* phân biệt `is_suggested` vs `verified` (hoặc 1 cột trạng thái tương đương)
* có `confidence`
* có `evidence` (snippet + trỏ tới chunk/page/section)
* có metadata ai duyệt / duyệt lúc nào

Nếu bạn chưa có các thứ này, graph vẫn chạy, nhưng GraphRAG sẽ dễ:

* mở rộng sang tài liệu không liên quan
* kéo nhầm “căn cứ” vì edge yếu
* khó debug vì không có bằng chứng

---

## B) 6 bảng này đã đủ cho “GraphRAG” chưa?

### Kết luận nhanh

**Chưa thể khẳng định “đủ GraphRAG” chỉ dựa vào 6 bảng này**, vì GraphRAG cần thêm ít nhất 3 khối chức năng/bảng dữ liệu nữa:

1. **Corpus retrieval layer**

* Bảng chunks (hoặc đoạn văn) + mapping chunk → document
* Embeddings / vector index (pgvector) hoặc cơ chế search khác

2. **Graph expansion policy**

* Quy tắc mở rộng: hop limit, relation whitelist/blacklist, threshold confidence, verified-only, v.v.
* Cái này có thể đặt trong code hoặc lưu rule/config trong DB (không bắt buộc bảng riêng, nhưng phải có)

3. **Citation grounding**

* Khi trả lời, bạn phải trỏ được về **chunk_id / page / đoạn** để làm citation.
* Nếu edge chỉ trỏ document mà không trỏ tới evidence chunk/page, bạn vẫn làm RAG được nhưng citation sẽ yếu.

👉 Nói cách khác: **6 bảng này đủ để quản lý graph**, nhưng GraphRAG “chạy ngon” còn cần **chunks + embeddings + orchestration**.

---

## C) Checklist “đủ để chạy GraphRAG ổn định” (bạn tự đối chiếu nhanh)

### 1) Tối thiểu để chạy end-to-end

* [ ] Có bảng **documents** (metadata) và **chunks** (nội dung chia đoạn)
* [ ] Có **vector search** (pgvector) hoặc hybrid search hoạt động
* [ ] `graph_documents` map được 1-1 (hoặc 1-n) với tài liệu gốc
* [ ] `graph_edges` có relation_type rõ ràng + index tốt
* [ ] Trong pipeline query: retrieve → graph expand → re-rank/merge → generate answer

### 2) Để không “link sai làm hỏng RAG”

* [ ] `graph_edges` có `verified` hoặc status rõ ràng
* [ ] Có `confidence` + threshold
* [ ] Có `evidence` trỏ được tới chunk/page
* [ ] Có rule chống vòng lặp / hop limit

### 3) Để vận hành như sản phẩm

* [ ] `graph_validation_rules` có rule cơ bản (no cycles, no self-loop, unique edge…)
* [ ] `graph_validation_log` dùng được để mở “inbox lỗi”
* [ ] `graph_changelog` ghi lại thay đổi manual (ai sửa edge nào)

---

## Gợi ý hành động ngay (không cần thêm bảng mới nếu bạn đã có chunks/embeddings)

1. Chạy 2–3 truy vấn kiểm tra “graph đủ chất lượng”:

* % edge có `verified=true`
* % edge có evidence (snippet + chunk/page)
* số lượng cycle (nếu có) / self-loop
* độ phân bố degree (node nào degree quá cao bất thường)

2. Thiết lập policy mở rộng trong GraphRAG:

* mặc định **verified-only**
* hop=1 hoặc 2
* whitelist relation: `BASED_ON`, `AMENDS`, `SUPERSEDES`, `REFERS_TO` (tuỳ domain)
* confidence ≥ 0.8 (tuỳ bạn)

---

Nếu bạn paste **DDL (CREATE TABLE)** của 6 bảng này (hoặc ít nhất là cột của `graph_documents` và `graph_edges`) + cho mình biết bạn đã có bảng **chunks/embeddings** chưa (tên bảng cũng được), mình sẽ trả lời dứt khoát:

* “Bạn đã đủ chạy GraphRAG chưa”
* thiếu đúng những cột/index nào
* và đề xuất query/CTE + policy mở rộng hợp lý để linking không bị “nhiễu”.

Đúng — nếu bạn có **rule check metadata của doc** thì bước linking sẽ “dễ thở” hơn rất nhiều, vì bạn biến một phần vấn đề từ *“AI/regex đoán xem có liên quan không”* thành *“lọc theo điều kiện chắc chắn trước, rồi mới link”*.

Cụ thể nó giúp 3 chuyện lớn:

1. **Giảm không gian tìm kiếm (candidate set)**
   Thay vì A có thể link với hàng ngàn doc, bạn chỉ cho phép link trong nhóm “hợp lệ” theo metadata.

2. **Giảm link sai / link rác**
   Edge tự động thường sai vì doc giống từ khóa. Metadata rule chặn các case “không thể đúng” (khác loại văn bản, sai thời gian, sai scope…).

3. **Dễ debug và review**
   Validation log sẽ nói rõ: “Doc A thiếu law_id” hay “issue_date > effective_date” → sửa metadata trước khi link.

---

## Nên kiểm metadata theo 2 lớp: “Doc-level” và “Edge-level”

### A) Doc-level rules (mỗi document tự nó có hợp lệ không?)

Ví dụ rule “bắt buộc”:

* `doc_number`/`law_id` **không được null**
* `doc_type` thuộc tập cho phép (enum)
* `issue_date` hợp lệ (không ở tương lai, không null)
* `hierarchy_level` không null (nếu bạn dùng phân cấp)
* `department`/`owner` không null (nếu dùng để routing)

Ví dụ rule “mềm” (warning):

* title quá ngắn
* thiếu tags/keywords
* level auto_classified_confidence thấp

**Lợi ích:** doc “bẩn metadata” sẽ được đưa vào `graph_validation_log` để sửa trước, tránh link bừa.

---

### B) Edge-level rules (2 doc link với nhau có hợp logic không?)

Đây là phần giúp bạn “dễ thở” nhất khi hardlink/suggest link:

Ví dụ:

* **Cấm self-loop**: A không được link A
* **Cấm cycle** trong các relation kiểu parent/BASED_ON
* **Constraint theo type**:

  * `SOP` chỉ được `BASED_ON` `POLICY/LAW`, không được `BASED_ON` `SOP`
* **Constraint theo level**:

  * level 3 chỉ được `BASED_ON` level 0/1/2
* **Constraint theo thời gian**:

  * nếu relation `AMENDS/SUPERSEDES` thì `issue_date(source) >= issue_date(target)` (tuỳ định nghĩa)
* **Constraint theo scope**:

  * khác `law_id` thì chỉ cho `REFERS_TO`, không cho `BASED_ON` (tuỳ domain)

**Lợi ích:** bạn có thể auto-generate candidate edges rồi để rule gạn lọc, reviewer chỉ xem “đống đã qua rule”.

---

## Bạn có thể triển khai rule check metadata bằng chính 2 bảng bạn đã có

* `graph_validation_rules`: lưu SQL query kiểm tra
* `graph_validation_log`: lưu các bản ghi vi phạm

### Mẫu rule kiểu “doc thiếu field bắt buộc”

Ý tưởng: `rule_query` trả về danh sách `graph_doc_id` vi phạm + message.

Ví dụ (logic):

* Rule: “doc_number không được null”
* Query trả về mọi doc có `doc_number is null`

Sau đó pipeline chạy rule → insert vào `graph_validation_log`.

---

## Gợi ý 5 rule metadata “đáng làm ngay” (ROI cao)

1. **doc identity đầy đủ**: `doc_number/law_id/title` không null
2. **doc_type hợp lệ**: nằm trong set chuẩn
3. **hierarchy_level hợp lệ**: không null + không vượt giới hạn
4. **issue_date hợp lệ**: không null và không ở tương lai
5. **edge compatibility theo doc_type + level** (edge-level)

Chỉ 5 rule này thôi là chất lượng link thường cải thiện thấy rõ.

---

## Mẹo vận hành: đừng để rule thành “cục đá chặn đường”

* severity = `warning` cho các field “đẹp thì tốt” (tags, department…)
* severity = `error` cho các field “thiếu là link sai” (doc_number/law_id/doc_type/issue_date)
* linking pipeline mặc định:

  * `error` → không cho tạo edge suggested
  * `warning` → vẫn cho nhưng đánh `is_suggested=true` và giảm confidence

---

Nếu bạn nói cho mình metadata hiện bạn có những cột nào trong `graph_documents` (vd: `doc_number`, `law_id`, `doc_type`, `issue_date`, `department`, `hierarchy_level`…), mình sẽ đề xuất luôn **bộ rule SQL cụ thể** phù hợp + cách ghi vào `graph_validation_log` để bạn chạy batch mỗi lần ingest.


