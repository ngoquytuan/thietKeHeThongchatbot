# 🤖 AGENT ONBOARDING — chatbotR4 Database V14
> Dành cho: **Claude Code / Aider (CLI agent)**
> Cách dùng:
>   Claude Code : paste vào đầu session hoặc lưu thành CLAUDE.md ở root project
>   Aider       : aider --read agent_prompt_v14.md <files...>

---

## 1. NHIỆM VỤ & PHONG CÁCH LÀM VIỆC

Bạn là coding agent làm việc với database **chatbotR4 V14** — hệ thống RAG
xử lý văn bản pháp luật tiếng Việt.

**Nhiệm vụ theo thứ tự ưu tiên:**
1. Kiểm tra schema / debug data integrity
2. Viết và chạy SQL query tối ưu
3. Viết Python code (FastAPI, Pydantic V2, DB adapter)
4. Tạo test data và seed scripts

**Nguyên tắc làm việc với CLI agent:**
- **Verify trước khi sửa**: Luôn chạy `EXPLAIN ANALYZE` trước khi đề xuất index mới
- **Không tự ý xóa**: Không DROP table/column mà không hỏi xác nhận
- **Atomic changes**: Mỗi thay đổi schema phải nằm trong transaction `BEGIN/COMMIT`
- **Test data có prefix**: Mọi seed data test phải có `title` bắt đầu bằng `[TEST]`
  để dễ cleanup: `DELETE FROM documents_metadata_v2 WHERE title LIKE '[TEST]%'`

---

## 1b. SETUP ĐẶC THÙ CHO CLAUDE CODE / AIDER

### Nếu dùng Claude Code
Lưu file này thành `CLAUDE.md` ở root project — Claude Code tự động đọc mỗi session:
```bash
cp agent_prompt_v14.md CLAUDE.md
```

Cấu trúc project nên có:
```
project-root/
├── CLAUDE.md                          ← file này (auto-loaded)
├── chatbotR4_schema_v14.sql           ← schema đầy đủ
├── src/
│   ├── models/canonical_v3.py         ← Pydantic models
│   └── utils/postgres_adapter_v14.py  ← DB adapter
└── tests/
    └── seed_v14.py                    ← test data
```

### Nếu dùng Aider
```bash
# Task SQL / debug
aider --read agent_prompt_v14.md queries/search.sql

# Task Python adapter
aider --read agent_prompt_v14.md src/utils/postgres_adapter_v14.py

# Deep debug — load cả schema
aider --read agent_prompt_v14.md --read chatbotR4_schema_v14.sql src/
```

### Bash aliases hữu ích (thêm vào ~/.bashrc)
```bash
alias pgv14='psql -h 192.168.1.70 -p 15432 -U postgres -d chatbotR4_v14'
alias pgv14-validate='pgv14 -c "SELECT component, status, details FROM validate_schema_v14();"'
alias pgv14-cleanup='pgv14 -c "DELETE FROM documents_metadata_v2 WHERE title LIKE '"'"'[TEST]%'"'"';"'
alias pgv14-stats='pgv14 -c "SELECT * FROM bm25_collection_stats WHERE stats_id = 1;"'
```

---

## 2. THÔNG TIN KẾT NỐI DATABASE

```
Host     : 192.168.1.70
Port     : 15432
Database : chatbotR4_v14        ← database MỚI, fresh install
User     : postgres
Schema   : public
PG Ver   : PostgreSQL 15
```

```python
# Connection string
DATABASE_URL = "postgresql://postgres:@192.168.1.70:15432/chatbotR4_v14"

# asyncpg (FastAPI)
ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:@192.168.1.70:15432/chatbotR4_v14"
```

---

## 3. BỐI CẢNH HỆ THỐNG

### Đây là gì?
- **RAG system** cho văn bản pháp luật Việt Nam
- Hybrid search: **Vector (ChromaDB)** + **BM25 (PostgreSQL native)**
- Có **Knowledge Graph** để truy vết quan hệ giữa các văn bản luật
- Embedding model: `Qwen/Qwen3-Embedding-0.6B` (1024 dimensions)

### V14 là gì? (khác gì V13?)
V14 là bản nâng cấp schema, **không phải rewrite**. Thay đổi chính:

| Thay đổi | Chi tiết |
|----------|----------|
| **6 cột phẳng mới** | `document_number`, `issue_date`, `signer`, `keywords[]`, `tags[]`, `reference_docs[]` — promoted từ `metadata JSONB` |
| **Trigger tự sync** | `trg_sync_flat_columns` — tự điền 6 cột trên khi INSERT/UPDATE `metadata` |
| **Enum sạch** | `documentstatus` chỉ còn lowercase: `pending`, `processing`, `completed`... |
| **FK fix** | `overlap_source_prev/next` trong `document_chunks_enhanced` có `ON DELETE SET NULL` |
| **Normalize fix** | `normalize_vietnamese_text()` dùng `unaccent()` đúng cách |
| **Signature fix** | `check_all_signatures_v14()` — sửa logic OR→AND tránh false positive |

---

## 4. SƠ ĐỒ BẢNG QUAN TRỌNG

```
users
  └── user_sessions
  └── data_ingestion_jobs
        └── chunk_processing_logs
        └── pipeline_metrics
        └── processing_errors

documents_metadata_v2          ← BẢNG TRUNG TÂM
  ├── document_id (PK, uuid)
  ├── source_document_id (UNIQUE) ← business ID từ hệ thống nguồn
  ├── title, content, document_type, status
  ├── department_owner, author
  │
  ├── [V14 FLAT COLUMNS] ─────────────────────────────────────
  │   ├── document_number VARCHAR(100)   ← số hiệu: "123/2024/QĐ-BTC"
  │   ├── issue_date DATE                ← ngày ban hành
  │   ├── signer VARCHAR(255)            ← người ký
  │   ├── keywords TEXT[]               ← từ khóa (GIN indexed)
  │   ├── tags TEXT[]                   ← tags phân loại (GIN indexed)
  │   └── reference_docs TEXT[]         ← số hiệu VB liên quan (GIN indexed)
  │
  ├── metadata JSONB           ← source of truth, giữ nguyên
  └── search_tokens tsvector

  └── document_chunks_enhanced
        ├── chunk_id, document_id, chunk_content
        ├── chunk_position, chunk_size_tokens
        ├── bm25_tokens tsvector
        ├── overlap_source_prev uuid → self (ON DELETE SET NULL)
        └── overlap_source_next uuid → self (ON DELETE SET NULL)

  └── document_signatures
        ├── file_fingerprints JSONB  { md5_hash, sha256_hash, file_size }
        ├── content_signatures JSONB { content_hash, semantic_hash, ... }
        └── semantic_features JSONB  { document_features: { total_chunks, total_words } }

  └── document_bm25_index      ← BM25 inverted index thủ công
        ├── term, term_frequency, document_frequency, bm25_score
        └── FK → document_chunks_enhanced

  └── graph_documents           ← Knowledge Graph nodes
        └── graph_edges         ← Knowledge Graph edges (quan hệ luật)

search_logs                     ← mỗi query tạo 1 record
  └── search_log_results        ← chi tiết từng kết quả trả về

search_analytics                ← business analytics (satisfaction, dept)
bm25_global_terms               ← IDF global cho BM25
bm25_collection_stats           ← stats toàn collection (stats_id = 1 duy nhất)
```

---

## 5. ENUM REFERENCE

```sql
-- Dùng lowercase, KHÔNG dùng uppercase (V13 bug đã fix)
documentstatus: pending | processing | quality_check | chunking |
                embedding | storage | indexing | completed |
                failed | cancelled | retrying

processingstage: extraction | validation | quality_control | chunking |
                 embedding | storage | indexing | finalization

document_type_enum: policy | procedure | technical_guide | report |
                    manual | specification | template | form |
                    presentation | training_material | other

document_status_enum: draft | review | approved | published | archived | deprecated

access_level_enum: public | employee_only | manager_only | director_only | system_admin

userlevel: GUEST | EMPLOYEE | MANAGER | DIRECTOR | SYSTEM_ADMIN
userstatus: ACTIVE | INACTIVE | SUSPENDED | PENDING
chunking_method_enum: fixed_size | sentence_based | semantic_boundary |
                      paragraph_based | hybrid
```

---

## 6. JSONB METADATA STRUCTURE

`documents_metadata_v2.metadata` có cấu trúc:

```json
{
  "identification": {
    "document_number": "123/2024/QĐ-BTC",
    "issue_date": "2024-03-15",
    "task_code": "TASK-001"
  },
  "authority": {
    "signer": "Nguyễn Văn A",
    "issuing_body": "Bộ Tài chính"
  },
  "domain": {
    "keywords": ["ngân sách", "tài chính công"]
  },
  "classification": {
    "tags": ["chinh-sach", "ngan-sach"]
  },
  "references": {
    "doc_numbers": ["99/2023/QĐ-BTC", "45/2022/NĐ-CP"]
  },
  "hierarchy": {
    "rank_level": 3
  },
  "law_id": "LAW-2024-001"
}
```

**Lưu ý quan trọng**: Trigger `trg_sync_flat_columns` tự động đọc các path trên
và điền vào 6 cột phẳng. Khi INSERT, bạn chỉ cần ghi vào `metadata` JSONB,
6 cột kia sẽ tự được điền. Hoặc ghi trực tiếp vào cột phẳng — cả hai đều đúng.

---

## 7. STORED FUNCTIONS QUAN TRỌNG

```sql
-- BM25 search chính
SELECT * FROM search_bm25_with_global_terms(
    'từ khóa tìm kiếm',   -- query text
    10,                    -- limit
    0.1                    -- min_score
);

-- Duplicate detection (dùng trước khi INSERT document mới)
SELECT * FROM check_all_signatures_v14(
    'md5hash',     -- input_md5
    'sha256hash',  -- input_sha256
    12345,         -- file_size
    'contenthash', -- content_hash
    'semhash',     -- semantic_hash
    'textfp',      -- text_fingerprint
    25,            -- total_chunks (optional)
    3500           -- total_words (optional)
);

-- Graph traversal
SELECT * FROM get_document_tree_up('graph_doc_id'::uuid, 3);   -- tìm văn bản cha
SELECT * FROM get_document_tree_down('graph_doc_id'::uuid, 3); -- tìm văn bản con

-- Sync document lên Knowledge Graph
SELECT sync_document_to_graph('document_id'::uuid);

-- Cập nhật BM25 stats (chạy sau khi nạp batch documents)
SELECT update_bm25_collection_stats();
SELECT update_all_idf_cache();

-- Kiểm tra schema OK
SELECT * FROM validate_schema_v14();
-- Expected: tất cả rows status = 'OK'
```

---

## 8. PYTHON STACK CONTEXT

```python
# Models
from pydantic import BaseModel
from enum import Enum

# DB
import asyncpg          # async driver
import psycopg2         # sync driver
from sqlalchemy import text

# Key model đang dùng
# src/models/canonical_v3.py → CanonicalMetadataV3
# src/utils/postgres_adapter_v14.py → PostgresMetadataAdapter

# Embedding
# Model: Qwen/Qwen3-Embedding-0.6B
# Dimensions: 1024
# Vector DB: ChromaDB (separate service)

# Python version: 3.10
# Framework: FastAPI
# Pydantic: V2
```

---

## 9. NHỮNG ĐIỀU KHÔNG ĐƯỢC LÀM

```
❌ Không INSERT documentstatus với giá trị UPPERCASE ('PENDING', 'COMPLETED'...)
   → Dùng lowercase: 'pending', 'completed'

❌ Không dùng cột tên "references" (reserved word SQL)
   → Bảng dùng tên "reference_docs"

❌ Không DELETE document_chunks_enhanced mà không xử lý overlap chain
   → overlap_source_prev/next đã có ON DELETE SET NULL, nhưng hãy verify sau delete

❌ Không query JSONB metadata->>'field' trong WHERE clause nếu đã có cột phẳng
   → Dùng cột phẳng: WHERE document_number = '...' thay vì WHERE metadata->>'...'

❌ Không UPDATE bm25_collection_stats stats_id != 1
   → Chỉ có 1 row duy nhất với stats_id = 1

❌ Không tạo thêm row trong bm25_collection_stats
   → Luôn UPDATE WHERE stats_id = 1
```

---

## 10. QUICK SANITY CHECK

Sau khi connect, chạy ngay các lệnh này để verify môi trường:

```sql
-- 1. Schema version
SELECT version, description, applied_at
FROM schema_migrations ORDER BY applied_at DESC LIMIT 1;
-- Expected: V14.0

-- 2. Validate toàn bộ schema
SELECT * FROM validate_schema_v14();
-- Expected: 7 rows, tất cả status = 'OK'

-- 3. Kiểm tra trigger hoạt động
INSERT INTO documents_metadata_v2 (
    title, document_type, access_level, department_owner, author,
    metadata
) VALUES (
    'Test V14 Trigger', 'policy', 'employee_only', 'IT', 'Agent Test',
    '{"identification": {"document_number": "TEST/001", "issue_date": "2026-01-01"},
      "authority": {"signer": "Test Signer"},
      "domain": {"keywords": ["test"]},
      "classification": {"tags": ["dev"]},
      "references": {"doc_numbers": []}}'
) RETURNING document_id, document_number, issue_date, signer, keywords;
-- Expected: document_number='TEST/001', issue_date='2026-01-01', signer='Test Signer'

-- 4. Cleanup test
DELETE FROM documents_metadata_v2 WHERE title = 'Test V14 Trigger';

-- 5. BM25 stats initialized
SELECT * FROM bm25_collection_stats WHERE stats_id = 1;
-- Expected: 1 row (có thể total_documents = 0 nếu DB mới)
```

---

## 11. GHI CHÚ KHI GẶP LỖI THƯỜNG GẶP

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| `invalid input value for enum documentstatus: "PENDING"` | Code cũ dùng uppercase | Đổi thành `'pending'` |
| `duplicate key value violates unique constraint "bm25_global_terms_term_key"` | Term đã tồn tại | Dùng `upsert_global_term()` thay vì INSERT |
| `null value in column "department_owner"` | Trường NOT NULL bị bỏ qua | `department_owner` là required |
| `ERROR: column "references" does not exist` | Tên cột cũ từ V13 plan | Dùng `reference_docs` |
| Trigger không sync cột phẳng | metadata path sai | Kiểm tra JSON path theo mục 6 |
| `FK violation on overlap_source_*` | Không nên xảy ra ở V14 | Nếu có, báo lại — đây là bug |

---

## 12. WORKFLOW CHUẨN CHO CLAUDE CODE / AIDER

### Khi bắt đầu session mới
```
1. pgv14-validate                    → confirm schema OK
2. Mô tả task cụ thể cho agent
3. Agent đề xuất → bạn review → approve
4. pgv14-cleanup                     → xóa test data sau khi done
```

### Cách giao task hiệu quả nhất cho CLI agent

**THAY VÌ:**
> "Làm cho search nhanh hơn"

**HÃY NÓI:**
> "Viết SQL query tìm tất cả documents có `document_type = 'policy'`,
>  `issue_date` trong năm 2024, và `keywords` chứa 'ngân sách'.
>  Dùng cột phẳng V14, không dùng JSONB. Thêm EXPLAIN ANALYZE."

**THAY VÌ:**
> "Tạo test data"

**HÃY NÓI:**
> "Tạo seed script Python insert 5 documents test vào `documents_metadata_v2`.
>  Title prefix '[TEST]'. Cover đủ 3 document_type khác nhau.
>  Dùng `metadata` JSONB để trigger tự sync cột phẳng, verify bằng
>  SELECT document_number, issue_date, signer sau INSERT."

### Task templates hay dùng

```bash
# Debug: tại sao query chậm?
"Chạy EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) cho query này và giải thích kết quả: [query]"

# Viết adapter:
"Viết PostgresMetadataAdapter.prepare_upsert_payload() nhận CanonicalMetadataV3,
 trả về dict cho INSERT vào documents_metadata_v2 V14. Mapping theo mục 6."

# Kiểm tra data integrity:
"Viết query kiểm tra xem có document nào mà document_number IS NULL
 nhưng metadata->'identification'->>'document_number' IS NOT NULL không.
 Đây là dấu hiệu trigger sync bị lỗi."

# Seed BM25:
"Viết Python function nhận chunk_id và chunk_content,
 tokenize tiếng Việt đơn giản (split + filter stopwords),
 insert vào document_bm25_index và update bm25_global_terms dùng upsert_global_term()."
```

---

*Schema file đầy đủ: `chatbotR4_schema_v14.sql` (2231 dòng)*
*Validate function: `SELECT * FROM validate_schema_v14();`*
*Phiên bản prompt: v14.1 — tối ưu cho Claude Code / Aider CLI*
