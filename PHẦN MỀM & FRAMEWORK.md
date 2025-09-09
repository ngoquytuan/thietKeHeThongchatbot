Dựa trên tất cả tài liệu handover và project knowledge, tôi sẽ lập danh sách đầy đủ các phần mềm, framework và công nghệ thực sự đã sử dụng trong dự án này:

# **📋 DANH SÁCH PHẦN MỀM & FRAMEWORK ĐÃ SỬ DỤNG TRONG DỰ ÁN**

## **🐍 PYTHON & FRAMEWORK BACKEND**

### **Python Core**
- **Python**: `3.9+` - `3.11` (khuyến nghị 3.11)
- **pip**: `23.0+`
- **venv**: Python virtual environment
- **Poetry**: `1.5+` (optional, cho dependency management)

### **Web Frameworks**
- **FastAPI**: `0.104.1` - Primary REST API framework
- **Uvicorn**: `0.24.0` - ASGI server với `[standard]` extras
- **Streamlit**: `1.28.2` - Web UI cho FR-03.1 tool

### **Data Validation & Schema**
- **Pydantic**: `2.4.2` - `2.5.0` - Data validation và serialization
- **Pydantic-settings**: `2.0.3` - Settings management

## **🗄️ DATABASES & STORAGE**

### **Relational Database**
- **PostgreSQL**: `13+` - `15` - Primary database
- **asyncpg**: `0.29.0` - Async PostgreSQL driver
- **psycopg2-binary**: `2.9.7` - PostgreSQL adapter

### **Vector Database**
- **ChromaDB**: `0.4.15` - `1.0.0` - Vector embeddings storage
- **FAISS**: `1.7.4` (`faiss-cpu` hoặc `faiss-gpu`) - Vector similarity search

### **Cache & Session Store**
- **Redis**: `6+` - `7` - Caching và session management
- **Redis Python**: `5.0.1` - Redis client

### **Search Engine**
- **Elasticsearch**: `8.10.1` - `8.11.0` - Full-text search
- **Whoosh**: `2.7.4` - Lightweight search alternative

## **🤖 AI/ML & NLP**

### **LLM Integration**
- **OpenAI**: `1.0.0` - `1.3.5` - GPT models API
- **Anthropic**: `0.8.0` - Claude API
- **Google AI**: Google Gemini API integration
- **Grok**: X.AI Grok API integration
- **OpenRouter**: Multi-LLM provider

### **Embedding Models**
- **sentence-transformers**: `2.2.2` - Embedding model framework
- **transformers**: `4.35.2` - Hugging Face transformers
- **torch**: `2.0.0+cu118` - `2.1.1` - PyTorch với CUDA support
- **tiktoken**: `0.5.0` - `0.5.1` - Token counting

### **Vietnamese NLP**
- **underthesea**: `6.7.0` - Vietnamese NLP toolkit
- **pyvi**: `0.1.1+` - Vietnamese text processing
- **NLTK**: `3.8.1` - Natural language toolkit
- **spaCy**: `3.7.2` - Advanced NLP

### **ML Utilities**
- **numpy**: `1.24.3` - Numerical computing
- **pandas**: `2.0.3` - Data manipulation
- **scikit-learn**: `1.3.2` - Machine learning utilities

## **🔐 AUTHENTICATION & SECURITY**

### **Authentication**
- **python-jose**: `3.3.0` với `[cryptography]` - JWT handling
- **passlib**: `1.7.4` với `[bcrypt]` - Password hashing
- **python-multipart**: `0.0.6` - Form data handling
- **cryptography**: `3.4.8+` - Cryptographic operations

## **🌐 HTTP & API**

### **HTTP Clients**
- **httpx**: `0.25.0` - Async HTTP client
- **aiofiles**: `23.2.1` - Async file operations

### **Template Engines**
- **Jinja2**: `3.1.0+` - Template engine cho synthesis

## **📊 DATA PROCESSING**

### **Document Processing**
- **langchain**: `0.0.335` - `0.1.0+` - LLM orchestration
- **langchain-community**: `0.0.5` - Community extensions
- **langchain-text-splitters**: `0.0.1` - Text chunking
- **PyPDF2**: `3.0.1` - PDF processing
- **python-docx**: `1.1.0` - Word document processing
- **python-pptx**: `0.6.23` - PowerPoint processing

## **📈 MONITORING & LOGGING**

### **Logging**
- **loguru**: `0.7.2` - Advanced logging
- **structlog**: `21.1.0+` - `23.0.0` - Structured logging

### **Metrics & Monitoring**
- **prometheus-client**: `0.11.0+` - `0.17.0` - Metrics collection

## **🐳 CONTAINERIZATION & DEPLOYMENT**

### **Container Technology**
- **Docker**: `20.10+` - Containerization
- **Docker Compose**: `2.0+` - Multi-container orchestration
- **Docker Desktop**: `4.20+` - Development environment

### **Container Images Used**
- **postgres**: `13` - `15` - PostgreSQL database
- **redis**: `6-alpine` - `7-alpine` - Redis cache
- **nginx**: Latest - Reverse proxy (production)
- **adminer**: Latest - Database administration

## **🧪 TESTING & QUALITY**

### **Testing Frameworks**
- **pytest**: `7.4.3` - Testing framework
- **pytest-asyncio**: `0.21.1` - Async testing support
- **pytest-cov**: `4.0.0+` - Coverage testing

### **Code Quality**
- **black**: `23.9.1` - `23.11.0` - Code formatting
- **isort**: `5.12.0` - Import sorting
- **flake8**: `6.1.0` - Linting
- **mypy**: `1.6.1` - Type checking
- **ruff**: `0.0.280+` - Fast linter
- **pre-commit**: `3.3.0+` - Git hooks

## **🔧 UTILITIES & HELPERS**

### **Configuration**
- **python-dotenv**: `1.0.0` - Environment variables
- **tenacity**: `8.2.0` - `8.2.3` - Retry mechanisms

### **CLI Tools**
- **typer**: `0.9.0` - CLI framework
- **alembic**: `1.7.1+` - `1.12.1` - Database migrations

### **Database ORM**
- **SQLAlchemy**: `1.4.23+` - `2.0.23` với `[asyncio]` - Database ORM

## **🌍 FRONTEND (Planned/Partial)**

### **Next.js Stack** (cho future UI development)
- **Node.js**: `18.17.0+` LTS
- **Next.js**: `13.4+` - React framework
- **React**: `18.2+` - UI library
- **TypeScript**: `5.0+` - Type safety
- **Tailwind CSS**: `3.3+` - Styling

### **UI Libraries** (planned)
- **Ant Design**: `5.0.0` - Component library
- **Socket.IO Client**: `4.7+` - Real-time communication

## **🛠️ DEVELOPMENT TOOLS**

### **IDEs & Editors**
- **Visual Studio Code** - Primary IDE
- **PyCharm Professional** - Alternative IDE
- **Cursor AI** - AI-assisted development

### **VS Code Extensions Used**
- Python Extension Pack
- Docker Extension
- PostgreSQL Extension
- REST Client/Thunder Client
- GitLens
- Prettier - Code formatter
- ESLint

### **Version Control**
- **Git**: `2.30+` - `2.40+`
- **GitHub CLI** - Git repository management

## **📊 PRODUCTION INFRASTRUCTURE**

### **Orchestration**
- **Kubernetes**: Planned для production deployment
- **Nginx**: Reverse proxy và load balancer

### **Monitoring Stack**
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboard
- **Jaeger**: Distributed tracing

## **🎯 SUMMARY BY MODULE**

| Module | Primary Technologies |
|--------|---------------------|
| **FR-01** (Embedding) | `sentence-transformers`, `torch`, `underthesea`, `pyvi` |
| **FR-02** (Database) | `PostgreSQL`, `Redis`, `ChromaDB`, `FastAPI`, `SQLAlchemy` |
| **FR-03.1** (Raw-to-Clean) | `Streamlit`, `PyPDF2`, `python-docx`, `underthesea` |
| **FR-03.3** (Data Ingestion) | `FastAPI`, `ChromaDB`, `PostgreSQL`, `tiktoken`, `langchain` |
| **FR-04.1** (Retrieval) | `ChromaDB`, `Elasticsearch`, `FAISS`, `sentence-transformers` |
| **FR-04.2** (Synthesis) | `Jinja2`, `langchain`, `tiktoken`, `FastAPI` |
| **FR-04.3** (Generation) | `OpenAI`, `Anthropic`, `Google AI`, `FastAPI` |

## **📋 REQUIREMENTS.TXT CONSOLIDATION**

Tổng hợp file requirements.txt chính cho toàn dự án:

```txt
# Core Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
streamlit==1.28.2

# Data Validation
pydantic==2.5.0
pydantic-settings==2.0.3

# Databases
psycopg2-binary==2.9.7
asyncpg==0.29.0
sqlalchemy[asyncio]==2.0.23
alembic==1.12.1
redis==5.0.1

# Vector & Search
chromadb==1.0.0
sentence-transformers==2.2.2
transformers==4.35.2
torch>=2.0.0+cu118
faiss-cpu==1.7.4
elasticsearch==8.11.0

# LLM Integration
openai==1.3.5
anthropic==0.8.0
langchain==0.1.0
langchain-community==0.0.5
tiktoken==0.5.1

# Vietnamese NLP
underthesea==6.7.0
pyvi>=0.1.1

# Document Processing
PyPDF2==3.0.1
python-docx==1.1.0
python-pptx==0.6.23

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# HTTP & Async
httpx==0.25.0
aiofiles==23.2.1

# Templates & Utils
jinja2>=3.1.0
python-dotenv==1.0.0
loguru==0.7.2
typer==0.9.0
tenacity==8.2.3

# ML Utilities
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov>=4.0.0

# Code Quality
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.6.1

# Monitoring
prometheus-client>=0.17.0
structlog>=23.0.0
```

**📌 Lưu ý**: Dự án này sử dụng chủ yếu **Python ecosystem** với **FastAPI** làm backbone, **PostgreSQL + ChromaDB** làm dual database, và **Docker** cho deployment. Frontend với **Next.js/React** vẫn đang trong giai đoạn planning cho Phase 4.
