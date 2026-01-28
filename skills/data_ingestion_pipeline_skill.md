# Data Ingestion Pipeline Skill (FR03.3)

## Overview
This skill enables Claude to assist with developing a robust data ingestion pipeline for Vietnamese RAG systems. The pipeline handles file uploads, format parsing, validation, preprocessing, and storage orchestration with error handling and progress tracking.

## System Context

### Architecture Overview
```
┌─────────────────┐
│  File Upload    │
│  (Web/API)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validation     │
│  & Quarantine   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Format Parser  │
│  (PDF/DOCX/...)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Preprocessing  │
│  (Vietnamese)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Metadata       │
│  Extraction     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Storage Orchestration      │
│  ┌──────────┬─────────────┐ │
│  │PostgreSQL│  ChromaDB   │ │
│  │(Metadata)│  (Vectors)  │ │
│  └──────────┴─────────────┘ │
└─────────────────────────────┘
```

### Technology Stack
```python
# Core Components
- FastAPI: Upload endpoints & async processing
- Celery/RQ: Async task queue
- Redis: Task status & caching
- PyPDF2/pymupdf: PDF parsing
- python-docx: DOCX parsing
- openpyxl: Excel parsing
- BeautifulSoup4: HTML parsing
- underthesea: Vietnamese text processing
- PostgreSQL: File metadata & status tracking
- MinIO/S3: File storage (optional)
```

## Core Components

### 1. File Upload Handler

#### Multi-part Upload Support
```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import os
from typing import List
import hashlib

app = FastAPI()

UPLOAD_DIR = "/mnt/user-data/uploads"
CHUNK_SIZE = 1024 * 1024 * 5  # 5MB chunks

class UploadManager:
    def __init__(self):
        self.active_uploads = {}  # track multipart uploads
    
    async def upload_file(
        self, 
        file: UploadFile,
        user_id: str,
        document_type: str = "GENERAL"
    ):
        """
        Handle single file upload with validation
        """
        # 1. Validate file
        validation_result = await self.validate_file(file)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=validation_result["error"]
            )
        
        # 2. Generate unique filename
        file_hash = await self.compute_hash(file)
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{file_hash}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # 3. Check for duplicates
        if os.path.exists(file_path):
            return {
                "status": "duplicate",
                "file_id": file_hash,
                "message": "File already exists"
            }
        
        # 4. Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # 5. Create database record
        file_record = await self.create_file_record(
            file_id=file_hash,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            user_id=user_id,
            document_type=document_type
        )
        
        # 6. Trigger async processing
        from tasks import process_document
        task = process_document.delay(file_hash)
        
        return {
            "status": "uploaded",
            "file_id": file_hash,
            "task_id": task.id,
            "filename": file.filename
        }
    
    async def validate_file(self, file: UploadFile) -> dict:
        """
        Validate file before processing
        """
        # Allowed formats
        ALLOWED_EXTENSIONS = {
            '.pdf', '.docx', '.doc', '.txt', 
            '.html', '.xlsx', '.xls', '.csv'
        }
        
        # Max file size (100MB)
        MAX_SIZE = 100 * 1024 * 1024
        
        # Check extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return {
                "valid": False,
                "error": f"Unsupported file format: {file_ext}"
            }
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset
        
        if file_size > MAX_SIZE:
            return {
                "valid": False,
                "error": f"File too large: {file_size} bytes (max: {MAX_SIZE})"
            }
        
        if file_size == 0:
            return {
                "valid": False,
                "error": "Empty file"
            }
        
        return {"valid": True}
    
    async def compute_hash(self, file: UploadFile) -> str:
        """
        Compute SHA256 hash for deduplication
        """
        sha256_hash = hashlib.sha256()
        file.file.seek(0)
        
        while chunk := await file.read(8192):
            sha256_hash.update(chunk)
        
        file.file.seek(0)  # Reset for later reading
        return sha256_hash.hexdigest()
    
    async def create_file_record(
        self, 
        file_id: str, 
        original_filename: str,
        file_path: str,
        file_size: int,
        user_id: str,
        document_type: str
    ):
        """
        Create database record for uploaded file
        """
        import psycopg2
        from psycopg2.extras import Json
        from datetime import datetime
        
        conn = psycopg2.connect(
            host="192.168.1.88",
            port=15432,
            database="chatbotR4",
            user="kb_admin",
            password="1234567890"
        )
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO uploaded_files (
                    file_id,
                    original_filename,
                    file_path,
                    file_size,
                    file_extension,
                    user_id,
                    document_type,
                    upload_status,
                    upload_timestamp,
                    processing_metadata
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (file_id) DO UPDATE 
                SET upload_status = 'duplicate'
                RETURNING file_id
            """, (
                file_id,
                original_filename,
                file_path,
                file_size,
                os.path.splitext(original_filename)[1],
                user_id,
                document_type,
                'uploaded',
                datetime.utcnow(),
                Json({
                    "upload_method": "api",
                    "validation_passed": True
                })
            ))
            conn.commit()
        
        conn.close()
        return file_id

# FastAPI Endpoints
@app.post("/api/v1/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = "default_user",
    document_type: str = "GENERAL"
):
    """
    Upload single document
    """
    manager = UploadManager()
    result = await manager.upload_file(file, user_id, document_type)
    return JSONResponse(content=result)

@app.post("/api/v1/upload/batch")
async def upload_batch(
    files: List[UploadFile] = File(...),
    user_id: str = "default_user",
    document_type: str = "GENERAL"
):
    """
    Upload multiple documents
    """
    manager = UploadManager()
    results = []
    
    for file in files:
        try:
            result = await manager.upload_file(file, user_id, document_type)
            results.append({
                "filename": file.filename,
                "status": "success",
                "data": result
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    return JSONResponse(content={"results": results})
```

### 2. Format Parsers

#### PDF Parser
```python
import fitz  # pymupdf
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class PDFParser:
    """
    Parse PDF documents with Vietnamese text support
    """
    
    def parse(self, file_path: str) -> Dict:
        """
        Extract text, metadata, and structure from PDF
        """
        try:
            doc = fitz.open(file_path)
            
            result = {
                "text": "",
                "metadata": {},
                "pages": [],
                "structure": {
                    "total_pages": len(doc),
                    "has_toc": False,
                    "bookmarks": []
                }
            }
            
            # Extract metadata
            result["metadata"] = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", "")
            }
            
            # Extract table of contents
            toc = doc.get_toc()
            if toc:
                result["structure"]["has_toc"] = True
                result["structure"]["bookmarks"] = [
                    {
                        "level": item[0],
                        "title": item[1],
                        "page": item[2]
                    }
                    for item in toc
                ]
            
            # Extract text page by page
            full_text = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text with layout preservation
                text = page.get_text("text")
                
                # Extract images info
                images = page.get_images()
                
                page_data = {
                    "page_number": page_num + 1,
                    "text": text,
                    "char_count": len(text),
                    "image_count": len(images),
                    "has_tables": self._detect_tables(page)
                }
                
                result["pages"].append(page_data)
                full_text.append(text)
            
            result["text"] = "\n\n".join(full_text)
            
            doc.close()
            return result
            
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {str(e)}")
            raise
    
    def _detect_tables(self, page) -> bool:
        """
        Detect if page contains tables
        """
        # Simple heuristic: look for many horizontal/vertical lines
        drawings = page.get_drawings()
        horizontal_lines = sum(1 for d in drawings if d["type"] == "l" and abs(d["rect"].y1 - d["rect"].y0) < 1)
        vertical_lines = sum(1 for d in drawings if d["type"] == "l" and abs(d["rect"].x1 - d["rect"].x0) < 1)
        
        return horizontal_lines > 3 and vertical_lines > 3
```

#### DOCX Parser
```python
from docx import Document
from typing import Dict, List

class DOCXParser:
    """
    Parse DOCX documents with Vietnamese text support
    """
    
    def parse(self, file_path: str) -> Dict:
        """
        Extract text, metadata, and structure from DOCX
        """
        doc = Document(file_path)
        
        result = {
            "text": "",
            "metadata": {},
            "structure": {
                "total_paragraphs": 0,
                "total_tables": 0,
                "headings": []
            },
            "paragraphs": [],
            "tables": []
        }
        
        # Extract core properties
        core_props = doc.core_properties
        result["metadata"] = {
            "title": core_props.title or "",
            "author": core_props.author or "",
            "subject": core_props.subject or "",
            "keywords": core_props.keywords or "",
            "created": str(core_props.created) if core_props.created else "",
            "modified": str(core_props.modified) if core_props.modified else ""
        }
        
        # Extract paragraphs and structure
        full_text = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            
            para_data = {
                "text": text,
                "style": para.style.name,
                "is_heading": para.style.name.startswith('Heading')
            }
            
            if para_data["is_heading"]:
                result["structure"]["headings"].append({
                    "level": para.style.name,
                    "text": text
                })
            
            result["paragraphs"].append(para_data)
            full_text.append(text)
        
        result["structure"]["total_paragraphs"] = len(result["paragraphs"])
        
        # Extract tables
        for table in doc.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                table_data.append(row_data)
            result["tables"].append(table_data)
        
        result["structure"]["total_tables"] = len(result["tables"])
        result["text"] = "\n\n".join(full_text)
        
        return result
```

#### Universal Text Extractor
```python
import os
from typing import Dict

class UniversalTextExtractor:
    """
    Router for different file formats
    """
    
    def __init__(self):
        self.parsers = {
            '.pdf': PDFParser(),
            '.docx': DOCXParser(),
            '.doc': DOCXParser(),  # Requires conversion
            '.txt': self._parse_txt,
            '.html': self._parse_html,
            '.xlsx': self._parse_excel,
            '.xls': self._parse_excel
        }
    
    def extract(self, file_path: str) -> Dict:
        """
        Extract text from any supported format
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in self.parsers:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        parser = self.parsers[file_ext]
        
        if callable(parser):
            return parser(file_path)
        else:
            return parser.parse(file_path)
    
    def _parse_txt(self, file_path: str) -> Dict:
        """Parse plain text files"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return {
            "text": text,
            "metadata": {},
            "structure": {
                "char_count": len(text),
                "line_count": text.count('\n') + 1
            }
        }
    
    def _parse_html(self, file_path: str) -> Dict:
        """Parse HTML files"""
        from bs4 import BeautifulSoup
        
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator='\n')
        
        # Extract title and meta
        title = soup.find('title')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        
        return {
            "text": text,
            "metadata": {
                "title": title.string if title else "",
                "description": meta_desc.get('content', '') if meta_desc else ""
            },
            "structure": {
                "has_html": True
            }
        }
    
    def _parse_excel(self, file_path: str) -> Dict:
        """Parse Excel files"""
        import openpyxl
        
        wb = openpyxl.load_workbook(file_path, data_only=True)
        
        result = {
            "text": "",
            "metadata": {},
            "structure": {
                "sheet_count": len(wb.sheetnames),
                "sheets": []
            }
        }
        
        all_text = []
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            
            sheet_text = []
            for row in ws.iter_rows(values_only=True):
                row_text = ' | '.join(str(cell) for cell in row if cell is not None)
                if row_text:
                    sheet_text.append(row_text)
            
            result["structure"]["sheets"].append({
                "name": sheet_name,
                "row_count": ws.max_row,
                "col_count": ws.max_column
            })
            
            all_text.extend(sheet_text)
        
        result["text"] = "\n".join(all_text)
        
        return result
```

### 3. Vietnamese Text Preprocessing

```python
from underthesea import word_tokenize
import re
import unicodedata

class VietnamesePreprocessor:
    """
    Preprocessing pipeline for Vietnamese text
    """
    
    def __init__(self):
        # Vietnamese stopwords
        self.stopwords = set([
            'và', 'của', 'có', 'được', 'là', 'trong', 'với', 
            'cho', 'đến', 'về', 'từ', 'theo', 'như', 'để',
            'các', 'này', 'đó', 'những', 'một', 'khi', 'do'
        ])
    
    def preprocess(self, text: str, options: dict = None) -> Dict:
        """
        Full preprocessing pipeline
        
        Args:
            text: Raw Vietnamese text
            options: Processing options
                - normalize_unicode: True/False
                - remove_stopwords: True/False
                - tokenize: True/False
                - lowercase: True/False
        
        Returns:
            Dict with processed text and metadata
        """
        options = options or {}
        
        result = {
            "original_text": text,
            "processed_text": text,
            "metadata": {
                "original_length": len(text),
                "processing_steps": []
            }
        }
        
        # Step 1: Normalize Unicode
        if options.get('normalize_unicode', True):
            text = self.normalize_unicode(text)
            result["metadata"]["processing_steps"].append("unicode_normalized")
        
        # Step 2: Clean text
        text = self.clean_text(text)
        result["metadata"]["processing_steps"].append("cleaned")
        
        # Step 3: Lowercase (optional)
        if options.get('lowercase', True):
            text = text.lower()
            result["metadata"]["processing_steps"].append("lowercased")
        
        # Step 4: Tokenize (optional)
        if options.get('tokenize', False):
            tokens = word_tokenize(text)
            
            # Remove stopwords if requested
            if options.get('remove_stopwords', False):
                tokens = [t for t in tokens if t not in self.stopwords]
                result["metadata"]["processing_steps"].append("stopwords_removed")
            
            result["tokens"] = tokens
            result["processed_text"] = ' '.join(tokens)
        else:
            result["processed_text"] = text
        
        result["metadata"]["processed_length"] = len(result["processed_text"])
        
        return result
    
    def normalize_unicode(self, text: str) -> str:
        """
        Normalize Vietnamese Unicode characters
        """
        # NFD normalization for Vietnamese
        text = unicodedata.normalize('NFC', text)
        return text
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special control characters but keep Vietnamese diacritics
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\t')
        
        # Normalize quotation marks
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        return text.strip()
    
    def extract_legal_codes(self, text: str) -> List[str]:
        """
        Extract Vietnamese legal document codes
        CRITICAL: Preserve numbers and special characters
        """
        patterns = [
            r'Số\s*[:：]?\s*(\d+/[\w-]+)',
            r'Quyết định số\s*(\d+/QĐ-[\w-]+)',
            r'Nghị định số\s*(\d+/NĐ-CP)',
            r'Thông tư số\s*(\d+/TT-[\w-]+)',
            r'Nghị quyết số\s*(\d+/NQ-[\w-]+)',
            r'Chỉ thị số\s*(\d+/CT-[\w-]+)'
        ]
        
        codes = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            codes.extend(matches)
        
        return list(set(codes))  # Deduplicate
```

### 4. Async Task Processing with Celery

```python
from celery import Celery, Task
from celery.result import AsyncResult
import logging

# Initialize Celery
celery_app = Celery(
    'rag_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Ho_Chi_Minh',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
)

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks.process_document')
def process_document(self, file_id: str):
    """
    Main document processing task
    
    Pipeline:
    1. Load file from storage
    2. Parse format
    3. Preprocess Vietnamese text
    4. Extract metadata
    5. Generate embeddings
    6. Store in PostgreSQL + ChromaDB
    """
    try:
        # Update task state
        self.update_state(
            state='PROCESSING',
            meta={'current_step': 'loading', 'progress': 10}
        )
        
        # Step 1: Load file metadata
        file_info = get_file_info(file_id)
        file_path = file_info['file_path']
        
        # Step 2: Parse document
        self.update_state(
            state='PROCESSING',
            meta={'current_step': 'parsing', 'progress': 20}
        )
        
        extractor = UniversalTextExtractor()
        parsed_data = extractor.extract(file_path)
        
        # Step 3: Preprocess Vietnamese text
        self.update_state(
            state='PROCESSING',
            meta={'current_step': 'preprocessing', 'progress': 40}
        )
        
        preprocessor = VietnamesePreprocessor()
        processed = preprocessor.preprocess(
            parsed_data['text'],
            options={
                'normalize_unicode': True,
                'lowercase': False,  # Keep original case for legal docs
                'tokenize': False
            }
        )
        
        # Step 4: Extract metadata
        self.update_state(
            state='PROCESSING',
            meta={'current_step': 'metadata_extraction', 'progress': 60}
        )
        
        from metadata_extractor_v3 import MetadataEnricher
        enricher = MetadataEnricher()
        metadata = enricher.extract_metadata(processed['processed_text'])
        
        # Step 5: Chunk document
        self.update_state(
            state='PROCESSING',
            meta={'current_step': 'chunking', 'progress': 70}
        )
        
        chunks = chunk_document(
            processed['processed_text'],
            chunk_size=512,
            chunk_overlap=50
        )
        
        # Step 6: Generate embeddings
        self.update_state(
            state='PROCESSING',
            meta={'current_step': 'embedding', 'progress': 80}
        )
        
        from embedding_generator import generate_embeddings
        embeddings = generate_embeddings(chunks)
        
        # Step 7: Store in databases
        self.update_state(
            state='PROCESSING',
            meta={'current_step': 'storing', 'progress': 90}
        )
        
        # Store in PostgreSQL
        store_in_postgresql(file_id, metadata, chunks)
        
        # Store in ChromaDB
        store_in_chromadb(file_id, chunks, embeddings, metadata)
        
        # Update file status
        update_file_status(file_id, 'completed')
        
        return {
            'status': 'success',
            'file_id': file_id,
            'chunks_count': len(chunks),
            'metadata': metadata
        }
        
    except Exception as e:
        logger.error(f"Error processing document {file_id}: {str(e)}")
        update_file_status(file_id, 'failed', error=str(e))
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        raise

# Helper function to check task status
def get_task_status(task_id: str) -> Dict:
    """
    Get status of processing task
    """
    task = AsyncResult(task_id, app=celery_app)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is waiting to be processed'
        }
    elif task.state == 'PROCESSING':
        response = {
            'state': task.state,
            'current_step': task.info.get('current_step', ''),
            'progress': task.info.get('progress', 0)
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.result
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'error': str(task.info)
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    
    return response
```

### 5. Error Handling & Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class ErrorHandler:
    """
    Centralized error handling for ingestion pipeline
    """
    
    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def with_retry(func, *args, **kwargs):
        """
        Execute function with retry logic
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    
    @staticmethod
    def handle_parsing_error(file_id: str, file_path: str, error: Exception):
        """
        Handle parsing errors
        """
        error_info = {
            'file_id': file_id,
            'file_path': file_path,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stage': 'parsing'
        }
        
        logger.error(f"Parsing error: {error_info}")
        
        # Store error in database
        store_processing_error(error_info)
        
        # Move to quarantine
        quarantine_file(file_id, file_path)
        
        return {
            'status': 'failed',
            'error': error_info
        }
    
    @staticmethod
    def handle_embedding_error(file_id: str, chunk_id: str, error: Exception):
        """
        Handle embedding generation errors
        """
        logger.error(f"Embedding error for chunk {chunk_id}: {str(error)}")
        
        # Mark chunk as failed but continue with others
        mark_chunk_failed(file_id, chunk_id)
        
        return {
            'status': 'partial_success',
            'failed_chunk': chunk_id
        }

def quarantine_file(file_id: str, file_path: str):
    """
    Move problematic files to quarantine folder
    """
    import shutil
    
    quarantine_dir = "/mnt/user-data/quarantine"
    os.makedirs(quarantine_dir, exist_ok=True)
    
    quarantine_path = os.path.join(quarantine_dir, file_id)
    shutil.move(file_path, quarantine_path)
    
    logger.info(f"File {file_id} moved to quarantine")
```

## Database Schema

### PostgreSQL Tables

```sql
-- Uploaded files tracking
CREATE TABLE IF NOT EXISTS uploaded_files (
    file_id VARCHAR(64) PRIMARY KEY,
    original_filename VARCHAR(500) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    file_extension VARCHAR(20),
    user_id VARCHAR(100) NOT NULL,
    document_type VARCHAR(50) DEFAULT 'GENERAL',
    upload_status VARCHAR(50) DEFAULT 'uploaded',
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    processing_metadata JSONB,
    error_message TEXT,
    CONSTRAINT valid_status CHECK (
        upload_status IN (
            'uploaded', 'processing', 'completed', 
            'failed', 'duplicate', 'quarantined'
        )
    )
);

-- Create index for faster queries
CREATE INDEX idx_uploaded_files_user_id ON uploaded_files(user_id);
CREATE INDEX idx_uploaded_files_status ON uploaded_files(upload_status);
CREATE INDEX idx_uploaded_files_timestamp ON uploaded_files(upload_timestamp DESC);

-- Processing errors log
CREATE TABLE IF NOT EXISTS processing_errors (
    error_id SERIAL PRIMARY KEY,
    file_id VARCHAR(64) REFERENCES uploaded_files(file_id),
    error_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_stage VARCHAR(50),
    error_type VARCHAR(100),
    error_message TEXT,
    stack_trace TEXT,
    retry_count INTEGER DEFAULT 0,
    resolved BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_errors_file_id ON processing_errors(file_id);
CREATE INDEX idx_errors_unresolved ON processing_errors(resolved) WHERE resolved = FALSE;

-- Document chunks
CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id VARCHAR(100) PRIMARY KEY,
    file_id VARCHAR(64) REFERENCES uploaded_files(file_id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_size INTEGER,
    start_char INTEGER,
    end_char INTEGER,
    embedding_status VARCHAR(50) DEFAULT 'pending',
    chromadb_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_embedding_status CHECK (
        embedding_status IN ('pending', 'completed', 'failed')
    )
);

CREATE INDEX idx_chunks_file_id ON document_chunks(file_id);
CREATE INDEX idx_chunks_status ON document_chunks(embedding_status);
```

## API Endpoints Reference

```python
# Status check endpoint
@app.get("/api/v1/status/{task_id}")
async def check_task_status(task_id: str):
    """
    Check processing task status
    """
    status = get_task_status(task_id)
    return JSONResponse(content=status)

# File info endpoint
@app.get("/api/v1/files/{file_id}")
async def get_file_details(file_id: str):
    """
    Get file processing details
    """
    file_info = get_file_info(file_id)
    return JSONResponse(content=file_info)

# List files endpoint
@app.get("/api/v1/files")
async def list_files(
    user_id: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 20
):
    """
    List uploaded files with filters
    """
    files = list_user_files(
        user_id=user_id,
        status=status,
        skip=skip,
        limit=limit
    )
    return JSONResponse(content={"files": files, "total": len(files)})

# Delete file endpoint
@app.delete("/api/v1/files/{file_id}")
async def delete_file(file_id: str):
    """
    Delete file and all associated data
    """
    result = delete_file_completely(file_id)
    return JSONResponse(content=result)

# Retry failed processing
@app.post("/api/v1/retry/{file_id}")
async def retry_processing(file_id: str):
    """
    Retry processing for failed file
    """
    task = process_document.delay(file_id)
    return JSONResponse(content={
        "status": "retry_initiated",
        "task_id": task.id
    })
```

## Performance Optimization

### Batch Processing
```python
@celery_app.task(name='tasks.batch_process_documents')
def batch_process_documents(file_ids: List[str]):
    """
    Process multiple documents in batch
    """
    results = []
    
    for file_id in file_ids:
        try:
            result = process_document(file_id)
            results.append({
                'file_id': file_id,
                'status': 'success',
                'data': result
            })
        except Exception as e:
            results.append({
                'file_id': file_id,
                'status': 'failed',
                'error': str(e)
            })
    
    return {
        'total': len(file_ids),
        'succeeded': sum(1 for r in results if r['status'] == 'success'),
        'failed': sum(1 for r in results if r['status'] == 'failed'),
        'results': results
    }
```

### Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def parallel_extract_embeddings(chunks: List[str], max_workers: int = 4):
    """
    Generate embeddings in parallel
    """
    embeddings = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(generate_single_embedding, chunk): i 
            for i, chunk in enumerate(chunks)
        }
        
        for future in as_completed(futures):
            idx = futures[future]
            try:
                embedding = future.result()
                embeddings.append((idx, embedding))
            except Exception as e:
                logger.error(f"Error generating embedding for chunk {idx}: {str(e)}")
                embeddings.append((idx, None))
    
    # Sort by original index
    embeddings.sort(key=lambda x: x[0])
    return [emb for _, emb in embeddings]
```

## Testing Guidelines

### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch

def test_file_upload():
    """Test file upload functionality"""
    manager = UploadManager()
    
    # Mock file
    mock_file = Mock()
    mock_file.filename = "test_document.pdf"
    mock_file.read = Mock(return_value=b"test content")
    
    result = await manager.upload_file(
        mock_file, 
        user_id="test_user",
        document_type="LEGAL_RND"
    )
    
    assert result["status"] == "uploaded"
    assert "file_id" in result
    assert "task_id" in result

def test_pdf_parser():
    """Test PDF parsing"""
    parser = PDFParser()
    result = parser.parse("tests/fixtures/test_doc.pdf")
    
    assert "text" in result
    assert "metadata" in result
    assert "structure" in result
    assert result["structure"]["total_pages"] > 0

def test_vietnamese_preprocessing():
    """Test Vietnamese text preprocessing"""
    preprocessor = VietnamesePreprocessor()
    
    text = "Quyết định số 123/QĐ-ABC ngày 15 tháng 10 năm 2024"
    result = preprocessor.preprocess(text)
    
    assert result["processed_text"] is not None
    assert len(result["metadata"]["processing_steps"]) > 0
    
    # Test legal code extraction
    codes = preprocessor.extract_legal_codes(text)
    assert "123/QĐ-ABC" in codes
```

### Integration Tests
```python
def test_end_to_end_ingestion():
    """Test complete ingestion pipeline"""
    # 1. Upload file
    response = client.post(
        "/api/v1/upload",
        files={"file": open("tests/fixtures/test_doc.pdf", "rb")},
        data={"user_id": "test_user", "document_type": "LEGAL_RND"}
    )
    
    assert response.status_code == 200
    data = response.json()
    file_id = data["file_id"]
    task_id = data["task_id"]
    
    # 2. Wait for processing
    import time
    max_wait = 60  # seconds
    start = time.time()
    
    while time.time() - start < max_wait:
        status_response = client.get(f"/api/v1/status/{task_id}")
        status_data = status_response.json()
        
        if status_data["state"] == "SUCCESS":
            break
        
        time.sleep(2)
    
    assert status_data["state"] == "SUCCESS"
    
    # 3. Verify data in databases
    # Check PostgreSQL
    file_info = get_file_info(file_id)
    assert file_info["upload_status"] == "completed"
    
    # Check ChromaDB
    from chromadb_client import search_by_file_id
    results = search_by_file_id(file_id)
    assert len(results) > 0
```

## Monitoring & Logging

### Structured Logging
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """
    Structured logging for better observability
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(self._json_formatter)
        self.logger.addHandler(handler)
    
    def _json_formatter(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data)
    
    def log_ingestion_event(
        self, 
        event_type: str, 
        file_id: str, 
        details: dict
    ):
        """
        Log ingestion pipeline events
        """
        self.logger.info(
            f"Ingestion event: {event_type}",
            extra={
                "event_type": event_type,
                "file_id": file_id,
                **details
            }
        )

# Usage
logger = StructuredLogger("ingestion_pipeline")

logger.log_ingestion_event(
    "file_uploaded",
    file_id="abc123",
    details={
        "filename": "document.pdf",
        "size": 1024000,
        "user_id": "user123"
    }
)
```

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
files_uploaded = Counter(
    'rag_files_uploaded_total',
    'Total number of files uploaded',
    ['document_type', 'status']
)

processing_time = Histogram(
    'rag_processing_seconds',
    'Time spent processing documents',
    ['stage']
)

active_tasks = Gauge(
    'rag_active_tasks',
    'Number of active processing tasks'
)

# Usage in code
files_uploaded.labels(document_type='LEGAL_RND', status='success').inc()

with processing_time.labels(stage='parsing').time():
    parsed_data = parser.parse(file_path)
```

## Troubleshooting Guide

### Issue 1: Upload Fails with Large Files
**Symptom**: Timeout or connection reset with files >50MB

**Solution**:
```python
# Increase FastAPI limits
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Increase max request size
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600
)

# Use streaming upload
@app.post("/api/v1/upload/stream")
async def upload_stream(request: Request):
    async with aiofiles.open(temp_path, 'wb') as f:
        async for chunk in request.stream():
            await f.write(chunk)
```

### Issue 2: Celery Tasks Stuck
**Symptom**: Tasks remain in PENDING state

**Solution**:
```bash
# Check Celery workers
celery -A tasks inspect active

# Check Redis connection
redis-cli ping

# Restart workers
celery -A tasks control shutdown
celery -A tasks worker --loglevel=info
```

### Issue 3: Vietnamese Characters Corrupted
**Symptom**: Diacritics display incorrectly

**Solution**:
```python
# Ensure UTF-8 encoding everywhere
import sys
import locale

# Set default encoding
if sys.version_info[0] >= 3:
    sys.stdout.reconfigure(encoding='utf-8')

# PostgreSQL connection with UTF-8
conn = psycopg2.connect(
    host="192.168.1.88",
    port=15432,
    database="chatbotR4",
    user="kb_admin",
    password="1234567890",
    client_encoding='UTF8'
)
```

### Issue 4: Memory Issues with Large PDFs
**Symptom**: OOM errors when processing large files

**Solution**:
```python
# Process PDFs in streaming mode
import fitz

def parse_pdf_streaming(file_path: str, callback):
    """Process PDF page by page"""
    doc = fitz.open(file_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # Process page immediately
        callback(page_num, text)
        
        # Clear page from memory
        page = None
    
    doc.close()

# Chunk and store incrementally
def process_large_document(file_path: str):
    def process_page(page_num, text):
        # Generate embedding
        embedding = generate_embedding(text)
        
        # Store immediately
        store_chunk(file_id, page_num, text, embedding)
    
    parse_pdf_streaming(file_path, process_page)
```

## Quick Reference Commands

```bash
# Start Celery worker
celery -A tasks worker --loglevel=info --concurrency=4

# Start Celery beat (for scheduled tasks)
celery -A tasks beat --loglevel=info

# Monitor Celery with Flower
celery -A tasks flower --port=5555

# Check task status
celery -A tasks inspect active
celery -A tasks inspect scheduled
celery -A tasks inspect reserved

# Purge all tasks
celery -A tasks purge

# Check Redis
redis-cli info

# Test file upload
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_document.pdf" \
  -F "user_id=test_user" \
  -F "document_type=LEGAL_RND"

# Check processing status
curl "http://localhost:8000/api/v1/status/{task_id}"

# List uploaded files
curl "http://localhost:8000/api/v1/files?user_id=test_user&status=completed"
```

## Vietnamese-Specific Considerations

### Legal Document Patterns
```python
# Always preserve these patterns in preprocessing
PRESERVE_PATTERNS = [
    r'\d+/[\w-]+',  # Document codes (123/QĐ-ABC)
    r'Điều \d+',     # Article numbers
    r'Khoản \d+',    # Clause numbers
    r'Điểm [a-z]',   # Point markers
]

def preprocess_legal_text(text: str) -> str:
    """
    Preprocess while preserving legal structure
    """
    # Extract and protect legal codes
    codes = extract_legal_codes(text)
    
    # Replace with placeholders
    for i, code in enumerate(codes):
        text = text.replace(code, f"__CODE_{i}__")
    
    # Normal preprocessing
    text = clean_text(text)
    
    # Restore codes
    for i, code in enumerate(codes):
        text = text.replace(f"__CODE_{i}__", code)
    
    return text
```

### File Naming Conventions
```python
def generate_vietnamese_friendly_filename(original_name: str) -> str:
    """
    Generate storage-safe filename from Vietnamese filename
    """
    import unicodedata
    
    # Normalize Unicode
    name = unicodedata.normalize('NFC', original_name)
    
    # Keep Vietnamese characters but remove problematic ones
    safe_chars = set(
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789'
        'áàảãạăắằẳẵặâấầẩẫậ'
        'éèẻẽẹêếềểễệ'
        'íìỉĩị'
        'óòỏõọôốồổỗộơớờởỡợ'
        'úùủũụưứừửữự'
        'ýỳỷỹỵ'
        'đ'
        'ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ'
        'ÉÈẺẼẸÊẾỀỂỄỆ'
        'ÍÌỈĨỊ'
        'ÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ'
        'ÚÙỦŨỤƯỨỪỬỮỰ'
        'ÝỲỶỸỴ'
        'Đ'
        '.-_ '
    )
    
    cleaned = ''.join(c if c in safe_chars else '_' for c in name)
    
    # Remove multiple underscores
    import re
    cleaned = re.sub(r'_+', '_', cleaned)
    
    return cleaned.strip('_')
```

## Success Criteria

- ✅ Supports all required formats (PDF, DOCX, TXT, HTML, Excel)
- ✅ Handles Vietnamese text correctly (Unicode, diacritics)
- ✅ Async processing with status tracking
- ✅ Error handling and retry mechanisms
- ✅ Deduplication via file hashing
- ✅ Progress tracking for long operations
- ✅ Batch processing capabilities
- ✅ Integration with PostgreSQL + ChromaDB
- ✅ Monitoring and logging
- ✅ API endpoints for all operations

## End of Skill File
