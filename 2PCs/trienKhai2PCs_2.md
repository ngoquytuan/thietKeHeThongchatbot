Tuyệt vời! Việc chia hệ thống ra 2 PC là strategy rất thông minh. Tôi sẽ phân tích và đưa ra phương án chia module tối ưu:## **🏗️ PHƯƠNG ÁN CHIA MODULE TỐI ỨU CHO 2 PC**

Dựa trên yêu cầu GPU và database, đây là phân chia chi tiết:

### **🖥️ PC1 - UBUNTU (DATABASE & INFRASTRUCTURE SERVER)**

```mermaid
graph TB
    subgraph "💾 PC1 - Ubuntu Database Server"
        subgraph "📊 Infrastructure Tier (FR-2x)"
            DB[🗄️ PostgreSQL 15<br/>Unified Database]
            Cache[🔴 Redis Cluster<br/>Session + Cache]
            Vector[📊 ChromaDB<br/>Vector Storage]
            Storage[📁 File Storage<br/>Documents + Backups]
        end
        
        subgraph "🛠️ Platform Services (FR-5x)"
            Monitor[📈 Monitoring Stack<br/>Prometheus + Grafana]
            Admin[🔧 Admin Tools<br/>FR-08]
            Analytics[📊 Analytics API<br/>FR-07]
            Backup[💾 Backup Services<br/>Automated]
        end
        
        subgraph "🌐 Web Services"
            Gateway[🌐 API Gateway<br/>nginx + load balancer]
            Auth[🔐 Authentication<br/>FR-06]
            WebUI[💻 Web Interface<br/>FR-05]
        end
    end
    
    Internet[🌍 Internet] --> Gateway
    Gateway --> Auth
    Gateway --> WebUI
    Gateway --> Analytics
```

**Chi tiết triển khai PC1:**

#### **🔧 Docker Compose Configuration:**
```yaml
# docker-compose.pc1.yml
version: '3.8'
services:
  # Infrastructure Services
  postgres:
    image: postgres:15-alpine
    container_name: rag_postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: knowledge_base_unified
      POSTGRES_USER: kb_admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'

  redis:
    image: redis:7-alpine
    container_name: rag_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --maxmemory 4gb --maxmemory-policy allkeys-lru

  chromadb:
    image: ghcr.io/chroma-core/chroma:latest
    container_name: rag_chromadb
    ports:
      - "8000:8000"
    volumes:
      - chromadb_data:/chroma/chroma
    environment:
      CHROMA_SERVER_HOST: 0.0.0.0

  # Platform Services
  monitoring:
    build: ./monitoring
    container_name: rag_monitoring
    ports:
      - "9090:9090"  # Prometheus
      - "3000:3000"  # Grafana
    volumes:
      - monitoring_data:/data

  admin_tools:
    build: ./FR-08
    container_name: rag_admin
    ports:
      - "8002:8002"
    environment:
      DATABASE_URL: postgresql://kb_admin:${POSTGRES_PASSWORD}@postgres:5432/knowledge_base_unified
      REDIS_URL: redis://redis:6379

  analytics:
    build: ./FR-07
    container_name: rag_analytics
    ports:
      - "8003:8003"
    depends_on:
      - postgres
      - redis

  # Web Services
  auth_service:
    build: ./FR-06
    container_name: rag_auth
    ports:
      - "8001:8001"
    environment:
      DATABASE_URL: postgresql://kb_admin:${POSTGRES_PASSWORD}@postgres:5432/knowledge_base_unified
      REDIS_URL: redis://redis:6379

  web_interface:
    build: ./FR-05
    container_name: rag_web
    ports:
      - "3001:3000"
    environment:
      API_BASE_URL: http://localhost:8080

  nginx:
    image: nginx:alpine
    container_name: rag_gateway
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - auth_service
      - analytics
      - web_interface

volumes:
  postgres_data:
  redis_data:
  chromadb_data:
  monitoring_data:
```

### **⚡ PC2 - GPU SERVER (AI PROCESSING & RAG CORE)**

```mermaid
graph TB
    subgraph "🚀 PC2 - GPU Processing Server"
        subgraph "🤖 AI Processing (GPU Accelerated)"
            Embedding[🔢 Embedding Service<br/>Qwen Model + GPU]
            LLM[🧠 LLM Services<br/>Local Models]
            NLP[🇻🇳 Vietnamese NLP<br/>pyvi + underthesea]
        end
        
        subgraph "📥 Data Pipeline (FR-3x)"
            DataPrep[📋 Data Preparation<br/>FR-03.1]
            QualityControl[✅ Quality Control<br/>FR-03.2]
            Ingestion[📥 Data Ingestion<br/>FR-03.3]
        end
        
        subgraph "🤖 RAG Core Engine (FR-4x)"
            Retrieval[🔍 Retrieval Router<br/>FR-04.1]
            Synthesis[🔧 Synthesis Engine<br/>FR-04.2]
            Generation[💬 Generation Engine<br/>FR-04.3]
            RAGAPI[🌐 RAG API<br/>FR-04.4]
        end
    end
    
    Network[🌐 Network to PC1] --> RAGAPI
```

**Chi tiết triển khai PC2:**

#### **🔧 Docker Compose Configuration:**
```yaml
# docker-compose.pc2.yml
version: '3.8'
services:
  # AI Processing Services (GPU)
  embedding_service:
    build: 
      context: ./embedding-service
      dockerfile: Dockerfile.gpu
    container_name: rag_embedding
    ports:
      - "8010:8000"
    environment:
      MODEL_NAME: Qwen/Qwen3-Embedding-0.6B
      DEVICE: cuda
      BATCH_SIZE: 32
      MAX_LENGTH: 512
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - model_cache:/root/.cache

  vietnamese_nlp:
    build: ./nlp-service
    container_name: rag_nlp
    ports:
      - "8011:8000"
    environment:
      GPU_ENABLED: "true"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Data Pipeline Services
  data_preparation:
    build: ./FR-03.1
    container_name: rag_data_prep
    ports:
      - "8020:8000"
    volumes:
      - documents_processing:/tmp/processing

  quality_control:
    build: ./FR-03.2
    container_name: rag_quality
    ports:
      - "8021:8000"
    environment:
      GPU_ENABLED: "true"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  data_ingestion:
    build: ./FR-03.3
    container_name: rag_ingestion
    ports:
      - "8022:8000"
    environment:
      DATABASE_URL: postgresql://kb_admin:${POSTGRES_PASSWORD}@${PC1_IP}:5432/knowledge_base_unified
      CHROMADB_URL: http://${PC1_IP}:8000
      EMBEDDING_SERVICE_URL: http://embedding_service:8000

  # RAG Core Services
  retrieval_router:
    build: ./FR-04.1
    container_name: rag_retrieval
    ports:
      - "8030:8000"
    environment:
      DATABASE_URL: postgresql://kb_admin:${POSTGRES_PASSWORD}@${PC1_IP}:5432/knowledge_base_unified
      CHROMADB_URL: http://${PC1_IP}:8000

  synthesis_engine:
    build: ./FR-04.2
    container_name: rag_synthesis
    ports:
      - "8031:8000"

  generation_engine:
    build: ./FR-04.3
    container_name: rag_generation
    ports:
      - "8032:8000"
    environment:
      GPU_ENABLED: "true"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  rag_api:
    build: ./FR-04.4
    container_name: rag_api
    ports:
      - "8080:8000"
    environment:
      RETRIEVAL_URL: http://retrieval_router:8000
      SYNTHESIS_URL: http://synthesis_engine:8000
      GENERATION_URL: http://generation_engine:8000
      AUTH_SERVICE_URL: http://${PC1_IP}:8001

volumes:
  model_cache:
  documents_processing:
```

## **🔗 NETWORK & INTEGRATION SETUP**

### **📡 Network Configuration:**
```yaml
# .env.network
PC1_IP=192.168.1.95  # IP của PC1 (Database server,Ubuntu)
PC2_IP=192.168.1.10  # IP của PC2 (GPU server, windows)

# PC1 exposes:
# - PostgreSQL: 5432
# - Redis: 6379  
# - ChromaDB: 8000
# - Web Interface: 80/443
# - Admin APIs: 8001-8003

# PC2 exposes:
# - RAG API: 8080 (main endpoint)
# - AI Services: 8010-8032
```

### **⚙️ System Requirements:**

| **Component** | **PC1 (Ubuntu)** | **PC2 (GPU)** |
|---------------|-------------------|---------------|
| **CPU** | 8+ cores | 8+ cores |
| **RAM** | 32GB+ | 32GB+ |
| **Storage** | 1TB SSD | 500GB SSD |
| **GPU** | Integrated/Optional | RTX 4080/4090+ |
| **Network** | Gigabit Ethernet | Gigabit Ethernet |
| **OS** | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS hoặc Windows + WSL2 |

### **🚀 Deployment Commands:**

```bash
# PC1 - Start infrastructure
cd pc1-deployment
docker-compose -f docker-compose.pc1.yml up -d

# PC2 - Start AI services  
cd pc2-deployment
docker-compose -f docker-compose.pc2.yml up -d

# Verify cross-PC connectivity
curl http://192.168.1.100:5432  # Test database
curl http://192.168.1.101:8080/health  # Test RAG API
```

### **📊 Load Balancing Strategy:**

```mermaid
graph LR
    Users[👥 Users] --> LB[⚖️ Load Balancer<br/>PC1]
    LB --> Web[💻 Web UI<br/>PC1]
    LB --> API[🌐 RAG API<br/>PC2]
    
    API --> GPU1[🚀 Embedding<br/>PC2 GPU]
    API --> GPU2[🤖 Generation<br/>PC2 GPU]
    API --> GPU3[🇻🇳 NLP<br/>PC2 GPU]
    
    API --> DB[🗄️ Database<br/>PC1]
    API --> Cache[🔴 Redis<br/>PC1]
```

## **✅ ADVANTAGES CỦA KIẾN TRÚC NÀY:**

1. **GPU Optimization**: Tất cả AI workloads trên PC2 với GPU mạnh
2. **Database Performance**: PC1 tập trung vào I/O và storage
3. **Scalability**: Có thể thêm PC2 khác để load balancing
4. **Resource Isolation**: Database và AI processing không tranh tài nguyên
5. **Development Friendly**: Có thể dev/test từng PC độc lập
6. **Cost Effective**: Tận dụng tối đa GPU trên PC2, storage trên PC1

**Kết quả: Setup này sẽ cho performance tối ưu với GPU acceleration cho AI tasks và database performance ổn định!**
---
Tôi sẽ tạo cho bạn bộ file môi trường hoàn chỉnh để đảm bảo tính nhất quán giữa 2 PC và tất cả modules:

## **🌐 GLOBAL ENVIRONMENT CONFIGURATION**

### **📁 `.env.global` - Shared Configuration**

```env
# =============================================================================
# GLOBAL CONFIGURATION FOR VIETNAMESE RAG CHATBOT SYSTEM
# =============================================================================
# Project: Vietnamese Knowledge Assistant RAG System
# Architecture: 2-PC Deployment (PC1: Database, PC2: GPU Processing)
# Date: $(date '+%Y-%m-%d')
# =============================================================================

# -----------------------------------------------------------------------------
# NETWORK CONFIGURATION
# -----------------------------------------------------------------------------
PC1_IP=192.168.1.100
PC2_IP=192.168.1.101
DOMAIN_NAME=chatbot.local
EXTERNAL_DOMAIN=your-domain.com

# -----------------------------------------------------------------------------
# STANDARD CREDENTIALS (ALL SERVICES)
# -----------------------------------------------------------------------------
STANDARD_USERNAME=chatbotAIhome
STANDARD_PASSWORD=chatbotAI601

# Database Master Credentials
DB_MASTER_USER=chatbotAIhome
DB_MASTER_PASSWORD=chatbotAI601
DB_READONLY_USER=chatbotAI_readonly
DB_READONLY_PASSWORD=chatbotAI601_readonly

# -----------------------------------------------------------------------------
# SECURITY CONFIGURATION
# -----------------------------------------------------------------------------
# JWT Configuration
JWT_SECRET_KEY=chatbotAI601_jwt_secret_key_vietnamese_rag_system_2024
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption Keys
ENCRYPTION_KEY=chatbotAI601_encryption_key_for_vietnamese_system
API_SECRET_KEY=chatbotAI601_api_secret_key_2024_vietnamese_rag

# -----------------------------------------------------------------------------
# PORT ALLOCATION MATRIX
# -----------------------------------------------------------------------------
# Infrastructure Services (PC1)
POSTGRES_PORT=5432
REDIS_PORT=6379
CHROMADB_PORT=8000

# Web & API Gateway (PC1)
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
API_GATEWAY_PORT=8080

# Platform Services (PC1) - 8001-8009
AUTH_SERVICE_PORT=8001
ADMIN_TOOLS_PORT=8002
ANALYTICS_API_PORT=8003
WEB_INTERFACE_PORT=8004
MONITORING_PROMETHEUS_PORT=8005
MONITORING_GRAFANA_PORT=8006
BACKUP_SERVICE_PORT=8007
FILE_SERVICE_PORT=8008
HEALTH_CHECK_PORT=8009

# AI Processing Services (PC2) - 8010-8019
EMBEDDING_SERVICE_PORT=8010
VIETNAMESE_NLP_PORT=8011
LLM_SERVICE_PORT=8012
MODEL_MANAGER_PORT=8013

# Data Pipeline Services (PC2) - 8020-8029
DATA_PREPARATION_PORT=8020
QUALITY_CONTROL_PORT=8021
DATA_INGESTION_PORT=8022

# RAG Core Services (PC2) - 8030-8039
RETRIEVAL_ROUTER_PORT=8030
SYNTHESIS_ENGINE_PORT=8031
GENERATION_ENGINE_PORT=8032
RAG_API_MAIN_PORT=8033

# Development & Testing - 9000-9099
DEV_API_PORT=9000
TEST_API_PORT=9001
MOCK_SERVICES_PORT=9002

# -----------------------------------------------------------------------------
# DATABASE CONFIGURATION
# -----------------------------------------------------------------------------
# PostgreSQL Unified Database
POSTGRES_DB=vietnamese_knowledge_base
POSTGRES_HOST=${PC1_IP}
POSTGRES_USER=${DB_MASTER_USER}
POSTGRES_PASSWORD=${DB_MASTER_PASSWORD}
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
ASYNC_DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# Redis Configuration
REDIS_HOST=${PC1_IP}
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}
REDIS_PASSWORD=${STANDARD_PASSWORD}

# ChromaDB Configuration
CHROMADB_HOST=${PC1_IP}
CHROMADB_URL=http://${CHROMADB_HOST}:${CHROMADB_PORT}
CHROMADB_COLLECTION=vietnamese_knowledge_v1
CHROMADB_AUTH_TOKEN=${STANDARD_PASSWORD}

# -----------------------------------------------------------------------------
# AI MODELS CONFIGURATION
# -----------------------------------------------------------------------------
# Embedding Model
EMBEDDING_MODEL_NAME=Qwen/Qwen3-Embedding-0.6B
EMBEDDING_DIMENSION=1024
EMBEDDING_DEVICE=cuda
EMBEDDING_BATCH_SIZE=32
EMBEDDING_MAX_LENGTH=512

# Vietnamese NLP
VIETNAMESE_LANGUAGE=vi
ENABLE_PYVI=true
ENABLE_UNDERTHESEA=true
NLP_CACHE_SIZE=10000

# Generation Models
PRIMARY_LLM_MODEL=gpt-4-turbo-preview
FALLBACK_LLM_MODEL=gpt-3.5-turbo
LOCAL_LLM_MODEL=Qwen/Qwen2-7B-Instruct

# -----------------------------------------------------------------------------
# ENVIRONMENT SETTINGS
# -----------------------------------------------------------------------------
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
TIMEZONE=Asia/Ho_Chi_Minh

# Performance Settings
MAX_WORKERS=8
CONNECTION_POOL_SIZE=20
CACHE_TTL=3600
REQUEST_TIMEOUT=30

# -----------------------------------------------------------------------------
# MONITORING & ALERTING
# -----------------------------------------------------------------------------
PROMETHEUS_URL=http://${PC1_IP}:${MONITORING_PROMETHEUS_PORT}
GRAFANA_URL=http://${PC1_IP}:${MONITORING_GRAFANA_PORT}
GRAFANA_ADMIN_USER=${STANDARD_USERNAME}
GRAFANA_ADMIN_PASSWORD=${STANDARD_PASSWORD}

# Alert Thresholds
CPU_THRESHOLD=80.0
MEMORY_THRESHOLD=85.0
DISK_THRESHOLD=90.0
RESPONSE_TIME_THRESHOLD=2000

# -----------------------------------------------------------------------------
# BACKUP CONFIGURATION
# -----------------------------------------------------------------------------
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
BACKUP_LOCATION=/app/backups
S3_BACKUP_ENABLED=false

# -----------------------------------------------------------------------------
# CORS & SECURITY
# -----------------------------------------------------------------------------
ALLOWED_ORIGINS=http://localhost:3000,http://${PC1_IP}:${WEB_INTERFACE_PORT},http://${DOMAIN_NAME}
ALLOWED_HOSTS=${PC1_IP},${PC2_IP},localhost,127.0.0.1,${DOMAIN_NAME}
CORS_ALLOW_CREDENTIALS=true
```

## **💻 PC1 ENVIRONMENT FILES**

### **📁 `.env.pc1` - Database & Infrastructure Server**

```env
# =============================================================================
# PC1 ENVIRONMENT - UBUNTU DATABASE & INFRASTRUCTURE SERVER
# =============================================================================
# Load global config first, then override specific settings
include .env.global

# -----------------------------------------------------------------------------
# PC1 SPECIFIC CONFIGURATION
# -----------------------------------------------------------------------------
SERVER_ROLE=database_infrastructure
SERVER_IP=${PC1_IP}
SERVER_NAME=pc1-database-server

# -----------------------------------------------------------------------------
# POSTGRESQL CONFIGURATION
# -----------------------------------------------------------------------------
POSTGRES_INITDB_ARGS="--encoding=UTF8 --locale=C"
POSTGRES_SHARED_PRELOAD_LIBRARIES=pg_stat_statements
POSTGRES_MAX_CONNECTIONS=200
POSTGRES_SHARED_BUFFERS=2GB
POSTGRES_EFFECTIVE_CACHE_SIZE=6GB
POSTGRES_WORK_MEM=64MB
POSTGRES_MAINTENANCE_WORK_MEM=512MB

# Database Extensions
POSTGRES_EXTENSIONS=vector,pg_trgm,unaccent,pg_stat_statements

# -----------------------------------------------------------------------------
# REDIS CONFIGURATION
# -----------------------------------------------------------------------------
REDIS_MAXMEMORY=4gb
REDIS_MAXMEMORY_POLICY=allkeys-lru
REDIS_SAVE="900 1 300 10 60 10000"
REDIS_APPENDONLY=yes
REDIS_APPENDFSYNC=everysec

# -----------------------------------------------------------------------------
# CHROMADB CONFIGURATION
# -----------------------------------------------------------------------------
CHROMA_SERVER_HOST=0.0.0.0
CHROMA_SERVER_HTTP_PORT=${CHROMADB_PORT}
CHROMA_PERSIST_DIRECTORY=/chroma/chroma
CHROMA_SERVER_CORS_ALLOW_ORIGINS=["http://${PC2_IP}:*","http://localhost:*"]

# -----------------------------------------------------------------------------
# WEB SERVICES CONFIGURATION (PC1)
# -----------------------------------------------------------------------------
# Authentication Service
AUTH_DATABASE_URL=${DATABASE_URL}
AUTH_REDIS_URL=${REDIS_URL}
AUTH_JWT_SECRET_KEY=${JWT_SECRET_KEY}

# Analytics Service
ANALYTICS_DATABASE_URL=${DATABASE_URL}
ANALYTICS_REDIS_URL=${REDIS_URL}
ANALYTICS_CACHE_ENABLED=true
ANALYTICS_EXPORT_PATH=/app/exports

# Admin Tools
ADMIN_DATABASE_URL=${DATABASE_URL}
ADMIN_REDIS_URL=${REDIS_URL}
ADMIN_CHROMADB_URL=${CHROMADB_URL}
ADMIN_BACKUP_ENABLED=true

# Web Interface
WEB_API_BASE_URL=http://${PC2_IP}:${RAG_API_MAIN_PORT}
WEB_AUTH_SERVICE_URL=http://localhost:${AUTH_SERVICE_PORT}
WEB_ANALYTICS_URL=http://localhost:${ANALYTICS_API_PORT}

# -----------------------------------------------------------------------------
# NGINX CONFIGURATION
# -----------------------------------------------------------------------------
NGINX_WORKER_PROCESSES=auto
NGINX_WORKER_CONNECTIONS=1024
NGINX_CLIENT_MAX_BODY_SIZE=100M
NGINX_PROXY_TIMEOUT=60s

# SSL Configuration (if enabled)
SSL_CERTIFICATE_PATH=/etc/nginx/ssl/cert.pem
SSL_PRIVATE_KEY_PATH=/etc/nginx/ssl/key.pem

# -----------------------------------------------------------------------------
# MONITORING CONFIGURATION
# -----------------------------------------------------------------------------
PROMETHEUS_RETENTION_TIME=15d
PROMETHEUS_SCRAPE_INTERVAL=15s
PROMETHEUS_EVALUATION_INTERVAL=15s

GRAFANA_SECURITY_ADMIN_USER=${STANDARD_USERNAME}
GRAFANA_SECURITY_ADMIN_PASSWORD=${STANDARD_PASSWORD}
GRAFANA_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel

# -----------------------------------------------------------------------------
# BACKUP CONFIGURATION (PC1)
# -----------------------------------------------------------------------------
POSTGRES_BACKUP_PATH=/backups/postgres
REDIS_BACKUP_PATH=/backups/redis
CHROMADB_BACKUP_PATH=/backups/chromadb
BACKUP_COMPRESSION=gzip
BACKUP_ENCRYPTION_ENABLED=true

# -----------------------------------------------------------------------------
# RESOURCE LIMITS (PC1)
# -----------------------------------------------------------------------------
POSTGRES_MEMORY_LIMIT=8g
POSTGRES_CPUS_LIMIT=4
REDIS_MEMORY_LIMIT=4g
REDIS_CPUS_LIMIT=2
CHROMADB_MEMORY_LIMIT=4g
CHROMADB_CPUS_LIMIT=2

# -----------------------------------------------------------------------------
# LOG CONFIGURATION
# -----------------------------------------------------------------------------
LOG_PATH=/var/log/vietnamese-rag
LOG_ROTATION_SIZE=100MB
LOG_RETENTION_DAYS=7
STRUCTURED_LOGGING=true
```

### **📁 `.env.pc1.docker-compose` - PC1 Docker Compose Override**

```env
# Docker Compose specific overrides for PC1
COMPOSE_PROJECT_NAME=vietnamese-rag-pc1
COMPOSE_HTTP_TIMEOUT=120

# Volume mappings
POSTGRES_DATA_PATH=./data/postgres
REDIS_DATA_PATH=./data/redis
CHROMADB_DATA_PATH=./data/chromadb
BACKUP_DATA_PATH=./data/backups
LOG_DATA_PATH=./data/logs

# Network configuration
DOCKER_NETWORK_NAME=vietnamese-rag-network
DOCKER_SUBNET=172.20.0.0/16
PC1_DOCKER_IP=172.20.0.10
```

## **⚡ PC2 ENVIRONMENT FILES**

### **📁 `.env.pc2` - GPU Processing Server**

```env
# =============================================================================
# PC2 ENVIRONMENT - GPU AI PROCESSING SERVER  
# =============================================================================
# Load global config first, then override specific settings
include .env.global

# -----------------------------------------------------------------------------
# PC2 SPECIFIC CONFIGURATION
# -----------------------------------------------------------------------------
SERVER_ROLE=gpu_ai_processing
SERVER_IP=${PC2_IP}
SERVER_NAME=pc2-gpu-server

# -----------------------------------------------------------------------------
# GPU CONFIGURATION
# -----------------------------------------------------------------------------
CUDA_VISIBLE_DEVICES=0
GPU_MEMORY_FRACTION=0.9
NVIDIA_VISIBLE_DEVICES=all
NVIDIA_DRIVER_CAPABILITIES=compute,utility

# GPU Monitoring
GPU_MONITORING_ENABLED=true
GPU_MEMORY_THRESHOLD=90
GPU_TEMPERATURE_THRESHOLD=85

# -----------------------------------------------------------------------------
# AI MODELS CONFIGURATION (PC2)
# -----------------------------------------------------------------------------
# Model Cache
MODEL_CACHE_DIR=/models/cache
HF_CACHE_DIR=/models/huggingface
TRANSFORMERS_CACHE=/models/transformers

# Embedding Service
EMBEDDING_SERVICE_HOST=0.0.0.0
EMBEDDING_SERVICE_PORT=${EMBEDDING_SERVICE_PORT}
EMBEDDING_MODEL_PATH=/models/embedding
EMBEDDING_WORKERS=4
EMBEDDING_GPU_ENABLED=true

# Vietnamese NLP Service
NLP_SERVICE_HOST=0.0.0.0
NLP_SERVICE_PORT=${VIETNAMESE_NLP_PORT}
PYVI_CACHE_DIR=/models/pyvi
UNDERTHESEA_CACHE_DIR=/models/underthesea
NLP_GPU_ENABLED=true

# LLM Service
LLM_SERVICE_HOST=0.0.0.0
LLM_SERVICE_PORT=${LLM_SERVICE_PORT}
LLM_MODEL_PATH=/models/llm
LLM_GPU_ENABLED=true
LLM_MAX_LENGTH=4096
LLM_TEMPERATURE=0.7

# -----------------------------------------------------------------------------
# DATA PIPELINE SERVICES (PC2)
# -----------------------------------------------------------------------------
# Data Preparation
DATA_PREP_HOST=0.0.0.0
DATA_PREP_PORT=${DATA_PREPARATION_PORT}
DATA_PREP_TEMP_DIR=/tmp/data_prep
DATA_PREP_MAX_FILE_SIZE=100MB

# Quality Control
QUALITY_CONTROL_HOST=0.0.0.0
QUALITY_CONTROL_PORT=${QUALITY_CONTROL_PORT}
QUALITY_CONTROL_GPU_ENABLED=true
QUALITY_THRESHOLD=0.7

# Data Ingestion
INGESTION_HOST=0.0.0.0
INGESTION_PORT=${DATA_INGESTION_PORT}
INGESTION_BATCH_SIZE=32
INGESTION_MAX_CONCURRENT_JOBS=5

# -----------------------------------------------------------------------------
# RAG CORE SERVICES (PC2)
# -----------------------------------------------------------------------------
# Retrieval Router
RETRIEVAL_HOST=0.0.0.0
RETRIEVAL_PORT=${RETRIEVAL_ROUTER_PORT}
RETRIEVAL_TOP_K=10
RETRIEVAL_SIMILARITY_THRESHOLD=0.7

# Synthesis Engine
SYNTHESIS_HOST=0.0.0.0
SYNTHESIS_PORT=${SYNTHESIS_ENGINE_PORT}
SYNTHESIS_MAX_CONTEXT_LENGTH=2048
SYNTHESIS_OVERLAP_RATIO=0.1

# Generation Engine
GENERATION_HOST=0.0.0.0
GENERATION_PORT=${GENERATION_ENGINE_PORT}
GENERATION_GPU_ENABLED=true
GENERATION_MAX_TOKENS=1024
GENERATION_TEMPERATURE=0.7

# RAG API Main
RAG_API_HOST=0.0.0.0
RAG_API_PORT=${RAG_API_MAIN_PORT}

# -----------------------------------------------------------------------------
# EXTERNAL SERVICE CONNECTIONS (PC2 -> PC1)
# -----------------------------------------------------------------------------
# Database connections
EXTERNAL_DATABASE_URL=postgresql://${DB_MASTER_USER}:${DB_MASTER_PASSWORD}@${PC1_IP}:${POSTGRES_PORT}/${POSTGRES_DB}
EXTERNAL_REDIS_URL=redis://${PC1_IP}:${REDIS_PORT}
EXTERNAL_CHROMADB_URL=http://${PC1_IP}:${CHROMADB_PORT}

# PC1 Services
AUTH_SERVICE_URL=http://${PC1_IP}:${AUTH_SERVICE_PORT}
ANALYTICS_SERVICE_URL=http://${PC1_IP}:${ANALYTICS_API_PORT}
ADMIN_SERVICE_URL=http://${PC1_IP}:${ADMIN_TOOLS_PORT}

# -----------------------------------------------------------------------------
# PERFORMANCE TUNING (PC2)
# -----------------------------------------------------------------------------
# Worker Processes
AI_WORKERS=8
PIPELINE_WORKERS=4
API_WORKERS=6

# Memory Settings
TORCH_MEMORY_POOL=2048
HF_MEMORY_LIMIT=8192
CUDA_MEMORY_POOL=4096

# Batch Processing
DEFAULT_BATCH_SIZE=16
MAX_BATCH_SIZE=64
BATCH_TIMEOUT=30

# -----------------------------------------------------------------------------
# RESOURCE LIMITS (PC2)
# -----------------------------------------------------------------------------
EMBEDDING_MEMORY_LIMIT=8g
EMBEDDING_CPUS_LIMIT=4
NLP_MEMORY_LIMIT=4g
NLP_CPUS_LIMIT=2
GENERATION_MEMORY_LIMIT=12g
GENERATION_CPUS_LIMIT=6
RAG_API_MEMORY_LIMIT=2g
RAG_API_CPUS_LIMIT=2

# -----------------------------------------------------------------------------
# MONITORING (PC2)
# -----------------------------------------------------------------------------
PROMETHEUS_GATEWAY_URL=http://${PC1_IP}:${MONITORING_PROMETHEUS_PORT}
METRICS_PUSH_INTERVAL=15s
GPU_METRICS_ENABLED=true

# Health Checks
HEALTH_CHECK_INTERVAL=30s
HEALTH_CHECK_TIMEOUT=10s
HEALTH_CHECK_RETRIES=3

# -----------------------------------------------------------------------------
# DEVELOPMENT & DEBUGGING (PC2)
# -----------------------------------------------------------------------------
ENABLE_DEBUG_ENDPOINTS=false
PROFILE_PERFORMANCE=false
TRACE_REQUESTS=false
DEVELOPMENT_MODE=false
```

### **📁 `.env.pc2.docker-compose` - PC2 Docker Compose Override**

```env
# Docker Compose specific overrides for PC2
COMPOSE_PROJECT_NAME=vietnamese-rag-pc2
COMPOSE_HTTP_TIMEOUT=120

# GPU Configuration
DOCKER_RUNTIME=nvidia
GPU_DEVICE_IDS=0

# Volume mappings
MODEL_CACHE_PATH=./models
TEMP_PROCESSING_PATH=./temp
LOG_DATA_PATH=./logs

# Network configuration
DOCKER_NETWORK_NAME=vietnamese-rag-network
DOCKER_SUBNET=172.20.0.0/16
PC2_DOCKER_IP=172.20.0.20

# Resource allocation
GPU_MEMORY_RESERVATION=8g
SHM_SIZE=2g
```

## **🔗 NETWORK & INTEGRATION**

### **📁 `.env.network` - Cross-PC Communication**

```env
# =============================================================================
# NETWORK CONFIGURATION FOR CROSS-PC COMMUNICATION
# =============================================================================

# -----------------------------------------------------------------------------
# SERVICE DISCOVERY MAP
# -----------------------------------------------------------------------------
# PC1 Services (Database & Web)
PC1_POSTGRES=postgresql://${DB_MASTER_USER}:${DB_MASTER_PASSWORD}@${PC1_IP}:5432/${POSTGRES_DB}
PC1_REDIS=redis://${PC1_IP}:6379
PC1_CHROMADB=http://${PC1_IP}:8000
PC1_AUTH=http://${PC1_IP}:8001
PC1_ADMIN=http://${PC1_IP}:8002
PC1_ANALYTICS=http://${PC1_IP}:8003
PC1_WEB=http://${PC1_IP}:8004
PC1_MONITORING=http://${PC1_IP}:8005

# PC2 Services (AI Processing)
PC2_EMBEDDING=http://${PC2_IP}:8010
PC2_NLP=http://${PC2_IP}:8011
PC2_LLM=http://${PC2_IP}:8012
PC2_DATA_PREP=http://${PC2_IP}:8020
PC2_QUALITY=http://${PC2_IP}:8021
PC2_INGESTION=http://${PC2_IP}:8022
PC2_RETRIEVAL=http://${PC2_IP}:8030
PC2_SYNTHESIS=http://${PC2_IP}:8031
PC2_GENERATION=http://${PC2_IP}:8032
PC2_RAG_API=http://${PC2_IP}:8033

# -----------------------------------------------------------------------------
# HEALTH CHECK ENDPOINTS
# -----------------------------------------------------------------------------
HEALTH_ENDPOINTS="
${PC1_IP}:5432,
${PC1_IP}:6379,
${PC1_IP}:8000,
${PC1_IP}:8001/health,
${PC1_IP}:8002/health,
${PC1_IP}:8003/health,
${PC2_IP}:8010/health,
${PC2_IP}:8011/health,
${PC2_IP}:8020/health,
${PC2_IP}:8021/health,
${PC2_IP}:8022/health,
${PC2_IP}:8030/health,
${PC2_IP}:8031/health,
${PC2_IP}:8032/health,
${PC2_IP}:8033/health
"

# -----------------------------------------------------------------------------
# LOAD BALANCER CONFIGURATION
# -----------------------------------------------------------------------------
UPSTREAM_RAG_SERVERS="server ${PC2_IP}:8033"
UPSTREAM_AUTH_SERVERS="server ${PC1_IP}:8001"
UPSTREAM_WEB_SERVERS="server ${PC1_IP}:8004"

# Timeouts
PROXY_CONNECT_TIMEOUT=5s
PROXY_SEND_TIMEOUT=60s
PROXY_READ_TIMEOUT=60s
```

## **🚀 DEPLOYMENT SCRIPTS**

### **📁 `deploy-pc1.sh` - PC1 Deployment Script**

```bash
#!/bin/bash
# =============================================================================
# PC1 DEPLOYMENT SCRIPT - Database & Infrastructure Server
# =============================================================================

set -e

echo "🚀 Starting PC1 (Database & Infrastructure) Deployment..."

# Load environment
source .env.global
source .env.pc1
source .env.network

# Create directories
sudo mkdir -p /data/{postgres,redis,chromadb,backups,logs}
sudo chown -R $(id -u):$(id -g) /data

# Start infrastructure services
echo "📊 Starting database services..."
docker-compose -f docker-compose.pc1.yml up -d postgres redis chromadb

# Wait for databases
echo "⏳ Waiting for databases to be ready..."
sleep 30

# Run database migrations
echo "🗄️ Running database migrations..."
docker exec vietnamese-rag-pc1_postgres_1 psql -U ${DB_MASTER_USER} -d ${POSTGRES_DB} -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Start platform services
echo "🛠️ Starting platform services..."
docker-compose -f docker-compose.pc1.yml up -d admin_tools analytics auth_service

# Start web services
echo "🌐 Starting web services..."
docker-compose -f docker-compose.pc1.yml up -d web_interface nginx

# Health checks
echo "❤️ Running health checks..."
sleep 30
curl -f http://localhost:8001/health || exit 1
curl -f http://localhost:8002/health || exit 1
curl -f http://localhost:8003/health || exit 1

echo "✅ PC1 deployment completed successfully!"
echo "🌐 Web Interface: http://${PC1_IP}:80"
echo "🔧 Admin Tools: http://${PC1_IP}:8002"
echo "📊 Analytics: http://${PC1_IP}:8003"
```

### **📁 `deploy-pc2.sh` - PC2 Deployment Script**

```bash
#!/bin/bash
# =============================================================================
# PC2 DEPLOYMENT SCRIPT - GPU AI Processing Server
# =============================================================================

set -e

echo "🚀 Starting PC2 (GPU AI Processing) Deployment..."

# Load environment
source .env.global
source .env.pc2
source .env.network

# Check GPU availability
nvidia-smi || { echo "❌ GPU not available!"; exit 1; }

# Create directories
mkdir -p ./models/{cache,huggingface,transformers,embedding,llm}
mkdir -p ./temp ./logs

# Download models
echo "📥 Downloading AI models..."
python3 scripts/download_models.py

# Start AI processing services
echo "🤖 Starting AI processing services..."
docker-compose -f docker-compose.pc2.yml up -d embedding_service vietnamese_nlp

# Start data pipeline
echo "📥 Starting data pipeline services..."
docker-compose -f docker-compose.pc2.yml up -d data_preparation quality_control data_ingestion

# Start RAG core services
echo "🧠 Starting RAG core services..."
docker-compose -f docker-compose.pc2.yml up -d retrieval_router synthesis_engine generation_engine

# Start main RAG API
echo "🌐 Starting main RAG API..."
docker-compose -f docker-compose.pc2.yml up -d rag_api

# Health checks
echo "❤️ Running health checks..."
sleep 60
curl -f http://localhost:8010/health || exit 1
curl -f http://localhost:8033/health || exit 1

echo "✅ PC2 deployment completed successfully!"
echo "🤖 RAG API: http://${PC2_IP}:8033"
echo "🔢 Embedding Service: http://${PC2_IP}:8010"
echo "📥 Data Ingestion: http://${PC2_IP}:8022"
```

## **✅ VALIDATION & TESTING**

### **📁 `validate-system.sh` - System Integration Test**

```bash
#!/bin/bash
# =============================================================================
# SYSTEM VALIDATION SCRIPT
# =============================================================================

source .env.global
source .env.network

echo "🧪 Running system integration tests..."

# Test PC1 services
echo "Testing PC1 services..."
curl -f ${PC1_POSTGRES%/*}/health 2>/dev/null || echo "❌ PostgreSQL not accessible"
curl -f ${PC1_REDIS}/ping 2>/dev/null || echo "❌ Redis not accessible"
curl -f ${PC1_CHROMADB}/api/v1/heartbeat 2>/dev/null || echo "❌ ChromaDB not accessible"
curl -f ${PC1_AUTH}/health 2>/dev/null && echo "✅ Auth Service OK"
curl -f ${PC1_ADMIN}/health 2>/dev/null && echo "✅ Admin Tools OK"

# Test PC2 services
echo "Testing PC2 services..."
curl -f ${PC2_EMBEDDING}/health 2>/dev/null && echo "✅ Embedding Service OK"
curl -f ${PC2_RAG_API}/health 2>/dev/null && echo "✅ RAG API OK"

# Test cross-PC communication
echo "Testing cross-PC communication..."
curl -X POST ${PC2_RAG_API}/test-connection \
  -H "Content-Type: application/json" \
  -d '{"test": "pc1-connection"}' 2>/dev/null && echo "✅ Cross-PC communication OK"

echo "🎉 System validation completed!"
```

**Những file cấu hình này đảm bảo:**
- ✅ Tất cả ports được chuẩn hóa và không trung lặp
- ✅ Username/password thống nhất: `chatbotAIhome` / `chatbotAI601`
- ✅ Cross-PC communication được cấu hình đúng
- ✅ Resource limits và performance tuning
- ✅ Security và monitoring được thiết lập
- ✅ Easy deployment với scripts tự động
