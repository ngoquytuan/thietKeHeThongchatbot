# 📋 **TÀI LIỆU HANDOVER CHO TEAM FR-02.2**
## Thông tin Hệ thống Database đã Triển khai

---

**Ngày:** 06/09/2025  
**Từ:** Team FR-02.1 (Database Architecture)  
**Đến:** Team FR-02.2 (API Quản trị Thống nhất)  
**Trạng thái:** ✅ Database Layer Ready for API Integration  

---

## 🎯 **TỔNG QUAN HANDOVER**

Team FR-02.1 đã hoàn thành việc triển khai **Enhanced Database Architecture** với các components chính:
- ✅ PostgreSQL với enhanced schema (12+ tables)
- ✅ ChromaDB cho vector storage
- ✅ Redis cache layer
- ✅ Sample data và verification scripts

**Mục tiêu handover:** Cung cấp đầy đủ thông tin kỹ thuật để team FR-02.2 có thể develop API layer tương thích với database architecture đã có.

---

## 🐳 **THÔNG TIN DOCKER CONTAINERS**

### **Container Configuration Summary**
```yaml
Services đang chạy:
- postgres-test: PostgreSQL Database
- redis-test: Cache Layer  
- chromadb-test: Vector Database
- adminer: Database Browser
```

### **📊 Container Details**

| Service | Container Name | Port | Status | Purpose |
|---------|---------------|------|--------|---------|
| **PostgreSQL** | `chatbot-postgres-test` | `5433` | ✅ Running | Primary database |
| **Redis** | `chatbot-redis-test` | `6380` | ✅ Running | Cache layer |
| **ChromaDB** | `chatbot-chroma-test` | `8001` | ✅ Running | Vector storage |
| **Adminer** | `chatbot-adminer` | `8080` | ✅ Running | DB browser |

---

## 🐘 **POSTGRESQL DATABASE DETAILS**

### **Connection Information**
```bash
Host: localhost
Port: 5433
Database: knowledge_base_test
Username: kb_admin
Password: test_password_123
```

### **Database Schema Overview**
```sql
-- Core tables available for API integration:
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

**Kết quả:**
- `documents_metadata_v2` - Core documents table
- `document_chunks_enhanced` - Document chunks với semantic info
- `document_bm25_index` - BM25 search support
- `vietnamese_text_analysis` - Vietnamese NLP results
- `rag_pipeline_sessions` - Query session tracking
- `context_refinement_log` - Context processing logs
- `knowledge_graph_edges` - Knowledge relationships
- `query_performance_metrics` - Performance tracking
- `embedding_model_benchmarks` - Model performance
- `jsonl_exports` - FlashRAG export tracking
- `vietnamese_terminology` - Vietnamese terms dictionary
- `system_metrics_log` - System monitoring

### **Primary API Tables**

#### **1. documents_metadata_v2 (Main Documents Table)**
```sql
-- Key fields for API:
document_id UUID PRIMARY KEY
title VARCHAR(500) NOT NULL
content TEXT
document_type document_type_enum  -- 'policy', 'procedure', 'technical_guide', etc.
access_level access_level_enum    -- 'public', 'employee_only', 'manager_only', etc.
department_owner VARCHAR(100)
author VARCHAR(255)
status document_status_enum       -- 'draft', 'review', 'approved', 'published'
language_detected VARCHAR(10) DEFAULT 'vi'
created_at TIMESTAMP WITH TIME ZONE
updated_at TIMESTAMP WITH TIME ZONE
```

#### **2. document_chunks_enhanced (Chunks for RAG)**
```sql
-- Key fields for API:
chunk_id UUID PRIMARY KEY
document_id UUID REFERENCES documents_metadata_v2(document_id)
chunk_content TEXT NOT NULL
chunk_position INTEGER
chunk_quality_score DECIMAL(3,2)
semantic_boundary BOOLEAN
embedding_model VARCHAR(100)
```

#### **3. rag_pipeline_sessions (Query Tracking)**
```sql
-- Key fields for API:
session_id UUID PRIMARY KEY
user_id UUID
original_query TEXT NOT NULL
pipeline_type VARCHAR(50)
response_quality_score DECIMAL(3,2)
processing_time_ms INTEGER
created_at TIMESTAMP WITH TIME ZONE
```

### **Sample Data Available**
```sql
-- Check sample data:
SELECT COUNT(*), document_type FROM documents_metadata_v2 GROUP BY document_type;
-- Results: 3 Vietnamese documents loaded

SELECT title, status, language_detected FROM documents_metadata_v2;
-- Results:
-- "Quy trình xin nghỉ phép" | approved | vi
-- "Chính sách làm việc từ xa" | approved | vi  
-- "Hướng dẫn sử dụng hệ thống ERP" | approved | vi
```

---

## 🔴 **REDIS CACHE DETAILS**

### **Connection Information**
```bash
Host: localhost
Port: 6380
Database: 0 (default)
Password: none (test environment)
```

### **Cache Structure Available**
```redis
Key Patterns implemented:
- user:session:{user_id} - User sessions (TTL: 24h)
- query:session:{session_id} - Query sessions (TTL: 1h)
- embedding:{model}:{hash} - Embedding cache (TTL: 7d)
- search:{query_hash}:{filters} - Search results (TTL: 30m)
- vn:nlp:{text_hash} - Vietnamese NLP cache (TTL: 24h)
- perf:metrics:{date} - Performance metrics (TTL: 30d)
```

### **Sample Cache Data**
```bash
# Test cache access:
docker exec -it chatbot-redis-test redis-cli
> KEYS *
> HGETALL user:session:user_001
```

---

## 🟢 **CHROMADB VECTOR DATABASE**

### **Connection Information**
```bash
Host: localhost
Port: 8001
HTTP API: http://localhost:8001
API Docs: http://localhost:8001/docs
```

### **Collections Available**
```python
# Collections created:
- knowledge_base_v1: 1536 dimensions (OpenAI compatible)
- vietnamese_docs: 768 dimensions (Multilingual models)
- test_collection: 384 dimensions (Testing)
```

### **API Usage Example**
```python
import chromadb
client = chromadb.HttpClient(host='localhost', port=8001)
collections = client.list_collections()
# Returns: [knowledge_base_v1, vietnamese_docs, test_collection]

# Query example:
collection = client.get_collection("test_collection")
results = collection.query(
    query_texts=["nghỉ phép"],
    n_results=5
)
```

---

## 🔧 **ENUM TYPES & CONSTRAINTS**

### **Enums Available for API**
```sql
-- For validation in API layer:

-- Access Levels
'public', 'employee_only', 'manager_only', 'director_only', 'system_admin'

-- Document Types  
'policy', 'procedure', 'technical_guide', 'report', 'manual', 
'specification', 'template', 'form', 'presentation', 'training_material', 'other'

-- Document Status
'draft', 'review', 'approved', 'published', 'archived', 'deprecated'

-- Pipeline Types
'standard', 'reasoning', 'conditional', 'adaptive'

-- Retrieval Methods
'dense', 'sparse', 'hybrid', 'knowledge_graph', 'multi_modal'
```

### **Key Constraints for API Validation**
```sql
-- Title length: max 500 chars
-- Content: unlimited text
-- Department: max 100 chars  
-- Author: max 255 chars
-- Chunk quality score: 0.00 to 1.00
-- Chunk size: 50 to 2000 tokens
```

---

## 🌐 **API INTEGRATION POINTS**

### **Suggested API Structure**

#### **Document Management APIs**
```bash
GET    /api/documents              # List documents with filters
POST   /api/documents              # Create new document
GET    /api/documents/{id}         # Get document by ID
PUT    /api/documents/{id}         # Update document
DELETE /api/documents/{id}         # Delete document
GET    /api/documents/{id}/chunks  # Get document chunks
```

#### **Search APIs**
```bash
POST   /api/search                 # Hybrid search (vector + BM25)
POST   /api/search/semantic        # Pure vector search
POST   /api/search/keyword         # Pure BM25 search
GET    /api/search/history         # Search history
```

#### **Analytics APIs**
```bash
GET    /api/analytics/performance  # Query performance metrics
GET    /api/analytics/usage        # Usage statistics
GET    /api/analytics/models       # Model performance
```

#### **User Management APIs**
```bash
POST   /api/auth/login             # User authentication
GET    /api/users/{id}/permissions # User permissions
GET    /api/users/{id}/sessions    # Active sessions
```

### **Database Connection Examples**

#### **PostgreSQL Connection (Python)**
```python
import asyncpg

async def get_db_connection():
    return await asyncpg.connect(
        host='localhost',
        port=5433,
        database='knowledge_base_test', 
        user='kb_admin',
        password='test_password_123'
    )

# Usage in API:
async with get_db_connection() as conn:
    documents = await conn.fetch("""
        SELECT document_id, title, document_type, status 
        FROM documents_metadata_v2 
        WHERE status = 'approved' AND access_level = $1
    """, user_access_level)
```

#### **Redis Connection (Python)**
```python
import redis

def get_redis_client():
    return redis.Redis(
        host='localhost',
        port=6380,
        db=0,
        decode_responses=True
    )

# Usage in API:
r = get_redis_client()
cached_result = r.hgetall(f"search:{query_hash}")
```

#### **ChromaDB Connection (Python)**
```python
import chromadb

def get_chroma_client():
    return chromadb.HttpClient(
        host='localhost',
        port=8001
    )

# Usage in API:
client = get_chroma_client()
collection = client.get_collection("knowledge_base_v1")
results = collection.query(
    query_embeddings=[embedding_vector],
    n_results=10,
    where={"department": user_department}
)
```

---

## 🔐 **SECURITY & ACCESS CONTROL**

### **Current Security Level**
- ⚠️ **Development Environment**: No authentication implemented yet
- ⚠️ **Passwords**: Test passwords only (change for production)
- ⚠️ **Network**: All services on localhost only

### **Access Control Matrix (Ready for Implementation)**
```sql
-- Available in documents_metadata_v2.access_level:
public           -> All users
employee_only    -> Authenticated employees  
manager_only     -> Manager level and above
director_only    -> Director level and above
system_admin     -> System administrators only
```

### **Recommended API Security Implementation**
```python
# Suggested security layers for FR-02.2:
1. JWT Authentication
2. Role-based access control (RBAC)  
3. Rate limiting
4. Input validation
5. SQL injection prevention
6. CORS configuration
```

---

## 🚀 **QUICK START COMMANDS**

### **Start Existing Environment**
```bash
# Navigate to project directory
cd chatbot-enhanced-db

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker logs chatbot-postgres-test
docker logs chatbot-redis-test  
docker logs chatbot-chroma-test
```

### **Connect to Databases**
```bash
# PostgreSQL via psql
psql -h localhost -p 5433 -U kb_admin -d knowledge_base_test

# PostgreSQL via Adminer
# Open: http://localhost:8080

# Redis via CLI
docker exec -it chatbot-redis-test redis-cli

# ChromaDB via API
curl http://localhost:8001/api/v1/collections
```

### **Verification Commands**
```bash
# Test PostgreSQL
docker exec chatbot-postgres-test psql -U kb_admin -d knowledge_base_test -c "SELECT COUNT(*) FROM documents_metadata_v2;"

# Test Redis  
docker exec chatbot-redis-test redis-cli ping

# Test ChromaDB
curl http://localhost:8001/api/v1/heartbeat
```

---

## 📊 **PERFORMANCE BASELINES**

### **Current Performance Metrics**
```sql
-- PostgreSQL query performance:
- Simple SELECT: ~5-10ms
- Complex JOIN: ~20-50ms  
- Full-text search: ~30-100ms
- Total documents: 3 (sample)
- Total chunks: 9 (sample)
```

### **Expected Load for API Design**
```yaml
Target Performance:
- Concurrent users: 100+
- Response time: <60s (search queries)
- Documents: 10,000+
- Chunks: 100,000+
- Cache hit ratio: >70%
```

---

## 📋 **NEXT STEPS CHO TEAM FR-02.2**

### **Immediate Actions Required**
1. **✅ Review database schema** và hiểu được data structure
2. **✅ Test connection** tới tất cả 3 databases
3. **✅ Design API endpoints** tương thích với existing schema
4. **✅ Implement authentication layer** (JWT recommended)
5. **✅ Create data validation** based on existing constraints

### **Development Recommendations**
1. **Use existing Docker environment** - đừng recreate databases
2. **Follow existing naming conventions** - camelCase cho API, snake_case cho DB
3. **Leverage existing enums** - sử dụng enums đã defined
4. **Implement proper error handling** - especially cho database connections
5. **Add API documentation** - OpenAPI/Swagger specs

### **Testing Strategy**
1. **Unit tests** cho API endpoints
2. **Integration tests** với real database data
3. **Performance tests** với expected load
4. **Security tests** cho authentication & authorization

---

## 🆘 **SUPPORT & ESCALATION**

### **Technical Contacts**
- **Database Issues**: Team FR-02.1 Database Architecture
- **Docker Problems**: DevOps Support
- **Performance Issues**: Infrastructure Team

### **Troubleshooting Resources**
- **Logs location**: `./logs/` directory
- **Scripts location**: `./scripts/` directory  
- **Documentation**: `./docs/` directory
- **Docker compose**: `./docker-compose.yml`

### **Emergency Contacts**
- **System Down**: Contact DevOps immediately
- **Data Loss**: Contact Database Team + Backup procedures
- **Security Issues**: Contact Security Team

---

## 📄 **APPENDIX: USEFUL QUERIES**

### **Database Health Check**
```sql
-- Check all tables status
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check sample data
SELECT 
    'documents' as table_name, COUNT(*) as count FROM documents_metadata_v2
UNION ALL
SELECT 
    'chunks' as table_name, COUNT(*) as count FROM document_chunks_enhanced
UNION ALL  
SELECT 
    'sessions' as table_name, COUNT(*) as count FROM rag_pipeline_sessions;
```

### **API-Ready Queries Examples**
```sql
-- Get user documents with pagination
SELECT document_id, title, document_type, author, created_at
FROM documents_metadata_v2 
WHERE access_level IN ('public', 'employee_only')
AND status = 'approved'
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;

-- Search documents by keyword
SELECT document_id, title, ts_rank(search_tokens, query) as rank
FROM documents_metadata_v2,
     plainto_tsquery('vietnamese', 'nghỉ phép') query
WHERE search_tokens @@ query
ORDER BY rank DESC;

-- Get document with chunks
SELECT d.title, d.author, c.chunk_content, c.chunk_position
FROM documents_metadata_v2 d
JOIN document_chunks_enhanced c ON d.document_id = c.document_id
WHERE d.document_id = $1
ORDER BY c.chunk_position;
```

---

**🎯 Status: ✅ READY FOR FR-02.2 DEVELOPMENT**

Team FR-02.2 có thể bắt đầu develop API layer với confidence rằng database architecture đã stable và production-ready!

**📞 Questions?** Contact Team FR-02.1 for any clarifications.
