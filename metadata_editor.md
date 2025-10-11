

---

# 🧾 Handover Document — Metadata Editor & Retrieval System

**Tên dự án:** `metadata-editor`
**Phiên bản bàn giao:** 2025-10-08
**Tác giả:** đội phát triển nội bộ + ChatGPT hỗ trợ thiết kế kiến trúc
**Mục tiêu:** xây dựng hệ thống quản lý, chỉnh sửa và khai thác metadata tài liệu song song trên **PostgreSQL (BM25)** và **ChromaDB (Vector Store)**, làm nền cho hệ thống hỏi đáp (RAG – Retrieval-Augmented Generation).

---

## 1️⃣ Mục tiêu dự án

Hệ thống được phát triển nhằm:

* Cho phép **quản lý metadata tài liệu nội bộ** trong doanh nghiệp (HR, IT, Policy, Training...).
* **Đồng bộ song song** giữa hai cơ sở dữ liệu:

  * PostgreSQL → phục vụ BM25 full-text search.
  * ChromaDB → phục vụ semantic search (vector search).
* Cung cấp **API & UI** để:

  * Hiển thị, chỉnh sửa, tìm kiếm và đồng bộ metadata.
  * Làm nền tảng cho hệ thống **LLM Q&A reasoning** trong tương lai.

### 🎯 Kết quả đạt được

* Hệ thống chạy ổn định với FastAPI backend và giao diện quản lý đơn giản (HTML/JS).
* Dữ liệu PostgreSQL và ChromaDB được **đồng bộ hai chiều**, không mất dữ liệu.
* Metadata JSON được **lưu phẳng (flatten)** đúng chuẩn Chroma, không lỗi kiểu dữ liệu.
* Có cơ chế **Hybrid Search (BM25 + Semantic)** với filter theo metadata (`department`, `tags`, `access_level`).

---

## 2️⃣ Cấu trúc mã nguồn chính

```
metadata-editor/
├── backend/
│   ├── main.py                # FastAPI entrypoint
│   ├── config/                # Logging & Settings
│   ├── core/
│   │   └── database.py        # Kết nối PostgreSQL / ChromaDB
│   ├── services/
│   │   ├── postgres_service.py # Query BM25 và thao tác metadata SQL
│   │   ├── chroma_service.py   # Tương tác với ChromaDB (vector, metadata)
│   │   ├── sync_service.py     # Đồng bộ hai cơ sở dữ liệu (SQL ↔ Chroma)
│   ├── routers/
│   │   ├── collections.py     # API: danh sách collection, document
│   │   ├── documents.py       # API: xem, chỉnh sửa, lưu metadata
│   ├── models/
│   │   └── schemas.py         # Pydantic schemas (Document, MetadataUpdate,…)
│   └── logging.py             # Cấu hình log cho backend
│
├── frontend/
│   ├── templates/
│   │   ├── index.html         # Trang chính – danh sách collections
│   │   ├── documents.html     # Danh sách tài liệu trong collection
│   │   └── edit.html          # Giao diện chỉnh sửa metadata JSON
│   └── static/css/style.css   # Giao diện CSS
│
├── tests/
│   ├── scan_chroma_schema.py  # Quét cấu trúc metadata trong Chroma
│   ├── scan_postgres_metadata.py # Kiểm tra schema SQL
│   ├── test_04_api.py         # Test API endpoints
│   ├── semantic_search_with_filters.py # Script test search vector có filter
│   └── test_chromaDB.py       # Kiểm tra kết nối Chroma cơ bản
│
├── .env                       # Thông số kết nối DB
├── requirements.txt           # Thư viện Python cần thiết
├── Dockerfile                 # Docker hóa backend
└── README.md / handover_metadata.md
```

---

## 3️⃣ Mô tả chức năng chính

| Module                              | Chức năng                                                                                     |
| ----------------------------------- | --------------------------------------------------------------------------------------------- |
| **main.py**                         | Khởi động FastAPI, đăng ký router, khởi tạo kết nối DB                                        |
| **postgres_service.py**             | Thực hiện các truy vấn BM25 (`ts_rank_cd`), filter JSON metadata                              |
| **chroma_service.py**               | Cập nhật vector metadata, tìm kiếm theo cosine similarity                                     |
| **sync_service.py**                 | Khi người dùng lưu metadata → cập nhật đồng thời SQL & Chroma                                 |
| **collections.py**                  | API hiển thị danh sách collection và document theo phòng ban                                  |
| **documents.py**                    | API xem/sửa metadata chi tiết, nhận PUT update                                                |
| **scan_chroma_schema.py**           | Xuất toàn bộ metadata từ Chroma để so sánh với SQL                                            |
| **semantic_search_with_filters.py** | Test tìm kiếm ngữ nghĩa kèm filter theo metadata (`tags`, `access_level`, `department_owner`) |

---

## 4️⃣ Mô hình hoạt động tổng thể

```
User (Web UI)
   │
   ▼
FastAPI Backend
   ├── PostgresService  → BM25 Search
   ├── ChromaService    → Semantic Search
   └── SyncService      → Cập nhật metadata đồng bộ
   │
   ▼
Databases
   ├── PostgreSQL (documents_metadata_v2)
   └── ChromaDB (vector store)
```

**Workflow:**

1. Người dùng chỉnh sửa metadata trong UI.
2. FastAPI nhận JSON và gửi tới `SyncService`.
3. `SyncService`:

   * Cập nhật PostgreSQL (`metadata` JSONB).
   * Flatten metadata → cập nhật sang ChromaDB (`custom_*` keys).
4. Khi tìm kiếm, người dùng có thể gọi:

   * **BM25 search** (Postgres full-text).
   * **Semantic search** (Chroma vector).
   * **Hybrid search** kết hợp hai kết quả.

---

## 5️⃣ Điểm nổi bật

* 🧠 **Flatten JSON metadata chuẩn**: mọi dict/list được `json.dumps()` → lưu được cả trong Chroma.
* 🔍 **Hybrid Search**: kết hợp `semantic_weight` và `keyword_weight`.
* 🧩 **Auto Collection Detection**: tự tìm đúng collection chứa tài liệu khi đồng bộ.
* ⚙️ **Filter thông minh**: theo `department_owner`, `access_level`, `custom_tags`.
* 🧾 **Logging chi tiết**: ghi toàn bộ quá trình đồng bộ & tìm kiếm.
* 🧪 **Test script độc lập**: dễ kiểm tra từng tầng (DB, API, Semantic).

---

## 6️⃣ Hạn chế hiện tại

| Hạn chế                                         | Ảnh hưởng                                                                                      |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Chưa có LLM reasoning                           | Không trả lời được câu hỏi dạng phủ định hoặc suy luận logic (“điều nào không được thực hiện”) |
| Chưa có bảng liên kết tài liệu (document_links) | Chưa truy vấn được ảnh hưởng giữa các quy định                                                 |
| Chưa có reranker (ranking model)                | Hybrid search chưa tối ưu độ chính xác cuối                                                    |
| BM25 index chưa cập nhật tự động                | Cần chạy refresh khi thêm tài liệu mới                                                         |
| UI đơn giản                                     | Chưa có phân quyền hoặc giao diện người dùng nâng cao                                          |

---

## 7️⃣ Khả năng mở rộng

### 🚀 7.1 Kết hợp LLM cơ bản (Q&A Reasoning)

Thêm module `llm_reasoner.py`:

* Nhận input `user_query`.
* Gọi retriever (BM25 + Chroma).
* Xây dựng prompt theo template:

  ```
  Dựa trên nội dung sau, hãy trả lời câu hỏi nghiệp vụ.
  Nếu câu hỏi có dạng "điều nào KHÔNG được thực hiện", hãy liệt kê điều bị cấm.
  ```
* Gọi LLM (Qwen / GPT / Claude) để sinh câu trả lời cuối.

➡ Cho phép hệ thống hiểu được các câu hỏi nghiệp vụ logic, không chỉ truy hồi văn bản.

---

### 🧩 7.2 Danh mục nội dung (Domain / Category Routing)

Thêm trường `category` trong bảng `documents_metadata_v2`
→ giá trị: `hr`, `it`, `policy`, `training`, `general`.

Tích hợp router logic:

```python
def route_query(query):
    if "MikroTik" in query or "thiết bị" in query:
        return "it"
    if "nghỉ phép" in query or "phúc lợi" in query:
        return "hr"
    return "general"
```

LLM hoặc rule engine sẽ chọn collection phù hợp để **tăng tốc độ truy hồi và độ chính xác.**

---

### 🧮 7.3 Nghiệp vụ: “Điều nào dưới đây không được thực hiện?”

**Yêu cầu:** LLM reasoning layer.
Quy trình:

1. BM25 + Chroma → lấy top-n đoạn văn.
2. Prompt LLM:

   > “Dựa vào nội dung dưới đây, hãy xác định hành vi nào không được phép thực hiện.”
3. LLM phân tích logic phủ định, trích dẫn nội dung quy định.

→ Giúp hệ thống hiểu và trả lời câu hỏi phủ định hoặc kiểm tra tuân thủ.

---

### 📈 7.4 Nghiệp vụ: “Tăng lương cơ bản sẽ ảnh hưởng đến những quy định, hướng dẫn nào?”

**Yêu cầu:** bảng quan hệ `document_links` + LLM reasoning.

Bổ sung bảng:

```sql
CREATE TABLE document_links (
  source_id UUID,
  target_id UUID,
  relation_type VARCHAR, -- 'refer', 'impact', 'depend'
  confidence FLOAT
);
```

Quy trình:

1. Retriever tìm các văn bản có nội dung “lương cơ bản”.
2. Từ document_id đó, lấy danh sách tài liệu liên quan (`impact`, `depend`).
3. LLM tóm tắt chuỗi ảnh hưởng.

Ví dụ prompt:

```
Các quy định sau có thể bị ảnh hưởng bởi việc tăng lương cơ bản:
- Quy định chi trả lương
- Hướng dẫn đóng BHXH
- Quy trình tính thuế TNCN
```

---

## 8️⃣ Kiến trúc RAG định hướng mở rộng

```text
[ User Query ]
      │
      ▼
[ Query Router (domain/category) ]
      │
      ▼
[ Hybrid Retriever ]
   ├── PostgreSQL (BM25)
   └── ChromaDB (semantic)
      │
      ▼
[ LLM Reasoner ]
   ├── Trả lời câu hỏi phủ định
   ├── Phân tích ảnh hưởng (impact)
   └── Giải thích logic + trích dẫn nguồn
```

---

## 9️⃣ Kết luận bàn giao

✅ **Hệ thống hiện tại** đã:

* Quản lý metadata hiệu quả.
* Đồng bộ chính xác giữa PostgreSQL và ChromaDB.
* Cho phép tìm kiếm hybrid + filter theo metadata.

⚙️ **Có thể mở rộng nhanh chóng** để:

* Kết hợp LLM trả lời nghiệp vụ.
* Phân loại truy vấn theo danh mục (Domain Routing).
* Thực hiện các nghiệp vụ phân tích phủ định, quan hệ ảnh hưởng giữa quy định.

---

### 📦 Gợi ý triển khai tiếp theo

1. Tích hợp module `llm_reasoner.py` (sử dụng OpenAI/Qwen API).
2. Tạo bảng `document_links` để quản lý quan hệ “impact / depend”.
3. Bổ sung UI “Domain Routing” cho người dùng chọn lĩnh vực.
4. Viết unit test cho từng pipeline: retrieval, sync, reasoning.

---

**Tài liệu bàn giao kết thúc tại đây — phiên bản 2025-10-08.**
Hệ thống đã sẵn sàng cho giai đoạn **mở rộng sang RAG + nghiệp vụ phân tích chính sách doanh nghiệp.**

---

