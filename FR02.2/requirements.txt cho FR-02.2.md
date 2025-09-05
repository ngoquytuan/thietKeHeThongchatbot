Dựa trên requirements của FR-02.2 và các quy tắc đã định, tôi sẽ tạo requirements.txt hoàn chỉnh cho API Quản trị Thống nhất:

## 📝 **requirements.txt cho FR-02.2**

```txt
# ========================
# FR-02.2 API QUẢN TRỊ THỐNG NHẤT
# Knowledge Assistant - Unified Management API
# Python 3.10.11 Required
# ========================

# ================================
# CORE WEB FRAMEWORK & SERVER
# ================================
fastapi==0.104.1                    # Main web framework
uvicorn[standard]==0.24.0           # ASGI server with performance extras
pydantic==2.4.2                     # Data validation and serialization
pydantic-settings==2.0.3            # Settings management
starlette==0.27.0                   # ASGI framework (FastAPI dependency)

# ================================
# DATABASE CONNECTIONS
# ================================
# PostgreSQL (Primary Database)
psycopg2-binary==2.9.7             # PostgreSQL adapter
asyncpg==0.29.0                    # Async PostgreSQL driver
sqlalchemy==2.0.23                 # ORM framework
alembic==1.12.1                    # Database migrations

# Redis (Cache Layer)
redis==5.0.1                       # Redis Python client
aioredis==2.0.1                    # Async Redis client

# ChromaDB (Vector Database) 
chromadb==0.4.15                   # Vector database for embeddings
sentence-transformers>=2.2.2       # Required embedding library (as per rules)

# ================================
# AUTHENTICATION & SECURITY
# ================================
python-jose[cryptography]==3.3.0   # JWT token handling
passlib[bcrypt]==1.7.4             # Password hashing
python-multipart==0.0.6            # Form data handling
cryptography==41.0.7               # Encryption utilities

# ================================
# HTTP CLIENT & ASYNC SUPPORT
# ================================
httpx==0.25.0                      # Modern HTTP client
aiofiles==23.2.1                   # Async file operations
asyncio==3.4.3                     # Async programming support

# ================================
# VIETNAMESE LANGUAGE PROCESSING
# ================================
# Required for Vietnamese text processing (as per rules)
pyvi>=0.1.1                        # Vietnamese text processing
underthesea==6.7.0                 # Vietnamese NLP toolkit

# ================================
# AI & EMBEDDINGS
# ================================
# GPU Support Required (as per rules)
torch>=2.0.0                       # PyTorch with GPU support
transformers==4.35.2               # Hugging Face transformers
numpy==1.24.3                      # Numerical computing
scipy==1.11.4                      # Scientific computing

# ================================
# API DOCUMENTATION & VALIDATION
# ================================
python-dotenv==1.0.0               # Environment variables
email-validator==2.1.0             # Email validation
phonenumbers==8.13.24              # Phone number validation

# ================================
# MONITORING & LOGGING
# ================================
loguru==0.7.2                      # Advanced logging
prometheus-client==0.19.0          # Metrics collection
structlog==23.2.0                  # Structured logging

# ================================
# UTILITIES & HELPERS
# ================================
python-dateutil==2.8.2             # Date manipulation
pytz==2023.3                       # Timezone handling
ujson==5.8.0                       # Fast JSON serialization
orjson==3.9.10                     # Faster JSON library
pyyaml==6.0.1                      # YAML configuration support

# ================================
# DEVELOPMENT & TESTING
# ================================
pytest==7.4.3                      # Testing framework
pytest-asyncio==0.21.1             # Async testing support
pytest-cov==4.1.0                  # Test coverage
httpx==0.25.0                      # HTTP testing client
faker==19.12.0                     # Test data generation

# ================================
# CODE QUALITY & FORMATTING
# ================================
black==23.9.1                      # Code formatting
isort==5.12.0                      # Import sorting
flake8==6.1.0                      # Linting
mypy==1.6.1                        # Type checking
bandit==1.7.5                      # Security analysis
safety==2.3.4                      # Dependency vulnerability check

# ================================
# PRODUCTION DEPLOYMENT
# ================================
gunicorn==21.2.0                   # Production WSGI server
supervisor==4.2.5                  # Process management
celery==5.3.4                      # Background task processing
redis==5.0.1                       # Celery broker (also used for caching)

# ================================
# API RATE LIMITING & CACHING
# ================================
slowapi==0.1.9                     # Rate limiting for FastAPI
cachetools==5.3.2                  # In-memory caching utilities

# ================================
# FILE PROCESSING & EXPORT
# ================================
openpyxl==3.1.2                    # Excel file processing
pypdf2==3.0.1                      # PDF processing
python-docx==0.8.11                # Word document processing
```

## 🔧 **requirements-dev.txt (Development Only)**

```txt
# ========================
# DEVELOPMENT DEPENDENCIES
# ========================
-r requirements.txt

# Development Tools
pre-commit==3.5.0                  # Git hooks
jupyter==1.0.0                     # Notebooks for testing
ipython==8.17.2                    # Enhanced Python shell

# Advanced Testing
pytest-mock==3.12.0                # Mocking for tests
pytest-xdist==3.3.1               # Parallel testing
pytest-benchmark==4.0.0            # Performance benchmarking
locust==2.17.0                     # Load testing

# Documentation
mkdocs==1.5.3                      # Documentation generator
mkdocs-material==9.4.7             # Material theme for docs
pdoc==14.1.0                       # API documentation generator

# Debugging & Profiling
py-spy==0.3.14                     # Python profiler
memory-profiler==0.61.0            # Memory usage profiler
line-profiler==4.1.1               # Line-by-line profiling
```

## 🐳 **requirements-docker.txt (Container Optimized)**

```txt
# ========================
# DOCKER OPTIMIZED DEPENDENCIES
# Smaller versions for container deployment
# ========================

# Core Framework (Alpine compatible)
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.4.2

# Database (compiled versions)
psycopg2==2.9.7                    # Non-binary version for Alpine
asyncpg==0.29.0
sqlalchemy==2.0.23
redis==5.0.1

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Vietnamese Processing
pyvi>=0.1.1
underthesea==6.7.0

# AI Models (CPU only for containers without GPU)
torch==2.0.0+cpu                   # CPU-only version
sentence-transformers>=2.2.2

# Utilities
python-dotenv==1.0.0
loguru==0.7.2
ujson==5.8.0
```

## 📦 **Installation Commands**

### **Development Environment:**
```bash
# Tạo virtual environment (Python 3.10.11 required)
python3.10 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify Vietnamese processing tools
python -c "import pyvi, underthesea; print('Vietnamese tools ready!')"

# Verify GPU support for torch
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### **Production Environment:**
```bash
# Production install (no dev dependencies)
pip install -r requirements.txt --no-dev
```

### **Docker Environment:**
```dockerfile
# Trong Dockerfile
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt
```

## ⚠️ **Lưu ý quan trọng:**

1. **Python Version**: Phải sử dụng Python 3.10.11 để hỗ trợ `underthesea` và `pyvi`
2. **GPU Support**: Torch được cài với GPU support theo quy tắc
3. **Vietnamese Processing**: `pyvi>=0.1.1` và `underthesea` required
4. **Embedding Model**: `sentence-transformers>=2.2.2` bắt buộc theo quy tắc
5. **Database**: PostgreSQL, Redis, ChromaDB support đầy đủ

## 🚀 **Next Steps:**

Sau khi cài requirements.txt, bạn có thể:
1. **Setup project structure** cho FastAPI
2. **Configure database connections** với thông tin từ FR-02.1
3. **Create API models** dựa trên existing schema
4. **Implement authentication** với JWT

**Bạn có muốn tôi tiếp tục tạo project structure và setup database connections không?**
