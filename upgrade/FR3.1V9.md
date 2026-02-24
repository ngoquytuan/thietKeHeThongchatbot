Mình đã đọc các bản metadata bạn gửi và thấy **metadata3 (golden/manual)** + **metadata4 (golden/manual LLM-lite)** là “nguồn chuẩn” tốt nhất cho các field lõi; **metadata2 (hybrid)** giàu chi tiết nhưng nhiều nhánh sâu → nên **đưa vào JSONB** để không phá schema hiện tại; **metadata1 (nlp)** có vài field hữu ích (deliverables dạng object + search_hints tốt) nhưng có sai lệch nhẹ về hierarchy/implements.    

Dưới đây là **JSON flat “chuẩn dùng chung”** (đủ để map vào `documents_metadata_v2` + dùng làm metadata cho Chroma; khi đưa vào Chroma bạn có thể lược bớt các `*_json` hoặc field ít dùng filter).

---

## 1) JSON flat đề xuất (canonical)

```json
{
  "document_id": "4b9dd4c8-a889-4b49-beb7-925b2abc8d21",
  "source_document_id": "TTGV01.2025/TTGV-NCPT",

  "title": "Thỏa thuận giao việc thực hiện chế tạo sản phẩm mẫu thuộc nhiệm vụ KH&CN đồng hồ thời gian chuẩn sử dụng GPS",
  "description": "Thỏa thuận giao việc số 01/2025/TTGV-NCPT ... Tổng giá trị: 102.876.204 VNĐ ... Hạn hoàn thành: 30/10/2025.",
  "content": null,

  "document_type": "thoa_thuan",
  "doc_type_group": "THOA_THUAN",
  "access_level": "public",
  "status": "draft",

  "department_owner": "Phòng Nghiên cứu Phát triển",
  "organization": "Công ty TNHH Kỹ thuật Quản lý bay",

  "author_name": "Ngô Quý Tuấn",
  "author_email": "tuannq@attech.com",
  "author_display": "Ngô Quý Tuấn <tuannq@attech.com>",

  "signer_display": "Nguyễn Hoàng Giang (Bên A - Giao việc), Nguyễn Anh Tuấn (Bên B - Phó trưởng phòng NCPT), Ngô Quý Tuấn (Bên B - Chủ nhiệm nhiệm vụ)",

  "document_number": "01/2025/TTGV-NCPT",
  "issue_date": "2025-10-06T00:00:00Z",
  "effective_date": "2025-10-06T00:00:00Z",
  "deadline_date": "2025-10-30",

  "subject": "Thực hiện Chế tạo sản phẩm mẫu thuộc Nhiệm vụ KH&CN \"Nghiên cứu, thiết kế, chế tạo đồng hồ thời gian chuẩn sử dụng GPS\"",
  "task_code": null,
  "project_code": "NCPT.GPS.2025",

  "language_detected": "vi",

  "pages": 3,
  "words": 1506,
  "passages": 6,
  "total_tokens": 1530,
  "avg_tokens_per_passage": 255.0,
  "chunk_size": 256,
  "chunk_count": 0,

  "quality_score": 1.0,
  "metadata_completeness": 98.0,
  "extraction_method": "golden_standard_manual",
  "generated_by": "Golden Standard (Manual)",
  "version": "3.0",

  "flashrag_collection": "kb_rnd_public",
  "chromadb_primary": "kb_rnd_public",

  "searchable_text": "thỏa thuận giao việc đồng hồ GPS thời gian chuẩn chế tạo sản phẩm mẫu LED phần mềm nhúng ...",
  "boost_keywords_json": ["đồng hồ GPS", "chế tạo sản phẩm mẫu", "thỏa thuận giao việc", "LED hiển thị"],
  "keywords_json": [
    "đồng hồ thời gian chuẩn GPS",
    "chế tạo sản phẩm mẫu",
    "LED 7 thanh",
    "LED ma trận",
    "phần mềm nhúng",
    "GPS",
    "nhiệm vụ KH&CN",
    "Quỹ phát triển KH&CN",
    "nguồn AC-DC",
    "nghiên cứu thiết kế chế tạo"
  ],
  "tags_json": [
    "thỏa thuận giao việc",
    "chế tạo sản phẩm mẫu",
    "đồng hồ GPS",
    "nhiệm vụ KH&CN",
    "quỹ phát triển KH&CN",
    "nghiên cứu phát triển"
  ],

  "references_json": ["654/QĐ-CTCT", "324/QĐ-CTCT", "751/QĐ-CTCT", "443/QĐ-CTCT", "635/QĐ-HĐQLQ", "574/QĐ-HĐQLQ", "737/QĐ-CQĐHQ"],

  "budget_total": 102876204.0,
  "budget_before_vat": 97482406.0,
  "vat_amount": 5393798.0,
  "currency": "VND",
  "budget_source": "Quỹ phát triển KH&CN",
  "budget_breakdown_json": [
    {"item": "Nhân công chế tạo phần cơ khí", "amount": 8689244.0},
    {"item": "Tiền thù lao tham gia chế tạo sản phẩm mẫu", "amount": 12307692.0},
    {"item": "Chi mua vật tư linh kiện chế tạo sản phẩm mẫu", "amount_before_vat": 67422480.0, "vat": 5393798.0, "amount_with_vat": 72816278.0},
    {"item": "Chi quản lý chung (5%)", "amount": 4420971.0},
    {"item": "Dự phòng phí (5%)", "amount": 4642019.0}
  ],

  "deliverables_json": [
    "01 đồng hồ GPS hiển thị LED 7 thanh treo tường sử dụng nguồn AC-DC",
    "01 đồng hồ GPS hiển thị LED ma trận treo tường sử dụng nguồn AC-DC",
    "01 đĩa lưu trữ phần mềm nhúng"
  ],
  "acceptance_unit": "Phòng Kỹ thuật An toàn Chất lượng",
  "copies": 4,

  "recipients_primary_json": ["Phòng Nghiên cứu Phát triển"],
  "recipients_cc_json": ["Phòng Kỹ thuật An toàn Chất lượng"],

  "rank_level": 5,
  "rank_label": "PROJECT",
  "parent_id": "737/QĐ-CQĐHQ",
  "root_id": "654/QĐ-CTCT",
  "path": "/654/QĐ-CTCT/635/QĐ-HĐQLQ/737/QĐ-CQĐHQ/01/2025/TTGV-NCPT",

  "implements": "737/QĐ-CQĐHQ",
  "related_people_json": ["Nguyễn Hoàng Giang", "Nguyễn Anh Tuấn", "Ngô Quý Tuấn"],
  "related_technologies_json": ["GPS", "LED 7 thanh", "LED ma trận", "phần mềm nhúng", "nguồn AC-DC"],
  "related_projects_json": ["Đồng hồ thời gian chuẩn sử dụng GPS", "Nhiệm vụ KH&CN chế tạo đồng hồ GPS"],

  "source_file": "TTGV01_2025_TTGV-NCPT_CT_SPM_NVKHCN_DonghoGPS_1.md",
  "file_format": "markdown",
  "file_size_bytes": null,

  "created_at": "2026-02-13T23:00:32.830484Z",
  "updated_at": "2026-02-15T00:00:00Z",

  "llm_summary": null,
  "llm_main_topics_json": null,
  "llm_applicable_scope": null,

  "raw_metadata_json": {}
}
```

**Nguồn field lõi** mình ưu tiên lấy theo bản “golden/manual”: `document_type=thoa_thuan`, `document_number`, `issue_date`, `keywords/tags`, `financial.*`, `hierarchy.*`, `search_hints.*`…  
Field `project_code` xuất hiện rõ ở bản nlp (custom_fields.project_code) nên mình giữ lại như scalar để filter. 

---

## 2) Map JSON flat → `documents_metadata_v2` (không cần đổi schema)

Bạn có schema hiện tại rất “bự” và đã có `metadata JSONB` để chứa phần dư. Vì vậy map đề xuất như sau:

### A) Ghi vào cột top-level (để index/filter/query nhanh)

* `document_id` ← `document_id`
* `source_document_id` ← `source_document_id`
* `title` ← `title`
* `content` ← `content` (nếu bạn lưu full text ở đây)
* `document_type` ← `document_type` (enum)
* `access_level` ← `access_level` (enum)
* `department_owner` ← `department_owner`
* `author` ← `author_display` *(hoặc chỉ author_name; nhưng 1 string hợp với schema hiện tại)*
* `status` ← `status`
* `language_detected` ← `language_detected`
* `flashrag_collection` ← `flashrag_collection`
* `chunk_count` ← `chunk_count`
* `file_size_bytes` ← `file_size_bytes`
* `original_file_info` ← JSONB: `{source_file,file_format,file_size_bytes}` (nếu muốn)
* `search_text_normalized` / `indexable_content` ← từ pipeline chuẩn hoá của bạn
* `extracted_emails`, `extracted_phones`, `extracted_dates` ← từ pipeline extractor hiện tại (nếu có)

### B) Nhét vào `metadata` (JSONB) – phần giàu ngữ nghĩa/đồ thị/quan hệ

Gợi ý: lưu **nguyên khối** tất cả field còn lại (đặc biệt các `*_json`, hierarchy/relationships/graph/financial breakdown/deliverables…). Điều này giúp Deep Validation Phase của bạn truy ngược dễ hơn mà không phải ALTER TABLE liên tục.

---

## 3) Vì sao “flat + *_json” hợp cả Postgres & Chroma

* Postgres: `*_json` = JSONB, dễ query với GIN nếu cần (vd `tags_json ? '...'`).
* Chroma: metadata filter thường ổn nhất với scalar; bạn chỉ giữ lại:

  * `document_number`, `issue_date`, `document_type`, `access_level`, `department_owner`, `chromadb_primary/flashrag_collection`, `project_code`, `budget_total`…
  * Còn `keywords_json/tags_json/references_json/budget_breakdown_json/...` bạn **lược bỏ** hoặc stringify tuỳ nhu cầu.

---

Nếu bạn muốn mình đi thêm 1 bước: mình có thể viết luôn **đoạn mapping mẫu (pseudo-code)** để convert từ các bản metadata nguồn (nlp/hybrid/golden) sang JSON flat canonical này theo rule “ưu tiên golden > hybrid > nlp > llm”, nhằm dùng cho Deep Validation Phase (triangulation) mà không bị loạn version.
