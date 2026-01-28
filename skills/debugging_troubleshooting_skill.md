# Debugging & Troubleshooting Skill for Vietnamese RAG System

## Overview
This skill provides comprehensive debugging strategies, common error patterns, diagnostic tools, and step-by-step troubleshooting workflows for Vietnamese RAG systems. Focus on practical solutions with real error examples.

## 🎯 Quick Error Finder

### "Tôi gặp lỗi này" → "Làm sao fix?"

| Error Pattern | Category | Jump to Section |
|--------------|----------|-----------------|
| `UnicodeDecodeError` / `UnicodeEncodeError` | Vietnamese Encoding | [Vietnamese Encoding Issues](#vietnamese-encoding-issues) |
| `CUDA out of memory` | GPU/Memory | [GPU Memory Issues](#gpu-memory-issues) |
| `Connection refused` / Database errors | Database | [Database Debugging](#database-debugging) |
| `ChromaDB: Collection not found` | Vector DB | [ChromaDB Issues](#chromadb-issues) |
| Slow retrieval / High latency | Performance | [Performance Debugging](#performance-debugging) |
| `AttributeError: 'NoneType'` | Null Values | [Null Pointer Debugging](#null-pointer-debugging) |
| API returns 500 / 503 | Backend | [API Debugging](#api-debugging) |
| Import errors / Module not found | Dependencies | [Dependency Issues](#dependency-issues) |
| Vietnamese text corrupted | NLP Processing | [Vietnamese Text Issues](#vietnamese-text-processing-issues) |
| LLM returns gibberish | Generation | [LLM Integration Issues](#llm-integration-issues) |
| File upload fails | File Processing | [File Upload Debugging](#file-upload-debugging) |
| JWT token invalid | Authentication | [Auth Debugging](#authentication-debugging) |
| Memory leak | Memory Management | [Memory Leak Detection](#memory-leak-detection) |

---

## 🔧 Essential Debugging Tools

### 1. Python Debugger (pdb)

```python
import pdb

# Method 1: Set breakpoint in code
def problematic_function(data):
    result = process_data(data)
    pdb.set_trace()  # Execution stops here
    return result

# Method 2: Post-mortem debugging
try:
    risky_operation()
except Exception:
    import pdb; pdb.post_mortem()

# Method 3: Run entire script with debugger
# python -m pdb script.py

# Common pdb commands:
# n (next) - Execute next line
# s (step) - Step into function
# c (continue) - Continue execution
# p variable - Print variable value
# l (list) - Show current code
# b linenum - Set breakpoint
# q (quit) - Exit debugger
```

### 2. IPython Debugger (ipdb)

```python
# Better interface than pdb
import ipdb

def debug_retrieval(query):
    results = retrieve_documents(query)
    ipdb.set_trace()  # Interactive debugging with autocomplete
    return results

# Auto-start on exception
import sys
from IPython.core import ultratb
sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux')
```

### 3. Logging Configuration

```python
import logging
import sys
from datetime import datetime

# Advanced logging setup
def setup_logging(level=logging.DEBUG):
    """
    Setup comprehensive logging for debugging
    """
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (with colors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler(
        f'debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return root_logger

# Usage
logger = setup_logging()

def retrieve_documents(query):
    logger.debug(f"Query received: {query}")
    logger.debug(f"Query length: {len(query)}")
    
    try:
        results = search_engine.search(query)
        logger.info(f"Found {len(results)} results")
        logger.debug(f"Results: {results}")
        return results
    except Exception as e:
        logger.error(f"Search failed: {str(e)}", exc_info=True)
        raise
```

### 4. Function Execution Timer

```python
import time
import functools
import logging

logger = logging.getLogger(__name__)

def debug_timer(func):
    """
    Decorator to time function execution and log details
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"[ENTER] {func_name}")
        logger.debug(f"Args: {args}")
        logger.debug(f"Kwargs: {kwargs}")
        
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.debug(f"[EXIT] {func_name} - Success in {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"[ERROR] {func_name} - Failed after {elapsed:.3f}s: {str(e)}")
            raise
    
    return wrapper

# Usage
@debug_timer
def retrieve_and_rank(query, top_k=5):
    results = retriever.retrieve(query, top_k=top_k * 2)
    ranked = reranker.rerank(query, results, top_k=top_k)
    return ranked
```

### 5. Variable Inspector

```python
import inspect
import pprint

def debug_inspect(obj, name="object"):
    """
    Comprehensive object inspection for debugging
    """
    print(f"\n{'='*60}")
    print(f"DEBUG INSPECT: {name}")
    print(f"{'='*60}")
    
    # Type and ID
    print(f"Type: {type(obj)}")
    print(f"ID: {id(obj)}")
    
    # Value
    print(f"\nValue:")
    pprint.pprint(obj, width=80, depth=3)
    
    # Attributes (if object)
    if hasattr(obj, '__dict__'):
        print(f"\nAttributes:")
        pprint.pprint(vars(obj), width=80, depth=2)
    
    # Methods (if object)
    if hasattr(obj, '__class__'):
        print(f"\nMethods:")
        methods = [m for m in dir(obj) if not m.startswith('_') and callable(getattr(obj, m))]
        pprint.pprint(methods)
    
    # Size (if applicable)
    try:
        import sys
        print(f"\nMemory size: {sys.getsizeof(obj)} bytes")
    except:
        pass
    
    # Length (if applicable)
    try:
        print(f"Length: {len(obj)}")
    except:
        pass
    
    print(f"{'='*60}\n")

# Usage
result = retrieve_documents("test query")
debug_inspect(result, "retrieval_result")
```

---

## 🐛 Common Error Categories

## Vietnamese Encoding Issues

### Error 1: UnicodeDecodeError

```python
# ❌ WRONG - This will fail with Vietnamese text
with open('document.txt', 'r') as f:  # Default encoding
    text = f.read()

# Error:
# UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 123
```

**Root Cause**: File contains UTF-8 Vietnamese characters but Python opens with system default encoding (often cp1252 on Windows)

**Solution**:
```python
# ✅ CORRECT - Always specify UTF-8
with open('document.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# ✅ CORRECT - Handle errors gracefully
with open('document.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# ✅ CORRECT - Or replace problematic characters
with open('document.txt', 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()
```

**Debugging Script**:
```python
def debug_file_encoding(filepath):
    """
    Detect and diagnose file encoding issues
    """
    import chardet
    
    # Read raw bytes
    with open(filepath, 'rb') as f:
        raw_data = f.read()
    
    # Detect encoding
    detection = chardet.detect(raw_data)
    print(f"Detected encoding: {detection['encoding']}")
    print(f"Confidence: {detection['confidence']}")
    
    # Try reading with detected encoding
    try:
        with open(filepath, 'r', encoding=detection['encoding']) as f:
            text = f.read()
        print("✅ Successfully read file")
        print(f"First 100 chars: {text[:100]}")
    except Exception as e:
        print(f"❌ Failed to read: {str(e)}")
    
    # Try UTF-8
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        print("✅ UTF-8 works")
    except Exception as e:
        print(f"❌ UTF-8 failed: {str(e)}")

# Usage
debug_file_encoding('vietnamese_document.txt')
```

### Error 2: Vietnamese Characters Display as �

```python
# Problem: Vietnamese text looks like: "Vi���t Nam"
```

**Debugging**:
```python
def debug_vietnamese_text(text):
    """
    Diagnose Vietnamese text encoding issues
    """
    import unicodedata
    
    print(f"Original text: {text}")
    print(f"Text length: {len(text)}")
    print(f"Byte length: {len(text.encode('utf-8'))}")
    
    # Check for replacement characters
    if '�' in text:
        print("⚠️ Contains replacement characters - encoding issue detected")
    
    # Show character details
    print("\nCharacter analysis (first 20):")
    for i, char in enumerate(text[:20]):
        try:
            name = unicodedata.name(char)
        except ValueError:
            name = "UNKNOWN"
        print(f"{i}: '{char}' - U+{ord(char):04X} - {name}")
    
    # Test normalize
    normalized = unicodedata.normalize('NFC', text)
    if normalized != text:
        print("\n⚠️ Text can be normalized")
        print(f"Normalized: {normalized}")
    
    # Vietnamese character check
    vietnamese_chars = set('àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ')
    has_vietnamese = any(c.lower() in vietnamese_chars for c in text)
    print(f"\nContains Vietnamese characters: {has_vietnamese}")

# Usage
debug_vietnamese_text("Việt Nam")
```

**Common Fixes**:
```python
# Fix 1: Normalize Unicode
import unicodedata

def fix_vietnamese_encoding(text):
    """
    Normalize Vietnamese text encoding
    """
    # NFC normalization for Vietnamese
    text = unicodedata.normalize('NFC', text)
    return text

# Fix 2: Re-encode if wrong encoding was used
def fix_wrong_encoding(text):
    """
    Fix text that was decoded with wrong encoding
    """
    try:
        # If text was decoded as latin-1 but is actually UTF-8
        bytes_data = text.encode('latin-1')
        fixed_text = bytes_data.decode('utf-8')
        return fixed_text
    except:
        return text

# Fix 3: Clean invisible characters
def clean_vietnamese_text(text):
    """
    Remove invisible and control characters
    """
    import re
    
    # Remove zero-width characters
    text = re.sub(r'[\u200b-\u200f\ufeff]', '', text)
    
    # Remove other control characters but keep newlines/tabs
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\t')
    
    return text
```

---

## GPU Memory Issues

### Error: CUDA out of memory

```python
# Error message:
# RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB 
# (GPU 0; 10.76 GiB total capacity; 8.79 GiB already allocated)
```

**Debugging Script**:
```python
import torch
import numpy as np

def debug_gpu_memory():
    """
    Comprehensive GPU memory diagnostics
    """
    if not torch.cuda.is_available():
        print("❌ CUDA not available")
        return
    
    device = torch.cuda.current_device()
    
    print(f"{'='*60}")
    print(f"GPU Memory Diagnostics")
    print(f"{'='*60}")
    
    # Device info
    print(f"\nDevice: {torch.cuda.get_device_name(device)}")
    print(f"Device capability: {torch.cuda.get_device_capability(device)}")
    
    # Memory info
    total_memory = torch.cuda.get_device_properties(device).total_memory
    allocated = torch.cuda.memory_allocated(device)
    reserved = torch.cuda.memory_reserved(device)
    free = total_memory - reserved
    
    print(f"\nMemory Status:")
    print(f"Total memory: {total_memory / 1024**3:.2f} GB")
    print(f"Allocated: {allocated / 1024**3:.2f} GB ({allocated/total_memory*100:.1f}%)")
    print(f"Reserved: {reserved / 1024**3:.2f} GB ({reserved/total_memory*100:.1f}%)")
    print(f"Free: {free / 1024**3:.2f} GB ({free/total_memory*100:.1f}%)")
    
    # Peak memory
    peak = torch.cuda.max_memory_allocated(device)
    print(f"\nPeak allocated: {peak / 1024**3:.2f} GB")
    
    # Memory summary
    print(f"\nDetailed Memory Summary:")
    print(torch.cuda.memory_summary(device, abbreviated=False))
    
    return {
        'total_gb': total_memory / 1024**3,
        'allocated_gb': allocated / 1024**3,
        'free_gb': free / 1024**3,
        'utilization_pct': allocated/total_memory*100
    }

# Usage
memory_stats = debug_gpu_memory()
```

**Solutions**:

```python
# Solution 1: Clear cache regularly
def clear_gpu_memory():
    """
    Clear GPU memory cache
    """
    import gc
    import torch
    
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
    
    print("✅ GPU cache cleared")

# Solution 2: Reduce batch size dynamically
def adaptive_batch_size(texts, model, max_memory_gb=8.0):
    """
    Automatically adjust batch size based on available memory
    """
    import torch
    
    batch_size = 32  # Start optimistic
    
    while batch_size > 0:
        try:
            # Check available memory
            available_memory = (max_memory_gb * 1024**3) - torch.cuda.memory_allocated()
            
            # Estimate memory needed (rough approximation)
            estimated_memory_per_sample = 10 * 1024 * 1024  # 10MB per sample
            safe_batch_size = int(available_memory / (estimated_memory_per_sample * 2))
            
            batch_size = min(batch_size, safe_batch_size)
            
            if batch_size == 0:
                batch_size = 1
            
            # Try encoding
            sample_batch = texts[:batch_size]
            embeddings = model.encode(sample_batch)
            
            print(f"✅ Using batch_size: {batch_size}")
            return batch_size
            
        except RuntimeError as e:
            if "out of memory" in str(e):
                clear_gpu_memory()
                batch_size = batch_size // 2
                print(f"⚠️ OOM, reducing batch_size to {batch_size}")
            else:
                raise
    
    raise RuntimeError("Cannot find working batch size")

# Solution 3: Process in chunks with memory monitoring
def safe_batch_encode(texts, model, target_memory_gb=8.0):
    """
    Encode texts in batches with memory monitoring
    """
    import torch
    
    embeddings = []
    batch_size = adaptive_batch_size(texts, model, target_memory_gb)
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        # Monitor memory before encoding
        mem_before = torch.cuda.memory_allocated() / 1024**3
        
        # Encode
        batch_embeddings = model.encode(batch)
        embeddings.append(batch_embeddings)
        
        # Monitor memory after encoding
        mem_after = torch.cuda.memory_allocated() / 1024**3
        print(f"Batch {i//batch_size + 1}: Memory {mem_before:.2f}GB → {mem_after:.2f}GB")
        
        # Clear cache periodically
        if (i + batch_size) % (batch_size * 10) == 0:
            clear_gpu_memory()
    
    return np.vstack(embeddings)

# Solution 4: Use gradient checkpointing (for training)
def model_with_gradient_checkpointing(model):
    """
    Enable gradient checkpointing to save memory
    """
    from torch.utils.checkpoint import checkpoint
    
    # Wrap forward pass
    original_forward = model.forward
    
    def checkpointed_forward(*args, **kwargs):
        return checkpoint(original_forward, *args, **kwargs)
    
    model.forward = checkpointed_forward
    return model

# Solution 5: Use mixed precision
def encode_with_mixed_precision(texts, model):
    """
    Use FP16 to reduce memory usage
    """
    import torch
    from torch.cuda.amp import autocast
    
    with autocast():
        embeddings = model.encode(texts)
    
    return embeddings
```

---

## Database Debugging

### PostgreSQL Connection Issues

```python
# Error:
# psycopg2.OperationalError: could not connect to server: Connection refused
```

**Debugging Script**:
```python
import psycopg2
from psycopg2 import sql
import logging

logger = logging.getLogger(__name__)

def debug_postgres_connection(
    host="192.168.1.88",
    port=15432,
    database="chatbotR4",
    user="kb_admin",
    password="1234567890"
):
    """
    Comprehensive PostgreSQL connection diagnostics
    """
    print(f"\n{'='*60}")
    print("PostgreSQL Connection Diagnostics")
    print(f"{'='*60}\n")
    
    # Test 1: Basic connectivity
    print("Test 1: Basic connectivity")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Can reach {host}:{port}")
        else:
            print(f"❌ Cannot reach {host}:{port}")
            print("   Check: Firewall, network, PostgreSQL running?")
            return False
    except Exception as e:
        print(f"❌ Network error: {str(e)}")
        return False
    
    # Test 2: PostgreSQL connection
    print("\nTest 2: PostgreSQL authentication")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=10
        )
        print("✅ Connected to PostgreSQL")
        
        # Test 3: Database version
        print("\nTest 3: Database version")
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"PostgreSQL version: {version}")
        
        # Test 4: List tables
        print("\nTest 4: Available tables")
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cur.fetchall()
            print(f"Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
        
        # Test 5: Test query
        print("\nTest 5: Sample query")
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM documents;
            """)
            count = cur.fetchone()[0]
            print(f"✅ Found {count} documents")
        
        conn.close()
        print("\n✅ All database tests passed")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if PostgreSQL is running: sudo systemctl status postgresql")
        print("2. Check pg_hba.conf for authentication settings")
        print("3. Verify credentials")
        print("4. Check port is correct")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

# Usage
debug_postgres_connection()
```

**Common Fixes**:

```python
# Fix 1: Connection pooling to avoid "too many connections"
from psycopg2 import pool

class DatabasePool:
    """
    Connection pool for PostgreSQL
    """
    def __init__(self, minconn=1, maxconn=10):
        self.pool = pool.SimpleConnectionPool(
            minconn,
            maxconn,
            host="192.168.1.88",
            port=15432,
            database="chatbotR4",
            user="kb_admin",
            password="1234567890"
        )
    
    def get_connection(self):
        return self.pool.getconn()
    
    def return_connection(self, conn):
        self.pool.putconn(conn)
    
    def close_all(self):
        self.pool.closeall()

# Usage
db_pool = DatabasePool()

def query_database(query):
    conn = db_pool.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()
        return result
    finally:
        db_pool.return_connection(conn)

# Fix 2: Automatic retry on connection failures
import time
from functools import wraps

def retry_on_db_error(max_retries=3, delay=1):
    """
    Decorator to retry database operations
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except psycopg2.OperationalError as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Database operation failed after {max_retries} attempts")
                        raise
                    logger.warning(f"Database error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
        return wrapper
    return decorator

@retry_on_db_error(max_retries=3)
def fetch_documents(doc_ids):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM documents WHERE id = ANY(%s)", (doc_ids,))
        return cur.fetchall()
```

### Database Query Performance Issues

```python
def debug_slow_query(query, params=None, explain=True):
    """
    Analyze slow database queries
    """
    import psycopg2
    import time
    
    conn = psycopg2.connect(
        host="192.168.1.88",
        port=15432,
        database="chatbotR4",
        user="kb_admin",
        password="1234567890"
    )
    
    print(f"\n{'='*60}")
    print("Query Performance Analysis")
    print(f"{'='*60}\n")
    
    print(f"Query: {query}")
    if params:
        print(f"Parameters: {params}")
    
    with conn.cursor() as cur:
        # EXPLAIN ANALYZE
        if explain:
            print("\n--- EXPLAIN ANALYZE ---")
            explain_query = f"EXPLAIN ANALYZE {query}"
            cur.execute(explain_query, params)
            explain_result = cur.fetchall()
            for row in explain_result:
                print(row[0])
        
        # Actual execution time
        print("\n--- Execution Time ---")
        start = time.time()
        cur.execute(query, params)
        results = cur.fetchall()
        elapsed = time.time() - start
        
        print(f"Execution time: {elapsed:.3f} seconds")
        print(f"Rows returned: {len(results)}")
        print(f"Time per row: {elapsed/len(results)*1000:.2f} ms" if results else "N/A")
        
        # Check for missing indexes
        if "WHERE" in query.upper():
            print("\n--- Index Suggestions ---")
            # Extract table name
            import re
            table_match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
            if table_match:
                table_name = table_match.group(1)
                
                # Check existing indexes
                cur.execute("""
                    SELECT indexname, indexdef 
                    FROM pg_indexes 
                    WHERE tablename = %s;
                """, (table_name,))
                indexes = cur.fetchall()
                
                print(f"Existing indexes on {table_name}:")
                for idx_name, idx_def in indexes:
                    print(f"  - {idx_name}: {idx_def}")
    
    conn.close()
    print(f"\n{'='*60}\n")

# Usage
debug_slow_query("""
    SELECT * FROM documents 
    WHERE metadata->>'document_type' = 'LEGAL_RND'
    AND created_at > '2024-01-01'
""")
```

---

## ChromaDB Issues

### Error: Collection not found

```python
def debug_chromadb_connection(
    host="localhost",
    port=8000,
    collection_name="rag_documents"
):
    """
    Debug ChromaDB connection and collection issues
    """
    import chromadb
    
    print(f"\n{'='*60}")
    print("ChromaDB Diagnostics")
    print(f"{'='*60}\n")
    
    try:
        # Test 1: Connect to ChromaDB
        print("Test 1: ChromaDB connection")
        client = chromadb.HttpClient(host=host, port=port)
        print(f"✅ Connected to ChromaDB at {host}:{port}")
        
        # Test 2: List all collections
        print("\nTest 2: List collections")
        collections = client.list_collections()
        print(f"Found {len(collections)} collections:")
        for coll in collections:
            print(f"  - {coll.name} ({coll.count()} documents)")
        
        # Test 3: Check specific collection
        print(f"\nTest 3: Check collection '{collection_name}'")
        try:
            collection = client.get_collection(collection_name)
            count = collection.count()
            print(f"✅ Collection exists with {count} documents")
            
            # Sample metadata
            if count > 0:
                print("\nSample document:")
                sample = collection.peek(1)
                print(f"  IDs: {sample['ids']}")
                print(f"  Metadatas: {sample['metadatas']}")
                print(f"  Documents: {sample['documents'][:100] if sample['documents'] else 'None'}...")
            
        except Exception as e:
            print(f"❌ Collection not found: {str(e)}")
            print("\nTroubleshooting:")
            print(f"1. Create collection: client.create_collection('{collection_name}')")
            print("2. Check collection name spelling")
            print("3. Verify data was imported")
        
        # Test 4: Test query
        if count > 0:
            print("\nTest 4: Test query")
            results = collection.query(
                query_texts=["test query"],
                n_results=1
            )
            print(f"✅ Query successful: {results['ids']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if ChromaDB is running: docker ps | grep chroma")
        print("2. Verify host and port")
        print("3. Check firewall settings")
        return False

# Usage
debug_chromadb_connection()
```

**Fix Collection Issues**:

```python
def fix_chromadb_collection(collection_name="rag_documents"):
    """
    Fix or recreate ChromaDB collection
    """
    import chromadb
    
    client = chromadb.HttpClient()
    
    try:
        # Try to get existing collection
        collection = client.get_collection(collection_name)
        count = collection.count()
        
        print(f"Collection '{collection_name}' exists with {count} documents")
        
        # Option 1: Clear and rebuild
        choice = input("Clear and rebuild? (y/n): ")
        if choice.lower() == 'y':
            client.delete_collection(collection_name)
            print("✅ Collection deleted")
    
    except:
        print(f"Collection '{collection_name}' does not exist")
    
    # Create fresh collection
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}  # Cosine similarity
    )
    
    print(f"✅ Collection '{collection_name}' created")
    return collection
```

---

## Performance Debugging

### Profiling Code Execution

```python
import cProfile
import pstats
from pstats import SortKey

def profile_function(func):
    """
    Profile function execution
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = func(*args, **kwargs)
        
        profiler.disable()
        
        # Print stats
        stats = pstats.Stats(profiler)
        stats.strip_dirs()
        stats.sort_stats(SortKey.CUMULATIVE)
        
        print(f"\n{'='*60}")
        print(f"Profile: {func.__name__}")
        print(f"{'='*60}")
        stats.print_stats(20)  # Top 20 functions
        
        return result
    
    return wrapper

# Usage
@profile_function
def slow_retrieval_function(query):
    results = retriever.retrieve(query, top_k=100)
    ranked = reranker.rerank(query, results)
    return ranked
```

### Memory Profiling

```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    """
    Profile memory usage line-by-line
    """
    # Large list
    big_list = [i for i in range(1000000)]
    
    # Process
    processed = [x * 2 for x in big_list]
    
    return processed

# Run with: python -m memory_profiler script.py
```

### Identify Bottlenecks

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(name="Operation"):
    """
    Context manager to time code blocks
    """
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"{name} took {elapsed:.3f} seconds")

# Usage
def debug_retrieval_pipeline(query):
    """
    Identify bottlenecks in retrieval pipeline
    """
    with timer("Total Pipeline"):
        
        with timer("  Query Preprocessing"):
            processed_query = preprocess_query(query)
        
        with timer("  Vector Search"):
            vector_results = vector_search(processed_query, top_k=50)
        
        with timer("  BM25 Search"):
            bm25_results = bm25_search(processed_query, top_k=50)
        
        with timer("  Hybrid Ranking"):
            hybrid_results = hybrid_rank(vector_results, bm25_results)
        
        with timer("  Reranking"):
            final_results = rerank(processed_query, hybrid_results, top_k=5)
        
        with timer("  Context Building"):
            context = build_context(final_results)
        
        with timer("  LLM Generation"):
            response = generate_response(query, context)
    
    return response

# Example output:
#   Query Preprocessing took 0.005 seconds
#   Vector Search took 0.124 seconds
#   BM25 Search took 0.089 seconds
#   Hybrid Ranking took 0.012 seconds
#   Reranking took 0.456 seconds  <- BOTTLENECK!
#   Context Building took 0.008 seconds
#   LLM Generation took 1.234 seconds
# Total Pipeline took 1.928 seconds
```

---

## Vietnamese Text Processing Issues

### Problem: Tokenization Errors

```python
def debug_vietnamese_tokenization(text):
    """
    Debug Vietnamese tokenization issues
    """
    from underthesea import word_tokenize
    import logging
    
    logger = logging.getLogger(__name__)
    
    print(f"\n{'='*60}")
    print("Vietnamese Tokenization Debug")
    print(f"{'='*60}\n")
    
    print(f"Original text ({len(text)} chars):")
    print(f"{text}\n")
    
    try:
        # Test tokenization
        tokens = word_tokenize(text)
        print(f"✅ Tokenization successful")
        print(f"Token count: {len(tokens)}")
        print(f"Tokens: {tokens}\n")
        
        # Check for issues
        issues = []
        
        # Issue 1: Single character tokens (might indicate problem)
        single_chars = [t for t in tokens if len(t) == 1 and t not in '.,;:!?']
        if len(single_chars) > len(tokens) * 0.3:  # >30% single chars
            issues.append(f"Too many single-character tokens: {len(single_chars)}/{len(tokens)}")
        
        # Issue 2: Tokens with special characters
        special_tokens = [t for t in tokens if any(not c.isalnum() and c not in ' -_' for c in t)]
        if special_tokens:
            issues.append(f"Tokens with special chars: {special_tokens[:5]}")
        
        # Issue 3: Very long tokens (might be errors)
        long_tokens = [t for t in tokens if len(t) > 50]
        if long_tokens:
            issues.append(f"Unusually long tokens: {long_tokens}")
        
        if issues:
            print("⚠️ Potential issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ No issues detected")
        
        return tokens
        
    except Exception as e:
        print(f"❌ Tokenization failed: {str(e)}")
        logger.error("Tokenization error", exc_info=True)
        return None

# Usage
text = "Nghị định số 123/NĐ-CP ngày 15/10/2024 về việc thực hiện chính sách."
debug_vietnamese_tokenization(text)
```

### Problem: Legal Code Extraction Fails

```python
def debug_legal_code_extraction(text):
    """
    Debug legal document code extraction
    """
    import re
    
    print(f"\n{'='*60}")
    print("Legal Code Extraction Debug")
    print(f"{'='*60}\n")
    
    # Patterns for Vietnamese legal codes
    patterns = {
        'Nghị định': r'Nghị định số\s*(\d+/NĐ-[\w-]+)',
        'Quyết định': r'Quyết định số\s*(\d+/QĐ-[\w-]+)',
        'Thông tư': r'Thông tư số\s*(\d+/TT-[\w-]+)',
        'Luật': r'Luật\s+([\w\s]+)\s+số\s*(\d+/\d{4}/QH\d+)',
        'Generic số': r'Số\s*[:：]?\s*(\d+/[\w-]+)'
    }
    
    print(f"Text to analyze:\n{text}\n")
    
    all_codes = []
    for doc_type, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            print(f"✅ {doc_type}: {matches}")
            all_codes.extend(matches)
        else:
            print(f"❌ {doc_type}: No matches")
    
    if not all_codes:
        print("\n⚠️ No legal codes found!")
        print("\nDebugging suggestions:")
        print("1. Check if text contains legal codes")
        print("2. Verify Vietnamese encoding is correct")
        print("3. Check if preprocessing removed numbers/slashes")
        
        # Show character-level analysis
        print("\nCharacter analysis (first 200 chars):")
        for i, char in enumerate(text[:200]):
            if char.isdigit() or char in '/-':
                print(f"  Position {i}: '{char}'")
    else:
        print(f"\n✅ Total codes found: {len(all_codes)}")
    
    return all_codes

# Usage
text = """
Căn cứ Nghị định số 123/NĐ-CP ngày 15/10/2024 của Chính phủ;
Căn cứ Quyết định số 456/QĐ-TTg ngày 20/09/2024 của Thủ tướng Chính phủ;
"""
debug_legal_code_extraction(text)
```

---

## LLM Integration Issues

### Problem: API Errors

```python
def debug_llm_api_call(query, context, provider="anthropic"):
    """
    Debug LLM API calls with detailed logging
    """
    import logging
    import json
    
    logger = logging.getLogger(__name__)
    
    print(f"\n{'='*60}")
    print(f"LLM API Call Debug ({provider})")
    print(f"{'='*60}\n")
    
    print(f"Query: {query}")
    print(f"Context length: {len(context)} chars")
    print(f"Context preview: {context[:200]}...\n")
    
    if provider == "anthropic":
        from anthropic import Anthropic
        
        try:
            client = Anthropic()
            
            # Test API key
            print("Test 1: API Key validation")
            # Key is valid if client initializes
            print("✅ API key loaded\n")
            
            # Test message creation
            print("Test 2: Create message")
            
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": f"Context: {context}\n\nQuestion: {query}"
                }]
            )
            
            print(f"✅ Message created")
            print(f"Response length: {len(message.content[0].text)} chars")
            print(f"Token usage: {message.usage}")
            print(f"\nResponse preview:")
            print(message.content[0].text[:300])
            
            return message.content[0].text
            
        except Exception as e:
            print(f"❌ API call failed: {str(e)}")
            logger.error("LLM API error", exc_info=True)
            
            # Specific error handling
            if "authentication" in str(e).lower():
                print("\nTroubleshooting:")
                print("1. Check ANTHROPIC_API_KEY environment variable")
                print("2. Verify API key is valid")
                print("3. Check API quota/limits")
            elif "rate_limit" in str(e).lower():
                print("\nRate limit exceeded")
                print("1. Implement exponential backoff")
                print("2. Reduce request frequency")
            elif "overloaded" in str(e).lower():
                print("\nAPI overloaded - retry with backoff")
            
            return None

# Usage
debug_llm_api_call(
    "What is this document about?",
    "This is a Vietnamese legal document...",
    provider="anthropic"
)
```

### Problem: Poor Response Quality

```python
def debug_llm_response_quality(query, context, response):
    """
    Analyze LLM response quality
    """
    print(f"\n{'='*60}")
    print("LLM Response Quality Analysis")
    print(f"{'='*60}\n")
    
    # Check 1: Response length
    print(f"Response length: {len(response)} chars")
    if len(response) < 50:
        print("⚠️ Response too short")
    elif len(response) > 2000:
        print("⚠️ Response might be too verbose")
    else:
        print("✅ Response length OK")
    
    # Check 2: Vietnamese language
    vietnamese_chars = set('àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ')
    has_vietnamese = any(c.lower() in vietnamese_chars for c in response)
    
    if not has_vietnamese:
        print("❌ Response not in Vietnamese")
    else:
        print("✅ Vietnamese detected")
    
    # Check 3: Citations present
    import re
    citations = re.findall(r'\[Source \d+\]', response)
    if citations:
        print(f"✅ Found {len(citations)} citations")
    else:
        print("⚠️ No citations found")
    
    # Check 4: Repetition
    sentences = response.split('.')
    unique_sentences = len(set(sentences))
    if unique_sentences < len(sentences) * 0.8:
        print("⚠️ High repetition detected")
    else:
        print("✅ No excessive repetition")
    
    # Check 5: Relevance to query
    query_terms = set(query.lower().split())
    response_terms = set(response.lower().split())
    overlap = len(query_terms & response_terms)
    
    if overlap < len(query_terms) * 0.3:
        print(f"⚠️ Low query-response overlap: {overlap}/{len(query_terms)}")
    else:
        print(f"✅ Good query-response overlap: {overlap}/{len(query_terms)}")
    
    # Check 6: Uses context
    context_sample = ' '.join(context.split()[:50])
    context_terms = set(context_sample.lower().split())
    context_overlap = len(context_terms & response_terms)
    
    if context_overlap < 3:
        print("❌ Response doesn't seem to use provided context")
    else:
        print(f"✅ Response uses context: {context_overlap} overlapping terms")

# Usage
debug_llm_response_quality(query, context, response)
```

---

## File Upload Debugging

```python
def debug_file_upload(file_path):
    """
    Comprehensive file upload debugging
    """
    import os
    import mimetypes
    
    print(f"\n{'='*60}")
    print("File Upload Debug")
    print(f"{'='*60}\n")
    
    # Check 1: File exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    print(f"✅ File exists: {file_path}")
    
    # Check 2: File size
    size = os.path.getsize(file_path)
    size_mb = size / (1024 * 1024)
    print(f"File size: {size_mb:.2f} MB")
    
    if size == 0:
        print("❌ File is empty")
        return False
    elif size_mb > 100:
        print("⚠️ File is very large (>100MB)")
    else:
        print("✅ File size OK")
    
    # Check 3: File type
    mime_type, _ = mimetypes.guess_type(file_path)
    print(f"MIME type: {mime_type}")
    
    allowed_types = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'text/html'
    ]
    
    if mime_type in allowed_types:
        print("✅ File type supported")
    else:
        print(f"❌ File type not supported: {mime_type}")
    
    # Check 4: File readable
    try:
        with open(file_path, 'rb') as f:
            _ = f.read(100)
        print("✅ File is readable")
    except Exception as e:
        print(f"❌ Cannot read file: {str(e)}")
        return False
    
    # Check 5: Test parsing
    print("\nTest parsing:")
    try:
        from data_ingestion import UniversalTextExtractor
        extractor = UniversalTextExtractor()
        result = extractor.extract(file_path)
        
        print(f"✅ Parsing successful")
        print(f"Extracted text length: {len(result['text'])} chars")
        print(f"Text preview: {result['text'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Parsing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Usage
debug_file_upload('/path/to/document.pdf')
```

---

## Authentication Debugging

```python
def debug_jwt_token(token):
    """
    Debug JWT token issues
    """
    import jwt
    import json
    from datetime import datetime
    
    print(f"\n{'='*60}")
    print("JWT Token Debug")
    print(f"{'='*60}\n")
    
    print(f"Token: {token[:50]}...\n")
    
    try:
        # Decode without verification (to inspect)
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        print("Token payload:")
        print(json.dumps(decoded, indent=2))
        
        # Check expiration
        if 'exp' in decoded:
            exp_timestamp = decoded['exp']
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            now = datetime.now()
            
            print(f"\nExpiration: {exp_datetime}")
            print(f"Current time: {now}")
            
            if now > exp_datetime:
                print("❌ Token expired")
            else:
                remaining = exp_datetime - now
                print(f"✅ Token valid for {remaining}")
        
        # Now verify signature
        try:
            SECRET_KEY = os.getenv("JWT_SECRET_KEY")
            verified = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print("\n✅ Signature valid")
            return verified
        except jwt.InvalidSignatureError:
            print("\n❌ Invalid signature")
        except Exception as e:
            print(f"\n❌ Verification failed: {str(e)}")
        
    except jwt.DecodeError:
        print("❌ Token is malformed")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    return None

# Usage
debug_jwt_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
```

---

## Memory Leak Detection

```python
import tracemalloc
import gc

def debug_memory_leaks(func):
    """
    Detect memory leaks in function
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Start tracing
        tracemalloc.start()
        gc.collect()
        
        # Snapshot before
        snapshot_before = tracemalloc.take_snapshot()
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Force garbage collection
        gc.collect()
        
        # Snapshot after
        snapshot_after = tracemalloc.take_snapshot()
        
        # Compare
        top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
        
        print(f"\n{'='*60}")
        print(f"Memory Leak Analysis: {func.__name__}")
        print(f"{'='*60}\n")
        
        print("Top 10 memory allocations:")
        for stat in top_stats[:10]:
            print(f"{stat}")
        
        # Check for concerning patterns
        total_diff = sum(stat.size_diff for stat in top_stats)
        if total_diff > 10 * 1024 * 1024:  # 10MB
            print(f"\n⚠️ WARNING: Function allocated {total_diff / 1024**2:.2f} MB")
            print("This might indicate a memory leak")
        
        tracemalloc.stop()
        return result
    
    return wrapper

# Usage
@debug_memory_leaks
def potentially_leaky_function():
    # Your code here
    results = []
    for i in range(10000):
        results.append(large_object())
    return results
```

---

## Quick Debugging Checklist

```markdown
### When You Encounter an Error:

1. ☐ Read the error message completely
2. ☐ Check the stack trace for file/line number
3. ☐ Add print statements around error location
4. ☐ Check if error is reproducible
5. ☐ Isolate minimal failing example
6. ☐ Check logs (application + system)
7. ☐ Verify inputs are correct type/format
8. ☐ Check environment variables
9. ☐ Restart services (if applicable)
10. ☐ Search error message in this skill file
11. ☐ Check relevant system status (DB, GPU, etc.)
12. ☐ Try with smaller/simpler input
13. ☐ Check for recent code changes
14. ☐ Verify dependencies are installed
15. ☐ Ask for help with full context

### Before Asking for Help:

Provide:
- ✅ Full error message + stack trace
- ✅ Minimal code to reproduce
- ✅ Python version, OS, GPU info
- ✅ What you've tried already
- ✅ Expected vs actual behavior
- ✅ Relevant logs
```

---

## Emergency Debug Commands

```bash
# Check Python environment
python --version
pip list | grep -E "torch|transformers|chromadb|fastapi"

# Check GPU
nvidia-smi

# Check disk space
df -h

# Check memory
free -h

# Check PostgreSQL
sudo systemctl status postgresql
psql -U kb_admin -d chatbotR4 -c "SELECT version();"

# Check ChromaDB
docker ps | grep chroma
curl http://localhost:8000/api/v1/heartbeat

# Check logs
tail -f /var/log/rag_system.log
journalctl -u rag-api -f

# Check network
netstat -tuln | grep -E "8000|5432|6379"

# Python package conflicts
pip check

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

## Success Criteria

- ✅ Can diagnose 90% of errors within 15 minutes
- ✅ Comprehensive logging in place
- ✅ Error messages are actionable
- ✅ All edge cases have unit tests
- ✅ Performance bottlenecks identified
- ✅ Memory usage monitored
- ✅ Database queries optimized

## End of Skill File
