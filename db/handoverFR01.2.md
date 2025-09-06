# Document Ingestion System - Handover Documentation

## Project Overview

**Project Name**: Enhanced Vietnamese Document Ingestion System  
**Status**: Development Phase - Functional MVP with Known Issues  
**Last Updated**: September 2025  
**Primary Language**: Python 3.10+  
**Tech Stack**: PostgreSQL, ChromaDB, Redis, Streamlit, FastAPI

## What We Built

A document processing pipeline that ingests various file formats, performs Vietnamese language analysis, generates semantic embeddings, and stores everything in a multi-database architecture for advanced search capabilities.

### Core Capabilities
- Multi-format document ingestion (TXT, DOCX, PDF, XLSX)
- Vietnamese text processing and analysis
- Semantic chunking and vector embeddings
- Dual search system (full-text + semantic)
- Web interface for document management

## Database Architecture

### Primary Database: PostgreSQL
**Connection Details:**
- Host: localhost
- Port: 5433
- Database: knowledge_base_test
- User: kb_admin
- Password: test_password_123
- Access URL: http://localhost:8080 (Adminer)

### Database Tables

#### 1. documents_metadata_v2
**Purpose**: Main document storage with metadata
```sql
Columns:
- document_id (SERIAL PRIMARY KEY)
- title (VARCHAR(500))
- content (TEXT)
- document_type (VARCHAR(50))
- access_level (VARCHAR(50))
- department_owner (VARCHAR(100))
- author (VARCHAR(200))
- status (VARCHAR(50))
- language_detected (VARCHAR(10))
- vietnamese_segmented (BOOLEAN)
- file_size_bytes (BIGINT)
- embedding_model_primary (VARCHAR(100))
- chunk_count (INTEGER)
- flashrag_collection (VARCHAR(100))
- jsonl_export_ready (BOOLEAN)
- search_tokens (TSVECTOR)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### 2. document_chunks_enhanced
**Purpose**: Stores semantic chunks of documents
```sql
Columns:
- chunk_id (SERIAL PRIMARY KEY)
- document_id (INTEGER REFERENCES documents_metadata_v2)
- chunk_content (TEXT)
- chunk_position (INTEGER)
- chunk_size_tokens (INTEGER)
- chunk_method (VARCHAR(50))
- semantic_boundary (BOOLEAN)
- chunk_quality_score (DECIMAL(3,2))
- embedding_model (VARCHAR(100))
- created_at (TIMESTAMP)
```

#### 3. vietnamese_text_analysis
**Purpose**: Vietnamese language processing results
```sql
Columns:
- analysis_id (SERIAL PRIMARY KEY)
- document_id (INTEGER REFERENCES documents_metadata_v2)
- original_text (TEXT)
- processed_text (TEXT)
- word_segmentation (JSONB)
- pos_tagging (JSONB)
- compound_words (TEXT[])
- proper_nouns (TEXT[])
- readability_score (DECIMAL(3,2))
- formality_level (VARCHAR(20))
- created_at (TIMESTAMP)
```

### Vector Database: ChromaDB
**Connection Details:**
- Host: localhost
- Port: 8001
- Collection: knowledge_base
- Access URL: http://localhost:8001

**Purpose**: Stores vector embeddings for semantic search
- Document chunk embeddings (384-dimensional vectors)
- Metadata: document_id, chunk_position, document_title
- Embedding Model: paraphrase-multilingual-MiniLM-L12-v2

### Cache Database: Redis
**Connection Details:**
- Host: localhost
- Port: 6380
- Purpose: Caching layer (currently minimal usage)

## How to Connect to Our Databases

### For Applications
```python
# PostgreSQL Connection
import asyncpg

async def connect_postgres():
    return await asyncpg.connect(
        host='localhost',
        port=5433,
        database='knowledge_base_test',
        user='kb_admin',
        password='test_password_123'
    )

# ChromaDB Connection
import chromadb

def connect_chromadb():
    return chromadb.HttpClient(
        host='localhost',
        port=8001
    )

# Redis Connection
import redis

def connect_redis():
    return redis.Redis(
        host='localhost',
        port=6380,
        decode_responses=True
    )
```

### For Database Administration
- **Adminer Web Interface**: http://localhost:8080
  - Server: postgres-test
  - Username: kb_admin
  - Password: test_password_123
  - Database: knowledge_base_test

### For Direct Database Access
```bash
# PostgreSQL CLI
psql -h localhost -p 5433 -U kb_admin -d knowledge_base_test

# Or via Docker
docker exec -it postgres-test psql -U kb_admin -d knowledge_base_test
```

## Current Data Schema Examples

### Sample Document Record
```json
{
  "document_id": 1,
  "title": "Company Leave Policy",
  "document_type": "policy",
  "access_level": "employee_only",
  "department_owner": "HR",
  "author": "HR Manager",
  "status": "approved",
  "language_detected": "vi",
  "chunk_count": 5,
  "created_at": "2025-09-04T10:30:00"
}
```

### Sample Chunk Record
```json
{
  "chunk_id": 1,
  "document_id": 1,
  "chunk_content": "Nhân viên cần nộp đơn xin nghỉ phép...",
  "chunk_position": 0,
  "chunk_size_tokens": 45,
  "chunk_method": "semantic",
  "chunk_quality_score": 0.85
}
```

### Sample Vietnamese Analysis
```json
{
  "analysis_id": 1,
  "document_id": 1,
  "word_segmentation": {
    "words": ["Nhân_viên", "cần", "nộp", "đơn"],
    "count": 4
  },
  "compound_words": ["Nhân_viên", "xin_nghỉ", "phép_năm"],
  "proper_nouns": ["HR", "Manager"],
  "readability_score": 0.75
}
```

## System Access Points

### Web Interface
- **Document Upload**: http://localhost:8501
- **Search Interface**: http://localhost:8501
- **Analytics Dashboard**: http://localhost:8501

### APIs (Future Development)
- REST API endpoints not yet implemented
- Planned FastAPI integration

## Known Issues and Limitations

### Critical Issues
1. **Database Connection Conflicts**: Search functionality may fail after document upload
2. **Transaction Locking**: Some operations may leave locks that affect subsequent queries
3. **Memory Management**: Large documents may cause performance issues

### Stability Issues
- System requires periodic Docker container restarts
- Event loop conflicts in Streamlit integration
- Limited error recovery mechanisms

### Performance Limitations
- Single document processing only
- No batch processing capabilities
- Embedding generation can be slow for large documents

## Dependencies and Requirements

### Python Dependencies
```
asyncpg==0.29.0
streamlit==1.28.2
sentence-transformers==2.2.2
chromadb==1.0.0
underthesea==6.7.0
pyvi==0.1.1
python-docx==1.1.0
PyPDF2==3.0.1
pandas==2.0.3
```

### Infrastructure Requirements
- Docker and Docker Compose
- PostgreSQL 13+
- Python 3.10+
- CUDA-capable GPU (optional, for faster embeddings)

## Recommended Next Steps

### For Production Readiness
1. Fix database connection management issues
2. Implement comprehensive error handling
3. Add proper logging and monitoring
4. Create unit and integration test suites
5. Implement security measures (authentication, authorization)

### For Feature Enhancement
1. Batch document processing
2. Advanced search filters and sorting
3. Document versioning system
4. User management and permissions
5. API development for external integrations

## Contact and Support

**Primary Codebase Location**: `tools/document_ingestion/`
**Key Files**:
- `document_processor.py`: Core processing logic
- `streamlit_app.py`: Web interface
- `checkENV_DB.py`: Environment validation
- `tool_requirements.txt`: Dependencies

**Environment Setup**: Requires Docker containers for PostgreSQL, ChromaDB, and Redis to be running before system startup.

This system provides a solid foundation for document management with advanced Vietnamese language processing capabilities, but requires additional stability work before production deployment.
