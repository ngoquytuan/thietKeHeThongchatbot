Đây là bản thiết kế **Master Flat Metadata Schema** được tôi tinh lọc từ cả hai bản JSON của bạn (NLP/Regex-based và LLM-generated).

Thiết kế này tuân thủ nguyên tắc: **Một bộ khóa duy nhất (Single Source of Truth)**. Bạn có thể lưu toàn bộ vào cột JSONB của PostgreSQL, và khi đẩy vào ChromaDB, bạn chỉ cần lọc bỏ các trường quá dài (như description hoặc summary) để tối ưu hiệu năng.

### 1. Master Flat JSON Schema (Đề xuất)

```json
{
  "doc_id": "4b9dd4c8-a889-4b49-beb7-925b2abc8d21",
  "doc_number": "01/2025/TTGV-NCPT",
  "title": "Thỏa thuận giao việc thực hiện chế tạo sản phẩm mẫu đồng hồ thời gian chuẩn sử dụng GPS",
  "doc_type": "thoa_thuan_giao_viec",
  "doc_group": "LEGAL_RND",
  "department": "Phòng Nghiên cứu phát triển",
  "organization": "Công Ty TNHH Kỹ Thuật Quản Lý Bay",
  "access_level": "public",
  "status": "active",
  
  "issue_date": "2025-10-06",
  "issue_date_int": 20251006,
  "year": 2025,
  "month": 10,
  
  "signer": "Nguyễn Hoàng Giang, Ngô Quý Tuấn",
  "budget": 102876204.0,
  "currency": "VND",
  
  "parent_id": "654/QĐ-CTCT",
  "rank_level": 3,
  "is_derived": true,
  
  "language": "vi",
  "page_count": 3,
  "chunk_size": 256,
  
  "tags": "thỏa thuận giao việc, chế tạo sản phẩm mẫu, quỹ phát triển KH&CN, LED hiển thị",
  "summary_short": "Thỏa thuận giao việc chế tạo đồng hồ GPS giữa Quỹ KH&CN và ATTECH ký ngày 06/10/2025.",
  
  "source_system": "attech_dms",
  "ingested_at": 1707865232
}

```

---

### 2. Phân tích các thay đổi "đắt giá"

| Nhóm trường | Tên trường mới | Lý do lựa chọn & Tinh chỉnh |
| --- | --- | --- |
| **Thời gian** | `issue_date_int` | Chuyển từ ISO `2025-10-06T00:00:00Z` sang `20251006` (Integer). Giúp bạn filter `$gte` / `$lte` trong ChromaDB cực nhanh. |
| **Phân loại** | `doc_type` | Lấy từ `identification.document_type`. Nếu null, dùng `doc_type_group` để fallback. |
| **Quyền hạn** | `access_level` | Giữ nguyên từ bản LLM vì nó đã được chuẩn hóa (public/internal). |
| **Danh mục** | `tags` | **Flatten Array**: Thay vì để mảng `["tag1", "tag2"]`, ta gộp thành chuỗi cách nhau bởi dấu phẩy. ChromaDB không lọc tốt trong Array, nhưng lọc String chứa từ khóa thì ổn. |
| **Mối quan hệ** | `parent_id` & `rank_level` | Lấy từ nhóm `hierarchy`. Đây là chìa khóa để bạn xây dựng Graph-RAG sau này. |
| **LLM Insights** | `summary_short` | Lấy từ `_llm_summary` nhưng cắt ngắn lại. Dùng để hiển thị nhanh kết quả tìm kiếm cho user mà không cần load toàn bộ văn bản. |

---

### 3. Hướng dẫn Map dữ liệu (Logic Code)

Khi bạn viết script Python để gộp 2 bản JSON này, hãy áp dụng logic ưu tiên sau:

1. **Định danh:** Luôn ưu tiên `document_id` từ bản JSON NLP (thường là UUID hệ thống).
2. **Ngày tháng:** Dùng thư viện `dateutil` để parse `issue_date`.
* Nếu có dạng ISO (JSON 1): Parse bình thường.
* Nếu có dạng DD/MM/YYYY (JSON 2): Convert về YYYY-MM-DD.


3. **Hành chính:** `signer` nên gộp từ bản LLM vì nó thường trích xuất tên người sạch hơn regex.
4. **Tài chính:** Lấy từ nhóm `financial` của JSON 1 (độ chính xác số học cao hơn LLM).

### 4. Cách dùng cho từng Database

* **Tại PostgreSQL:** Lưu toàn bộ bản Flat JSON này vào một cột `metadata` (kiểu `JSONB`). Bạn có thể tạo **GIN Index** trên cột này để query mọi trường.
* **Tại ChromaDB:** * **Giữ lại:** Các trường ID, Date_int, Dept, Type, Rank, Access_level (để Filter).
* **Loại bỏ:** `summary_short`, `title` (nếu quá dài), `currency` (nếu không định search theo tiền). Việc này giúp Vector Database chạy nhẹ hơn.



Bạn có muốn tôi viết một đoạn code Python mẫu để "merge" tự động 2 bản JSON trên thành bản Flat này không?

Would you like me to write a Python script to automate the merging of these two JSON files into the proposed flat structure?


Dưới đây là **một thiết kế JSON “flat”** (ưu tiên dùng chung cho **PostgreSQL** và **Chroma**). Ý tưởng:

* Các trường hay query/filter → để **scalar** (string/number/bool).
* Các trường nhiều phần tử / cấu trúc (list/object) → gom vào **`*_json`** (bạn lưu **JSONB** trong PostgreSQL; với Chroma thì bạn có thể lược bỏ hoặc stringify tùy chiến lược).

```json
{
  "document_id": "4b9dd4c8-a889-4b49-beb7-925b2abc8d21",
  "version": "3.0",
  "version_origin": "regex|llm|merged",
  "generated_by": "LLM (OpenRouter)",
  "doc_type_group": "LEGAL_RND",

  "title": "Thỏa thuận giao việc thực hiện chế tạo sản phẩm mẫu đồng hồ thời gian chuẩn sử dụng GPS",
  "description": "Thỏa thuận giao việc giữa Quỹ phát triển KH&CN và Công ty TNHH Kỹ thuật Quản lý bay về nhiệm vụ nghiên cứu, thiết kế, chế tạo đồng hồ GPS",

  "type": "quyet_dinh",
  "document_number": "01/2025/TTGV-NCPT",
  "issue_date": "2025-10-06T00:00:00Z",
  "subject": "Thực hiện Chế tạo sản phẩm mẫu thuộc Nhiệm vụ KH&CN Nghiên cứu, thiết kế, chế tạo đồng hồ thời gian chuẩn sử dụng GPS",
  "task_code": null,

  "organization": "Công Ty TNHH Kỹ Thuật Quản Lý Bay",
  "department": "Phòng Nghiên cứu phát triển",
  "signer": "Nguyễn Hoàng Giang (bên giao), Ngô Quý Tuấn (bên nhận)",
  "signer_title": null,

  "access_level": "public",

  "author_name": "Ngô quý tuấn",
  "author_email": "tuannq@attech.com",
  "author_created_at": "2026-02-13T23:00:32.830484Z",

  "budget": 102876204.0,
  "currency": "VND",
  "budget_source": "Ngân sách",

  "pages": 3,
  "words": 1506,
  "passages": 6,
  "total_tokens": 1530,
  "avg_tokens_per_passage": 255.0,
  "language": "vi",

  "quality_score": 1.0,
  "metadata_completeness": 93.3,
  "extraction_method": "nlp|llm|regex",
  "chunk_size": 256,

  "chromadb_collection": "kb_rnd_public",
  "collection_strategy": "auto_department",
  "fallback_collections_json": ["knowledge_base_general"],

  "source_file": "unknown",
  "created_at": "2026-02-13T23:00:32.830484Z",
  "extracted_at": "2026-02-13T23:00:32.830484Z",
  "last_updated": "2026-02-13T23:00:32.830484Z",

  "is_valid": true,
  "is_derived": true,
  "usage_instructions": null,

  "doc_number_custom": "01/2025/TTGV-NCPT",

  "keywords_json": ["chế tạo sản phẩm mẫu", "Quỹ phát triển KH&CN", "LED hiển thị"],
  "tags_json": ["thỏa thuận giao việc", "chế tạo sản phẩm mẫu", "quỹ phát triển KH&CN"],
  "boost_keywords_json": ["chế tạo sản phẩm mẫu", "Quỹ phát triển KHCN", "LED hiển thị"],

  "references_json": ["654/QĐ-CTCT", "324/QĐ-CTCT", "751/QĐ-CTCT", "443/QĐ-CTCT", "635/QĐ-HĐQLQ", "574/QĐ-HĐQLQ", "737/QĐ-CQĐHQ"],

  "relationships_json": {
    "based_on": ["654/QĐ-CTCT", "324/QĐ-CTCT", "751/QĐ-CTCT", "443/QĐ-CTCT", "635/QĐ-HĐQLQ", "574/QĐ-HĐQLQ", "737/QĐ-CQĐHQ"],
    "relates_to": ["2025/TTGV-NCPT"],
    "supersedes": null,
    "superseded_by": null
  },

  "rank_level": 3,
  "rank_label": "DIRECTOR_DECISION",
  "parent_id": "654/QĐ-CTCT",
  "root_id": "654/QĐ-CTCT",
  "path": null,

  "governing_laws_json": [],
  "execution_scope": "Phòng Nghiên cứu phát triển",
  "dependency_type": "DIRECT",

  "graph_referenced_by_json": [],
  "graph_implements": "654/QĐ-CTCT",
  "related_projects_json": ["Đồng Hồ GPS", "Đồng Hồ Thời Gian Chuẩn Sử Dụng GPS"],
  "related_people_json": ["Nguyễn Hoàng Giang (bên giao), Ngô Quý Tuấn (bên nhận)", "Nguyễn Hoàng Giang"],
  "related_technologies_json": ["Gps", "Led", "Đồng Hồ Gps"],
  "aviation_products_json": ["đồng hồ gps"],
  "aviation_tasks_json": ["Đồng hồ GPS"],
  "tag_keywords_json": ["Thực", "hiện", "phẩm", "thuộc", "Nhiệm", "KH&CN", "Nghiên", "thiết", "đồng", "thời"],

  "recipients_primary_json": [],
  "recipients_cc_json": [],

  "searchable_text": "",

  "llm_summary": "Thỏa thuận giao việc giữa Quỹ phát triển KH&CN và Công ty TNHH Kỹ thuật Quản lý bay về việc thực hiện chế tạo sản phẩm mẫu đồng hồ thời gian chuẩn sử dụng GPS...",
  "llm_main_topics_json": ["Thỏa thuận giao việc", "Chế tạo sản phẩm mẫu", "Đồng hồ GPS", "Nhiệm vụ KH&CN"],
  "llm_applicable_scope": "Áp dụng cho việc thực hiện nhiệm vụ nghiên cứu, thiết kế, chế tạo đồng hồ thời gian chuẩn sử dụng GPS tại Công ty TNHH Kỹ thuật Quản lý bay",
  "llm_note": "This row may contain merged metadata from regex/nlp and llm sources."
}
```

### Lý do chọn như vậy (ngắn gọn, để bạn dùng ngay)

* **PostgreSQL**:

  * Các trường `*_json` bạn map sang **JSONB** (hoặc TEXT nếu muốn stringify).
  * Các trường scalar map sang cột thường để index/filter nhanh (`document_number`, `issue_date`, `department`, `access_level`, `type`, `doc_type_group`, `chromadb_collection`, …).
* **Chroma**:

  * Bạn dùng subset: `document_id`, `title`, `description`, `type`, `department`, `access_level`, `document_number`, `issue_date`, `language`, `quality_score`, `chromadb_collection`, …
  * Các `*_json` nếu cần thì bạn tự **lược bỏ** hoặc chuyển sang chuỗi.

Nếu bạn muốn, mình có thể gợi ý luôn **mapping cột PostgreSQL** (DDL kiểu `CREATE TABLE ...` với JSONB + index) theo đúng JSON flat này.

