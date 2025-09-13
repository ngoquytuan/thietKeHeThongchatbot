# FR-03.3 DATA INGESTION PIPELINE - FILE PROCESSING WORKFLOW
## QUY TRÌNH XỬ LÝ FILES SAU KHI UNZIP

---

**Target:** FR-03.3 Development Team  
**Integration:** FR-02.1 v2.0 Database Schema  
**Environment:** Hoàn toàn Local Processing  
**Date:** 12/09/2025  

---

## 📋 **QUY TRÌNH TỔNG QUAN**

```mermaid
graph TD
    A[FR03.1 Export ZIP] --> B[Extract & Validate]
    B --> C{Validation OK?}
    C -->|No| D[Move to Failed]
    C -->|Yes| E[Stage 1: Direct Import]
    E --> F[Stage 2: Enhanced Processing]
    F --> G[Stage 3: Vector DB Import]
    G --> H[Stage 4: Search Index]
    H --> I[Stage 5: Archive]
    
    D --> J[Log Error & Alert]
    I --> K[Update Job Status]
    
    style A fill:#e3f2fd
    style E fill:#e8f5e8
    style F fill:#fff3e0
    style G fill:#f3e5f5
    style I fill:#e0f2f1
    style D fill:#ffebee
```

## 🗂️ **CẤU TRÚC THƒ MỤC LÀM VIỆC**

```bash
/opt/chatbot-data/
├── incoming/                    # ZIP files từ FR03.1
├── processing/                  # Đang xử lý
│   └── {job_id}/               # Temporary workspace per job
│       ├── extracted/          # Unzipped content
│       ├── staging/            # Processed data ready for import
│       └── logs/               # Processing logs
├── completed/                  # Processed successfully
├── failed/                     # Processing failed
└── archive/                    # Long-term storage
```

## 🔧 **STAGE 1: EXTRACTION & VALIDATION**

### **1.1 File Extraction**
```python
import zipfile
import json
import os
from pathlib import Path
from datetime import datetime
import logging

def extract_and_validate_package(zip_path: str, job_id: str) -> dict:
    """Extract FR03.1 export package and validate structure"""
    
    base_dir = f"/opt/chatbot-data/processing/{job_id}"
    extracted_dir = f"{base_dir}/extracted"
    
    try:
        # Extract ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)
        
        # Validate package structure
        validation_result = validate_package_structure(extracted_dir)
        
        if validation_result['valid']:
            logging.info(f"Package {job_id} extracted and validated successfully")
            return {
                'status': 'success',
                'extracted_path': extracted_dir,
                'validation': validation_result
            }
        else:
            raise ValueError(f"Package validation failed: {validation_result['errors']}")
            
    except Exception as e:
        logging.error(f"Extraction failed for {job_id}: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e),
            'extracted_path': None
        }

def validate_package_structure(extracted_dir: str) -> dict:
    """Validate FR03.1 export package structure"""
    
    required_files = [
        "manifest.json",
        "FOR_DATABASE/document_metadata_v2.json", 
        "FOR_DATABASE/chunks_enhanced_v2.jsonl",
        "FOR_DATABASE/vietnamese_analysis_v2.json",
        "FOR_VECTOR_DB/embeddings_preparation.json"
    ]
    
    validation_errors = []
    
    for file_path in required_files:
        full_path = os.path.join(extracted_dir, file_path)
        if not os.path.exists(full_path):
            validation_errors.append(f"Missing required file: {file_path}")
        else:
            # Validate JSON format
            try:
                if file_path.endswith('.json'):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                elif file_path.endswith('.jsonl'):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            json.loads(line.strip())
            except json.JSONDecodeError as e:
                validation_errors.append(f"Invalid JSON in {file_path}: {str(e)}")
    
    return {
        'valid': len(validation_errors) == 0,
        'errors': validation_errors,
        'files_found': len([f for f in required_files if os.path.exists(os.path.join(extracted_dir, f))])
    }
```

## 🎯 **STAGE 2: DIRECT IMPORTS**

### **2.1 Document Metadata Import**
```python
import asyncpg
import uuid
from datetime import datetime

async def import_document_metadata(extracted_dir: str, job_id: str, conn: asyncpg.Connection):
    """Direct import document metadata to PostgreSQL"""
    
    metadata_file = f"{extracted_dir}/FOR_DATABASE/document_metadata_v2.json"
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        document_data = json.load(f)
    
    # Prepare for database insertion
    insert_query = """
        INSERT INTO documents_metadata_v2 (
            document_id, title, content, document_type, access_level,
            department_owner, author, status, language_detected,
            vietnamese_segmented, diacritics_normalized, tone_marks_preserved,
            search_text_normalized, indexable_content, extracted_emails,
            extracted_phones, extracted_dates, embedding_model_primary,
            chunk_count, file_size_bytes, search_tokens, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, 
            $15, $16, $17, $18, $19, $20, to_tsvector('simple', $13), $21, $22
        )
        ON CONFLICT (document_id) DO UPDATE SET
            updated_at = EXCLUDED.updated_at,
            chunk_count = EXCLUDED.chunk_count
        RETURNING document_id
    """
    
    try:
        # Insert document metadata
        document_id = await conn.fetchval(
            insert_query,
            uuid.UUID(document_data['document_id']),
            document_data['title'],
            document_data.get('content', ''),
            document_data['document_type'], 
            document_data['access_level'],
            document_data['department_owner'],
            document_data['author'],
            document_data.get('status', 'approved'),
            document_data.get('language_detected', 'vi'),
            document_data.get('vietnamese_segmented', True),
            document_data.get('diacritics_normalized', True),
            document_data.get('tone_marks_preserved', True),
            document_data.get('search_text_normalized', ''),
            document_data.get('indexable_content', ''),
            document_data.get('extracted_emails', []),
            document_data.get('extracted_phones', []),
            document_data.get('extracted_dates', []),
            document_data.get('embedding_model_primary', 'Qwen/Qwen3-Embedding-0.6B'),
            document_data.get('chunk_count', 0),
            document_data.get('file_size_bytes', 0),
            datetime.now(),
            datetime.now()
        )
        
        logging.info(f"Document metadata imported: {document_id}")
        return document_id
        
    except Exception as e:
        logging.error(f"Failed to import document metadata: {str(e)}")
        raise

### **2.2 Job Metadata Import**
async def import_job_metadata(extracted_dir: str, job_id: str, conn: asyncpg.Connection):
    """Import ingestion job metadata"""
    
    manifest_file = f"{extracted_dir}/manifest.json"
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    job_insert_query = """
        INSERT INTO data_ingestion_jobs (
            job_id, job_name, job_type, source_path, target_collection,
            chunking_method, chunk_size_tokens, overlap_tokens, embedding_model,
            status, progress_percentage, documents_processed, chunks_created,
            started_at, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16
        )
        ON CONFLICT (job_id) DO UPDATE SET
            updated_at = EXCLUDED.updated_at,
            progress_percentage = EXCLUDED.progress_percentage
    """
    
    await conn.execute(
        job_insert_query,
        uuid.UUID(job_id),
        manifest.get('package_name', f'Import_{datetime.now().strftime("%Y%m%d_%H%M%S")}'),
        'document_processing',
        extracted_dir,
        'knowledge_base_v2',
        'semantic_boundary',
        512,
        50,
        'Qwen/Qwen3-Embedding-0.6B',
        'processing',
        0.0,
        1,
        manifest.get('chunk_count', 0),
        datetime.now(),
        datetime.now(),
        datetime.now()
    )
```

## ⚙️ **STAGE 3: ENHANCED PROCESSING**

### **3.1 Chunks Processing và Import**
```python
async def process_and_import_chunks(extracted_dir: str, document_id: uuid.UUID, 
                                  job_id: str, conn: asyncpg.Connection):
    """Process enhanced chunks and import to database"""
    
    chunks_file = f"{extracted_dir}/FOR_DATABASE/chunks_enhanced_v2.jsonl"
    staging_dir = f"/opt/chatbot-data/processing/{job_id}/staging"
    os.makedirs(staging_dir, exist_ok=True)
    
    processed_chunks = []
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            chunk_data = json.loads(line.strip())
            
            # Enhanced processing
            processed_chunk = await enhance_chunk_data(chunk_data, document_id)
            processed_chunks.append(processed_chunk)
    
    # Batch insert chunks
    chunk_insert_query = """
        INSERT INTO document_chunks_enhanced (
            chunk_id, document_id, chunk_content, chunk_position, chunk_size_tokens,
            semantic_boundary, overlap_with_prev, overlap_with_next,
            overlap_source_prev, overlap_source_next, is_final_part,
            heading_context, chunk_method, chunk_quality_score,
            embedding_model, embedding_dimensions, bm25_tokens,
            created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, 
            to_tsvector('simple', $3), $17, $18
        )
    """
    
    for chunk in processed_chunks:
        try:
            await conn.execute(
                chunk_insert_query,
                uuid.UUID(chunk['chunk_id']),
                document_id,
                chunk['chunk_content'],
                chunk['chunk_position'],
                chunk['chunk_size_tokens'],
                chunk.get('semantic_boundary', False),
                chunk.get('overlap_with_prev', 0),
                chunk.get('overlap_with_next', 0),
                chunk.get('overlap_source_prev'),
                chunk.get('overlap_source_next'),
                chunk.get('is_final_part', False),
                chunk.get('heading_context', ''),
                chunk.get('chunk_method', 'semantic_boundary'),
                chunk.get('chunk_quality_score', 0.8),
                chunk.get('embedding_model', 'Qwen/Qwen3-Embedding-0.6B'),
                chunk.get('embedding_dimensions', 1024),
                datetime.now(),
                datetime.now()
            )
        except Exception as e:
            logging.error(f"Failed to insert chunk {chunk['chunk_id']}: {str(e)}")
            raise
    
    # Save processed chunks for vector DB
    processed_chunks_file = f"{staging_dir}/processed_chunks.json"
    with open(processed_chunks_file, 'w', encoding='utf-8') as f:
        json.dump(processed_chunks, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Processed and imported {len(processed_chunks)} chunks")
    return processed_chunks_file

async def enhance_chunk_data(chunk_data: dict, document_id: uuid.UUID) -> dict:
    """Enhance chunk data with additional processing"""
    
    enhanced_chunk = chunk_data.copy()
    
    # Generate missing fields
    if 'chunk_id' not in enhanced_chunk:
        enhanced_chunk['chunk_id'] = str(uuid.uuid4())
    
    enhanced_chunk['document_id'] = str(document_id)
    
    # Process Vietnamese content if needed
    content = enhanced_chunk['chunk_content']
    
    # Add BM25 token preview for logging
    tokens = content.lower().split()[:10]  # First 10 tokens preview
    enhanced_chunk['bm25_tokens_preview'] = ' '.join(tokens)
    
    # Ensure quality score is within range
    quality_score = enhanced_chunk.get('chunk_quality_score', 0.8)
    enhanced_chunk['chunk_quality_score'] = max(0.0, min(1.0, quality_score))
    
    return enhanced_chunk
```

### **3.2 Vietnamese Analysis Processing**
```python
async def process_vietnamese_analysis(extracted_dir: str, document_id: uuid.UUID, 
                                    conn: asyncpg.Connection):
    """Process and import Vietnamese text analysis"""
    
    analysis_file = f"{extracted_dir}/FOR_DATABASE/vietnamese_analysis_v2.json"
    
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # Process analysis data for database
    processed_analysis = {
        'analysis_id': str(uuid.uuid4()),
        'document_id': str(document_id),
        'original_text': analysis_data.get('original_text', ''),
        'processed_text': analysis_data.get('processed_text', ''),
        'word_segmentation': analysis_data.get('word_segmentation', {}),
        'pos_tagging': analysis_data.get('pos_tagging', {}),
        'compound_words': analysis_data.get('compound_words', []),
        'technical_terms': analysis_data.get('technical_terms', []),
        'proper_nouns': analysis_data.get('proper_nouns', []),
        'readability_score': analysis_data.get('readability_score', 0.5),
        'formality_level': analysis_data.get('formality_level', 'formal'),
        'language_quality_score': analysis_data.get('language_quality_score', 7.5),
        'diacritics_density': analysis_data.get('diacritics_density', 0.5),
        'token_diversity': analysis_data.get('token_diversity', 0.6)
    }
    
    analysis_insert_query = """
        INSERT INTO vietnamese_text_analysis (
            analysis_id, document_id, original_text, processed_text,
            word_segmentation, pos_tagging, compound_words, technical_terms,
            proper_nouns, readability_score, formality_level,
            language_quality_score, diacritics_density, token_diversity,
            created_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
        )
    """
    
    await conn.execute(
        analysis_insert_query,
        uuid.UUID(processed_analysis['analysis_id']),
        uuid.UUID(processed_analysis['document_id']),
        processed_analysis['original_text'],
        processed_analysis['processed_text'],
        json.dumps(processed_analysis['word_segmentation']),
        json.dumps(processed_analysis['pos_tagging']),
        processed_analysis['compound_words'],
        processed_analysis['technical_terms'],
        processed_analysis['proper_nouns'],
        processed_analysis['readability_score'],
        processed_analysis['formality_level'],
        processed_analysis['language_quality_score'],
        processed_analysis['diacritics_density'],
        processed_analysis['token_diversity'],
        datetime.now()
    )
```

## 🔍 **STAGE 4: VECTOR DATABASE IMPORT**

### **4.1 ChromaDB Processing**
```python
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

class VectorDBProcessor:
    def __init__(self):
        self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        self.embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')  # Local model
        
    async def process_for_vector_db(self, extracted_dir: str, processed_chunks_file: str, 
                                  job_id: str) -> bool:
        """Process and import data to ChromaDB"""
        
        try:
            # Load processed chunks
            with open(processed_chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            # Get or create collection
            collection_name = "knowledge_base_v2"
            try:
                collection = self.chroma_client.get_collection(collection_name)
            except:
                collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={
                        "description": "Vietnamese knowledge base v2.0",
                        "embedding_model": "all-mpnet-base-v2",
                        "dimension": 768
                    }
                )
            
            # Process chunks in batches
            batch_size = 10
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                await self._process_batch(collection, batch, job_id)
            
            logging.info(f"Successfully imported {len(chunks)} chunks to ChromaDB")
            return True
            
        except Exception as e:
            logging.error(f"ChromaDB import failed: {str(e)}")
            return False
    
    async def _process_batch(self, collection, batch: list, job_id: str):
        """Process a batch of chunks for ChromaDB"""
        
        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for chunk in batch:
            # Generate embedding
            content = chunk['chunk_content']
            embedding = self.embedding_model.encode(content).tolist()
            
            ids.append(chunk['chunk_id'])
            embeddings.append(embedding)
            documents.append(content)
            metadatas.append({
                'document_id': chunk['document_id'],
                'chunk_position': chunk['chunk_position'],
                'access_level': chunk.get('access_level', 'employee_only'),
                'department': chunk.get('department', ''),
                'language': 'vi',
                'quality_score': chunk.get('chunk_quality_score', 0.8),
                'job_id': job_id,
                'created_at': datetime.now().isoformat()
            })
        
        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
```

## 🔄 **STAGE 5: ORCHESTRATION & ERROR HANDLING**

### **5.1 Main Processing Pipeline**
```python
class DataIngestionOrchestrator:
    def __init__(self):
        self.db_pool = None
        self.vector_processor = VectorDBProcessor()
        
    async def process_package(self, zip_path: str) -> dict:
        """Main processing pipeline for FR03.1 export package"""
        
        job_id = str(uuid.uuid4())
        
        try:
            # Stage 1: Extract and validate
            extraction_result = extract_and_validate_package(zip_path, job_id)
            if extraction_result['status'] != 'success':
                return self._handle_failure(job_id, 'extraction_failed', extraction_result['error'])
            
            extracted_dir = extraction_result['extracted_path']
            
            # Database connection
            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    # Stage 2: Direct imports
                    job_metadata_result = await import_job_metadata(extracted_dir, job_id, conn)
                    document_id = await import_document_metadata(extracted_dir, job_id, conn)
                    
                    # Stage 3: Enhanced processing
                    processed_chunks_file = await process_and_import_chunks(
                        extracted_dir, document_id, job_id, conn
                    )
                    await process_vietnamese_analysis(extracted_dir, document_id, conn)
                    
                    # Update job progress
                    await self._update_job_progress(job_id, 50.0, conn)
            
            # Stage 4: Vector database (outside transaction)
            vector_result = await self.vector_processor.process_for_vector_db(
                extracted_dir, processed_chunks_file, job_id
            )
            
            if not vector_result:
                return self._handle_failure(job_id, 'vector_db_failed', 'ChromaDB import failed')
            
            # Stage 5: Finalize
            await self._finalize_processing(job_id, extracted_dir)
            
            return {
                'status': 'success',
                'job_id': job_id,
                'document_id': str(document_id),
                'message': 'Package processed successfully'
            }
            
        except Exception as e:
            logging.error(f"Processing failed for job {job_id}: {str(e)}")
            await self._rollback_processing(job_id, extracted_dir if 'extracted_dir' in locals() else None)
            return self._handle_failure(job_id, 'processing_failed', str(e))
    
    async def _update_job_progress(self, job_id: str, progress: float, conn: asyncpg.Connection):
        """Update job progress in database"""
        await conn.execute(
            "UPDATE data_ingestion_jobs SET progress_percentage = $1, updated_at = $2 WHERE job_id = $3",
            progress, datetime.now(), uuid.UUID(job_id)
        )
    
    async def _finalize_processing(self, job_id: str, extracted_dir: str):
        """Finalize successful processing"""
        
        # Update job status to completed
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE data_ingestion_jobs 
                SET status = 'completed', progress_percentage = 100.0, 
                    completed_at = $1, updated_at = $1
                WHERE job_id = $2
            """, datetime.now(), uuid.UUID(job_id))
        
        # Move to completed directory
        completed_dir = f"/opt/chatbot-data/completed/{job_id}"
        os.rename(f"/opt/chatbot-data/processing/{job_id}", completed_dir)
        
        logging.info(f"Job {job_id} completed successfully")
    
    async def _rollback_processing(self, job_id: str, extracted_dir: str = None):
        """Rollback failed processing"""
        
        try:
            # Database rollback
            async with self.db_pool.acquire() as conn:
                # Delete related records
                await conn.execute("DELETE FROM vietnamese_text_analysis WHERE analysis_id IN (SELECT analysis_id FROM vietnamese_text_analysis WHERE document_id IN (SELECT document_id FROM documents_metadata_v2 WHERE document_id IN (SELECT DISTINCT document_id FROM document_chunks_enhanced WHERE chunk_id IN (SELECT chunk_id FROM chunk_processing_logs WHERE job_id = $1))))", uuid.UUID(job_id))
                await conn.execute("DELETE FROM document_chunks_enhanced WHERE document_id IN (SELECT document_id FROM documents_metadata_v2 WHERE document_id IN (SELECT DISTINCT document_id FROM document_chunks_enhanced WHERE chunk_id IN (SELECT chunk_id FROM chunk_processing_logs WHERE job_id = $1)))", uuid.UUID(job_id))
                await conn.execute("DELETE FROM documents_metadata_v2 WHERE document_id IN (SELECT DISTINCT document_id FROM document_chunks_enhanced WHERE chunk_id IN (SELECT chunk_id FROM chunk_processing_logs WHERE job_id = $1))", uuid.UUID(job_id))
                await conn.execute("UPDATE data_ingestion_jobs SET status = 'failed', updated_at = $1 WHERE job_id = $2", datetime.now(), uuid.UUID(job_id))
            
            # ChromaDB rollback
            try:
                collection = self.vector_processor.chroma_client.get_collection("knowledge_base_v2")
                collection.delete(where={"job_id": job_id})
            except Exception as e:
                logging.warning(f"ChromaDB rollback warning: {str(e)}")
            
            # Move to failed directory
            if extracted_dir:
                failed_dir = f"/opt/chatbot-data/failed/{job_id}"
                processing_dir = f"/opt/chatbot-data/processing/{job_id}"
                if os.path.exists(processing_dir):
                    os.rename(processing_dir, failed_dir)
                    
        except Exception as e:
            logging.error(f"Rollback failed for job {job_id}: {str(e)}")
    
    def _handle_failure(self, job_id: str, error_type: str, error_message: str) -> dict:
        """Handle processing failure"""
        return {
            'status': 'failed',
            'job_id': job_id,
            'error_type': error_type,
            'error_message': error_message
        }
```

## 📝 **CONFIGURATION FILE**

### **config/fr03_3_config.py**
```python
import os
from pathlib import Path

class FR033Config:
    # Directory structure
    BASE_DATA_DIR = "/opt/chatbot-data"
    INCOMING_DIR = f"{BASE_DATA_DIR}/incoming"
    PROCESSING_DIR = f"{BASE_DATA_DIR}/processing"
    COMPLETED_DIR = f"{BASE_DATA_DIR}/completed"
    FAILED_DIR = f"{BASE_DATA_DIR}/failed"
    ARCHIVE_DIR = f"{BASE_DATA_DIR}/archive"
    
    # Database settings
    POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://kb_admin:password@localhost:5432/knowledge_base_v2")
    POSTGRES_POOL_SIZE = 10
    POSTGRES_MAX_OVERFLOW = 20
    
    # ChromaDB settings
    CHROMA_HOST = "localhost"
    CHROMA_PORT = 8000
    CHROMA_COLLECTION = "knowledge_base_v2"
    
    # Processing settings
    BATCH_SIZE = 10
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    PROCESSING_TIMEOUT = 3600  # 1 hour
    
    # Local embedding model
    EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # For local processing
    
    # Quality thresholds
    MIN_QUALITY_SCORE = 0.6
    MIN_CHUNK_SIZE_TOKENS = 10
    MAX_CHUNK_SIZE_TOKENS = 2000
    
    # Storage settings
    CLEANUP_COMPLETED_AFTER_DAYS = 30
    CLEANUP_FAILED_AFTER_DAYS = 7
    MAX_DISK_USAGE_PERCENT = 85
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = f"{BASE_DATA_DIR}/logs/fr03_3.log"
    
    @classmethod
    def ensure_directories(cls):
        """Create required directories if they don't exist"""
        for dir_path in [cls.INCOMING_DIR, cls.PROCESSING_DIR, cls.COMPLETED_DIR, 
                        cls.FAILED_DIR, cls.ARCHIVE_DIR, f"{cls.BASE_DATA_DIR}/logs"]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
```

## 🚀 **DEPLOYMENT SCRIPT**

### **scripts/start_fr03_3.py**
```python
#!/usr/bin/env python3

import asyncio
import asyncpg
import logging
from pathlib import Path
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.fr03_3_config import FR033Config
from services.data_ingestion_orchestrator import DataIngestionOrchestrator

async def main():
    """Main entry point for FR03.3 data ingestion service"""
    
    # Setup logging
    FR033Config.ensure_directories()
    logging.basicConfig(
        level=getattr(logging, FR033Config.LOG_LEVEL),
        format=FR033Config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(FR033Config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting FR03.3 Data Ingestion Pipeline")
    
    try:
        # Initialize database connection pool
        db_pool = await asyncpg.create_pool(
            FR033Config.POSTGRES_URL,
            min_size=5,
            max_size=FR033Config.POSTGRES_POOL_SIZE
        )
        
        # Initialize orchestrator
        orchestrator = DataIngestionOrchestrator()
        orchestrator.db_pool = db_pool
        
        # Process any existing files in incoming directory
        incoming_path = Path(FR033Config.INCOMING_DIR)
        for zip_file in incoming_path.glob("*.zip"):
            logger.info(f"Processing existing file: {zip_file}")
            result = await orchestrator.process_package(str(zip_file))
            logger.info(f"Processing result: {result}")
            
            # Move processed file
            if result['status'] == 'success':
                zip_file.unlink()  # Delete original ZIP
            else:
                # Move failed file to a failed directory
                failed_file = Path(FR033Config.FAILED_DIR) / zip_file.name
                zip_file.rename(failed_file)
        
        logger.info("FR03.3 initialization completed")
        
        # Keep service running for future file processing
        # In production, this would be a file watcher or queue consumer
        while True:
            await asyncio.sleep(60)  # Check every minute
            
    except Exception as e:
        logger.error(f"FR03.3 startup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

Quy trình này cung cấp framework hoàn chỉnh cho FR03.3 để xử lý files từ FR03.1 export một cách local, với error handling và rollback mechanisms đầy đủ.
