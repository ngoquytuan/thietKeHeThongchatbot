Tuyệt vời! Tôi sẽ hướng dẫn bạn từng bước để test kiến trúc database enhanced trên Windows với Docker.

## 🚀 **HƯỚNG DẪN TRIỂN KHAI TỪNG BƯỚC TRÊN WINDOWS**

### **Bước 1: Tạo cấu trúc thư mục**

Mở **Command Prompt** hoặc **PowerShell** với quyền Administrator và chạy:

```cmd
mkdir chatbot-enhanced-db
cd chatbot-enhanced-db

mkdir scripts
mkdir scripts\migrations
mkdir logs
mkdir test_results
mkdir data
mkdir data\sample_documents
mkdir config
mkdir config\grafana
mkdir config\grafana\dashboards
mkdir config\grafana\datasources
mkdir docker
mkdir tests

echo. > docker-compose.yml
```

### **Bước 2: Tạo Docker Compose file**

Tạo file `docker-compose.yml` trong thư mục gốc:

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL with enhanced schema
  postgres-test:
    image: postgres:15-alpine
    container_name: chatbot-postgres-test
    environment:
      POSTGRES_DB: knowledge_base_test
      POSTGRES_USER: kb_admin
      POSTGRES_PASSWORD: test_password_123
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres_test_data:/var/lib/postgresql/data
      - ./scripts/migrations:/docker-entrypoint-initdb.d:ro
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kb_admin -d knowledge_base_test"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - chatbot-test-network

  # Redis for caching
  redis-test:
    image: redis:7-alpine
    container_name: chatbot-redis-test
    ports:
      - "6380:6379"
    volumes:
      - redis_test_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - chatbot-test-network

  # ChromaDB for vector storage
  chromadb-test:
    image: chromadb/chroma:latest
    container_name: chatbot-chroma-test
    environment:
      CHROMA_SERVER_HOST: 0.0.0.0
      CHROMA_SERVER_HTTP_PORT: 8000
    volumes:
      - chromadb_test_data:/chroma/chroma
    ports:
      - "8001:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - chatbot-test-network

  # Database setup service
  db-setup:
    image: python:3.9-slim
    container_name: chatbot-db-setup
    environment:
      DB_HOST: postgres-test
      DB_PORT: 5432
      DB_NAME: knowledge_base_test
      DB_USER: kb_admin
      DB_PASSWORD: test_password_123
    volumes:
      - ./scripts:/app/scripts:ro
      - ./logs:/app/logs
    working_dir: /app
    depends_on:
      postgres-test:
        condition: service_healthy
      redis-test:
        condition: service_healthy
    command: >
      sh -c "
      pip install asyncpg psycopg2-binary &&
      python scripts/setup_database.py
      "
    networks:
      - chatbot-test-network

  # Monitoring dashboard
  adminer:
    image: adminer
    container_name: chatbot-adminer
    ports:
      - "8080:8080"
    environment:
      ADMINER_DEFAULT_SERVER: postgres-test
    depends_on:
      postgres-test:
        condition: service_healthy
    networks:
      - chatbot-test-network

volumes:
  postgres_test_data:
  redis_test_data:
  chromadb_test_data:

networks:
  chatbot-test-network:
    driver: bridge
```

### **Bước 3: Tạo Migration Scripts**

Tạo file `scripts/migrations/01_init_database.sql`:

```sql
-- scripts/migrations/01_init_database.sql

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create enhanced enum types
DO $$ BEGIN
    CREATE TYPE access_level_enum AS ENUM (
        'public', 'employee_only', 'manager_only', 'director_only', 'system_admin'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE document_type_enum AS ENUM (
        'policy', 'procedure', 'technical_guide', 'report', 
        'manual', 'specification', 'template', 'form', 
        'presentation', 'training_material', 'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE document_status_enum AS ENUM (
        'draft', 'review', 'approved', 'published', 'archived', 'deprecated'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Enhanced documents metadata table
CREATE TABLE IF NOT EXISTS documents_metadata_v2 (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Basic information
    title VARCHAR(500) NOT NULL,
    content TEXT,
    document_type document_type_enum NOT NULL,
    access_level access_level_enum NOT NULL DEFAULT 'employee_only',
    department_owner VARCHAR(100) NOT NULL,
    author VARCHAR(255) NOT NULL,
    status document_status_enum DEFAULT 'draft',
    
    -- Vietnamese language support
    language_detected VARCHAR(10) DEFAULT 'vi',
    vietnamese_segmented BOOLEAN DEFAULT false,
    diacritics_normalized BOOLEAN DEFAULT false,
    tone_marks_preserved BOOLEAN DEFAULT true,
    
    -- FlashRAG support
    flashrag_collection VARCHAR(100) DEFAULT 'default_collection',
    jsonl_export_ready BOOLEAN DEFAULT false,
    
    -- Search support
    search_tokens TSVECTOR,
    keyword_density JSONB,
    heading_structure JSONB,
    
    -- Metadata
    embedding_model_primary VARCHAR(100),
    chunk_count INTEGER DEFAULT 0,
    file_size_bytes BIGINT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enhanced document chunks table
CREATE TABLE IF NOT EXISTS document_chunks_enhanced (
    chunk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    
    -- Content data
    chunk_content TEXT NOT NULL,
    chunk_position INTEGER NOT NULL,
    chunk_size_tokens INTEGER,
    
    -- Semantic chunking metadata
    semantic_boundary BOOLEAN DEFAULT false,
    overlap_with_prev INTEGER DEFAULT 0,
    overlap_with_next INTEGER DEFAULT 0,
    heading_context TEXT,
    
    -- Quality and method
    chunk_method VARCHAR(20) DEFAULT 'semantic',
    chunk_quality_score DECIMAL(3,2) CHECK (chunk_quality_score BETWEEN 0.00 AND 1.00),
    
    -- Vector storage references
    embedding_model VARCHAR(100),
    embedding_dimensions INTEGER,
    
    -- BM25 support
    bm25_tokens TSVECTOR,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- BM25 support table
CREATE TABLE IF NOT EXISTS document_bm25_index (
    bm25_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES document_chunks_enhanced(chunk_id) ON DELETE CASCADE,
    
    term VARCHAR(255) NOT NULL,
    term_frequency INTEGER NOT NULL,
    document_frequency INTEGER NOT NULL,
    bm25_score DECIMAL(8,4),
    
    language VARCHAR(10) DEFAULT 'vi',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(chunk_id, term, language)
);

-- Pipeline tracking table
CREATE TABLE IF NOT EXISTS rag_pipeline_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Query information
    original_query TEXT NOT NULL,
    processed_query TEXT,
    query_language VARCHAR(10) DEFAULT 'vi',
    
    -- Pipeline metadata
    pipeline_type VARCHAR(50) NOT NULL DEFAULT 'standard',
    pipeline_method VARCHAR(50) NOT NULL DEFAULT 'hybrid',
    
    -- Performance metrics
    chunks_retrieved INTEGER,
    processing_time_ms INTEGER,
    response_quality_score DECIMAL(3,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vietnamese text analysis table
CREATE TABLE IF NOT EXISTS vietnamese_text_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES document_chunks_enhanced(chunk_id) ON DELETE CASCADE,
    
    original_text TEXT NOT NULL,
    processed_text TEXT,
    
    word_segmentation JSONB,
    pos_tagging JSONB,
    
    compound_words TEXT[],
    technical_terms TEXT[],
    proper_nouns TEXT[],
    
    readability_score DECIMAL(3,2),
    formality_level VARCHAR(20),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create performance indexes
CREATE INDEX IF NOT EXISTS idx_documents_v2_language ON documents_metadata_v2(language_detected);
CREATE INDEX IF NOT EXISTS idx_documents_v2_status ON documents_metadata_v2(status);
CREATE INDEX IF NOT EXISTS idx_documents_v2_collection ON documents_metadata_v2(flashrag_collection);
CREATE INDEX IF NOT EXISTS idx_documents_v2_search ON documents_metadata_v2 USING GIN(search_tokens);

CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_document ON document_chunks_enhanced(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_position ON document_chunks_enhanced(chunk_position);
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_semantic ON document_chunks_enhanced(semantic_boundary) WHERE semantic_boundary = true;

CREATE INDEX IF NOT EXISTS idx_bm25_term ON document_bm25_index(term);
CREATE INDEX IF NOT EXISTS idx_bm25_chunk ON document_bm25_index(chunk_id);
CREATE INDEX IF NOT EXISTS idx_bm25_score ON document_bm25_index(bm25_score DESC);

CREATE INDEX IF NOT EXISTS idx_pipeline_sessions_created ON rag_pipeline_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_sessions_type ON rag_pipeline_sessions(pipeline_type, pipeline_method);

-- Insert sample data
INSERT INTO documents_metadata_v2 (
    title, content, document_type, access_level, department_owner, author, status, jsonl_export_ready
) VALUES 
(
    'Quy trình xin nghỉ phép',
    'Quy trình xin nghỉ phép tại công ty bao gồm các bước sau: 1. Nhân viên điền đơn xin nghỉ phép 2. Gửi đơn cho quản lý trực tiếp 3. Quản lý phê duyệt trong vòng 2 ngày làm việc 4. HR cập nhật vào hệ thống 5. Thông báo kết quả cho nhân viên',
    'procedure',
    'employee_only',
    'HR',
    'HR Department',
    'approved',
    true
),
(
    'Chính sách làm việc từ xa',
    'Chính sách làm việc từ xa (Work From Home) được áp dụng như sau: - Nhân viên có thể làm việc từ xa tối đa 3 ngày/tuần - Cần đăng ký trước ít nhất 1 ngày - Đảm bảo môi trường làm việc ổn định - Tham gia đầy đủ các cuộc họp online - Báo cáo tiến độ công việc hàng ngày',
    'policy',
    'employee_only',
    'HR',
    'Management Team',
    'approved',
    true
),
(
    'Hướng dẫn sử dụng hệ thống ERP',
    'Hướng dẫn chi tiết sử dụng hệ thống ERP công ty: 1. Đăng nhập hệ thống - Sử dụng tài khoản company email - Mật khẩu được cấp ban đầu cần đổi ngay lần đầu đăng nhập 2. Module quản lý nhân sự - Cập nhật thông tin cá nhân - Đăng ký nghỉ phép - Xem bảng lương 3. Module quản lý dự án - Tạo task mới - Cập nhật tiến độ - Báo cáo hàng tuần',
    'technical_guide',
    'employee_only',
    'IT',
    'IT Support Team',
    'approved',
    true
)
ON CONFLICT DO NOTHING;

-- Update search tokens for sample documents
UPDATE documents_metadata_v2 
SET search_tokens = to_tsvector('simple', title || ' ' || COALESCE(content, ''))
WHERE search_tokens IS NULL;

-- Success message
DO $$ BEGIN
    RAISE NOTICE 'Enhanced Database Architecture initialized successfully!';
    RAISE NOTICE 'Sample Vietnamese documents loaded.';
    RAISE NOTICE 'Database is ready for testing.';
END $$;
```

### **Bước 4: Tạo Database Setup Script**

Tạo file `scripts/setup_database.py`:

```python
# scripts/setup_database.py
import asyncio
import asyncpg
import logging
import time
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def setup_enhanced_database():
    """Setup and verify enhanced database architecture"""
    
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'knowledge_base_test'),
        'user': os.getenv('DB_USER', 'kb_admin'),
        'password': os.getenv('DB_PASSWORD', 'test_password_123')
    }
    
    logger.info("🚀 Starting Enhanced Database Setup")
    
    # Wait for database to be ready
    max_retries = 30
    for attempt in range(max_retries):
        try:
            conn = await asyncpg.connect(**db_config)
            await conn.execute('SELECT 1')
            await conn.close()
            logger.info("✅ Database connection successful!")
            break
        except Exception as e:
            logger.info(f"⏳ Waiting for database... (attempt {attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                logger.error("❌ Database connection failed after maximum retries")
                return False
            await asyncio.sleep(2)
    
    # Connect to database
    try:
        conn = await asyncpg.connect(**db_config)
        logger.info("🔗 Connected to database")
        
        # Verify table creation
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        logger.info(f"📊 Database created with {len(tables)} tables:")
        for table in tables:
            logger.info(f"  ✅ {table['table_name']}")
        
        # Verify sample data
        doc_count = await conn.fetchval("SELECT COUNT(*) FROM documents_metadata_v2")
        logger.info(f"📄 Sample documents loaded: {doc_count}")
        
        if doc_count > 0:
            # Show sample documents
            docs = await conn.fetch("SELECT title, author, status FROM documents_metadata_v2 LIMIT 3")
            logger.info("📋 Sample documents:")
            for doc in docs:
                logger.info(f"  📄 '{doc['title']}' by {doc['author']} ({doc['status']})")
        
        # Test basic queries
        logger.info("🔍 Testing basic queries...")
        
        # Test Vietnamese search
        vn_docs = await conn.fetchval("""
            SELECT COUNT(*) FROM documents_metadata_v2 
            WHERE language_detected = 'vi'
        """)
        logger.info(f"  🇻🇳 Vietnamese documents: {vn_docs}")
        
        # Test full-text search capability
        search_ready = await conn.fetchval("""
            SELECT COUNT(*) FROM documents_metadata_v2 
            WHERE search_tokens IS NOT NULL
        """)
        logger.info(f"  🔍 Documents with search tokens: {search_ready}")
        
        # Test enum types
        enum_test = await conn.fetchval("""
            SELECT COUNT(DISTINCT document_type) FROM documents_metadata_v2
        """)
        logger.info(f"  📝 Document types in use: {enum_test}")
        
        # Create a sample pipeline session for testing
        session_id = await conn.fetchval("""
            INSERT INTO rag_pipeline_sessions (
                original_query, processed_query, pipeline_type, pipeline_method,
                chunks_retrieved, processing_time_ms, response_quality_score
            ) VALUES (
                'Quy trình xin nghỉ phép như thế nào?',
                'quy trình xin nghỉ phép',
                'standard',
                'hybrid',
                3,
                150,
                0.85
            ) RETURNING session_id
        """)
        
        logger.info(f"  ✅ Sample pipeline session created: {session_id}")
        
        # Generate database statistics
        db_size = await conn.fetchval("SELECT pg_size_pretty(pg_database_size(current_database()))")
        logger.info(f"💾 Database size: {db_size}")
        
        # Create comprehensive test report
        report = f"""
# Enhanced Database Architecture Test Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Database Information
- **Host**: {db_config['host']}:{db_config['port']}
- **Database**: {db_config['database']}
- **Size**: {db_size}

## Tables Created: {len(tables)}
{chr(10).join(f'- {table["table_name"]}' for table in tables)}

## Sample Data
- **Documents**: {doc_count}
- **Vietnamese Documents**: {vn_docs}
- **Search-Ready Documents**: {search_ready}
- **Document Types**: {enum_test}

## Features Tested
✅ Enhanced schema with Vietnamese support
✅ Multi-type enum support
✅ Full-text search capability
✅ Pipeline session tracking
✅ BM25 index structure
✅ FlashRAG compatibility structure

## Connection Information
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6380
- **ChromaDB**: localhost:8001
- **Adminer**: http://localhost:8080

## Next Steps
1. Access Adminer at http://localhost:8080 to browse database
2. Connect using: Server: postgres-test, Username: kb_admin, Password: test_password_123
3. Test queries using the sample Vietnamese documents
4. Explore enhanced schema features

## Test Status: ✅ SUCCESS
All components initialized and tested successfully!
        """
        
        # Write report to log file
        with open('/app/logs/setup_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("📄 Setup report saved to: /app/logs/setup_report.md")
        print(report)
        
        await conn.close()
        logger.info("🎉 Enhanced Database Architecture setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(setup_enhanced_database())
    sys.exit(0 if success else 1)
```

### **Bước 5: Chạy Docker Test**

Mở PowerShell trong thư mục `chatbot-enhanced-db` và chạy:

```powershell
# Khởi động các services
docker-compose up -d

# Kiểm tra trạng thái
docker-compose ps

# Xem logs của database setup
docker logs chatbot-db-setup

# Xem logs của PostgreSQL
docker logs chatbot-postgres-test
```

### **Bước 6: Kiểm tra kết quả**

1. **Mở Adminer (Database Browser)**:
   - Truy cập: http://localhost:8080
   - Server: `postgres-test`
   - Username: `kb_admin`
   - Password: `test_password_123`
   - Database: `knowledge_base_test`

2. **Kiểm tra ChromaDB**:
   ```powershell
   # Test ChromaDB API
   curl http://localhost:8001/api/v1/heartbeat
   ```

3. **Kiểm tra Redis**:
   ```powershell
   # Connect to Redis container
   docker exec -it chatbot-redis-test redis-cli ping
   ```

### **Bước 7: Test Database với PowerShell**

Tạo file `test_database.ps1`:

```powershell
# test_database.ps1

Write-Host "🔍 Testing Enhanced Database Architecture" -ForegroundColor Green

# Test PostgreSQL connection
Write-Host "`n📊 Testing PostgreSQL..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080" -Method Get
    Write-Host "✅ Adminer accessible at http://localhost:8080" -ForegroundColor Green
} catch {
    Write-Host "❌ Adminer not accessible" -ForegroundColor Red
}

# Test ChromaDB
Write-Host "`n🔢 Testing ChromaDB..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/heartbeat" -Method Get
    Write-Host "✅ ChromaDB accessible: $($response.nanosecond_heartbeat)" -ForegroundColor Green
} catch {
    Write-Host "❌ ChromaDB not accessible" -ForegroundColor Red
}

# Test Redis
Write-Host "`n🔴 Testing Redis..." -ForegroundColor Yellow
try {
    $redisTest = docker exec chatbot-redis-test redis-cli ping
    if ($redisTest -eq "PONG") {
        Write-Host "✅ Redis accessible: $redisTest" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Redis not accessible" -ForegroundColor Red
}

# Check logs
Write-Host "`n📋 Recent setup logs:" -ForegroundColor Yellow
docker logs --tail 10 chatbot-db-setup

Write-Host "`n🎉 Database test completed!" -ForegroundColor Green
Write-Host "Access Adminer: http://localhost:8080" -ForegroundColor Cyan
Write-Host "ChromaDB API: http://localhost:8001" -ForegroundColor Cyan

# Show connection info
Write-Host "`n📝 Connection Information:" -ForegroundColor Yellow
Write-Host "PostgreSQL: localhost:5433" -ForegroundColor White
Write-Host "Redis: localhost:6380" -ForegroundColor White
Write-Host "ChromaDB: localhost:8001" -ForegroundColor White
Write-Host "Adminer: http://localhost:8080" -ForegroundColor White
```

Chạy test:
```powershell
powershell -ExecutionPolicy Bypass -File test_database.ps1
```

### **Bước 8: Cleanup khi hoàn thành**

```powershell
# Dừng và xóa containers
docker-compose down

# Xóa volumes (nếu muốn xóa hết data)
docker-compose down -v

# Xóa images (nếu muốn cleanup hoàn toàn)
docker system prune -a
```

## 📊 **Kết quả mong đợi**

Sau khi chạy thành công, bạn sẽ có:

1. **✅ PostgreSQL** với enhanced schema running trên port 5433
2. **✅ Redis** cache running trên port 6380  
3. **✅ ChromaDB** vector database trên port 8001
4. **✅ Adminer** database browser tại http://localhost:8080
5. **✅ Sample Vietnamese documents** đã được load
6. **✅ Test report** trong `logs/setup_report.md`

**Tính năng đã test:**
- 🇻🇳 Vietnamese language support
- 🔍 Hybrid search structure (BM25 + Vector)
- 📊 Enhanced metadata schema
- ⚡ Performance indexes
- 📄 FlashRAG compatibility
- 🔄 Pipeline tracking

Bạn có gặp lỗi gì trong quá trình setup không? Tôi sẽ giúp troubleshoot!
