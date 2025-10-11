

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

Tốt — mình đã đọc cả `handover2.md` và `handover_template.md`.
Dưới đây là phiên bản **`handover_metadata.md`** hoàn chỉnh theo đúng **chuẩn cấu trúc và định dạng của handover_template.md**,
nhưng đã **bổ sung nội dung chi tiết từ handover2.md + các phần bạn yêu cầu (LLM, Domain Routing, nghiệp vụ “điều nào không được thực hiện”, “tăng lương cơ bản ảnh hưởng đến…”)**.

---

# 📘 Metadata Editor & Retrieval System – Handover Documentation

**Project Name**: Metadata Editor & Hybrid Search Platform
**Status**: Stable Release – Ready for Expansion
**Date**: October 2025
**Integration**: PostgreSQL (BM25), ChromaDB (Vector Store), FastAPI Backend
**Tech Stack**: Python 3.10+, FastAPI, PostgreSQL, ChromaDB, HTML/CSS Frontend, Loguru Logging

---

## 📋 Current Implementation Status

### ✅ Completed Steps

* **Step 1**: ✅ Kết nối PostgreSQL & ChromaDB hai chiều.
* **Step 2**: ✅ Chỉnh sửa metadata JSON từ frontend & đồng bộ sang DB.
* **Step 3**: ✅ Fix điều hướng frontend (`/` thay vì `/index.html`).
* **Step 4**: ✅ Xây dựng API RESTful (collections, documents, sync).
* **Step 5**: ✅ Hoàn thiện flatten metadata & serialize JSON chuẩn Chroma.
* **Step 6**: ✅ Tích hợp BM25 + Semantic Hybrid Search có filter metadata.
* **Step 7**: ✅ Hoàn thiện script kiểm thử semantic search (`semantic_search_with_filters.py`).

### 🎯 Next Steps

* **Step 8**: Tích hợp **LLM reasoning layer** (Q&A phủ định, impact analysis).
* **Step 9**: Thêm **Domain / Category Router** tự động chọn collection theo lĩnh vực.
* **Step 10**: Bổ sung **Impact Graph** (`document_links`) cho nghiệp vụ “tăng lương cơ bản ảnh hưởng đến…”.

---

## 🏗️ Project Structure

```
metadata-editor/
├── backend/
│   ├── main.py                  # FastAPI entrypoint
│   ├── config/                  # Logging & environment
│   ├── core/
│   │   └── database.py          # PostgreSQL / Chroma connections
│   ├── routers/
│   │   ├── collections.py       # List collections & documents
│   │   ├── documents.py         # CRUD metadata (JSON)
│   ├── services/
│   │   ├── postgres_service.py  # BM25 retrieval
│   │   ├── chroma_service.py    # Vector metadata update/query
│   │   ├── sync_service.py      # Two-way synchronization logic
│   ├── models/
│   │   └── schemas.py           # Pydantic models for API
│   ├── logging.py               # Log setup
│
├── frontend/
│   ├── templates/
│   │   ├── index.html           # Collections list
│   │   ├── documents.html       # Document list by collection
│   │   └── edit.html            # Edit metadata JSON
│   └── static/css/style.css     # Styling
│
├── tests/
│   ├── scan_chroma_schema.py          # Inspect Chroma metadata
│   ├── scan_postgres_metadata.py      # Inspect PostgreSQL schema
│   ├── semantic_search_with_filters.py# Semantic search test w/ filters
│   └── create_sample_data.py          # Generate demo data
│
├── requirements.txt
├── .env
└── Dockerfile
```

---

## 🔧 Environment Setup

### Prerequisites

* **Python**: 3.10+
* **PostgreSQL**: 14+
* **ChromaDB**: 0.5+
* **Uvicorn**: for FastAPI dev server

### 1️⃣ Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Environment Configuration

`.env` file:

```env
POSTGRES_HOST=192.168.1.95
POSTGRES_PORT=5432
POSTGRES_DB=knowledge_base_v2
POSTGRES_USER=kb_admin
POSTGRES_PASSWORD=1234567890

CHROMA_HOST=192.168.1.95
CHROMA_PORT=8001
CHROMA_AUTH_TOKEN=1234567890

API_PORT=8005
DEBUG=True
LOG_LEVEL=INFO
```

---

## 🚀 Running the Application

```bash
uvicorn backend.main:app --reload --port 8005
```

Access UI: [http://localhost:8005](http://localhost:8005)

---

## 📁 Key Files Description

| File                                    | Description                                                   |
| --------------------------------------- | ------------------------------------------------------------- |
| `backend/services/sync_service.py`      | Xử lý cập nhật metadata từ frontend → đồng bộ SQL + Chroma.   |
| `backend/services/chroma_service.py`    | Cập nhật vector metadata, flatten JSON hợp lệ (`json.dumps`). |
| `backend/services/postgres_service.py`  | Tìm kiếm BM25 (`ts_rank_cd`) + filter JSON metadata.          |
| `tests/semantic_search_with_filters.py` | Kiểm thử hybrid search có filter domain, tags, access.        |
| `frontend/edit.html`                    | Form sửa metadata JSON, nút “Lưu” & “Quay lại”.               |
| `.env`                                  | Thông tin kết nối DB.                                         |

---

## 🧪 Testing Steps

```bash
pytest tests -v -s
python tests/scan_postgres_metadata.py
python tests/scan_chroma_schema.py
```

Kỳ vọng:

* PostgreSQL trả về >0 document.
* Chroma có metadata `custom_tags`, `custom_quality` đúng JSON.
* `semantic_search_with_filters.py` chạy không lỗi, hiển thị similarity & metadata.

---

## 🔍 API Documentation

### Endpoints

```
GET    /api/collections/                 # Danh sách collection
GET    /api/collections/{name}/documents # Danh sách tài liệu
GET    /api/documents/{id}               # Xem chi tiết metadata
PUT    /api/documents/{id}               # Cập nhật metadata JSON
```

---

## 🗃️ Database Schema (Tóm lược)

```sql
CREATE TABLE documents_metadata_v2 (
  document_id UUID PRIMARY KEY,
  title VARCHAR NOT NULL,
  content TEXT,
  department_owner VARCHAR,
  access_level access_level_enum,
  status document_status_enum,
  metadata JSONB,
  search_tokens TSVECTOR,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);
```

---

## 🚨 Known Issues & Limitations

| Vấn đề                        | Giải thích                               | Mức độ |
| ----------------------------- | ---------------------------------------- | ------ |
| Chưa có LLM reasoning         | Chưa phân tích logic phủ định / tác động | ⚠️     |
| Chưa có bảng `document_links` | Chưa truy vết được tài liệu liên quan    | ⚠️     |
| UI đơn giản                   | Thiếu phân quyền / tìm kiếm nâng cao     | ⚙️     |
| BM25 chưa tự refresh          | Cần refresh thủ công khi thêm tài liệu   | ⚙️     |

---

## 🧠 Advanced Expansion Roadmap

### 🧩 1. LLM Reasoning Layer

Thêm module `llm_reasoner.py` để:

* Trả lời câu hỏi nghiệp vụ logic (“điều nào KHÔNG được thực hiện?”).
* Kết hợp top-n đoạn từ retriever (BM25 + Chroma).
* Prompt hướng dẫn LLM phân tích logic phủ định / điều cấm.

```text
Câu hỏi: "Điều nào dưới đây KHÔNG được thực hiện?"
→ BM25 + Chroma tìm đoạn chứa phủ định
→ LLM reasoning tóm tắt hành vi bị cấm.
```

---

### 🧭 2. Domain / Category Routing

Thêm trường `category` trong PostgreSQL (`hr`, `it`, `policy`, `training`).

Logic ví dụ:

```python
def route_query(query):
    if "MikroTik" in query:
        return "it"
    elif "nghỉ phép" in query:
        return "hr"
    return "general"
```

LLM hoặc rule engine sẽ chọn collection phù hợp → giảm nhiễu & tăng tốc.

---

### 🧮 3. Impact Analysis (“Tăng lương cơ bản ảnh hưởng đến…”)

Thêm bảng quan hệ:

```sql
CREATE TABLE document_links (
  source_id UUID,
  target_id UUID,
  relation_type VARCHAR, -- 'refer', 'impact', 'depend'
  confidence FLOAT
);
```

Quy trình:

1. BM25/Chroma tìm văn bản chứa “lương cơ bản”.
2. Truy vấn `document_links` lấy tài liệu `impact/depend`.
3. LLM tóm tắt ảnh hưởng:

   > “Tăng lương cơ bản ảnh hưởng đến: Quy định BHXH, hướng dẫn thưởng, quy trình tính thuế TNCN.”

---

### 🧠 4. Hybrid Q&A Pipeline

```text
User Query
   ↓
[Domain Router]
   ↓
[Hybrid Retriever] (BM25 + Chroma)
   ↓
[Context Builder]
   ↓
[LLM Reasoner]
   ↓
Answer (phủ định / ảnh hưởng / chính sách)
```

---

## 🧾 Production Checklist

* [x] PostgreSQL & ChromaDB credentials in `.env`
* [x] DEBUG=False trong production
* [x] HTTPS proxy (Nginx/Traefik)
* [x] Log rotation active
* [x] Database backup schedule
* [x] CORS allowlist kiểm soát domain frontend

---

## 📞 Support & Maintenance

* **Repository**: Internal Git (metadata-editor)
* **Documentation**: `handover_metadata.md` (bản này)
* **Integration**: PostgreSQL + ChromaDB hybrid system
* **Next Major Milestone**: Tích hợp LLM Reasoner (Q4/2025)

---

**Last Updated**: October 2025
**Project Status**: ✅ Stable & Expandable
**Next Milestone**: LLM Reasoning Integration + Impact Graph Expansion

---

✅ **Hệ thống Metadata Editor hiện tại đã sẵn sàng hoạt động production**
và có thể **mở rộng sang các nghiệp vụ hiểu & suy luận chính sách** (phủ định, ảnh hưởng, domain routing, Q&A logic).


---

