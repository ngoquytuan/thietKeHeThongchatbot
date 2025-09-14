Dựa trên cấu trúc export FR03.1 và schema FR-02.1 v2.0, đây là phân loại xử lý từng loại file:

## 📥 **FILES IMPORT TRỰC TIẾP VÀO DATABASE**

### **PostgreSQL Direct Import**
```bash
# Import ngay vào bảng mà không cần xử lý thêm
FOR_DATABASE/document_metadata_v2.json     → documents_metadata_v2 table
FOR_DATABASE/ingestion_job_metadata.json   → data_ingestion_jobs table
FOR_DATABASE/database_ready_check.json     → chunk_processing_logs table (status)
```

**SQL Import Example:**
```sql
-- Direct JSON import
INSERT INTO documents_metadata_v2 
SELECT * FROM json_populate_recordset(null::documents_metadata_v2, 
    pg_read_file('/import/document_metadata_v2.json')::json);
```

## ⚙️ **FILES CẦN XỬ LÝ TRƯỚC KHI IMPORT**

### **1. Enhanced Processing Required**
```bash
# Cần enrich thêm data trước khi insert
FOR_DATABASE/chunks_enhanced_v2.jsonl     → document_chunks_enhanced table
FOR_DATABASE/vietnamese_analysis_v2.json  → vietnamese_text_analysis table  
FOR_SEARCH/search_document.json          → Update search_tokens fields
```

**Processing Pipeline:**
```python
# chunks_enhanced_v2.jsonl processing
def process_chunks_for_database(chunks_file):
    chunks = read_jsonl(chunks_file)
    
    for chunk in chunks:
        # Generate BM25 tokens
        chunk['bm25_tokens'] = generate_tsvector(chunk['chunk_content'])
        
        # Calculate overlap references
        chunk['overlap_source_prev'] = find_overlap_source(chunk, 'prev')
        chunk['overlap_source_next'] = find_overlap_source(chunk, 'next')
        
        # Validate embedding dimensions
        if chunk['embedding_dimensions'] != 1024:
            chunk['embedding_dimensions'] = 1024  # Qwen default
    
    return chunks

# vietnamese_analysis processing  
def process_vietnamese_analysis(analysis_file):
    analysis = read_json(analysis_file)
    
    # Normalize quality scores to database format
    analysis['language_quality_score'] = round(analysis['vietnamese_specific']['language_purity'] * 10, 1)
    analysis['diacritics_density'] = analysis['vietnamese_specific']['diacritics_density'] 
    analysis['token_diversity'] = calculate_token_diversity(analysis['word_segmentation'])
    
    return analysis
```

### **2. Vector Database Processing**
```bash
# Xử lý để tạo embeddings và insert vào ChromaDB  
FOR_VECTOR_DB/embeddings_preparation.json → ChromaDB collections
FOR_VECTOR_DB/similarity_features.json   → Deduplication processing
```

**ChromaDB Processing:**
```python
def process_for_chroma(embeddings_prep_file):
    data = read_json(embeddings_prep_file)
    
    # Generate embeddings using Qwen model
    embedding_model = SentenceTransformer('Qwen/Qwen3-Embedding-0.6B')
    
    chroma_docs = []
    for item in data['chunks']:
        # Generate 1024-dim embeddings
        embedding = embedding_model.encode(item['content']).tolist()
        
        chroma_doc = {
            'id': item['chunk_id'],
            'embedding': embedding,
            'document': item['content'],
            'metadata': {
                'document_id': item['document_id'],
                'access_level': item['access_level'],
                'department': item['department'],
                'language': 'vi',
                'quality_score': item.get('chunk_quality_score', 0.8)
            }
        }
        chroma_docs.append(chroma_doc)
    
    return chroma_docs
```

## 🚫 **FILES KHÔNG ĐƯỢC XỬ LÝ/IMPORT**

### **Reference Only Files**
```bash
# Chỉ để tham khảo, không import vào database
manifest.json                    # Package summary only
user_info.json                   # Creator context only  
processed/document.md             # Human-readable format only
signatures/file_fingerprints.json # File integrity checking only
signatures/content_signatures.json # Content deduplication only
validation/processing_stats.json   # Processing metrics only
FOR_SEARCH/search_config.json     # Elasticsearch config only
```

### **Archive Files** 
```bash
# Lưu trữ tham chiếu, không active processing
signatures/semantic_features.json # Semantic analysis archive
validation/quality_score.json    # Quality assessment archive (used v2 instead)
```

## 📁 **STRATEGIC FILE STORAGE**

### **1. Database Storage (PostgreSQL)**
```sql
-- File gốc reference trong database
ALTER TABLE documents_metadata_v2 ADD COLUMN file_storage_info JSONB DEFAULT '{}';

-- Example storage info
{
  "original_file": {
    "path": "/storage/original/HR_POLICY_20250912_143022/original/employee_handbook.pdf",
    "size_bytes": 2847392,
    "checksum": "sha256:abc123...",
    "storage_tier": "warm"
  },
  "processed_files": {
    "export_package": "/storage/processed/HR_POLICY_20250912_143022.zip",
    "extraction_timestamp": "2025-09-12T14:30:22Z"
  }
}
```

### **2. File System Storage Strategy**

#### **Hot Storage (SSD) - Active Access**
```bash
/opt/chatbot-data/
├── processed/           # Processed packages ready for import
│   ├── pending/         # Awaiting import
│   ├── processing/      # Currently being imported  
│   └── completed/       # Successfully imported
├── temp/               # Temporary processing space
└── failed/             # Failed import packages
```

#### **Warm Storage (HDD) - Archive Access**
```bash
/opt/chatbot-archive/
├── original/                    # Original uploaded files
│   └── {DEPT}/{YYYY-MM}/       # Organized by department and date
│       └── {DEPT}_{TYPE}_{TIMESTAMP}/
│           └── original/        # Original file preservation
└── export-packages/            # Complete FR03.1 export packages
    └── {DEPT}_{TYPE}_{TIMESTAMP}.zip
```

#### **Cold Storage (Object Storage) - Long-term Archive**
```bash
# AWS S3 or equivalent
s3://chatbot-archive/
├── original-files/
│   └── {year}/{month}/{DEPT}_{TYPE}_{TIMESTAMP}/
└── export-packages/
    └── {year}/{month}/{DEPT}_{TYPE}_{TIMESTAMP}.zip
```

### **3. Storage Lifecycle Policy**
```python
STORAGE_POLICY = {
    "hot_storage": {
        "location": "/opt/chatbot-data/",
        "retention_days": 30,
        "purpose": "active processing and recent access"
    },
    "warm_storage": {
        "location": "/opt/chatbot-archive/", 
        "retention_months": 12,
        "purpose": "reference and compliance"
    },
    "cold_storage": {
        "location": "s3://chatbot-archive/",
        "retention_years": 7,
        "purpose": "legal compliance and disaster recovery"
    }
}
```

## 🔄 **IMPORT WORKFLOW SEQUENCE**

### **1. Pre-Import Validation**
```python
def validate_export_package(zip_path):
    checks = {
        "manifest_exists": check_file_exists(zip_path, "manifest.json"),
        "database_files_complete": check_database_files(zip_path),
        "quality_thresholds_met": validate_quality_scores(zip_path),
        "vietnamese_processing_done": check_vietnamese_analysis(zip_path),
        "chunk_integrity": validate_chunk_consistency(zip_path)
    }
    return all(checks.values()), checks
```

### **2. Import Sequence**
```bash
# Step 1: Extract and validate package
extract_package() → /opt/chatbot-data/processing/{job_id}/

# Step 2: Direct database imports
import_job_metadata() → data_ingestion_jobs table
import_document_metadata() → documents_metadata_v2 table  

# Step 3: Processed imports  
process_and_import_chunks() → document_chunks_enhanced table
process_and_import_analysis() → vietnamese_text_analysis table

# Step 4: Vector database import
generate_embeddings_and_import() → ChromaDB collections

# Step 5: Search index update
update_search_vectors() → PostgreSQL TSVECTOR fields

# Step 6: Move to completed storage
archive_package() → /opt/chatbot-data/completed/
```

### **3. Error Handling & Rollback**
```python
def rollback_import(job_id):
    # Remove database entries
    delete_from_tables(['documents_metadata_v2', 'document_chunks_enhanced'], 
                      where={'ingestion_job_id': job_id})
    
    # Remove from ChromaDB
    chroma_collection.delete(where={"job_id": job_id})
    
    # Move package to failed directory
    move_package(f"/opt/chatbot-data/processing/{job_id}/", 
                f"/opt/chatbot-data/failed/{job_id}/")
```

Cấu trúc này đảm bảo hiệu quả xử lý, khả năng trace back đầy đủ và tuân thủ compliance requirements trong khi tối ưu storage costs.
