Tôi sẽ phân tích schema V5 này so với cấu trúc export package để xem còn thiếu gì.# PHÂN TÍCH: SCHEMA V5 vs EXPORT PACKAGE REQUIREMENTS

## **🔍 TÌNH TRẠNG HIỆN TẠI**

Schema V5 **CHƯA ĐỦ** để nhận toàn bộ dữ liệu từ export package. Tôi sẽ phân tích chi tiết:

## **✅ ĐÃ ĐỦ - CÓ TABLE TƯƠNG ỨNG**

### **1. FOR_DATABASE/ Content**
```sql
✅ document_metadata.json      → documents_metadata_v2 table
✅ chunks_enhanced.jsonl       → document_chunks_enhanced table  
✅ vietnamese_analysis.json    → vietnamese_text_analysis table
✅ search_vectors.json         → documents_metadata_v2.search_tokens (TSVECTOR)
✅ ingestion_job_metadata.json → data_ingestion_jobs table
```

### **2. File Management**
```sql
✅ original/ files → documents_metadata_v2.original_file_info JSONB
✅ package files   → documents_metadata_v2.export_package_info JSONB  
✅ access control  → documents_metadata_v2.file_access_info JSONB
```

### **3. Processing Pipeline**
```sql
✅ Job tracking    → data_ingestion_jobs table
✅ Chunk logs      → chunk_processing_logs table
✅ Pipeline metrics → pipeline_metrics table
✅ Error handling  → processing_errors table
```

## **❌ THIẾU - CHƯA CÓ TABLE**

### **1. signatures/ Folder - HOÀN TOÀN THIẾU**

```sql
❌ file_fingerprints.json     → KHÔNG có table
❌ content_signatures.json    → KHÔNG có table  
❌ semantic_features.json     → KHÔNG có table
```

**Cần thêm table:**
```sql
CREATE TABLE document_signatures (
    signature_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id),
    file_fingerprint JSONB DEFAULT '{}',      -- SHA256, MD5, size, etc.
    content_signature JSONB DEFAULT '{}',     -- Text-based signatures
    semantic_features JSONB DEFAULT '{}',     -- NLP-based features
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **2. validation/ Folder - THIẾU PROCESSING STATS**

```sql
✅ quality_score.json → data_ingestion_jobs.quality_score (PARTIAL)
❌ processing_stats.json → KHÔNG có table chi tiết
```

**Cần thêm table:**
```sql
CREATE TABLE processing_statistics (
    stats_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id),
    job_id UUID REFERENCES data_ingestion_jobs(job_id),
    processing_stats JSONB DEFAULT '{}',      -- Chi tiết từ processing_stats.json
    performance_metrics JSONB DEFAULT '{}',   -- Timing, memory, CPU usage
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **3. FOR_VECTOR_DB/ Folder - HOÀN TOÀN THIẾU**

```sql
❌ embeddings_preparation.json → KHÔNG có table
❌ similarity_features.json    → KHÔNG có table
❌ collection_config.json      → KHÔNG có table (theo design mới)
```

**Cần thêm table:**
```sql
CREATE TABLE vector_database_config (
    config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id),
    collection_name VARCHAR(255) NOT NULL,
    embedding_preparation JSONB DEFAULT '{}',    -- embeddings_preparation.json
    similarity_features JSONB DEFAULT '{}',      -- similarity_features.json
    collection_config JSONB DEFAULT '{}',        -- dynamic collection rules
    vector_storage_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **4. FOR_SEARCH/ Folder - THIẾU SEARCH CONFIG**

```sql
✅ search_document.json → documents_metadata_v2.indexable_content (PARTIAL)
❌ search_config.json   → KHÔNG có table
❌ bm25_tokens.json     → document_bm25_index table (PARTIAL - thiếu config)
```

**Cần thêm table:**
```sql
CREATE TABLE search_engine_config (
    search_config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id),
    search_config JSONB DEFAULT '{}',           -- Vietnamese analyzer config
    bm25_config JSONB DEFAULT '{}',             -- BM25 parameters  
    elasticsearch_mapping JSONB DEFAULT '{}',    -- ES mapping configuration
    search_optimization JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **5. Package Metadata - THIẾU HOÀN TOÀN**

```sql
❌ manifest.json    → KHÔNG có table
❌ user_info.json   → KHÔNG có table
```

**Cần thêm table:**
```sql
CREATE TABLE export_package_metadata (
    package_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id),
    manifest_data JSONB DEFAULT '{}',           -- manifest.json content
    user_info JSONB DEFAULT '{}',               -- user_info.json content
    package_version VARCHAR(50),
    export_timestamp TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## **📋 CẬP NHẬT SCHEMA - 5 TABLES BỔ SUNG**

```sql
-- ================================================================================================
-- EXPORT PACKAGE SUPPORT TABLES (5 new tables needed)
-- ================================================================================================

-- Table 1: Document Signatures (signatures/ folder)
CREATE TABLE IF NOT EXISTS document_signatures (
    signature_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    file_fingerprint JSONB DEFAULT '{}',      -- file_fingerprints.json
    content_signature JSONB DEFAULT '{}',     -- content_signatures.json  
    semantic_features JSONB DEFAULT '{}',     -- semantic_features.json
    signature_algorithm VARCHAR(50) DEFAULT 'SHA256',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 2: Processing Statistics (validation/ folder)
CREATE TABLE IF NOT EXISTS processing_statistics (
    stats_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    job_id UUID REFERENCES data_ingestion_jobs(job_id) ON DELETE CASCADE,
    processing_stats JSONB DEFAULT '{}',      -- processing_stats.json detail
    performance_metrics JSONB DEFAULT '{}',   -- timing, memory, CPU
    validation_results JSONB DEFAULT '{}',    -- quality validation details
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 3: Vector Database Config (FOR_VECTOR_DB/ folder)  
CREATE TABLE IF NOT EXISTS vector_database_config (
    config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    collection_name VARCHAR(255) NOT NULL,
    embedding_preparation JSONB DEFAULT '{}',    -- embeddings_preparation.json
    similarity_features JSONB DEFAULT '{}',      -- similarity_features.json
    collection_config JSONB DEFAULT '{}',        -- dynamic collection rules
    vector_storage_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 4: Search Engine Config (FOR_SEARCH/ folder)
CREATE TABLE IF NOT EXISTS search_engine_config (
    search_config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), 
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    search_config JSONB DEFAULT '{}',           -- search_config.json
    bm25_config JSONB DEFAULT '{}',             -- bm25_tokens.json config
    elasticsearch_mapping JSONB DEFAULT '{}',    -- ES mapping
    vietnamese_analyzer_config JSONB DEFAULT '{}',
    search_optimization JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 5: Export Package Metadata (manifest.json + user_info.json)
CREATE TABLE IF NOT EXISTS export_package_metadata (
    package_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    manifest_data JSONB DEFAULT '{}',           -- manifest.json
    user_info JSONB DEFAULT '{}',               -- user_info.json  
    package_version VARCHAR(50),
    export_format VARCHAR(50) DEFAULT 'v2.0',
    package_size_bytes BIGINT,
    export_timestamp TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Additional Indexes for new tables
CREATE INDEX IF NOT EXISTS idx_document_signatures_document ON document_signatures(document_id);
CREATE INDEX IF NOT EXISTS idx_processing_statistics_document ON processing_statistics(document_id);  
CREATE INDEX IF NOT EXISTS idx_processing_statistics_job ON processing_statistics(job_id);
CREATE INDEX IF NOT EXISTS idx_vector_database_config_document ON vector_database_config(document_id);
CREATE INDEX IF NOT EXISTS idx_vector_database_config_collection ON vector_database_config(collection_name);
CREATE INDEX IF NOT EXISTS idx_search_engine_config_document ON search_engine_config(document_id);
CREATE INDEX IF NOT EXISTS idx_export_package_metadata_document ON export_package_metadata(document_id);
```

## **🎯 KẾT LUẬN**

**Schema V5 hiện tại:** **75% hoàn thành** cho export package support

**Cần bổ sung:** **5 tables** để đạt **100% compatibility**

**Ưu tiên triển khai:**
1. **HIGH**: `vector_database_config` - Cần thiết cho ChromaDB integration
2. **HIGH**: `document_signatures` - Cần thiết cho duplicate detection  
3. **MEDIUM**: `search_engine_config` - Cần thiết cho search optimization
4. **MEDIUM**: `export_package_metadata` - Cần thiết cho package tracking
5. **LOW**: `processing_statistics` - Nice-to-have cho detailed monitoring

**Khuyến nghị:** Bổ sung 5 tables này vào schema V6 để đạt full compatibility với export package structure.

# CHECKLIST KIỂM TRA EXPORT PACKAGE IMPORT - ADMINER 5.4.0

## **CHUẨN BỊ KIỂM TRA**

### **1. Kết nối Adminer**
```
URL: http://localhost:8081
System: PostgreSQL  
Server: localhost:5432
Username: kb_admin
Password: 1234567890
Database: knowledge_base_v2
```

### **2. Thông tin Export Package cần kiểm tra**
```
Package Format: {DEPT}_{TYPE}_{TIMESTAMP}.zip
VD: HR_POLICY_20250915_143022.zip
Document ID: [Cần xác định từ documents_metadata_v2]
```

---

## **📋 CHECKLIST CHI TIẾT**

### **BƯỚC 1: KIỂM TRA DOCUMENT CHÍNH** ✅

#### **1.1. Kiểm tra Document Metadata**
```sql
-- Query trong Adminer:
SELECT 
    document_id,
    title,
    document_type,
    department_owner,
    author,
    status,
    language_detected,
    vietnamese_segmented,
    diacritics_normalized,
    search_text_normalized,
    jsonl_export_ready,
    chunk_count,
    file_size_bytes,
    original_file_info,
    export_package_info,
    file_access_info,
    created_at,
    updated_at
FROM documents_metadata_v2 
WHERE title LIKE '%[TÊN_DOCUMENT]%'
OR document_id = '[DOCUMENT_ID]'
ORDER BY created_at DESC;
```

**Cần kiểm tra:**
- [ ] `title` khớp với document gốc
- [ ] `document_type` đúng (policy, procedure, manual, etc.)
- [ ] `department_owner` đúng (HR, IT, R&D, etc.)  
- [ ] `language_detected` = 'vi'
- [ ] `vietnamese_segmented` = true
- [ ] `search_text_normalized` có content (không null/empty)
- [ ] `jsonl_export_ready` = true
- [ ] `chunk_count` > 0 (thường 3-7 chunks)
- [ ] `original_file_info` JSONB có data (không empty {})
- [ ] `export_package_info` JSONB có data  
- [ ] `file_access_info` JSONB có data

#### **1.2. Kiểm tra Original File Info**
```sql
-- Xem chi tiết original_file_info:
SELECT 
    document_id,
    title,
    original_file_info->>'original_file_path' as file_path,
    original_file_info->>'original_filename' as filename,
    original_file_info->>'file_size_bytes' as size_bytes,
    original_file_info->>'file_hash' as file_hash,
    original_file_info->>'mime_type' as mime_type,
    original_file_info->>'preservation_status' as status
FROM documents_metadata_v2 
WHERE original_file_info != '{}'
ORDER BY created_at DESC;
```

**Cần kiểm tra:**
- [ ] `original_file_path` có format đúng: `/opt/chatbot-storage/original/YYYY/MM/DD/...`
- [ ] `original_filename` khớp với file gốc
- [ ] `file_size_bytes` > 0
- [ ] `file_hash` bắt đầu với "sha256:" 
- [ ] `mime_type` đúng (application/pdf, text/plain, etc.)
- [ ] `preservation_status` = "preserved"

### **BƯỚC 2: KIỂM TRA CHUNKS** ✅

#### **2.1. Kiểm tra Document Chunks**
```sql
-- Query chunks:
SELECT 
    chunk_id,
    document_id,
    chunk_position,
    chunk_size_tokens,
    semantic_boundary,
    overlap_with_prev,
    overlap_with_next,
    chunk_method,
    chunk_quality_score,
    embedding_model,
    embedding_dimensions,
    LEFT(chunk_content, 100) as content_preview,
    created_at
FROM document_chunks_enhanced 
WHERE document_id = '[DOCUMENT_ID]'
ORDER BY chunk_position;
```

**Cần kiểm tra:**
- [ ] Có ít nhất 3-7 chunks
- [ ] `chunk_position` liên tục (1, 2, 3, ...)
- [ ] `chunk_size_tokens` <= 800 tokens
- [ ] `semantic_boundary` = true cho hầu hết chunks
- [ ] `overlap_with_prev` và `overlap_with_next` khoảng 50 tokens
- [ ] `chunk_method` = 'semantic_boundary'
- [ ] `chunk_quality_score` > 0.5 (50%)
- [ ] `embedding_model` = 'Qwen/Qwen3-Embedding-0.6B'
- [ ] `embedding_dimensions` = 1024
- [ ] `chunk_content` có nội dung tiếng Việt

#### **2.2. Kiểm tra BM25 Index**
```sql
-- Kiểm tra BM25 tokens:
SELECT 
    document_id,
    COUNT(DISTINCT chunk_id) as chunks_with_bm25,
    COUNT(*) as total_bm25_terms,
    AVG(term_frequency) as avg_term_freq
FROM document_bm25_index 
WHERE document_id = '[DOCUMENT_ID]'
GROUP BY document_id;
```

**Cần kiểm tra:**
- [ ] `chunks_with_bm25` = chunk count từ bước trước
- [ ] `total_bm25_terms` > 100 (có nhiều terms được index)
- [ ] `avg_term_freq` > 1

### **BƯỚC 3: KIỂM TRA VIETNAMESE ANALYSIS** ✅

#### **3.1. Kiểm tra Vietnamese Text Analysis**
```sql
-- Query Vietnamese analysis:
SELECT 
    analysis_id,
    document_id,
    chunk_id,
    language_quality_score,
    diacritics_density,
    readability_score,
    formality_level,
    token_diversity,
    compound_words,
    technical_terms,
    proper_nouns,
    created_at
FROM vietnamese_text_analysis 
WHERE document_id = '[DOCUMENT_ID]'
ORDER BY created_at;
```

**Cần kiểm tra:**
- [ ] Có records cho từng chunk hoặc document level
- [ ] `language_quality_score` > 70 (chất lượng tiếng Việt tốt)
- [ ] `diacritics_density` > 0.5 (50% từ có dấu)
- [ ] `readability_score` > 0.5
- [ ] `compound_words` array có elements
- [ ] `technical_terms` array có elements (nếu là technical document)
- [ ] `proper_nouns` array có elements

### **BƯỚC 4: KIỂM TRA DATA INGESTION JOBS** ✅

#### **4.1. Kiểm tra Ingestion Jobs**
```sql
-- Query ingestion jobs:
SELECT 
    job_id,
    document_id,
    source_file,
    status,
    current_stage,
    total_chunks,
    processed_chunks,
    failed_chunks,
    quality_score,
    quality_passed,
    processing_duration_ms,
    chunking_method,
    embedding_model,
    created_at,
    completed_at
FROM data_ingestion_jobs 
WHERE document_id = '[DOCUMENT_ID]'
ORDER BY created_at DESC;
```

**Cần kiểm tra:**
- [ ] `status` = 'COMPLETED'
- [ ] `current_stage` = 'indexing' (final stage)
- [ ] `total_chunks` = chunk count từ bước 2
- [ ] `processed_chunks` = `total_chunks`
- [ ] `failed_chunks` = 0
- [ ] `quality_score` > 70
- [ ] `quality_passed` = true
- [ ] `processing_duration_ms` > 0
- [ ] `completed_at` không null

#### **4.2. Kiểm tra Chunk Processing Logs**
```sql
-- Query processing logs:
SELECT 
    job_id,
    stage,
    status,
    COUNT(*) as stage_count,
    AVG(processing_time_ms) as avg_time,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count
FROM chunk_processing_logs 
WHERE job_id = '[JOB_ID]'  -- Từ query trước
GROUP BY job_id, stage, status
ORDER BY stage;
```

**Cần kiểm tra:**
- [ ] Có logs cho tất cả stages: quality_control, chunking, embedding, storage, indexing
- [ ] `status` = 'success' cho tất cả stages
- [ ] `success_count` > 0 cho mỗi stage

### **BƯỚC 5: KIỂM TRA CÁC THIẾU SÓT** ❌

#### **5.1. Document Signatures (MISSING TABLE)**
```sql
-- Table này chưa tồn tại trong schema V5
-- Cần tạo table để lưu signatures/ folder content
SELECT 'document_signatures table MISSING' as status;
```

**Cần tạo table:**
- [ ] `document_signatures` table tồn tại
- [ ] Data từ `file_fingerprints.json` đã import
- [ ] Data từ `content_signatures.json` đã import  
- [ ] Data từ `semantic_features.json` đã import

#### **5.2. Vector Database Config (MISSING TABLE)**
```sql
-- Table này chưa tồn tại trong schema V5  
-- Cần tạo table để lưu FOR_VECTOR_DB/ content
SELECT 'vector_database_config table MISSING' as status;
```

**Cần tạo table:**
- [ ] `vector_database_config` table tồn tại
- [ ] Data từ `embeddings_preparation.json` đã import
- [ ] Data từ `similarity_features.json` đã import
- [ ] `collection_name` được set đúng

#### **5.3. Search Engine Config (MISSING TABLE)**
```sql
-- Table này chưa tồn tại trong schema V5
-- Cần tạo table để lưu FOR_SEARCH/ content  
SELECT 'search_engine_config table MISSING' as status;
```

**Cần tạo table:**
- [ ] `search_engine_config` table tồn tại
- [ ] Data từ `search_config.json` đã import
- [ ] Data từ `bm25_tokens.json` config đã import

#### **5.4. Export Package Metadata (MISSING TABLE)**
```sql
-- Table này chưa tồn tại trong schema V5
-- Cần tạo table để lưu manifest.json + user_info.json
SELECT 'export_package_metadata table MISSING' as status;
```

**Cần tạo table:**
- [ ] `export_package_metadata` table tồn tại  
- [ ] Data từ `manifest.json` đã import
- [ ] Data từ `user_info.json` đã import

### **BƯỚC 6: KIỂM TRA SEARCH FUNCTIONALITY** ✅

#### **6.1. Test Full-text Search**
```sql
-- Test search tokens:
SELECT 
    document_id,
    title,
    ts_rank(search_tokens, plainto_tsquery('vietnamese', 'chính sách')) as rank
FROM documents_metadata_v2 
WHERE search_tokens @@ plainto_tsquery('vietnamese', 'chính sách')
ORDER BY rank DESC;
```

**Cần kiểm tra:**
- [ ] Query trả về results
- [ ] `rank` > 0 cho documents liên quan
- [ ] Search hoạt động với tiếng Việt

#### **6.2. Test Vietnamese Search**
```sql
-- Test normalized search:
SELECT 
    document_id,
    title,
    search_text_normalized
FROM documents_metadata_v2 
WHERE search_text_normalized ILIKE '%chinh sach%'  -- Không dấu
OR search_text_normalized ILIKE '%chính sách%';   -- Có dấu
```

**Cần kiểm tra:**
- [ ] Cả 2 queries đều trả về kết quả
- [ ] `search_text_normalized` có content

### **BƯỚC 7: PERFORMANCE CHECK** ✅

#### **7.1. Kiểm tra Indexes**
```sql
-- Kiểm tra indexes được tạo:
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public'
AND (tablename LIKE 'document%' OR tablename LIKE 'data_ingestion%')
ORDER BY tablename, indexname;
```

**Cần kiểm tra:**
- [ ] Có index cho `documents_metadata_v2` trên các trường quan trọng
- [ ] Có GIN index cho `search_tokens`
- [ ] Có index cho `document_chunks_enhanced` 
- [ ] Có index cho foreign keys

#### **7.2. Kiểm tra Performance**
```sql
-- Test query performance:
EXPLAIN ANALYZE 
SELECT * FROM documents_metadata_v2 
WHERE search_tokens @@ plainto_tsquery('vietnamese', 'test');
```

**Cần kiểm tra:**
- [ ] Query time < 100ms
- [ ] Sử dụng Index Scan (không phải Seq Scan)

---

## **📊 SUMMARY CHECKLIST**

### **HOÀN THÀNH** ✅
- [ ] **Document Metadata**: documents_metadata_v2 có đầy đủ data
- [ ] **Chunks**: document_chunks_enhanced có 3-7 chunks properly sized
- [ ] **Vietnamese Analysis**: vietnamese_text_analysis có quality scores  
- [ ] **BM25 Index**: document_bm25_index có terms được index
- [ ] **Jobs**: data_ingestion_jobs có status COMPLETED
- [ ] **Processing Logs**: chunk_processing_logs có success records
- [ ] **Search**: Full-text search hoạt động với tiếng Việt

### **CHƯA HOÀN THÀNH** ❌  
- [ ] **Document Signatures**: Table chưa tồn tại (signatures/ folder)
- [ ] **Vector DB Config**: Table chưa tồn tại (FOR_VECTOR_DB/ folder)
- [ ] **Search Config**: Table chưa tồn tại (FOR_SEARCH/ folder) 
- [ ] **Package Metadata**: Table chưa tồn tại (manifest.json, user_info.json)

### **PERCENTAGE HOÀN THÀNH: ~75%**

**Cần bổ sung 4 tables để đạt 100% export package support.**
