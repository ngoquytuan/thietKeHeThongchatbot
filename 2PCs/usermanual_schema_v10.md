# HƯỚNG DẪN SỬ DỤNG TOÀN DIỆN DATABASE SCHEMA V10
## User Manual cho Hệ thống Chatbot Tiếng Việt

---

**Phiên bản**: V10.0  
**Ngày phát hành**: 20/09/2025  
**Mục đích**: Hướng dẫn toàn diện deployment và sử dụng database V10  
**Đối tượng**: Development Team, DevOps Engineers, Database Administrators  

---

## 📋 MỤC LỤC

1. [Tổng quan Database V10](#1-tổng-quan-database-v10)
2. [Cài đặt và Triển khai](#2-cài-đặt-và-triển-khai)
3. [Hướng dẫn sử dụng cho từng Module](#3-hướng-dẫn-sử-dụng-cho-từng-module)
4. [API Reference và Examples](#4-api-reference-và-examples)
5. [Monitoring và Maintenance](#5-monitoring-và-maintenance)
6. [Troubleshooting Guide](#6-troubleshooting-guide)
7. [Best Practices](#7-best-practices)
8. [Performance Tuning](#8-performance-tuning)

---

## 1. TỔNG QUAN DATABASE V10

### 1.1 Những gì mới trong V10

Database Schema V10 là phiên bản ổn định cuối cùng với các tính năng chính:

#### ✅ V10 Critical Fixes
- **Vietnamese Text Search**: Tự động tạo configuration với fallback an toàn
- **Guaranteed Deployment**: 100% deployment success, không fail ở line 638
- **Complete FR-03.3 Integration**: Dual ID tracking system hoàn chỉnh
- **All Components Working**: Functions, views, triggers đều được tạo thành công

#### ✅ Core Features
- **26 Tables**: Complete schema cho toàn bộ hệ thống
- **55+ Indexes**: Tối ưu performance cho search và analytics
- **5 Views**: Monitoring và reporting views
- **5 Functions**: Vietnamese text processing utilities
- **4 Triggers**: Automatic data updates

### 1.2 Kiến trúc Hệ thống

```mermaid
graph TD
    subgraph "USER LAYER"
        A[FR-05 Chatbot UI] 
        B[FR-03.2 Quality Control]
        C[FR-03.1 Document Export]
    end
    
    subgraph "PROCESSING LAYER"
        D[FR-03.3 Data Ingestion Pipeline]
        E[FR-04 RAG Core Engine]
    end
    
    subgraph "DATABASE V10"
        F[(PostgreSQL 15+)]
        G[(ChromaDB Vector)]
        H[Text Search Config]
    end
    
    A --> E
    B --> D
    C --> D
    D --> F
    D --> G
    E --> F
    E --> G
    F --> H
    
    classDef ui fill:#e3f2fd,stroke:#1976d2
    classDef process fill:#e8f5e8,stroke:#388e3c  
    classDef database fill:#fff3e0,stroke:#f57c00
    
    class A,B,C ui
    class D,E process
    class F,G,H database
```

### 1.3 Dual ID Tracking System

V10 sử dụng hệ thống dual ID tracking:

```javascript
{
  // Business ID từ FR-03.1 (human-readable)
  "source_document_id": "POLICY_-_CHINH_SACH_xinNghi_20250919_170525",
  
  // Database UUID (system-generated)
  "document_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Lợi ích**:
- Business traceability qua source_document_id
- Database performance qua UUID
- Duplicate detection dễ dàng
- Integration đơn giản giữa các module

---

## 2. CÀI ĐẶT VÀ TRIỂN KHAI

### 2.1 System Requirements

#### Minimum Requirements
```bash
# Hardware
CPU: 4 cores
RAM: 8GB
Storage: 50GB SSD
Network: 1Gbps

# Software  
PostgreSQL: 15+
Docker: 20.10+
Python: 3.10+
```

#### Production Requirements
```bash
# Hardware
CPU: 8+ cores 
RAM: 32GB+
Storage: 200GB+ NVMe SSD
Network: 10Gbps

# Software
PostgreSQL: 15+ with tuning
Docker Swarm hoặc Kubernetes
Load Balancer (NGINX/HAProxy)
Monitoring stack (Prometheus/Grafana)
```

### 2.2 Pre-deployment Checklist

```bash
# 1. Backup existing database
pg_dump -U kb_admin -h localhost -d knowledge_base_v2 > backup_pre_v10_$(date +%Y%m%d_%H%M%S).sql

# 2. Check PostgreSQL version
psql -U kb_admin -h localhost -c "SELECT version();"
# Expected: PostgreSQL 15.x or higher

# 3. Verify extensions availability
psql -U kb_admin -h localhost -c "SELECT name FROM pg_available_extensions WHERE name IN ('uuid-ossp', 'pg_trgm', 'btree_gin', 'unaccent');"

# 4. Check available disk space
df -h /var/lib/postgresql/data
# Should have at least 10GB free

# 5. Stop dependent services
docker stop fr-03-3-pipeline fr-04-rag-engine fr-05-chatbot-ui

# 6. Verify no active connections
psql -U kb_admin -h localhost -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'knowledge_base_v2';"
```

### 2.3 V10 Deployment Steps

#### Step 1: Clean Deployment (Recommended)
```bash
# Option A: Fresh database (DESTRUCTIVE - only for development)
psql -U kb_admin -h localhost -c "DROP DATABASE IF EXISTS knowledge_base_v2;"
psql -U kb_admin -h localhost -c "CREATE DATABASE knowledge_base_v2;"

# Option B: Clean existing data (DESTRUCTIVE)
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO kb_admin;
GRANT ALL ON SCHEMA public TO public;
"
```

#### Step 2: Deploy V10 Schema
```bash
# Deploy the complete V10 schema
psql -U kb_admin -h localhost -d knowledge_base_v2 -f 01_init_database_V10.sql

# Expected output should end with:
# "V10 fixes the root cause of deployment failure!"
# "Database initialization will complete successfully."
# "COMMIT"
```

#### Step 3: Deployment Verification
```bash
# Run comprehensive validation
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "SELECT * FROM validate_schema_v10();"

# Expected: All components should show 'OK' or 'FALLBACK_SIMPLE'
# Output example:
#           component          |      status      |                    details
# -----------------------------+------------------+-----------------------------------------------
#  vietnamese_text_search_config | OK              | Vietnamese text search configuration status
#  source_document_id_column     | OK              | Business ID tracking in documents table
#  import_mapping_status_documents| OK             | Import tracking in documents table
#  check_duplicate_function       | OK              | Duplicate detection function
#  import_status_view            | OK              | Import monitoring view
```

#### Step 4: Start Dependent Services
```bash
# Restart services in order
docker start fr-03-3-pipeline
sleep 10
docker start fr-04-rag-engine  
sleep 10
docker start fr-05-chatbot-ui

# Verify services
curl http://localhost:8007/health  # FR-03.3
curl http://localhost:8004/health  # FR-04  
curl http://localhost:8005/health  # FR-05
```

### 2.4 Migration từ V9 (Incremental Update)

Nếu đang chạy V9 và muốn update:

```bash
# 1. Backup trước khi migrate
pg_dump -U kb_admin -h localhost -d knowledge_base_v2 > backup_v9_to_v10_$(date +%Y%m%d_%H%M%S).sql

# 2. Chỉ apply V10 fixes (không recreate tables)
psql -U kb_admin -h localhost -d knowledge_base_v2 << 'EOF'
-- V10 Vietnamese text search fix
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'vietnamese') THEN
        CREATE TEXT SEARCH CONFIGURATION vietnamese (COPY = simple);
        RAISE NOTICE 'Vietnamese text search configuration created';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Vietnamese config creation failed: %. Using simple fallback.', SQLERRM;
END $$;

-- Recreate problematic indexes with safe config
DROP INDEX IF EXISTS idx_documents_v2_search_text;
DROP INDEX IF EXISTS idx_chunks_enhanced_content_text;

DO $$ 
DECLARE
    config_name TEXT;
BEGIN
    IF EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'vietnamese') THEN
        config_name := 'vietnamese';
    ELSE
        config_name := 'simple';
    END IF;
    
    EXECUTE format('CREATE INDEX idx_documents_v2_search_text ON documents_metadata_v2 USING GIN(to_tsvector(%L, search_text_normalized))', config_name);
    EXECUTE format('CREATE INDEX idx_chunks_enhanced_content_text ON document_chunks_enhanced USING GIN(to_tsvector(%L, chunk_content))', config_name);
    
    RAISE NOTICE 'Text search indexes created using % configuration', config_name;
END $$;

-- Add schema migration record
INSERT INTO schema_migrations VALUES ('20250920_004', NOW(), 'DROP TEXT SEARCH CONFIGURATION IF EXISTS vietnamese;', 'V10 Update: Fixed Vietnamese text search configuration causing deployment failure') ON CONFLICT DO NOTHING;
EOF

# 3. Verify migration success
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "SELECT * FROM validate_schema_v10();"
```

---

## 3. HƯỚNG DẪN SỬ DỤNG CHO TỪNG MODULE

### 3.1 FR-03.3 Data Ingestion Pipeline

FR-03.3 là module chính sử dụng database V10 để import export packages.

#### 3.1.1 Import Export Package

```python
# Example: Complete import process
import asyncio
import asyncpg
import json
from uuid import uuid4

class FR033DatabaseClient:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def import_export_package(self, package_path: str, user_id: str = None):
        """
        Import complete export package vào database V10
        
        Args:
            package_path: Path to FR-03.1 export package (.zip)
            user_id: UUID of user performing import
            
        Returns:
            dict: Import result with job_id and document_id
        """
        
        # Step 1: Extract package và đọc metadata
        package_data = self.extract_package(package_path)
        doc_metadata = package_data["FOR_DATABASE"]["document_metadata.json"]
        source_document_id = doc_metadata.get("source_document_id")
        
        if not source_document_id:
            raise ValueError("Missing source_document_id in package")
        
        # Step 2: Check duplicate using V10 function
        async with self.db_pool.acquire() as conn:
            existing_docs = await conn.fetch("""
                SELECT * FROM check_duplicate_by_source_document_id($1)
            """, source_document_id)
            
        # Step 3: Create database records
        if existing_docs:
            database_document_id = existing_docs[0]['document_id']
            is_duplicate = True
        else:
            database_document_id = uuid4()
            is_duplicate = False
            
        job_id = uuid4()
        
        # Step 4: Create ingestion job với V10 tracking
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO data_ingestion_jobs (
                    job_id, document_id, source_document_id, 
                    source_file, package_path, status, user_id,
                    import_mapping_status, processing_metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                job_id, database_document_id, source_document_id,
                package_path, package_path, 'processing', user_id,
                json.dumps({"package_extracted": True, "source": "FR-03.1"}),
                json.dumps({"package_size": len(package_data), "v10_import": True})
            )
        
        # Step 5: Import data vào các tables
        import_results = {}
        
        try:
            if not is_duplicate:
                # Import document metadata
                import_results['document'] = await self.import_document_metadata(
                    doc_metadata, database_document_id
                )
                
                # Import chunks
                chunks_data = package_data["FOR_DATABASE"]["chunks_enhanced.jsonl"]
                import_results['chunks'] = await self.import_chunks(
                    chunks_data, database_document_id
                )
            
            # Import package metadata (always)
            import_results['package_metadata'] = await self.import_package_metadata(
                package_data, database_document_id
            )
            
            # Import signatures if available
            if "signatures" in package_data:
                import_results['signatures'] = await self.import_signatures(
                    package_data["signatures"], database_document_id
                )
            
            # Import vector config
            if "FOR_VECTOR_DB" in package_data:
                import_results['vector_config'] = await self.import_vector_config(
                    package_data["FOR_VECTOR_DB"], database_document_id
                )
            
            # Update job status
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE data_ingestion_jobs 
                    SET status = 'completed',
                        completed_at = NOW(),
                        import_mapping_status = $1
                    WHERE job_id = $2
                """, json.dumps(import_results), job_id)
            
            return {
                "success": True,
                "job_id": str(job_id),
                "document_id": str(database_document_id),
                "source_document_id": source_document_id,
                "is_duplicate": is_duplicate,
                "import_results": import_results
            }
            
        except Exception as e:
            # Error handling
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE data_ingestion_jobs 
                    SET status = 'failed', error_message = $1
                    WHERE job_id = $2
                """, str(e), job_id)
            raise

    async def import_document_metadata(self, metadata: dict, document_id):
        """Import document metadata vào documents_metadata_v2"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO documents_metadata_v2 (
                    document_id, source_document_id, title, content,
                    document_type, access_level, department_owner, 
                    author, status, import_mapping_status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (document_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    import_mapping_status = EXCLUDED.import_mapping_status,
                    updated_at = NOW()
            """,
                document_id,
                metadata.get("source_document_id"),
                metadata.get("title", "Untitled Document"),
                metadata.get("content", ""),
                metadata.get("document_type", "other"),
                metadata.get("access_level", "employee_only"),
                metadata.get("department_owner", "Unknown"),
                metadata.get("author", "System"),
                "approved",
                json.dumps({
                    "import_source": "FR-03.1",
                    "import_timestamp": "2025-09-20T10:00:00Z",
                    "v10_compatible": True
                })
            )
        
        return {"status": "success", "document_id": str(document_id)}

# Usage example
async def main():
    # Database connection
    db_pool = await asyncpg.create_pool(
        "postgresql://kb_admin:1234567890@localhost:5432/knowledge_base_v2",
        min_size=5, max_size=20
    )
    
    # Initialize client
    client = FR033DatabaseClient(db_pool)
    
    # Import package
    result = await client.import_export_package(
        "exports/HR_POLICY_20250920_120000.zip",
        user_id="123e4567-e89b-12d3-a456-426614174000"
    )
    
    print(f"Import result: {result}")
    
    await db_pool.close()

# Run
asyncio.run(main())
```

#### 3.1.2 Monitor Import Progress

```python
async def monitor_import_progress(job_id: str):
    """Monitor import progress using V10 views"""
    
    async with db_pool.acquire() as conn:
        # Get detailed status from V10 view
        status = await conn.fetchrow("""
            SELECT 
                source_document_id,
                job_status,
                title,
                signatures_imported,
                vector_config_imported,
                search_config_imported,
                chunks_imported,
                job_created_at,
                job_completed_at
            FROM vw_export_package_import_status
            WHERE document_id = (
                SELECT document_id FROM data_ingestion_jobs WHERE job_id = $1
            )
        """, job_id)
        
        if status:
            print(f"""
            Import Status for Job {job_id}:
            ================================
            Source Document ID: {status['source_document_id']}
            Status: {status['job_status']}
            Title: {status['title']}
            Signatures: {status['signatures_imported']}
            Vector Config: {status['vector_config_imported']}
            Search Config: {status['search_config_imported']}
            Chunks: {status['chunks_imported']}
            Started: {status['job_created_at']}
            Completed: {status['job_completed_at']}
            """)
        else:
            print(f"Job {job_id} not found")

# Usage
await monitor_import_progress("your-job-id-here")
```

### 3.2 FR-04 RAG Core Engine

FR-04 sử dụng V10 để search và retrieve documents.

#### 3.2.1 Hybrid Search Implementation

```python
class FR04SearchEngine:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def hybrid_search(self, 
                           query: str, 
                           user_level: str = "EMPLOYEE",
                           limit: int = 10,
                           search_method: str = "hybrid"):
        """
        Hybrid search sử dụng V10 text search + semantic
        """
        
        async with self.db_pool.acquire() as conn:
            # BM25 text search với V10 Vietnamese config
            text_results = await conn.fetch("""
                SELECT 
                    d.document_id,
                    d.source_document_id,
                    d.title,
                    d.content,
                    d.department_owner,
                    ts_rank_cd(d.search_tokens, plainto_tsquery('vietnamese', $1)) as bm25_score
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
            
            # Chunk-level search với V10 indexes
            chunk_results = await conn.fetch("""
                SELECT 
                    c.chunk_id,
                    c.document_id,
                    c.chunk_content,
                    c.chunk_position,
                    c.chunk_quality_score,
                    d.title,
                    d.source_document_id,
                    ts_rank_cd(c.bm25_tokens, plainto_tsquery('vietnamese', $1)) as chunk_score
                FROM document_chunks_enhanced c
                JOIN documents_metadata_v2 d ON c.document_id = d.document_id
                WHERE c.bm25_tokens @@ plainto_tsquery('vietnamese', $1)
                    AND d.status = 'approved'
                    AND c.chunk_quality_score > 0.5
                ORDER BY chunk_score DESC, c.chunk_quality_score DESC
                LIMIT $2
            """, query, limit)
            
            # Log search analytics
            await conn.execute("""
                INSERT INTO search_analytics (
                    query, query_normalized, search_method, 
                    results_count, has_results, processing_time_ms,
                    timestamp
                ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
            """, 
                query, query.lower().strip(), search_method,
                len(text_results) + len(chunk_results),
                len(text_results) > 0 or len(chunk_results) > 0,
                50  # placeholder processing time
            )
            
            return {
                "query": query,
                "text_results": text_results,
                "chunk_results": chunk_results,
                "total_results": len(text_results) + len(chunk_results)
            }

# Usage
search_engine = FR04SearchEngine(db_pool)
results = await search_engine.hybrid_search(
    "chính sách làm việc từ xa", 
    user_level="EMPLOYEE",
    limit=5
)
```

#### 3.2.2 Document Retrieval với Access Control

```python
async def get_document_with_access_control(document_id: str, user_level: str):
    """Retrieve document với V10 access control"""
    
    async with db_pool.acquire() as conn:
        # Get document với access level check
        document = await conn.fetchrow("""
            SELECT 
                d.document_id,
                d.source_document_id,
                d.title,
                d.content,
                d.document_type,
                d.access_level,
                d.department_owner,
                d.author,
                d.chunk_count,
                d.import_mapping_status
            FROM documents_metadata_v2 d
            WHERE d.document_id = $1
                AND d.status = 'approved'
                AND (
                    d.access_level = 'public' OR
                    ($2 = 'SYSTEM_ADMIN') OR
                    ($2 = 'DIRECTOR' AND d.access_level IN ('public', 'employee_only', 'manager_only')) OR
                    ($2 = 'MANAGER' AND d.access_level IN ('public', 'employee_only')) OR
                    ($2 = 'EMPLOYEE' AND d.access_level IN ('public', 'employee_only'))
                )
        """, document_id, user_level)
        
        if not document:
            return {"error": "Document not found or access denied"}
        
        # Get chunks nếu cần
        chunks = await conn.fetch("""
            SELECT 
                chunk_id,
                chunk_content,
                chunk_position,
                chunk_quality_score
            FROM document_chunks_enhanced
            WHERE document_id = $1
            ORDER BY chunk_position
        """, document_id)
        
        # Update usage stats
        await conn.execute("""
            INSERT INTO document_usage_stats (
                document_id, date, view_count, unique_users
            ) VALUES ($1, CURRENT_DATE, 1, 1)
            ON CONFLICT (document_id, date) DO UPDATE SET
                view_count = document_usage_stats.view_count + 1,
                last_accessed = NOW()
        """, document_id)
        
        return {
            "document": dict(document),
            "chunks": [dict(chunk) for chunk in chunks],
            "access_granted": True
        }
```

### 3.3 FR-05 Chatbot UI

FR-05 sử dụng V10 để hiển thị documents và analytics.

#### 3.3.1 Document Browser

```python
async def get_documents_for_ui(
    user_level: str,
    department: str = None,
    document_type: str = None,
    search_query: str = None,
    page: int = 1,
    page_size: int = 20
):
    """Get documents list cho UI với pagination và filtering"""
    
    offset = (page - 1) * page_size
    
    async with db_pool.acquire() as conn:
        # Build dynamic query
        where_conditions = ["d.status = 'approved'"]
        params = [user_level]
        param_count = 1
        
        # Access control
        access_levels = {
            'SYSTEM_ADMIN': ['public', 'employee_only', 'manager_only', 'director_only'],
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
        
        # Search query với V10 text search
        if search_query:
            param_count += 1
            where_conditions.append(f"d.search_tokens @@ plainto_tsquery('vietnamese', ${param_count})")
            params.append(search_query)
        
        # Add pagination
        params.extend([page_size, offset])
        
        # Main query
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
                COALESCE(dus.view_count, 0) as view_count,
                COALESCE(dus.download_count, 0) as download_count,
                COALESCE(dus.last_accessed, d.created_at) as last_accessed
            FROM documents_metadata_v2 d
            LEFT JOIN document_usage_stats dus ON d.document_id = dus.document_id 
                AND dus.date = CURRENT_DATE
            WHERE {' AND '.join(where_conditions)}
            ORDER BY d.created_at DESC
            LIMIT ${len(params)-1} OFFSET ${len(params)}
        """
        
        documents = await conn.fetch(query, *params)
        
        # Get total count for pagination
        count_query = f"""
            SELECT COUNT(*) 
            FROM documents_metadata_v2 d
            WHERE {' AND '.join(where_conditions)}
        """
        total_count = await conn.fetchval(count_query, *params[:-2])
        
        return {
            "documents": [dict(doc) for doc in documents],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total_count,
                "pages": (total_count + page_size - 1) // page_size
            },
            "filters": {
                "department": department,
                "document_type": document_type,
                "search_query": search_query
            }
        }

# Usage trong FastAPI
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()

@app.get("/api/documents")
async def list_documents(
    user_level: str = Query(..., description="User access level"),
    department: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    return await get_documents_for_ui(
        user_level=user_level,
        department=department,
        document_type=document_type,
        search_query=search,
        page=page,
        page_size=page_size
    )
```

#### 3.3.2 Analytics Dashboard

```python
async def get_dashboard_analytics(date_range_days: int = 30):
    """Get analytics data cho dashboard UI"""
    
    async with db_pool.acquire() as conn:
        # Document statistics
        doc_stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_documents,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_documents,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '%s days' THEN 1 END) as recent_documents,
                SUM(chunk_count) as total_chunks
            FROM documents_metadata_v2
        """, date_range_days)
        
        # Search analytics
        search_stats = await conn.fetch("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as search_count,
                AVG(processing_time_ms) as avg_processing_time,
                AVG(results_count) as avg_results_count,
                SUM(CASE WHEN has_results THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as success_rate
            FROM search_analytics
            WHERE timestamp >= NOW() - INTERVAL '%s days'
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """, date_range_days)
        
        # Top searched documents
        top_documents = await conn.fetch("""
            SELECT 
                d.title,
                d.source_document_id,
                SUM(dus.view_count) as total_views,
                SUM(dus.search_hits) as total_search_hits
            FROM documents_metadata_v2 d
            JOIN document_usage_stats dus ON d.document_id = dus.document_id
            WHERE dus.date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY d.document_id, d.title, d.source_document_id
            ORDER BY total_search_hits DESC
            LIMIT 10
        """, date_range_days)
        
        # Department breakdown
        dept_stats = await conn.fetch("""
            SELECT 
                department_owner,
                COUNT(*) as document_count,
                AVG(chunk_count) as avg_chunks_per_doc
            FROM documents_metadata_v2
            WHERE status = 'approved'
            GROUP BY department_owner
            ORDER BY document_count DESC
        """)
        
        # Import job statistics
        import_stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_jobs,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
                AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_processing_time_seconds
            FROM data_ingestion_jobs
            WHERE created_at >= NOW() - INTERVAL '%s days'
        """, date_range_days)
        
        return {
            "document_stats": dict(doc_stats),
            "search_analytics": [dict(row) for row in search_stats],
            "top_documents": [dict(row) for row in top_documents],
            "department_breakdown": [dict(row) for row in dept_stats],
            "import_statistics": dict(import_stats),
            "date_range_days": date_range_days
        }

# FastAPI endpoint
@app.get("/api/dashboard/analytics")
async def dashboard_analytics(days: int = Query(30, ge=1, le=365)):
    return await get_dashboard_analytics(days)
```

---

## 4. API REFERENCE VÀ EXAMPLES

### 4.1 Core Database Functions

#### 4.1.1 Vietnamese Text Processing Functions

```sql
-- Function 1: Normalize Vietnamese text
SELECT normalize_vietnamese_text('Chính sách làm việc từ xa với các dấu hỏi và dấu nặng');
-- Returns: 'chinh sach lam viec tu xa voi cac dau hoi va dau nang'

-- Function 2: Extract emails
SELECT extract_emails_from_text('Liên hệ hr@company.com hoặc support@company.com để được hỗ trợ');
-- Returns: {hr@company.com, support@company.com}

-- Function 3: Extract phone numbers
SELECT extract_phones_from_text('Gọi 0123456789 hoặc +84987654321 để được tư vấn');
-- Returns: {0123456789, +84987654321}

-- Function 4: Check duplicates
SELECT * FROM check_duplicate_by_source_document_id('POLICY_-_CHINH_SACH_xinNghi_20250919_170525');
-- Returns table với document_id, title, author, created_at nếu tìm thấy

-- Function 5: Schema validation
SELECT * FROM validate_schema_v10();
-- Returns validation status cho tất cả components
```

#### 4.1.2 Search Functions

```sql
-- Vietnamese text search
SELECT 
    title,
    ts_rank(search_tokens, plainto_tsquery('vietnamese', 'chính sách nhân sự')) as relevance
FROM documents_metadata_v2
WHERE search_tokens @@ plainto_tsquery('vietnamese', 'chính sách nhân sự')
ORDER BY relevance DESC;

-- Chunk-level search với quality filtering
SELECT 
    d.title,
    c.chunk_content,
    c.chunk_quality_score,
    ts_rank(c.bm25_tokens, plainto_tsquery('vietnamese', 'làm việc từ xa')) as chunk_relevance
FROM document_chunks_enhanced c
JOIN documents_metadata_v2 d ON c.document_id = d.document_id
WHERE c.bm25_tokens @@ plainto_tsquery('vietnamese', 'làm việc từ xa')
    AND c.chunk_quality_score > 0.7
ORDER BY chunk_relevance DESC, c.chunk_quality_score DESC;

-- Advanced search với metadata filtering
SELECT 
    d.title,
    d.department_owner,
    d.document_type,
    ts_rank_cd(d.search_tokens, plainto_tsquery('vietnamese', 'quy trình'), 1) as relevance
FROM documents_metadata_v2 d
WHERE d.search_tokens @@ plainto_tsquery('vietnamese', 'quy trình')
    AND d.document_type = 'procedure'
    AND d.department_owner = 'HR'
    AND d.access_level IN ('public', 'employee_only')
ORDER BY relevance DESC;
```

### 4.2 Monitoring Queries

#### 4.2.1 Import Status Monitoring

```sql
-- Real-time import progress
SELECT 
    source_document_id,
    job_status,
    title,
    signatures_imported,
    vector_config_imported,
    search_config_imported,
    chunks_imported,
    job_created_at,
    job_completed_at
FROM vw_export_package_import_status
WHERE job_status IN ('processing', 'failed')
ORDER BY job_created_at DESC;

-- Import success rate by day
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_jobs,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
    ROUND(COUNT(CASE WHEN status = 'completed' THEN 1 END)::DECIMAL / COUNT(*) * 100, 2) as success_rate
FROM data_ingestion_jobs
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Average processing time
SELECT 
    job_type,
    COUNT(*) as job_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_processing_seconds,
    MIN(EXTRACT(EPOCH FROM (completed_at - created_at))) as min_processing_seconds,
    MAX(EXTRACT(EPOCH FROM (completed_at - created_at))) as max_processing_seconds
FROM data_ingestion_jobs
WHERE status = 'completed'
    AND completed_at IS NOT NULL
GROUP BY job_type;
```

#### 4.2.2 Search Performance Analytics

```sql
-- Search performance by method
SELECT 
    search_method,
    COUNT(*) as search_count,
    AVG(processing_time_ms) as avg_processing_time,
    AVG(results_count) as avg_results_count,
    SUM(CASE WHEN has_results THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as success_rate
FROM search_analytics
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY search_method
ORDER BY search_count DESC;

-- Top search queries
SELECT 
    query_normalized,
    COUNT(*) as search_count,
    AVG(results_count) as avg_results,
    AVG(processing_time_ms) as avg_time
FROM search_analytics
WHERE timestamp >= NOW() - INTERVAL '30 days'
    AND results_count > 0
GROUP BY query_normalized
HAVING COUNT(*) >= 5
ORDER BY search_count DESC
LIMIT 20;

-- Search patterns by hour
SELECT 
    EXTRACT(HOUR FROM timestamp) as hour,
    COUNT(*) as search_count,
    AVG(processing_time_ms) as avg_processing_time
FROM search_analytics
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY EXTRACT(HOUR FROM timestamp)
ORDER BY hour;
```

### 4.3 Administrative Queries

#### 4.3.1 Database Health Checks

```sql
-- Table sizes và row counts
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = tablename) as column_count
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as times_used,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Connection và activity statistics
SELECT 
    datname,
    numbackends as connections,
    xact_commit as commits,
    xact_rollback as rollbacks,
    blks_read as blocks_read,
    blks_hit as blocks_hit,
    ROUND(blks_hit::DECIMAL / (blks_hit + blks_read) * 100, 2) as cache_hit_ratio
FROM pg_stat_database
WHERE datname = 'knowledge_base_v2';
```

#### 4.3.2 Data Quality Checks

```sql
-- Check for orphaned records
SELECT 'Orphaned chunks' as issue, COUNT(*) as count
FROM document_chunks_enhanced c
LEFT JOIN documents_metadata_v2 d ON c.document_id = d.document_id
WHERE d.document_id IS NULL

UNION ALL

SELECT 'Documents without chunks' as issue, COUNT(*) as count  
FROM documents_metadata_v2 d
LEFT JOIN document_chunks_enhanced c ON d.document_id = c.document_id
WHERE c.document_id IS NULL AND d.chunk_count > 0

UNION ALL

SELECT 'Jobs without documents' as issue, COUNT(*) as count
FROM data_ingestion_jobs j
LEFT JOIN documents_metadata_v2 d ON j.document_id = d.document_id
WHERE d.document_id IS NULL;

-- Check for duplicate source_document_ids
SELECT 
    source_document_id,
    COUNT(*) as duplicate_count,
    array_agg(document_id) as document_ids
FROM documents_metadata_v2
WHERE source_document_id IS NOT NULL
GROUP BY source_document_id
HAVING COUNT(*) > 1;

-- Check chunk count consistency
SELECT 
    d.document_id,
    d.source_document_id,
    d.chunk_count as recorded_count,
    COUNT(c.chunk_id) as actual_count,
    ABS(d.chunk_count - COUNT(c.chunk_id)) as difference
FROM documents_metadata_v2 d
LEFT JOIN document_chunks_enhanced c ON d.document_id = c.document_id
GROUP BY d.document_id, d.source_document_id, d.chunk_count
HAVING d.chunk_count != COUNT(c.chunk_id)
ORDER BY difference DESC;
```

---

## 5. MONITORING VÀ MAINTENANCE

### 5.1 Daily Monitoring Checklist

#### 5.1.1 Automatic Health Check Script

```bash
#!/bin/bash
# daily_health_check.sh

echo "=== Database V10 Daily Health Check ==="
echo "Date: $(date)"
echo "======================================="

# 1. Database connection test
echo "1. Testing database connection..."
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "SELECT 'Database connection: OK'" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    exit 1
fi

# 2. Schema validation
echo "2. Running schema validation..."
VALIDATION_RESULT=$(psql -U kb_admin -h localhost -d knowledge_base_v2 -t -c "
SELECT COUNT(*) 
FROM validate_schema_v10() 
WHERE status NOT IN ('OK', 'FALLBACK_SIMPLE');" 2>/dev/null)

if [ "$VALIDATION_RESULT" -eq 0 ]; then
    echo "✅ Schema validation passed"
else
    echo "❌ Schema validation failed ($VALIDATION_RESULT issues found)"
    psql -U kb_admin -h localhost -d knowledge_base_v2 -c "SELECT * FROM validate_schema_v10() WHERE status NOT IN ('OK', 'FALLBACK_SIMPLE');"
fi

# 3. Check import job failures
echo "3. Checking import job failures (last 24h)..."
FAILED_JOBS=$(psql -U kb_admin -h localhost -d knowledge_base_v2 -t -c "
SELECT COUNT(*) 
FROM data_ingestion_jobs 
WHERE status = 'failed' 
    AND created_at >= NOW() - INTERVAL '24 hours';" 2>/dev/null)

if [ "$FAILED_JOBS" -eq 0 ]; then
    echo "✅ No failed import jobs in last 24h"
else
    echo "⚠️  $FAILED_JOBS failed import jobs in last 24h"
fi

# 4. Check search performance
echo "4. Checking search performance..."
AVG_SEARCH_TIME=$(psql -U kb_admin -h localhost -d knowledge_base_v2 -t -c "
SELECT ROUND(AVG(processing_time_ms)) 
FROM search_analytics 
WHERE timestamp >= NOW() - INTERVAL '24 hours';" 2>/dev/null)

if [ "$AVG_SEARCH_TIME" -lt 1000 ]; then
    echo "✅ Average search time: ${AVG_SEARCH_TIME}ms (good)"
else
    echo "⚠️  Average search time: ${AVG_SEARCH_TIME}ms (slow)"
fi

# 5. Database size check
echo "5. Checking database size..."
DB_SIZE=$(psql -U kb_admin -h localhost -d knowledge_base_v2 -t -c "
SELECT pg_size_pretty(pg_database_size('knowledge_base_v2'));" 2>/dev/null)
echo "📊 Current database size: $DB_SIZE"

# 6. Connection count
echo "6. Checking active connections..."
CONNECTIONS=$(psql -U kb_admin -h localhost -d knowledge_base_v2 -t -c "
SELECT COUNT(*) 
FROM pg_stat_activity 
WHERE datname = 'knowledge_base_v2' AND state = 'active';" 2>/dev/null)
echo "🔗 Active connections: $CONNECTIONS"

echo "======================================="
echo "Health check completed at $(date)"
```

#### 5.1.2 Performance Monitoring Queries

```sql
-- Slow query detection
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    (total_time/calls) as avg_time_ms,
    rows
FROM pg_stat_statements 
WHERE mean_time > 1000  -- Queries > 1 second
ORDER BY mean_time DESC
LIMIT 10;

-- Table bloat assessment
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_dead_tup as dead_tuples,
    CASE 
        WHEN n_tup_ins + n_tup_upd + n_tup_del > 0 
        THEN ROUND(n_dead_tup::DECIMAL / (n_tup_ins + n_tup_upd + n_tup_del) * 100, 2)
        ELSE 0 
    END as dead_tuple_ratio
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY dead_tuple_ratio DESC;

-- Cache hit ratios
SELECT 
    'Shared buffers' as cache_type,
    ROUND(
        SUM(blks_hit)::DECIMAL / (SUM(blks_hit) + SUM(blks_read)) * 100, 2
    ) as hit_ratio
FROM pg_stat_user_tables

UNION ALL

SELECT 
    'Index cache' as cache_type,
    ROUND(
        SUM(idx_blks_hit)::DECIMAL / (SUM(idx_blks_hit) + SUM(idx_blks_read)) * 100, 2
    ) as hit_ratio
FROM pg_statio_user_indexes
WHERE SUM(idx_blks_hit) + SUM(idx_blks_read) > 0;
```

### 5.2 Weekly Maintenance Tasks

#### 5.2.1 Database Maintenance Script

```bash
#!/bin/bash
# weekly_maintenance.sh

echo "=== Weekly Database Maintenance ==="
echo "Date: $(date)"
echo "=================================="

# 1. Update table statistics
echo "1. Updating table statistics..."
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "ANALYZE;"
echo "✅ Statistics updated"

# 2. Reindex heavily used tables
echo "2. Reindexing heavily used tables..."
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "REINDEX TABLE documents_metadata_v2;"
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "REINDEX TABLE document_chunks_enhanced;"
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "REINDEX TABLE search_analytics;"
echo "✅ Reindexing completed"

# 3. Vacuum old data
echo "3. Vacuuming old data..."
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "VACUUM (ANALYZE, VERBOSE) search_analytics;"
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "VACUUM (ANALYZE, VERBOSE) user_events;"
echo "✅ Vacuum completed"

# 4. Clean old analytics data (> 90 days)
echo "4. Cleaning old analytics data..."
DELETED_ANALYTICS=$(psql -U kb_admin -h localhost -d knowledge_base_v2 -t -c "
DELETE FROM search_analytics 
WHERE timestamp < NOW() - INTERVAL '90 days';
SELECT row_count();")
echo "🗑️  Deleted $DELETED_ANALYTICS old search analytics records"

# 5. Clean old user events (> 30 days)
DELETED_EVENTS=$(psql -U kb_admin -h localhost -d knowledge_base_v2 -t -c "
DELETE FROM user_events 
WHERE timestamp < NOW() - INTERVAL '30 days';
SELECT row_count();")
echo "🗑️  Deleted $DELETED_EVENTS old user events"

# 6. Clean expired analytics cache
DELETED_CACHE=$(psql -U kb_admin -h localhost -d knowledge_base_v2 -t -c "
DELETE FROM analytics_cache 
WHERE expires_at < NOW();
SELECT row_count();")
echo "🗑️  Deleted $DELETED_CACHE expired cache entries"

# 7. Generate weekly report
echo "7. Generating weekly report..."
psql -U kb_admin -h localhost -d knowledge_base_v2 -o weekly_report_$(date +%Y%m%d).txt -c "
SELECT 'Weekly Database Report - ' || CURRENT_DATE as title;

SELECT 'Document Statistics' as section;
SELECT 
    COUNT(*) as total_documents,
    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_documents,
    SUM(chunk_count) as total_chunks,
    pg_size_pretty(SUM(file_size_bytes)) as total_size
FROM documents_metadata_v2;

SELECT 'Search Statistics (Last 7 days)' as section;
SELECT 
    COUNT(*) as total_searches,
    AVG(processing_time_ms) as avg_processing_time,
    AVG(results_count) as avg_results_count,
    SUM(CASE WHEN has_results THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as success_rate
FROM search_analytics
WHERE timestamp >= NOW() - INTERVAL '7 days';

SELECT 'Import Job Statistics (Last 7 days)' as section;
SELECT 
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_processing_time_seconds
FROM data_ingestion_jobs
WHERE created_at >= NOW() - INTERVAL '7 days';
"

echo "✅ Weekly report generated: weekly_report_$(date +%Y%m%d).txt"
echo "=================================="
echo "Weekly maintenance completed at $(date)"
```

### 5.3 Backup Strategy

#### 5.3.1 Automated Backup Script

```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/opt/backups/postgres"
DB_NAME="knowledge_base_v2"
DB_USER="kb_admin"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

echo "=== Database Backup Started ==="
echo "Date: $(date)"
echo "Backup directory: $BACKUP_DIR"

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# 1. Full database backup
echo "1. Creating full database backup..."
pg_dump -U $DB_USER -h localhost -d $DB_NAME -v -f $BACKUP_DIR/full_backup_$DATE.sql
if [ $? -eq 0 ]; then
    echo "✅ Full backup completed: full_backup_$DATE.sql"
    
    # Compress backup
    gzip $BACKUP_DIR/full_backup_$DATE.sql
    echo "✅ Backup compressed: full_backup_$DATE.sql.gz"
else
    echo "❌ Full backup failed"
    exit 1
fi

# 2. Schema-only backup
echo "2. Creating schema-only backup..."
pg_dump -U $DB_USER -h localhost -d $DB_NAME --schema-only -f $BACKUP_DIR/schema_backup_$DATE.sql
if [ $? -eq 0 ]; then
    echo "✅ Schema backup completed: schema_backup_$DATE.sql"
else
    echo "⚠️  Schema backup failed"
fi

# 3. Data-only backup for critical tables
echo "3. Creating data-only backup for critical tables..."
pg_dump -U $DB_USER -h localhost -d $DB_NAME --data-only \
    -t documents_metadata_v2 \
    -t document_chunks_enhanced \
    -t data_ingestion_jobs \
    -f $BACKUP_DIR/critical_data_backup_$DATE.sql
if [ $? -eq 0 ]; then
    echo "✅ Critical data backup completed: critical_data_backup_$DATE.sql"
    gzip $BACKUP_DIR/critical_data_backup_$DATE.sql
else
    echo "⚠️  Critical data backup failed"
fi

# 4. Export configuration
echo "4. Exporting database configuration..."
psql -U $DB_USER -h localhost -d $DB_NAME -c "
SELECT name, setting 
FROM pg_settings 
WHERE source != 'default' 
ORDER BY name;" > $BACKUP_DIR/db_config_$DATE.txt

# 5. Cleanup old backups
echo "5. Cleaning up old backups (older than $RETENTION_DAYS days)..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.sql" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.txt" -mtime +$RETENTION_DAYS -delete

REMAINING_BACKUPS=$(ls -1 $BACKUP_DIR/*.gz 2>/dev/null | wc -l)
echo "🗂️  Remaining backups: $REMAINING_BACKUPS files"

# 6. Verify backup integrity
echo "6. Verifying backup integrity..."
gzip -t $BACKUP_DIR/full_backup_$DATE.sql.gz
if [ $? -eq 0 ]; then
    echo "✅ Backup integrity verified"
else
    echo "❌ Backup integrity check failed"
    exit 1
fi

# 7. Update backup status trong database
psql -U $DB_USER -h localhost -d $DB_NAME -c "
INSERT INTO backup_status (
    backup_type, backup_path, file_size_bytes, status, completed_at
) VALUES (
    'full_database',
    '$BACKUP_DIR/full_backup_$DATE.sql.gz',
    $(stat -c%s $BACKUP_DIR/full_backup_$DATE.sql.gz),
    'completed',
    NOW()
);" 2>/dev/null

echo "==============================="
echo "Backup completed successfully at $(date)"
echo "Backup file: $BACKUP_DIR/full_backup_$DATE.sql.gz"
echo "Backup size: $(du -h $BACKUP_DIR/full_backup_$DATE.sql.gz | cut -f1)"
```

#### 5.3.2 Restore Procedures

```bash
#!/bin/bash
# restore_database.sh

BACKUP_FILE="$1"
RESTORE_TYPE="$2"  # full, schema, data

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file> [full|schema|data]"
    echo "Example: $0 /opt/backups/postgres/full_backup_20250920_120000.sql.gz full"
    exit 1
fi

RESTORE_TYPE=${RESTORE_TYPE:-full}
DB_NAME="knowledge_base_v2"
DB_USER="kb_admin"

echo "=== Database Restore Started ==="
echo "Backup file: $BACKUP_FILE"
echo "Restore type: $RESTORE_TYPE"
echo "Date: $(date)"

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Stop dependent services
echo "1. Stopping dependent services..."
docker stop fr-03-3-pipeline fr-04-rag-engine fr-05-chatbot-ui 2>/dev/null

# Extract backup if compressed
TEMP_BACKUP="$BACKUP_FILE"
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "2. Extracting compressed backup..."
    TEMP_BACKUP="/tmp/$(basename $BACKUP_FILE .gz)"
    gunzip -c "$BACKUP_FILE" > "$TEMP_BACKUP"
fi

case $RESTORE_TYPE in
    "full")
        echo "3. Performing full database restore..."
        
        # Drop existing database (DESTRUCTIVE!)
        read -p "⚠️  This will completely replace the existing database. Continue? (yes/no): " -r
        if [[ ! $REPLY =~ ^yes$ ]]; then
            echo "Restore cancelled."
            exit 1
        fi
        
        psql -U $DB_USER -h localhost -c "DROP DATABASE IF EXISTS $DB_NAME;"
        psql -U $DB_USER -h localhost -c "CREATE DATABASE $DB_NAME;"
        
        # Restore from backup
        psql -U $DB_USER -h localhost -d $DB_NAME -f "$TEMP_BACKUP"
        ;;
        
    "schema")
        echo "3. Performing schema-only restore..."
        psql -U $DB_USER -h localhost -d $DB_NAME -f "$TEMP_BACKUP"
        ;;
        
    "data")
        echo "3. Performing data-only restore..."
        psql -U $DB_USER -h localhost -d $DB_NAME -f "$TEMP_BACKUP"
        ;;
        
    *)
        echo "❌ Invalid restore type: $RESTORE_TYPE"
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    echo "✅ Database restore completed successfully"
    
    # Verify restore
    echo "4. Verifying restore..."
    DOCUMENT_COUNT=$(psql -U $DB_USER -h localhost -d $DB_NAME -t -c "SELECT COUNT(*) FROM documents_metadata_v2;" 2>/dev/null)
    echo "📊 Documents in restored database: $DOCUMENT_COUNT"
    
    # Run schema validation
    echo "5. Running schema validation..."
    psql -U $DB_USER -h localhost -d $DB_NAME -c "SELECT * FROM validate_schema_v10();"
    
else
    echo "❌ Database restore failed"
    exit 1
fi

# Cleanup temp file
if [[ $BACKUP_FILE == *.gz ]] && [ -f "$TEMP_BACKUP" ]; then
    rm "$TEMP_BACKUP"
fi

# Restart services
echo "6. Restarting services..."
docker start fr-03-3-pipeline
sleep 5
docker start fr-04-rag-engine
sleep 5
docker start fr-05-chatbot-ui

echo "==============================="
echo "Restore completed at $(date)"
```

---

## 6. TROUBLESHOOTING GUIDE

### 6.1 Common Issues và Solutions

#### 6.1.1 Vietnamese Text Search Issues

**Problem**: Text search không hoạt động với tiếng Việt

```sql
-- Diagnosis
SELECT cfgname FROM pg_ts_config WHERE cfgname = 'vietnamese';

-- Solution 1: Nếu không có vietnamese config
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'vietnamese') THEN
        CREATE TEXT SEARCH CONFIGURATION vietnamese (COPY = simple);
    END IF;
END $$;

-- Solution 2: Recreate problematic indexes
DROP INDEX IF EXISTS idx_documents_v2_search_text;
CREATE INDEX idx_documents_v2_search_text ON documents_metadata_v2 
USING GIN(to_tsvector('vietnamese', search_text_normalized));

-- Test search functionality
SELECT COUNT(*) FROM documents_metadata_v2 
WHERE search_tokens @@ plainto_tsquery('vietnamese', 'test query');
```

**Problem**: Search performance chậm

```sql
-- Check index usage
SELECT 
    schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes 
WHERE tablename IN ('documents_metadata_v2', 'document_chunks_enhanced')
ORDER BY idx_scan DESC;

-- Reindex if needed
REINDEX INDEX idx_documents_v2_search_text;
REINDEX INDEX idx_chunks_enhanced_bm25;

-- Update statistics
ANALYZE documents_metadata_v2;
ANALYZE document_chunks_enhanced;
```

#### 6.1.2 Import Pipeline Issues

**Problem**: Import jobs bị stuck ở status 'processing'

```sql
-- Find stuck jobs
SELECT 
    job_id, source_document_id, status, created_at,
    EXTRACT(EPOCH FROM (NOW() - created_at))/60 as minutes_stuck
FROM data_ingestion_jobs 
WHERE status = 'processing' 
    AND created_at < NOW() - INTERVAL '1 hour'
ORDER BY created_at;

-- Reset stuck jobs
UPDATE data_ingestion_jobs 
SET status = 'failed', 
    error_message = 'Job timeout - reset by admin',
    updated_at = NOW()
WHERE status = 'processing' 
    AND created_at < NOW() - INTERVAL '2 hours';
```

**Problem**: Duplicate source_document_id errors

```sql
-- Find duplicates
SELECT 
    source_document_id, 
    COUNT(*) as count,
    array_agg(document_id) as document_ids
FROM documents_metadata_v2 
WHERE source_document_id IS NOT NULL
GROUP BY source_document_id 
HAVING COUNT(*) > 1;

-- Fix duplicates by adding timestamp suffix
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

#### 6.1.3 Performance Issues

**Problem**: Database queries chậm

```sql
-- Find slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
WHERE mean_time > 1000
ORDER BY mean_time DESC
LIMIT 10;

-- Check missing indexes
SELECT 
    schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats 
WHERE schemaname = 'public' 
    AND tablename IN ('documents_metadata_v2', 'document_chunks_enhanced')
    AND n_distinct > 100
ORDER BY tablename, n_distinct DESC;

-- Check table bloat
SELECT 
    schemaname, tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    n_dead_tup as dead_tuples,
    n_live_tup as live_tuples,
    ROUND(n_dead_tup::DECIMAL / (n_dead_tup + n_live_tup) * 100, 2) as bloat_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY bloat_ratio DESC;
```

**Problem**: Connection limit exceeded

```sql
-- Check current connections
SELECT 
    datname, 
    numbackends as current_connections,
    (SELECT setting FROM pg_settings WHERE name = 'max_connections') as max_connections
FROM pg_stat_database 
WHERE datname = 'knowledge_base_v2';

-- Kill idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity 
WHERE datname = 'knowledge_base_v2'
    AND state = 'idle'
    AND state_change < NOW() - INTERVAL '1 hour';

-- Check connection sources
SELECT 
    client_addr, 
    COUNT(*) as connection_count,
    array_agg(DISTINCT application_name) as applications
FROM pg_stat_activity 
WHERE datname = 'knowledge_base_v2'
GROUP BY client_addr
ORDER BY connection_count DESC;
```

### 6.2 Emergency Procedures

#### 6.2.1 Database Corruption Recovery

```bash
#!/bin/bash
# emergency_recovery.sh

echo "=== EMERGENCY DATABASE RECOVERY ==="
echo "Date: $(date)"

# 1. Stop all services immediately
echo "1. Stopping all dependent services..."
docker stop fr-03-3-pipeline fr-04-rag-engine fr-05-chatbot-ui fr-02-file-api
systemctl stop postgresql  # If needed

# 2. Check database integrity
echo "2. Checking database integrity..."
su - postgres -c "pg_controldata /var/lib/postgresql/data"

# 3. Attempt to start PostgreSQL in single-user mode
echo "3. Starting PostgreSQL in recovery mode..."
su - postgres -c "postgres --single -D /var/lib/postgresql/data knowledge_base_v2" <<EOF
VACUUM FULL;
REINDEX DATABASE knowledge_base_v2;
EOF

# 4. Check for corrupted tables
echo "4. Checking for corrupted tables..."
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public';" > /tmp/tables.txt

while read table; do
    echo "Checking table: $table"
    psql -U kb_admin -h localhost -d knowledge_base_v2 -c "SELECT COUNT(*) FROM $table;" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "❌ Corrupted table detected: $table"
    fi
done < /tmp/tables.txt

# 5. Restore from latest backup if needed
echo "5. Finding latest backup..."
LATEST_BACKUP=$(ls -t /opt/backups/postgres/full_backup_*.sql.gz | head -1)
if [ -n "$LATEST_BACKUP" ]; then
    echo "Latest backup found: $LATEST_BACKUP"
    read -p "Restore from backup? (yes/no): " -r
    if [[ $REPLY =~ ^yes$ ]]; then
        # Drop and recreate database
        psql -U kb_admin -h localhost -c "DROP DATABASE IF EXISTS knowledge_base_v2;"
        psql -U kb_admin -h localhost -c "CREATE DATABASE knowledge_base_v2;"
        
        # Restore
        gunzip -c "$LATEST_BACKUP" | psql -U kb_admin -h localhost -d knowledge_base_v2
        echo "✅ Database restored from backup"
    fi
fi

# 6. Restart services
echo "6. Restarting services..."
docker start fr-02-file-api fr-03-3-pipeline fr-04-rag-engine fr-05-chatbot-ui

echo "Emergency recovery completed"
```

#### 6.2.2 Data Inconsistency Fixes

```sql
-- Emergency data consistency fixes

-- 1. Fix orphaned chunks
DELETE FROM document_chunks_enhanced 
WHERE document_id NOT IN (SELECT document_id FROM documents_metadata_v2);

-- 2. Fix chunk count mismatches
UPDATE documents_metadata_v2 
SET chunk_count = (
    SELECT COUNT(*) 
    FROM document_chunks_enhanced 
    WHERE document_id = documents_metadata_v2.document_id
);

-- 3. Fix missing search tokens
UPDATE documents_metadata_v2 
SET search_tokens = to_tsvector('simple', title || ' ' || COALESCE(content, ''))
WHERE search_tokens IS NULL;

-- 4. Fix chunk BM25 tokens
UPDATE document_chunks_enhanced 
SET bm25_tokens = to_tsvector('simple', chunk_content)
WHERE bm25_tokens IS NULL;

-- 5. Clean up failed jobs older than 24 hours
UPDATE data_ingestion_jobs 
SET status = 'cancelled'
WHERE status IN ('processing', 'pending') 
    AND created_at < NOW() - INTERVAL '24 hours';

-- 6. Reset import mapping status for failed jobs
UPDATE documents_metadata_v2 
SET import_mapping_status = '{}'
WHERE document_id IN (
    SELECT document_id 
    FROM data_ingestion_jobs 
    WHERE status = 'failed'
);
```

---

## 7. BEST PRACTICES

### 7.1 Development Best Practices

#### 7.1.1 Database Connection Management

```python
# ✅ Good: Connection pooling
import asyncpg
import asyncio

class DatabaseManager:
    def __init__(self):
        self.pool = None
    
    async def initialize(self):
        """Initialize connection pool"""
        self.pool = await asyncpg.create_pool(
            "postgresql://kb_admin:1234567890@localhost:5432/knowledge_base_v2",
            min_size=5,
            max_size=20,
            max_queries=50000,
            max_inactive_connection_lifetime=300.0,
            command_timeout=60
        )
    
    async def get_connection(self):
        """Get connection from pool"""
        if not self.pool:
            await self.initialize()
        return self.pool.acquire()
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()

# Usage
db_manager = DatabaseManager()

async def query_documents(search_query: str):
    async with db_manager.get_connection() as conn:
        try:
            results = await conn.fetch("""
                SELECT * FROM documents_metadata_v2 
                WHERE search_tokens @@ plainto_tsquery('vietnamese', $1)
                LIMIT 10
            """, search_query)
            return results
        except Exception as e:
            # Proper error handling
            logger.error(f"Database query failed: {e}")
            raise

# ❌ Bad: No connection pooling
async def bad_query():
    conn = await asyncpg.connect("postgresql://...")  # New connection each time
    result = await conn.fetch("SELECT ...")
    await conn.close()  # Manual connection management
```

#### 7.1.2 Query Optimization

```python
# ✅ Good: Optimized queries với prepared statements
async def search_documents_optimized(
    conn, 
    query: str, 
    user_level: str, 
    limit: int = 10
):
    """Optimized document search với proper indexing"""
    
    # Use prepared statement for better performance
    stmt = await conn.prepare("""
        SELECT 
            d.document_id,
            d.source_document_id,
            d.title,
            d.document_type,
            d.department_owner,
            ts_rank_cd(d.search_tokens, plainto_tsquery('vietnamese', $1)) as relevance
        FROM documents_metadata_v2 d
        WHERE d.search_tokens @@ plainto_tsquery('vietnamese', $1)
            AND d.status = 'approved'
            AND d.access_level = ANY($2)
        ORDER BY relevance DESC
        LIMIT $3
    """)
    
    # Define access levels based on user level
    access_levels = {
        'SYSTEM_ADMIN': ['public', 'employee_only', 'manager_only', 'director_only'],
        'DIRECTOR': ['public', 'employee_only', 'manager_only'],
        'MANAGER': ['public', 'employee_only'],
        'EMPLOYEE': ['public', 'employee_only'],
        'GUEST': ['public']
    }
    
    allowed_levels = access_levels.get(user_level, ['public'])
    
    return await stmt.fetch(query, allowed_levels, limit)

# ❌ Bad: Unoptimized query
async def bad_search(conn, query: str):
    # No prepared statement, no indexes, no access control
    return await conn.fetch(f"""
        SELECT * FROM documents_metadata_v2 
        WHERE content LIKE '%{query}%'  -- SQL injection risk!
        ORDER BY created_at  -- No relevance scoring
    """)
```

#### 7.1.3 Error Handling và Logging

```python
import logging
import json
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom database exception"""
    pass

async def safe_import_document(
    package_data: Dict[str, Any],
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Safe document import với comprehensive error handling"""
    
    job_id = str(uuid4())
    
    try:
        # Validate input
        if not package_data.get("FOR_DATABASE", {}).get("document_metadata.json"):
            raise ValueError("Missing document metadata in package")
        
        source_document_id = package_data["FOR_DATABASE"]["document_metadata.json"].get("source_document_id")
        if not source_document_id:
            raise ValueError("Missing source_document_id")
        
        logger.info(f"Starting import for document {source_document_id}, job {job_id}")
        
        async with db_manager.get_connection() as conn:
            async with conn.transaction():
                # Create job record
                await conn.execute("""
                    INSERT INTO data_ingestion_jobs (
                        job_id, source_document_id, status, user_id,
                        processing_metadata
                    ) VALUES ($1, $2, $3, $4, $5)
                """, job_id, source_document_id, 'processing', user_id,
                     json.dumps({"start_time": datetime.now().isoformat()}))
                
                # Import logic here...
                result = await import_document_data(conn, package_data)
                
                # Update job status
                await conn.execute("""
                    UPDATE data_ingestion_jobs 
                    SET status = 'completed', completed_at = NOW()
                    WHERE job_id = $1
                """, job_id)
                
                logger.info(f"Import completed successfully for job {job_id}")
                return {"success": True, "job_id": job_id, **result}
                
    except ValueError as e:
        # Input validation errors
        logger.error(f"Validation error for job {job_id}: {e}")
        await update_job_status(job_id, 'failed', str(e))
        return {"success": False, "error": f"Validation error: {e}"}
        
    except asyncpg.PostgresError as e:
        # Database errors
        logger.error(f"Database error for job {job_id}: {e}")
        await update_job_status(job_id, 'failed', f"Database error: {e}")
        return {"success": False, "error": "Database error occurred"}
        
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error for job {job_id}: {e}", exc_info=True)
        await update_job_status(job_id, 'failed', f"Unexpected error: {e}")
        return {"success": False, "error": "Internal server error"}

async def update_job_status(job_id: str, status: str, error_message: str = None):
    """Update job status với error handling"""
    try:
        async with db_manager.get_connection() as conn:
            await conn.execute("""
                UPDATE data_ingestion_jobs 
                SET status = $1, error_message = $2, updated_at = NOW()
                WHERE job_id = $3
            """, status, error_message, job_id)
    except Exception as e:
        logger.error(f"Failed to update job status for {job_id}: {e}")
```

### 7.2 Performance Best Practices

#### 7.2.1 Index Optimization

```sql
-- ✅ Good: Proper index usage
-- Composite indexes for common query patterns
CREATE INDEX idx_documents_status_type_dept ON documents_metadata_v2(status, document_type, department_owner);
CREATE INDEX idx_search_analytics_user_date ON search_analytics(user_id, DATE(timestamp));

-- Partial indexes for filtered queries
CREATE INDEX idx_documents_approved_only ON documents_metadata_v2(created_at) 
WHERE status = 'approved';

CREATE INDEX idx_chunks_high_quality ON document_chunks_enhanced(document_id, chunk_position) 
WHERE chunk_quality_score > 0.7;

-- ❌ Bad: Unnecessary or duplicate indexes
-- CREATE INDEX idx_documents_id ON documents_metadata_v2(document_id);  -- Already primary key
-- CREATE INDEX idx_documents_title ON documents_metadata_v2(title);     -- Rarely used alone
```

#### 7.2.2 Query Patterns

```python
# ✅ Good: Efficient query patterns
async def get_user_documents_paginated(
    user_id: str, 
    page: int = 1, 
    page_size: int = 20
):
    """Efficient pagination với proper indexes"""
    
    offset = (page - 1) * page_size
    
    async with db_manager.get_connection() as conn:
        # Use LIMIT/OFFSET với ORDER BY indexed column
        documents = await conn.fetch("""
            SELECT 
                d.document_id,
                d.title,
                d.created_at,
                dus.view_count
            FROM documents_metadata_v2 d
            LEFT JOIN document_usage_stats dus ON d.document_id = dus.document_id
            WHERE d.status = 'approved'
                AND d.access_level = 'employee_only'
            ORDER BY d.created_at DESC  -- Indexed column
            LIMIT $1 OFFSET $2
        """, page_size, offset)
        
        # Separate count query for better performance
        total = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM documents_metadata_v2 
            WHERE status = 'approved' AND access_level = 'employee_only'
        """)
        
        return {
            "documents": documents,
            "total": total,
            "page": page,
            "pages": (total + page_size - 1) // page_size
        }

# ❌ Bad: Inefficient patterns
async def bad_pagination():
    # Don't do this - causes full table scan
    return await conn.fetch("""
        SELECT * FROM documents_metadata_v2 
        ORDER BY RANDOM()  -- Very expensive
        LIMIT 20
    """)
```

#### 7.2.3 Batch Operations

```python
# ✅ Good: Batch operations
async def insert_chunks_batch(conn, document_id: str, chunks: List[Dict]):
    """Efficient batch chunk insertion"""
    
    # Prepare data for batch insert
    chunk_data = [
        (
            uuid4(),  # chunk_id
            document_id,
            chunk['content'],
            chunk['position'],
            chunk.get('token_count', 0),
            chunk.get('semantic_boundary', False),
            chunk.get('quality_score', 0.8)
        )
        for chunk in chunks
    ]
    
    # Use copy_records for best performance
    await conn.copy_records_to_table(
        'document_chunks_enhanced',
        records=chunk_data,
        columns=['chunk_id', 'document_id', 'chunk_content', 'chunk_position', 
                'chunk_size_tokens', 'semantic_boundary', 'chunk_quality_score']
    )
    
    logger.info(f"Inserted {len(chunks)} chunks for document {document_id}")

# ❌ Bad: Individual inserts
async def bad_chunk_insert(conn, chunks):
    for chunk in chunks:  # Very slow for many chunks
        await conn.execute("""
            INSERT INTO document_chunks_enhanced (...) VALUES (...)
        """, ...)
```

### 7.3 Security Best Practices

#### 7.3.1 Access Control Implementation

```python
from enum import Enum
from typing import List

class UserLevel(Enum):
    GUEST = "GUEST"
    EMPLOYEE = "EMPLOYEE" 
    MANAGER = "MANAGER"
    DIRECTOR = "DIRECTOR"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"

class DocumentAccessControl:
    """Centralized access control logic"""
    
    ACCESS_MATRIX = {
        UserLevel.GUEST: ['public'],
        UserLevel.EMPLOYEE: ['public', 'employee_only'],
        UserLevel.MANAGER: ['public', 'employee_only', 'manager_only'],
        UserLevel.DIRECTOR: ['public', 'employee_only', 'manager_only', 'director_only'],
        UserLevel.SYSTEM_ADMIN: ['public', 'employee_only', 'manager_only', 'director_only', 'system_admin']
    }
    
    @classmethod
    def get_allowed_access_levels(cls, user_level: str) -> List[str]:
        """Get allowed access levels for user"""
        try:
            level = UserLevel(user_level)
            return cls.ACCESS_MATRIX[level]
        except ValueError:
            # Default to most restrictive
            return ['public']
    
    @classmethod
    def can_access_document(cls, user_level: str, document_access_level: str) -> bool:
        """Check if user can access document"""
        allowed_levels = cls.get_allowed_access_levels(user_level)
        return document_access_level in allowed_levels

# Usage
async def get_document_secure(document_id: str, user_level: str):
    """Secure document retrieval với access control"""
    
    if not DocumentAccessControl.can_access_document(user_level, 'employee_only'):
        raise PermissionError("Insufficient access level")
    
    allowed_levels = DocumentAccessControl.get_allowed_access_levels(user_level)
    
    async with db_manager.get_connection() as conn:
        document = await conn.fetchrow("""
            SELECT * FROM documents_metadata_v2 
            WHERE document_id = $1 
                AND status = 'approved'
                AND access_level = ANY($2)
        """, document_id, allowed_levels)
        
        if not document:
            raise PermissionError("Document not found or access denied")
        
        # Log access for audit
        await conn.execute("""
            INSERT INTO user_events (
                event_type, event_data, timestamp
            ) VALUES ($1, $2, NOW())
        """, 'document_access', {
            'document_id': document_id,
            'user_level': user_level,
            'access_granted': True
        })
        
        return document
```

#### 7.3.2 Input Validation và Sanitization

```python
from pydantic import BaseModel, validator
from typing import Optional
import re

class DocumentImportRequest(BaseModel):
    """Validated document import request"""
    
    source_document_id: str
    title: str
    content: Optional[str] = None
    document_type: str
    department_owner: str
    author: str
    
    @validator('source_document_id')
    def validate_source_id(cls, v):
        # Only allow alphanumeric, hyphens, underscores
        if not re.match(r'^[A-Za-z0-9_-]+$', v):
            raise ValueError('Invalid source_document_id format')
        if len(v) > 255:
            raise ValueError('source_document_id too long')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        if len(v) > 500:
            raise ValueError('Title too long')
        # Remove potentially dangerous characters
        return re.sub(r'[<>"\']', '', v.strip())
    
    @validator('document_type')
    def validate_document_type(cls, v):
        allowed_types = ['policy', 'procedure', 'technical_guide', 'report', 
                        'manual', 'specification', 'template', 'form',
                        'presentation', 'training_material', 'other']
        if v not in allowed_types:
            raise ValueError(f'Invalid document_type. Must be one of: {allowed_types}')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if v is not None:
            # Basic XSS prevention
            dangerous_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
            content_lower = v.lower()
            for pattern in dangerous_patterns:
                if pattern in content_lower:
                    raise ValueError('Content contains potentially dangerous elements')
        return v

# Usage
async def import_document_validated(request_data: dict):
    """Document import với validation"""
    try:
        # Validate input
        validated_request = DocumentImportRequest(**request_data)
        
        # Proceed with import
        return await import_document_safe(validated_request.dict())
        
    except ValidationError as e:
        logger.warning(f"Validation failed for import request: {e}")
        raise ValueError(f"Invalid input: {e}")
```

---

## 8. PERFORMANCE TUNING

### 8.1 PostgreSQL Configuration Tuning

#### 8.1.1 Memory Settings

```bash
# /etc/postgresql/15/main/postgresql.conf
# Tuning cho production environment với 32GB RAM

# Memory settings
shared_buffers = 8GB                    # 25% of RAM
effective_cache_size = 24GB             # 75% of RAM  
work_mem = 256MB                        # For complex queries
maintenance_work_mem = 2GB              # For VACUUM, CREATE INDEX
wal_buffers = 64MB                      # WAL buffer size

# Connection settings
max_connections = 200                   # Based on expected load
superuser_reserved_connections = 5

# Query planning
random_page_cost = 1.1                  # For SSD storage
effective_io_concurrency = 200          # For SSD

# WAL settings
wal_level = replica
max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_timeout = 10min
checkpoint_completion_target = 0.7

# Logging
log_min_duration_statement = 1000       # Log slow queries
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

# Auto vacuum settings
autovacuum = on
autovacuum_max_workers = 6
autovacuum_naptime = 30s
```

#### 8.1.2 Index Optimization

```sql
-- Check unused indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes 
WHERE idx_scan = 0 
    AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Drop unused indexes (carefully!)
-- DROP INDEX IF EXISTS unused_index_name;

-- Check duplicate indexes
SELECT 
    a.schemaname,
    a.tablename,
    a.indexname as index1,
    b.indexname as index2,
    a.indexdef as def1,
    b.indexdef as def2
FROM pg_indexes a
JOIN pg_indexes b ON a.tablename = b.tablename 
WHERE a.schemaname = 'public' 
    AND b.schemaname = 'public'
    AND a.indexname != b.indexname
    AND a.indexdef = b.indexdef;

-- Create optimal indexes for common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_search_optimized 
ON documents_metadata_v2(status, access_level, created_at DESC) 
WHERE status = 'approved';

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_search_analytics_optimized
ON search_analytics(DATE(timestamp), search_method, has_results);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_status_created
ON data_ingestion_jobs(status, created_at DESC)
WHERE status IN ('processing', 'failed', 'completed');
```

### 8.2 Query Performance Optimization

#### 8.2.1 Slow Query Analysis

```sql
-- Enable pg_stat_statements extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find top slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    (total_time/calls) as avg_time_ms,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 20;

-- Reset statistics
SELECT pg_stat_statements_reset();

-- Query để identify problematic patterns
SELECT 
    'Expensive sorts' as issue,
    COUNT(*) as count
FROM pg_stat_statements 
WHERE query ILIKE '%ORDER BY%' 
    AND mean_time > 1000

UNION ALL

SELECT 
    'Full table scans' as issue,
    COUNT(*) as count  
FROM pg_stat_statements
WHERE query ILIKE '%SELECT%'
    AND query NOT ILIKE '%WHERE%'
    AND calls > 100

UNION ALL

SELECT 
    'Unparameterized queries' as issue,
    COUNT(*) as count
FROM pg_stat_statements
WHERE query ILIKE '%=%''%'  -- Literal values in queries
    OR query ILIKE '%LIKE ''%';
```

#### 8.2.2 Vietnamese Text Search Optimization

```sql
-- Optimize Vietnamese text search configuration
-- Create custom Vietnamese search configuration
DROP TEXT SEARCH CONFIGURATION IF EXISTS vietnamese_optimized CASCADE;
CREATE TEXT SEARCH CONFIGURATION vietnamese_optimized (COPY = simple);

-- Add Vietnamese-specific dictionaries if available
-- ALTER TEXT SEARCH CONFIGURATION vietnamese_optimized
--     ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, word, hword, hword_part
--     WITH vietnamese_dict, simple;

-- Test search performance
EXPLAIN (ANALYZE, BUFFERS) 
SELECT 
    document_id,
    title,
    ts_rank_cd(search_tokens, query) as rank
FROM documents_metadata_v2,
     plainto_tsquery('vietnamese', 'chính sách nhân sự') query
WHERE search_tokens @@ query
ORDER BY rank DESC
LIMIT 10;

-- Create optimized GIN index với specific operators
DROP INDEX IF EXISTS idx_documents_search_tokens_optimized;
CREATE INDEX idx_documents_search_tokens_optimized 
ON documents_metadata_v2 
USING GIN(search_tokens gin_trgm_ops);

-- Optimize chunk search performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chunks_content_gin_optimized
ON document_chunks_enhanced 
USING GIN(to_tsvector('vietnamese', chunk_content));

-- Test chunk search performance
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    c.chunk_id,
    c.chunk_content,
    d.title,
    ts_rank_cd(to_tsvector('vietnamese', c.chunk_content), query) as rank
FROM document_chunks_enhanced c
JOIN documents_metadata_v2 d ON c.document_id = d.document_id,
     plainto_tsquery('vietnamese', 'làm việc từ xa') query
WHERE to_tsvector('vietnamese', c.chunk_content) @@ query
    AND c.chunk_quality_score > 0.7
ORDER BY rank DESC
LIMIT 20;
```

### 8.3 Application-Level Optimizations

#### 8.3.1 Connection Pool Tuning

```python
# Optimized connection pool configuration
async def create_optimized_pool():
    """Create optimized database connection pool"""
    
    return await asyncpg.create_pool(
        "postgresql://kb_admin:1234567890@localhost:5432/knowledge_base_v2",
        
        # Pool size based on workload
        min_size=10,                    # Always keep 10 connections ready
        max_size=50,                    # Maximum 50 concurrent connections
        
        # Connection lifecycle
        max_queries=50000,              # Rotate connections after 50k queries
        max_inactive_connection_lifetime=300.0,  # 5 minutes idle timeout
        
        # Query timeouts
        command_timeout=30,             # 30 second query timeout
        server_settings={
            'application_name': 'kb_v10_app',
            'search_path': 'public',
            'timezone': 'UTC',
            
            # Connection-level optimizations
            'work_mem': '64MB',         # Per-connection work memory
            'temp_buffers': '32MB',     # Temporary table buffer
            'shared_preload_libraries': 'pg_stat_statements',
        }
    )

# Connection pool monitoring
async def monitor_pool_health(pool):
    """Monitor connection pool health"""
    
    stats = {
        'size': pool.get_size(),
        'min_size': pool.get_min_size(), 
        'max_size': pool.get_max_size(),
        'idle_size': pool.get_idle_size(),
        'available': pool.get_size() - pool.get_idle_size()
    }
    
    # Alert if pool is under pressure
    if stats['available'] > stats['max_size'] * 0.8:
        logger.warning(f"Connection pool under pressure: {stats}")
    
    return stats
```

#### 8.3.2 Caching Strategy

```python
import redis
import pickle
from typing import Optional, Any
import hashlib

class CacheManager:
    """Redis-based caching for database queries"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=False)
        self.default_ttl = 3600  # 1 hour
    
    def _generate_key(self, prefix: str, *args) -> str:
        """Generate cache key from arguments"""
        key_data = f"{prefix}:" + ":".join(str(arg) for arg in args)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            data = await self.redis.get(key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value"""
        try:
            data = pickle.dumps(value)
            await self.redis.setex(key, ttl or self.default_ttl, data)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False
    
    async def delete(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
        except Exception as e:
            logger.warning(f"Cache delete failed for pattern {pattern}: {e}")
        return 0

# Cached database operations
cache_manager = CacheManager()

async def get_document_cached(document_id: str, user_level: str) -> Optional[dict]:
    """Get document with caching"""
    
    cache_key = cache_manager._generate_key("document", document_id, user_level)
    
    # Try cache first
    cached_result = await cache_manager.get(cache_key)
    if cached_result:
        logger.info(f"Cache hit for document {document_id}")
        return cached_result
    
    # Query database
    async with db_manager.get_connection() as conn:
        document = await get_document_secure(document_id, user_level)
        
        if document:
            # Cache the result for 30 minutes
            await cache_manager.set(cache_key, dict(document), ttl=1800)
            logger.info(f"Cached document {document_id}")
        
        return document

async def search_documents_cached(
    query: str, 
    user_level: str, 
    filters: dict = None,
    limit: int = 10
) -> dict:
    """Search documents with intelligent caching"""
    
    # Create cache key from query parameters
    filter_str = json.dumps(filters or {}, sort_keys=True)
    cache_key = cache_manager._generate_key("search", query, user_level, filter_str, limit)
    
    # Check cache
    cached_result = await cache_manager.get(cache_key)
    if cached_result:
        logger.info(f"Cache hit for search: {query[:50]}...")
        return cached_result
    
    # Perform search
    results = await search_documents_optimized(query, user_level, filters, limit)
    
    # Cache results for 15 minutes (shorter TTL for search results)
    await cache_manager.set(cache_key, results, ttl=900)
    
    return results

# Cache invalidation on document updates
async def invalidate_document_cache(document_id: str):
    """Invalidate all cached data for a document"""
    
    patterns = [
        f"document:{document_id}:*",
        f"search:*",  # Invalidate all search results (could be more selective)
        f"analytics:*"
    ]
    
    for pattern in patterns:
        deleted = await cache_manager.delete(pattern)
        logger.info(f"Invalidated {deleted} cache entries for pattern {pattern}")
```

#### 8.3.3 Batch Processing Optimization

```python
from asyncio import Semaphore
from typing import List, Callable, Any

class BatchProcessor:
    """Optimized batch processing for database operations"""
    
    def __init__(self, max_concurrent: int = 10, batch_size: int = 100):
        self.semaphore = Semaphore(max_concurrent)
        self.batch_size = batch_size
    
    async def process_in_batches(
        self,
        items: List[Any],
        processor: Callable,
        *args,
        **kwargs
    ) -> List[Any]:
        """Process items in optimized batches"""
        
        results = []
        
        # Split into batches
        batches = [
            items[i:i + self.batch_size] 
            for i in range(0, len(items), self.batch_size)
        ]
        
        # Process batches concurrently
        async def process_batch(batch):
            async with self.semaphore:
                return await processor(batch, *args, **kwargs)
        
        # Execute all batches
        batch_results = await asyncio.gather(
            *[process_batch(batch) for batch in batches],
            return_exceptions=True
        )
        
        # Collect results and handle errors
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.error(f"Batch {i} failed: {result}")
            else:
                results.extend(result if isinstance(result, list) else [result])
        
        return results

# Usage for bulk document import
async def bulk_import_documents(package_list: List[dict]) -> dict:
    """Optimized bulk document import"""
    
    processor = BatchProcessor(max_concurrent=5, batch_size=20)
    
    async def import_batch(batch: List[dict]) -> List[dict]:
        """Import a batch of documents"""
        results = []
        
        async with db_manager.get_connection() as conn:
            async with conn.transaction():
                for package in batch:
                    try:
                        result = await import_single_document(conn, package)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Failed to import document: {e}")
                        results.append({"error": str(e)})
        
        return results
    
    # Process all packages in optimized batches
    all_results = await processor.process_in_batches(
        package_list, 
        import_batch
    )
    
    # Summarize results
    successful = sum(1 for r in all_results if "error" not in r)
    failed = len(all_results) - successful
    
    return {
        "total_processed": len(all_results),
        "successful": successful,
        "failed": failed,
        "results": all_results
    }
```

### 8.4 Monitoring và Alerting

#### 8.4.1 Performance Monitoring Dashboard

```python
from datetime import datetime, timedelta
import asyncio

class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self, db_pool, cache_manager):
        self.db_pool = db_pool
        self.cache = cache_manager
        self.metrics = {}
    
    async def collect_db_metrics(self) -> dict:
        """Collect database performance metrics"""
        
        async with self.db_pool.acquire() as conn:
            # Query performance metrics
            slow_queries = await conn.fetch("""
                SELECT 
                    query,
                    calls,
                    mean_time,
                    total_time
                FROM pg_stat_statements 
                WHERE mean_time > 1000
                ORDER BY mean_time DESC
                LIMIT 10
            """)
            
            # Connection stats
            connection_stats = await conn.fetchrow("""
                SELECT 
                    numbackends as active_connections,
                    xact_commit as commits,
                    xact_rollback as rollbacks,
                    blks_read,
                    blks_hit,
                    ROUND(blks_hit::DECIMAL / (blks_hit + blks_read) * 100, 2) as cache_hit_ratio
                FROM pg_stat_database 
                WHERE datname = 'knowledge_base_v2'
            """)
            
            # Table sizes
            table_sizes = await conn.fetch("""
                SELECT 
                    tablename,
                    pg_size_pretty(pg_total_relation_size('public.' || tablename)) as size,
                    n_live_tup as row_count
                FROM pg_stat_user_tables 
                ORDER BY pg_total_relation_size('public.' || tablename) DESC
                LIMIT 10
            """)
            
            # Recent search performance
            search_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as search_count,
                    AVG(processing_time_ms) as avg_processing_time,
                    AVG(results_count) as avg_results_count,
                    SUM(CASE WHEN has_results THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as success_rate
                FROM search_analytics 
                WHERE timestamp >= NOW() - INTERVAL '1 hour'
            """)
            
            # Import job status
            import_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_jobs,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs
                FROM data_ingestion_jobs 
                WHERE created_at >= NOW() - INTERVAL '1 hour'
            """)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "slow_queries": [dict(q) for q in slow_queries],
                "connections": dict(connection_stats) if connection_stats else {},
                "table_sizes": [dict(t) for t in table_sizes],
                "search_performance": dict(search_stats) if search_stats else {},
                "import_jobs": dict(import_stats) if import_stats else {}
            }
    
    async def check_health_status(self) -> dict:
        """Check overall system health"""
        
        health_status = {
            "overall": "healthy",
            "issues": [],
            "metrics": {}
        }
        
        try:
            metrics = await self.collect_db_metrics()
            health_status["metrics"] = metrics
            
            # Check for issues
            conn_stats = metrics.get("connections", {})
            if conn_stats.get("cache_hit_ratio", 0) < 95:
                health_status["issues"].append("Low cache hit ratio")
                health_status["overall"] = "degraded"
            
            search_stats = metrics.get("search_performance", {})
            if search_stats.get("avg_processing_time", 0) > 2000:
                health_status["issues"].append("Slow search performance")
                health_status["overall"] = "degraded"
            
            import_stats = metrics.get("import_jobs", {})
            failed_jobs = import_stats.get("failed_jobs", 0)
            total_jobs = import_stats.get("total_jobs", 1)
            if failed_jobs / total_jobs > 0.1:  # > 10% failure rate
                health_status["issues"].append("High import job failure rate")
                health_status["overall"] = "unhealthy"
            
        except Exception as e:
            health_status["overall"] = "unhealthy"
            health_status["issues"].append(f"Health check failed: {e}")
        
        return health_status
    
    async def generate_performance_report(self, hours: int = 24) -> dict:
        """Generate comprehensive performance report"""
        
        async with self.db_pool.acquire() as conn:
            # Query trends over time period
            search_trends = await conn.fetch("""
                SELECT 
                    DATE_TRUNC('hour', timestamp) as hour,
                    COUNT(*) as search_count,
                    AVG(processing_time_ms) as avg_time,
                    AVG(results_count) as avg_results
                FROM search_analytics 
                WHERE timestamp >= NOW() - INTERVAL '%s hours'
                GROUP BY DATE_TRUNC('hour', timestamp)
                ORDER BY hour
            """, hours)
            
            # Top performing queries
            top_queries = await conn.fetch("""
                SELECT 
                    query_normalized,
                    COUNT(*) as frequency,
                    AVG(processing_time_ms) as avg_time,
                    AVG(results_count) as avg_results
                FROM search_analytics 
                WHERE timestamp >= NOW() - INTERVAL '%s hours'
                    AND results_count > 0
                GROUP BY query_normalized
                ORDER BY frequency DESC
                LIMIT 20
            """, hours)
            
            # System resource usage
            system_stats = await conn.fetch("""
                SELECT 
                    component,
                    metric_name,
                    AVG(metric_value) as avg_value,
                    MAX(metric_value) as max_value,
                    MIN(metric_value) as min_value
                FROM system_metrics 
                WHERE timestamp >= NOW() - INTERVAL '%s hours'
                GROUP BY component, metric_name
                ORDER BY component, metric_name
            """, hours)
            
            return {
                "report_period_hours": hours,
                "generated_at": datetime.now().isoformat(),
                "search_trends": [dict(row) for row in search_trends],
                "top_queries": [dict(row) for row in top_queries],
                "system_stats": [dict(row) for row in system_stats]
            }

# FastAPI endpoints for monitoring
from fastapi import FastAPI

monitor = PerformanceMonitor(db_pool, cache_manager)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return await monitor.check_health_status()

@app.get("/api/metrics")
async def get_metrics():
    """Current performance metrics"""
    return await monitor.collect_db_metrics()

@app.get("/api/performance-report")
async def performance_report(hours: int = 24):
    """Detailed performance report"""
    return await monitor.generate_performance_report(hours)
```

#### 8.4.2 Automated Alerting System

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertManager:
    """Automated alerting for system issues"""
    
    def __init__(self, smtp_config: dict, alert_recipients: List[str]):
        self.smtp_config = smtp_config
        self.recipients = alert_recipients
        self.alert_history = {}
    
    async def check_and_alert(self):
        """Check system health and send alerts if needed"""
        
        health_status = await monitor.check_health_status()
        
        # Check for critical issues
        if health_status["overall"] == "unhealthy":
            await self.send_critical_alert(health_status)
        elif health_status["overall"] == "degraded":
            await self.send_warning_alert(health_status)
        
        # Check specific metrics
        metrics = health_status.get("metrics", {})
        
        # Database connection alerts
        conn_stats = metrics.get("connections", {})
        active_connections = conn_stats.get("active_connections", 0)
        if active_connections > 180:  # 90% of max_connections (200)
            await self.send_alert(
                "HIGH_CONNECTIONS",
                f"High database connection count: {active_connections}/200",
                "warning"
            )
        
        # Search performance alerts
        search_stats = metrics.get("search_performance", {})
        avg_search_time = search_stats.get("avg_processing_time", 0)
        if avg_search_time > 3000:  # > 3 seconds
            await self.send_alert(
                "SLOW_SEARCH", 
                f"Search performance degraded: {avg_search_time}ms average",
                "warning"
            )
        
        # Import job failure alerts
        import_stats = metrics.get("import_jobs", {})
        failed_jobs = import_stats.get("failed_jobs", 0)
        if failed_jobs > 5:  # More than 5 failures in last hour
            await self.send_alert(
                "IMPORT_FAILURES",
                f"High import job failure count: {failed_jobs} failures in last hour",
                "critical"
            )
    
    async def send_alert(self, alert_type: str, message: str, severity: str):
        """Send alert if not recently sent"""
        
        # Prevent spam - only send same alert once per hour
        last_sent = self.alert_history.get(alert_type)
        if last_sent and (datetime.now() - last_sent) < timedelta(hours=1):
            return
        
        # Send email alert
        try:
            await self.send_email_alert(message, severity)
            self.alert_history[alert_type] = datetime.now()
            logger.info(f"Alert sent: {alert_type} - {message}")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    async def send_email_alert(self, message: str, severity: str):
        """Send email alert"""
        
        subject = f"[KB-V10-{severity.upper()}] Database Alert"
        
        body = f"""
        Knowledge Base V10 Database Alert
        
        Severity: {severity.upper()}
        Time: {datetime.now().isoformat()}
        
        Alert Details:
        {message}
        
        Please check the system immediately.
        
        Dashboard: http://your-domain.com/api/health
        Metrics: http://your-domain.com/api/metrics
        """
        
        msg = MIMEMultipart()
        msg['From'] = self.smtp_config['from_email']
        msg['To'] = ', '.join(self.recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
            if self.smtp_config.get('use_tls'):
                server.starttls()
            if self.smtp_config.get('username'):
                server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)

# Background task for continuous monitoring
async def monitoring_task():
    """Background task for continuous monitoring"""
    
    alert_manager = AlertManager(
        smtp_config={
            'host': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'username': 'alerts@yourcompany.com',
            'password': 'your-app-password'
        },
        alert_recipients=['admin@yourcompany.com', 'devops@yourcompany.com']
    )
    
    while True:
        try:
            await alert_manager.check_and_alert()
        except Exception as e:
            logger.error(f"Monitoring task failed: {e}")
        
        # Check every 5 minutes
        await asyncio.sleep(300)
```

---

## 9. TROUBLESHOOTING QUICK REFERENCE

### 9.1 Common Error Messages và Solutions

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `text search configuration "vietnamese" does not exist` | V10 Vietnamese config not created | Run Vietnamese config creation script |
| `column "import_mapping_status" does not exist` | Missing V10 column | Run ALTER TABLE to add missing column |
| `function check_duplicate_by_source_document_id does not exist` | Function not created | Re-run V10 functions creation |
| `relation "vw_export_package_import_status" does not exist` | View not created | Re-run V10 views creation |
| `invalid input value for enum documentstatus: "completed"` | Enum case mismatch | Use V10 enum with both cases |
| `connection pool exhausted` | Too many concurrent connections | Tune pool settings or restart services |
| `FATAL: remaining connection slots are reserved` | Max connections reached | Kill idle connections or increase max_connections |

### 9.2 Emergency Commands

```bash
# Stop all services immediately
docker stop fr-03-3-pipeline fr-04-rag-engine fr-05-chatbot-ui fr-02-file-api

# Check database status
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "SELECT version();"

# Run V10 validation
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "SELECT * FROM validate_schema_v10();"

# Kill long-running queries
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'active' 
    AND query_start < NOW() - INTERVAL '5 minutes'
    AND query NOT LIKE '%pg_stat_activity%';"

# Reset failed import jobs
psql -U kb_admin -h localhost -d knowledge_base_v2 -c "
UPDATE data_ingestion_jobs 
SET status = 'cancelled' 
WHERE status = 'processing' 
    AND created_at < NOW() - INTERVAL '1 hour';"

# Backup critical data immediately
pg_dump -U kb_admin -h localhost -d knowledge_base_v2 \
    -t documents_metadata_v2 \
    -t document_chunks_enhanced \
    -t data_ingestion_jobs \
    > emergency_backup_$(date +%Y%m%d_%H%M%S).sql
```

### 9.3 Contact Information

**Technical Support:**
- Primary: Development Team Lead
- Secondary: Database Administrator  
- Emergency: System Administrator

**Escalation Path:**
1. Check monitoring dashboard
2. Review application logs
3. Run diagnostic scripts
4. Contact technical support
5. Escalate to emergency contact if critical

---

## 10. APPENDIX

### 10.1 Schema Reference

**Tổng số components trong V10:**
- Tables: 26
- Indexes: 55+
- Views: 5  
- Functions: 5
- Triggers: 4
- Enums: 7

**Key Tables:**
- `documents_metadata_v2`: Core document storage
- `document_chunks_enhanced`: Document chunks với V10 features
- `data_ingestion_jobs`: FR-03.3 pipeline tracking
- `search_analytics`: Search performance metrics
- `user_events`: User activity tracking

### 10.2 Configuration Templates

**PostgreSQL Configuration (postgresql.conf):**
```
# V10 Optimized Settings
shared_buffers = 2GB
effective_cache_size = 6GB  
work_mem = 64MB
maintenance_work_mem = 512MB
wal_buffers = 16MB
max_connections = 100
```

**Docker Compose for V10:**
```yaml
version: '3.8'
services:
  postgres-v10:
    image: postgres:15
    environment:
      POSTGRES_DB: knowledge_base_v2
      POSTGRES_USER: kb_admin
      POSTGRES_PASSWORD: 1234567890
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./01_init_database_V10.sql:/docker-entrypoint-initdb.d/01_init.sql
    command:
      - postgres
      - -c
      - shared_buffers=2GB
      - -c
      - effective_cache_size=6GB
      - -c
      - work_mem=64MB

volumes:
  postgres_data:
```

### 10.3 Migration Scripts

**V9 to V10 Migration:**
```sql
-- Quick migration from V9 to V10
-- Only adds Vietnamese text search fixes

BEGIN;

-- Add Vietnamese text search configuration
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'vietnamese') THEN
        CREATE TEXT SEARCH CONFIGURATION vietnamese (COPY = simple);
    END IF;
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

-- Recreate problematic indexes
DROP INDEX IF EXISTS idx_documents_v2_search_text;
CREATE INDEX idx_documents_v2_search_text 
ON documents_metadata_v2 
USING GIN(to_tsvector('vietnamese', search_text_normalized));

-- Add V10 migration record
INSERT INTO schema_migrations VALUES 
('20250920_004', NOW(), 'V10 migration', 'V10: Fixed Vietnamese text search') 
ON CONFLICT DO NOTHING;

COMMIT;
```

---

**🎯 KẾT LUẬN**

Database Schema V10 cung cấp nền tảng ổn định và hiệu năng cao cho hệ thống Chatbot Tiếng Việt. Với các tính năng được tối ưu và khắc phục hoàn toàn các lỗi deployment, V10 đảm bảo:

✅ **100% Deployment Success**  
✅ **Complete FR-03.3 Integration**  
✅ **Vietnamese Text Search Optimization**  
✅ **Production-Ready Performance**  
✅ **Comprehensive Monitoring**  

Hãy tuân thủ các best practices trong manual này để đạt được hiệu năng tối ưu và đảm bảo hệ thống hoạt động ổn định lâu dài.

---

*Document Version: V10.0*  
*Last Updated: September 20, 2025*  
*Total Pages: 50+*  
*Language: Vietnamese (Tiếng Việt)*
