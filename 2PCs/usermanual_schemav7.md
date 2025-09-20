# HƯỚNG DẪN SỬ DỤNG 01_init_database_V7.sql
## Database Architecture Guide cho Hệ thống Chatbot Tiếng Việt

---

**Phiên bản**: V7.0  
**Ngày**: 20/09/2025  
**Mục đích**: Hướng dẫn toàn diện cho deployment và sử dụng database schema V7  
**Đối tượng**: Development Team, DevOps, Data Engineers  

---

## 1. TỔNG QUAN KIẾN TRÚC DATABASE V7

### 1.1 Thiết kế Dual ID System

```mermaid
graph TD
    subgraph "FR-03.1 Export Package"
        A[Business ID: POLICY_-_CHINH_SACH_xinNghi_20250919_170525]
        B[Export Package ZIP]
    end
    
    subgraph "FR-03.3 Data Ingestion"
        C[Read Business ID]
        D{Document exists?}
        E[Create Database UUID]
        F[Use Existing UUID]
    end
    
    subgraph "Database V7"
        G[(documents_metadata_v2)]
        H[(data_ingestion_jobs)]
        I[(document_chunks_enhanced)]
        J[(Vector & Search Tables)]
    end
    
    A --> C
    C --> D
    D -->|New| E
    D -->|Duplicate| F
    E --> G
    F --> G
    G --> H
    G --> I
    G --> J
    
    classDef fr031 fill:#e3f2fd,stroke:#1976d2
    classDef fr033 fill:#e8f5e8,stroke:#388e3c
    classDef database fill:#fff3e0,stroke:#f57c00
    
    class A,B fr031
    class C,D,E,F fr033
    class G,H,I,J database
```

### 1.2 Core Tables Overview

| Table Group | Tables | Mục đích | Module sử dụng |
|-------------|--------|----------|----------------|
| **User Management** | users, user_sessions, user_events | Authentication & Authorization | All modules |
| **Document Core** | documents_metadata_v2, document_chunks_enhanced | Document storage & chunking | FR-03.3, FR-04, FR-05 |
| **Export Package** | document_signatures, vector_database_config, search_engine_config | FR-03.1 package mapping | FR-03.3 |
| **Processing Pipeline** | data_ingestion_jobs, chunk_processing_logs, pipeline_metrics | FR-03.3 processing tracking | FR-03.3, Monitoring |
| **Search & Analytics** | search_analytics, vietnamese_text_analysis, document_bm25_index | Search optimization | FR-04, FR-05 |

---

## 2. DATABASE DEPLOYMENT

### 2.1 Prerequisites

```bash
# System requirements
PostgreSQL 15+
RAM: 8GB+ (16GB recommended)
Storage: 50GB+ SSD
CPU: 4+ cores

# Required extensions (được tự động install)
uuid-ossp
pg_trgm  
btree_gin
unaccent
```

### 2.2 Deployment Steps

```bash
# Step 1: Backup existing database (nếu có)
pg_dump -U kb_admin -h localhost -d knowledge_base_v2 > backup_$(date +%Y%m%d_%H%M%S).sql

# Step 2: Deploy V7 schema
psql -U kb_admin -h localhost -d knowledge_base_v2 -f 01_init_database_V7.sql

# Step 3: Verify deployment
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "
SELECT version, applied_at, description 
FROM schema_migrations 
ORDER BY applied_at DESC 
LIMIT 5;"

# Expected output: V7 migration với timestamp mới nhất
```

### 2.3 Post-deployment Validation

```sql
-- Check table count (should be 25)
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check indexes count (should be 50+)
SELECT COUNT(*) as index_count 
FROM pg_indexes 
WHERE schemaname = 'public';

-- Check sample data
SELECT COUNT(*) as sample_documents 
FROM documents_metadata_v2 
WHERE source_document_id LIKE 'POLICY_%';

-- Expected: 3 sample documents with source_document_id
```

---

## 3. FR-03.3 DATA IMPORT PROCESS

### 3.1 Export Package → Database Mapping

```python
# Complete mapping structure
EXPORT_PACKAGE_MAPPING = {
    "manifest.json": {
        "table": "export_package_metadata",
        "field": "manifest_data",
        "required": True
    },
    "user_info.json": {
        "table": "export_package_metadata", 
        "field": "user_info",
        "required": True
    },
    "signatures/file_fingerprints.json": {
        "table": "document_signatures",
        "field": "file_fingerprints",
        "required": False
    },
    "signatures/content_signatures.json": {
        "table": "document_signatures",
        "field": "content_signatures", 
        "required": False
    },
    "signatures/semantic_features.json": {
        "table": "document_signatures",
        "field": "semantic_features",
        "required": False
    },
    "validation/quality_score.json": {
        "table": "vietnamese_text_analysis",
        "field": "language_quality_score + readability_score",
        "required": True
    },
    "validation/processing_stats.json": {
        "table": "data_ingestion_jobs",
        "field": "processing_metadata",
        "required": False
    },
    "FOR_DATABASE/document_metadata.json": {
        "table": "documents_metadata_v2",
        "field": "core document fields",
        "required": True,
        "priority": "HIGH"
    },
    "FOR_DATABASE/chunks_enhanced.jsonl": {
        "table": "document_chunks_enhanced", 
        "field": "all chunk fields",
        "required": True,
        "priority": "HIGH"
    },
    "FOR_DATABASE/vietnamese_analysis.json": {
        "table": "vietnamese_text_analysis",
        "field": "all analysis fields",
        "required": True,
        "priority": "HIGH"
    },
    "FOR_VECTOR_DB/embeddings_preparation.json": {
        "table": "vector_database_config",
        "field": "embeddings_preparation",
        "required": True
    },
    "FOR_VECTOR_DB/similarity_features.json": {
        "table": "vector_database_config",
        "field": "similarity_features", 
        "required": False
    },
    "FOR_SEARCH/search_document.json": {
        "table": "search_engine_config",
        "field": "search_document",
        "required": True
    },
    "FOR_SEARCH/search_config.json": {
        "table": "search_engine_config",
        "field": "search_config",
        "required": True
    },
    "FOR_SEARCH/bm25_tokens.json": {
        "table": "search_engine_config",
        "field": "bm25_config",
        "required": True
    }
}
```

### 3.2 Complete Import Function (Template)

```python
import asyncio
import json
import zipfile
from pathlib import Path
from uuid import uuid4
import asyncpg

class ExportPackageImporter:
    def __init__(self, db_pool):
        self.db_pool = db_pool
        
    async def import_export_package(self, package_path: str, user_id: str = None):
        """
        Complete import của export package vào database V7
        
        Args:
            package_path: Path to .zip file
            user_id: UUID của user thực hiện import
            
        Returns:
            dict: Import result với job_id và document_id
        """
        
        # Step 1: Extract và validate package
        package_data = self.extract_package(package_path)
        
        # Step 2: Đọc source_document_id từ FOR_DATABASE/document_metadata.json
        doc_metadata = package_data["FOR_DATABASE"]["document_metadata.json"]
        source_document_id = doc_metadata.get("source_document_id")
        
        if not source_document_id:
            raise ValueError("Missing source_document_id in document_metadata.json")
        
        # Step 3: Check duplicate bằng business ID
        async with self.db_pool.acquire() as conn:
            existing_doc = await conn.fetchrow("""
                SELECT document_id, title, created_at 
                FROM documents_metadata_v2 
                WHERE source_document_id = $1
            """, source_document_id)
            
        # Step 4: Tạo database UUIDs
        if existing_doc:
            database_document_id = existing_doc['document_id']
            is_duplicate = True
            print(f"DUPLICATE DETECTED: {source_document_id} -> {database_document_id}")
        else:
            database_document_id = uuid4()
            is_duplicate = False
            print(f"NEW DOCUMENT: {source_document_id} -> {database_document_id}")
            
        job_id = uuid4()
        
        # Step 5: Tạo ingestion job
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO data_ingestion_jobs (
                    job_id, document_id, source_document_id, source_file, 
                    package_path, status, user_id, job_type,
                    import_mapping_status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, job_id, database_document_id, source_document_id,
                 Path(package_path).name, package_path, 'PROCESSING',
                 user_id, 'export_package_import', {})
        
        # Step 6: Import từng component theo thứ tự ưu tiên
        import_results = {}
        
        try:
            # 6.1 Import core document data (HIGH priority)
            if not is_duplicate:
                import_results['document_metadata'] = await self.import_document_metadata(
                    package_data["FOR_DATABASE"]["document_metadata.json"], 
                    database_document_id
                )
                
                import_results['chunks'] = await self.import_document_chunks(
                    package_data["FOR_DATABASE"]["chunks_enhanced.jsonl"],
                    database_document_id  
                )
                
                import_results['vietnamese_analysis'] = await self.import_vietnamese_analysis(
                    package_data["FOR_DATABASE"]["vietnamese_analysis.json"],
                    database_document_id
                )
            
            # 6.2 Import package metadata
            import_results['package_metadata'] = await self.import_package_metadata(
                package_data, database_document_id, package_path
            )
            
            # 6.3 Import signatures
            if "signatures" in package_data:
                import_results['signatures'] = await self.import_signatures(
                    package_data["signatures"], database_document_id
                )
            
            # 6.4 Import vector config
            if "FOR_VECTOR_DB" in package_data:
                import_results['vector_config'] = await self.import_vector_config(
                    package_data["FOR_VECTOR_DB"], database_document_id
                )
            
            # 6.5 Import search config
            if "FOR_SEARCH" in package_data:
                import_results['search_config'] = await self.import_search_config(
                    package_data["FOR_SEARCH"], database_document_id
                )
            
            # Step 7: Update job status và mapping status
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE data_ingestion_jobs 
                    SET status = 'COMPLETED', 
                        completed_at = NOW(),
                        import_mapping_status = $1,
                        processing_metadata = $2
                    WHERE job_id = $3
                """, json.dumps(import_results), 
                     json.dumps({"package_size": len(package_data)}), 
                     job_id)
            
            return {
                "job_id": str(job_id),
                "document_id": str(database_document_id), 
                "source_document_id": source_document_id,
                "is_duplicate": is_duplicate,
                "import_results": import_results,
                "status": "SUCCESS"
            }
            
        except Exception as e:
            # Rollback on error
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE data_ingestion_jobs 
                    SET status = 'FAILED', 
                        error_message = $1,
                        completed_at = NOW()
                    WHERE job_id = $2
                """, str(e), job_id)
            
            print(f"Import failed for {source_document_id}: {e}")
            raise

    async def import_document_metadata(self, metadata_json, document_id):
        """Import document metadata vào documents_metadata_v2"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO documents_metadata_v2 (
                    document_id, source_document_id, title, content,
                    document_type, access_level, department_owner, author,
                    language_detected, file_size_bytes, status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (document_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    updated_at = NOW()
            """, 
                document_id,
                metadata_json.get("source_document_id"),
                metadata_json.get("title"),
                metadata_json.get("content", ""),
                metadata_json.get("document_type", "other"),
                metadata_json.get("access_level", "employee_only"), 
                metadata_json.get("department_owner"),
                metadata_json.get("author"),
                metadata_json.get("language", "vi"),
                metadata_json.get("file_size_bytes", 0),
                "approved"
            )
        return {"status": "success", "document_id": str(document_id)}

    async def import_document_chunks(self, chunks_jsonl, document_id):
        """Import chunks từ JSONL file"""
        chunks = []
        for line in chunks_jsonl.strip().split('\n'):
            if line.strip():
                chunks.append(json.loads(line))
        
        async with self.db_pool.acquire() as conn:
            for i, chunk_data in enumerate(chunks):
                chunk_id = uuid4()
                await conn.execute("""
                    INSERT INTO document_chunks_enhanced (
                        chunk_id, document_id, chunk_content, chunk_position,
                        chunk_size_tokens, semantic_boundary, chunk_method,
                        chunk_quality_score, embedding_model
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                    chunk_id, document_id,
                    chunk_data.get("content"),
                    chunk_data.get("position", i),
                    chunk_data.get("token_count", 0),
                    chunk_data.get("semantic_boundary", False),
                    chunk_data.get("method", "semantic_boundary"),
                    chunk_data.get("quality_score", 0.8),
                    chunk_data.get("embedding_model", "Qwen/Qwen3-Embedding-0.6B")
                )
        
        return {"status": "success", "chunks_imported": len(chunks)}

    # Additional import methods...
    # (import_vietnamese_analysis, import_package_metadata, etc.)
```

### 3.3 Import Monitoring

```sql
-- Query để theo dõi import progress
SELECT 
    dij.source_document_id,
    dij.database_document_id as document_id,
    dij.status,
    dij.package_path,
    d.title,
    dij.import_mapping_status,
    dij.created_at,
    dij.completed_at,
    CASE 
        WHEN dij.completed_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (dij.completed_at - dij.created_at))
        ELSE NULL 
    END as processing_duration_seconds
FROM data_ingestion_jobs dij
LEFT JOIN documents_metadata_v2 d ON dij.document_id = d.document_id
WHERE dij.job_type = 'export_package_import'
ORDER BY dij.created_at DESC
LIMIT 10;

-- Detailed import status view
SELECT * FROM vw_export_package_import_status 
WHERE job_status IN ('PROCESSING', 'FAILED')
ORDER BY job_status DESC;
```

---

## 4. MODULE INTEGRATION GUIDELINES

### 4.1 FR-04 RAG Core Engine

#### 4.1.1 Document Retrieval

```python
# Hybrid search: BM25 + Semantic
async def hybrid_search(query: str, user_level: str = "EMPLOYEE", limit: int = 10):
    """
    Tìm kiếm documents sử dụng hybrid BM25 + semantic search
    """
    
    async with db_pool.acquire() as conn:
        # BM25 search với access control
        bm25_results = await conn.fetch("""
            SELECT DISTINCT
                d.document_id,
                d.title,
                d.source_document_id,
                ts_rank(d.search_tokens, plainto_tsquery('vietnamese', $1)) as bm25_score,
                d.department_owner,
                d.document_type
            FROM documents_metadata_v2 d
            WHERE d.search_tokens @@ plainto_tsquery('vietnamese', $1)
                AND d.status = 'approved'
                AND (
                    d.access_level = 'public' OR
                    ($2 = 'SYSTEM_ADMIN') OR
                    ($2 = 'DIRECTOR' AND d.access_level IN ('public', 'employee_only', 'manager_only')) OR
                    ($2 = 'MANAGER' AND d.access_level IN ('public', 'employee_only')) OR
                    ($2 = 'EMPLOYEE' AND d.access_level IN ('public', 'employee_only'))
                )
            ORDER BY bm25_score DESC
            LIMIT $3
        """, query, user_level, limit)
        
        # Semantic search trên chunks
        semantic_results = await conn.fetch("""
            SELECT 
                c.document_id,
                c.chunk_content,
                c.chunk_position,
                c.chunk_quality_score,
                d.title,
                d.source_document_id
            FROM document_chunks_enhanced c
            JOIN documents_metadata_v2 d ON c.document_id = d.document_id
            WHERE d.status = 'approved'
                AND c.chunk_quality_score > 0.5
                -- Semantic similarity sẽ được tính bằng vector embeddings
            ORDER BY c.chunk_quality_score DESC
            LIMIT $1
        """, limit)
        
        return {
            "bm25_results": bm25_results,
            "semantic_results": semantic_results,
            "query": query,
            "user_level": user_level
        }
```

#### 4.1.2 Vector Database Integration

```python
# ChromaDB integration với database V7
async def prepare_vector_data(document_id: str):
    """
    Lấy vector config và chunk data cho ChromaDB
    """
    
    async with db_pool.acquire() as conn:
        # Lấy vector config
        vector_config = await conn.fetchrow("""
            SELECT 
                vdc.embeddings_preparation,
                vdc.similarity_features,
                vdc.collection_name
            FROM vector_database_config vdc
            WHERE vdc.document_id = $1
        """, document_id)
        
        # Lấy chunks để tạo embeddings
        chunks = await conn.fetch("""
            SELECT 
                chunk_id,
                chunk_content,
                chunk_position,
                chunk_size_tokens,
                embedding_model
            FROM document_chunks_enhanced
            WHERE document_id = $1
            ORDER BY chunk_position
        """, document_id)
        
        return {
            "vector_config": vector_config,
            "chunks": chunks,
            "embedding_model": chunks[0]['embedding_model'] if chunks else "Qwen/Qwen3-Embedding-0.6B"
        }
```

### 4.2 FR-05 Chatbot UI

#### 4.2.1 Document Discovery

```python
# Document browsing với filtering
async def get_documents_for_ui(
    user_level: str,
    department: str = None,
    document_type: str = None,
    page: int = 1,
    page_size: int = 20
):
    """
    Lấy danh sách documents cho UI với pagination và filtering
    """
    
    offset = (page - 1) * page_size
    
    async with db_pool.acquire() as conn:
        where_conditions = ["d.status = 'approved'"]
        params = [user_level]
        param_count = 1
        
        # Access control
        if user_level != 'SYSTEM_ADMIN':
            access_levels = {
                'DIRECTOR': ['public', 'employee_only', 'manager_only'],
                'MANAGER': ['public', 'employee_only'],
                'EMPLOYEE': ['public', 'employee_only'],
                'GUEST': ['public']
            }
            param_count += 1
            where_conditions.append(f"d.access_level = ANY(${param_count})")
            params.append(access_levels.get(user_level, ['public']))
        
        # Department filter
        if department:
            param_count += 1
            where_conditions.append(f"d.department_owner = ${param_count}")
            params.append(department)
            
        # Document type filter  
        if document_type:
            param_count += 1
            where_conditions.append(f"d.document_type = ${param_count}")
            params.append(document_type)
        
        # Add pagination params
        params.extend([page_size, offset])
        
        query = f"""
            SELECT 
                d.document_id,
                d.source_document_id,
                d.title,
                d.document_type,
                d.department_owner,
                d.author,
                d.created_at,
                d.chunk_count,
                d.file_size_bytes,
                dus.view_count,
                dus.download_count
            FROM documents_metadata_v2 d
            LEFT JOIN document_usage_stats dus ON d.document_id = dus.document_id
            WHERE {' AND '.join(where_conditions)}
            ORDER BY d.created_at DESC
            LIMIT ${len(params)-1} OFFSET ${len(params)}
        """
        
        results = await conn.fetch(query, *params)
        
        # Get total count for pagination
        count_query = f"""
            SELECT COUNT(*) as total
            FROM documents_metadata_v2 d
            WHERE {' AND '.join(where_conditions)}
        """
        total_count = await conn.fetchval(count_query, *params[:-2])
        
        return {
            "documents": results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total_count,
                "pages": (total_count + page_size - 1) // page_size
            }
        }
```

#### 4.2.2 Search Analytics Integration

```python
# Track search analytics cho UI
async def track_search_analytics(
    user_id: str,
    query: str,
    search_method: str,
    results_count: int,
    processing_time_ms: int,
    session_id: str = None
):
    """
    Record search analytics cho monitoring và optimization
    """
    
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO search_analytics (
                user_id, session_id, query, query_normalized,
                search_method, results_count, has_results,
                processing_time_ms, timestamp
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
        """, 
            user_id, session_id, query, 
            query.lower().strip(),  # Normalized query
            search_method, results_count, results_count > 0,
            processing_time_ms
        )
```

### 4.3 Performance Optimization Guidelines

#### 4.3.1 Index Usage

```sql
-- Kiểm tra index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as usage_count,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Kiểm tra slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
WHERE query LIKE '%documents_metadata_v2%'
ORDER BY mean_time DESC
LIMIT 10;
```

#### 4.3.2 Connection Pooling

```python
# Recommended connection pool configuration
import asyncpg

DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "kb_admin", 
    "password": "1234567890",
    "database": "knowledge_base_v2",
    "min_size": 10,      # Minimum connections
    "max_size": 50,      # Maximum connections  
    "max_queries": 50000, # Max queries per connection
    "max_inactive_connection_lifetime": 300.0  # 5 minutes
}

async def create_db_pool():
    return await asyncpg.create_pool(**DATABASE_CONFIG)
```

---

## 5. MONITORING & MAINTENANCE

### 5.1 Performance Monitoring

```sql
-- Daily monitoring queries
-- 1. Import job status summary
SELECT 
    DATE(created_at) as date,
    status,
    COUNT(*) as job_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_duration_seconds
FROM data_ingestion_jobs
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(created_at), status
ORDER BY date DESC, status;

-- 2. Search performance
SELECT 
    DATE(timestamp) as date,
    search_method,
    COUNT(*) as search_count,
    AVG(processing_time_ms) as avg_processing_time,
    AVG(results_count) as avg_results_count,
    SUM(CASE WHEN has_results THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as success_rate
FROM search_analytics
WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(timestamp), search_method
ORDER BY date DESC, search_method;

-- 3. Database size monitoring
SELECT 
    pg_size_pretty(pg_database_size('knowledge_base_v2')) as database_size,
    pg_size_pretty(pg_total_relation_size('documents_metadata_v2')) as documents_table_size,
    pg_size_pretty(pg_total_relation_size('document_chunks_enhanced')) as chunks_table_size;
```

### 5.2 Backup Strategy

```bash
#!/bin/bash
# daily_backup.sh

DB_NAME="knowledge_base_v2"
DB_USER="kb_admin"
BACKUP_DIR="/opt/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

# Full database backup
pg_dump -U $DB_USER -h localhost -d $DB_NAME > $BACKUP_DIR/full_backup_$DATE.sql

# Schema-only backup
pg_dump -U $DB_USER -h localhost -d $DB_NAME --schema-only > $BACKUP_DIR/schema_backup_$DATE.sql

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### 5.3 Health Checks

```python
# Health check script
async def database_health_check():
    """
    Comprehensive database health check
    """
    
    health_status = {
        "database": "healthy",
        "tables": {},
        "performance": {},
        "errors": []
    }
    
    try:
        async with db_pool.acquire() as conn:
            # Check table counts
            tables_check = await conn.fetch("""
                SELECT 
                    table_name,
                    (xpath('/row/cnt/text()', 
                           query_to_xml(format('SELECT COUNT(*) as cnt FROM %I', table_name), 
                                       false, true, '')))[1]::text::int as row_count
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                    AND table_name IN ('documents_metadata_v2', 'document_chunks_enhanced', 'data_ingestion_jobs')
            """)
            
            for table in tables_check:
                health_status["tables"][table['table_name']] = table['row_count']
            
            # Check recent import jobs
            recent_jobs = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM data_ingestion_jobs 
                WHERE created_at >= NOW() - INTERVAL '1 hour'
                    AND status = 'FAILED'
            """)
            
            if recent_jobs > 5:
                health_status["errors"].append(f"High failure rate: {recent_jobs} failed jobs in last hour")
                health_status["database"] = "degraded"
            
            # Check database size
            db_size = await conn.fetchval("""
                SELECT pg_database_size('knowledge_base_v2')
            """)
            health_status["performance"]["database_size_mb"] = db_size // (1024 * 1024)
            
    except Exception as e:
        health_status["database"] = "unhealthy"
        health_status["errors"].append(str(e))
    
    return health_status
```

---

## 6. TROUBLESHOOTING GUIDE

### 6.1 Common Issues

#### 6.1.1 Duplicate Key Errors

```sql
-- Problem: Duplicate source_document_id
-- Solution: Check và resolve conflicts
SELECT 
    source_document_id,
    COUNT(*) as duplicate_count,
    array_agg(document_id) as document_ids
FROM documents_metadata_v2 
WHERE source_document_id IS NOT NULL
GROUP BY source_document_id 
HAVING COUNT(*) > 1;

-- Fix duplicates by updating source_document_id
UPDATE documents_metadata_v2 
SET source_document_id = source_document_id || '_' || EXTRACT(EPOCH FROM created_at)
WHERE document_id IN (
    SELECT document_id FROM (
        SELECT document_id, 
               ROW_NUMBER() OVER (PARTITION BY source_document_id ORDER BY created_at) as rn
        FROM documents_metadata_v2 
        WHERE source_document_id IS NOT NULL
    ) t WHERE rn > 1
);
```

#### 6.1.2 Performance Issues

```sql
-- Identify slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    (total_time/calls) as avg_time_ms
FROM pg_stat_statements 
WHERE mean_time > 1000  -- Queries > 1 second
ORDER BY mean_time DESC;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public' 
    AND tablename IN ('documents_metadata_v2', 'document_chunks_enhanced')
ORDER BY tablename, attname;
```

#### 6.1.3 Import Failures

```sql
-- Check failed import jobs
SELECT 
    source_document_id,
    package_path,
    error_message,
    import_mapping_status,
    created_at
FROM data_ingestion_jobs 
WHERE status = 'FAILED'
ORDER BY created_at DESC
LIMIT 20;

-- Retry failed imports
UPDATE data_ingestion_jobs 
SET status = 'PENDING', 
    error_message = NULL,
    updated_at = NOW()
WHERE status = 'FAILED' 
    AND created_at >= NOW() - INTERVAL '1 day';
```

### 6.2 Emergency Procedures

#### 6.2.1 Database Recovery

```bash
# If database corruption occurs
# 1. Stop application services
systemctl stop fr-03-3-pipeline
systemctl stop fr-04-rag-engine
systemctl stop fr-05-chatbot-ui

# 2. Restore from backup
psql -U kb_admin -d knowledge_base_v2 < /opt/backups/postgres/full_backup_YYYYMMDD_HHMMSS.sql

# 3. Verify restoration
psql -U kb_admin -d knowledge_base_v2 -c "SELECT COUNT(*) FROM documents_metadata_v2;"

# 4. Restart services
systemctl start fr-03-3-pipeline
systemctl start fr-04-rag-engine  
systemctl start fr-05-chatbot-ui
```

#### 6.2.2 Data Corruption Fix

```sql
-- Check data integrity
SELECT 
    d.document_id,
    d.source_document_id,
    d.title,
    COUNT(c.chunk_id) as chunk_count,
    d.chunk_count as recorded_chunk_count
FROM documents_metadata_v2 d
LEFT JOIN document_chunks_enhanced c ON d.document_id = c.document_id
GROUP BY d.document_id, d.source_document_id, d.title, d.chunk_count
HAVING COUNT(c.chunk_id) != d.chunk_count;

-- Fix chunk count mismatches
UPDATE documents_metadata_v2 
SET chunk_count = (
    SELECT COUNT(*) 
    FROM document_chunks_enhanced 
    WHERE document_id = documents_metadata_v2.document_id
);
```

---

## 7. DEVELOPMENT GUIDELINES

### 7.1 Code Standards

```python
# Database query patterns
class DatabaseClient:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def get_document_by_source_id(self, source_document_id: str):
        """Get document by business ID với error handling"""
        async with self.db_pool.acquire() as conn:
            try:
                result = await conn.fetchrow("""
                    SELECT 
                        document_id,
                        source_document_id,
                        title,
                        status,
                        created_at
                    FROM documents_metadata_v2 
                    WHERE source_document_id = $1
                """, source_document_id)
                
                return result
                
            except asyncpg.PostgresError as e:
                logger.error(f"Database error in get_document_by_source_id: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in get_document_by_source_id: {e}")
                raise
```

### 7.2 Testing Guidelines

```python
# Unit test template
import pytest
import asyncpg

@pytest.mark.asyncio
async def test_import_export_package():
    """Test complete export package import"""
    
    # Setup test database
    db_pool = await asyncpg.create_pool(
        "postgresql://kb_admin:1234567890@localhost:5432/knowledge_base_v2_test"
    )
    
    importer = ExportPackageImporter(db_pool)
    
    # Test data
    test_package_path = "test_data/HR_POLICY_20250920_test.zip"
    
    # Execute import
    result = await importer.import_export_package(test_package_path)
    
    # Assertions
    assert result["status"] == "SUCCESS"
    assert "document_id" in result
    assert "source_document_id" in result
    
    # Verify database state
    async with db_pool.acquire() as conn:
        doc = await conn.fetchrow("""
            SELECT * FROM documents_metadata_v2 
            WHERE source_document_id = $1
        """, result["source_document_id"])
        
        assert doc is not None
        assert doc["title"] is not None
    
    await db_pool.close()
```

---

## 8. APPENDIX

### 8.1 Complete Schema Reference

```sql
-- Table sizes và estimated row counts
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 8.2 Performance Benchmarks

| Operation | Target Time | Acceptable Time | Notes |
|-----------|-------------|-----------------|-------|
| Single document import | < 5 seconds | < 15 seconds | Phụ thuộc vào document size |
| BM25 search (10 results) | < 100ms | < 500ms | Với proper indexes |
| Chunk retrieval | < 50ms | < 200ms | Per document |
| Analytics query | < 1 second | < 5 seconds | Daily/weekly reports |

### 8.3 Resource Requirements

| Component | Development | Production | Notes |
|-----------|-------------|------------|-------|
| PostgreSQL RAM | 4GB | 16GB+ | Shared buffers = 25% RAM |
| PostgreSQL Storage | 20GB | 200GB+ | SSD recommended |
| Connection Pool | 10-20 | 50-100 | Phụ thuộc concurrent users |
| CPU | 2 cores | 8+ cores | For concurrent processing |

---

**KẾT LUẬN**

Database schema V7 đã được thiết kế để hỗ trợ toàn bộ lifecycle từ FR-03.1 export package đến FR-05 UI search. Hướng dẫn này cung cấp foundation cho team development thực hiện integration một cách hiệu quả và đáng tin cậy.

**Next Steps:**
1. Deploy schema V7 lên development environment
2. Implement FR-03.3 import logic theo template provided
3. Test end-to-end workflow với sample export packages
4. Setup monitoring và alerting
5. Prepare production deployment plan
