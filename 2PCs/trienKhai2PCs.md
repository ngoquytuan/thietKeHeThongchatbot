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
PC1_IP=192.168.1.100  # IP của PC1 (Database server)
PC2_IP=192.168.1.101  # IP của PC2 (GPU server)

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
Tôi sẽ tạo một hệ thống file môi trường hoàn chỉnh để đảm bảo tính nhất quán giữa 2 PC và tất cả modules:

## **🔧 HỆ THỐNG FILE MÔI TRƯỜNG THỐNG NHẤT**

### **📁 Cấu trúc thư mục môi trường:**

```
environment-config/
├── shared/
│   ├── .env.shared           # Cấu hình chung cho cả 2 PC
│   ├── .env.network          # Network và IP addresses
│   ├── .env.secrets          # Passwords và secrets
│   └── .env.ports            # Port mapping
├── pc1/
│   ├── .env.pc1              # Cấu hình riêng PC1
│   ├── .env.database         # Database settings
│   ├── .env.infrastructure   # Infrastructure services
│   └── .env.web              # Web services
├── pc2/
│   ├── .env.pc2              # Cấu hình riêng PC2
│   ├── .env.gpu              # GPU settings
│   ├── .env.ai               # AI services
│   └── .env.rag              # RAG pipeline
├── scripts/
│   ├── generate-secrets.sh   # Script tạo random passwords
│   ├── validate-config.sh    # Validate configuration
│   └── sync-env.sh          # Sync giữa 2 PC
└── docker-compose/
    ├── docker-compose.pc1.yml
    ├── docker-compose.pc2.yml
    └── docker-compose.override.yml
```

### **🔐 File cấu hình chi tiết:**

#### **1. shared/.env.shared - Cấu hình chung**
```bash
# ===========================================
# SHARED CONFIGURATION FOR BOTH PC1 & PC2
# ===========================================

# Project Information
PROJECT_NAME=vietnamese-rag-chatbot
VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# Timezone
TZ=Asia/Ho_Chi_Minh

# Language Settings
DEFAULT_LANGUAGE=vi
SUPPORTED_LANGUAGES=vi,en

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_RETENTION_DAYS=30

# Performance Settings
MAX_CONCURRENT_CONNECTIONS=100
REQUEST_TIMEOUT=300
HEALTH_CHECK_INTERVAL=30

# Vietnamese NLP Settings
VIETNAMESE_STOPWORDS_ENABLED=true
DIACRITICS_NORMALIZATION=true
WORD_SEGMENTATION=pyvi

# Embedding Configuration
EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
EMBEDDING_DIMENSION=1024
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MAX_CHUNK_LENGTH=1000

# Security
JWT_ALGORITHM=RS256
JWT_EXPIRE_HOURS=24
SESSION_TIMEOUT_MINUTES=60
RATE_LIMIT_PER_MINUTE=100

# Backup Settings
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE="0 2 * * *"
```

#### **2. shared/.env.network - Network Configuration**
```bash
# ===========================================
# NETWORK CONFIGURATION
# ===========================================

# PC IP Addresses (Update these for your network)
PC1_INTERNAL_IP=192.168.1.100
PC2_INTERNAL_IP=192.168.1.101

# PC1 External Access
PC1_EXTERNAL_IP=192.168.1.100
PC1_DOMAIN=rag-db.local

# PC2 External Access  
PC2_EXTERNAL_IP=192.168.1.101
PC2_DOMAIN=rag-ai.local

# Docker Networks
DOCKER_NETWORK_NAME=rag-network
DOCKER_SUBNET=172.20.0.0/16

# Cross-PC Communication
CROSS_PC_NETWORK_ENABLED=true
NETWORK_TIMEOUT=30
MAX_RETRIES=3

# DNS Settings (Optional)
USE_CUSTOM_DNS=false
DNS_SERVERS=8.8.8.8,8.8.4.4
```

#### **3. shared/.env.ports - Port Mapping**
```bash
# ===========================================
# UNIFIED PORT MAPPING - NO CONFLICTS
# ===========================================

# ===== PC1 PORTS (Infrastructure & Web) =====

# Infrastructure Services (5000-5999)
POSTGRES_PORT=5432
REDIS_PORT=6379
CHROMADB_PORT=8000

# Authentication & Security (6000-6099)
AUTH_SERVICE_PORT=6001
SESSION_SERVICE_PORT=6002

# Web Services (6100-6199)
WEB_INTERFACE_PORT=6100
ADMIN_PANEL_PORT=6101

# Platform Services (6200-6299)
ANALYTICS_API_PORT=6201
ADMIN_TOOLS_PORT=6202
MONITORING_PORT=6203

# Load Balancer & Gateway (80/443 + 6300-6399)
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
API_GATEWAY_PORT=6300

# Monitoring Stack (6400-6499)
PROMETHEUS_PORT=6401
GRAFANA_PORT=6402
ALERTMANAGER_PORT=6403

# ===== PC2 PORTS (AI & RAG Processing) =====

# AI Core Services (7000-7099)
EMBEDDING_SERVICE_PORT=7001
LLM_SERVICE_PORT=7002
VIETNAMESE_NLP_PORT=7003

# Data Pipeline (7100-7199)
DATA_PREPARATION_PORT=7101
QUALITY_CONTROL_PORT=7102
DATA_INGESTION_PORT=7103

# RAG Pipeline (7200-7299)
RETRIEVAL_ROUTER_PORT=7201
SYNTHESIS_ENGINE_PORT=7202
GENERATION_ENGINE_PORT=7203
RAG_API_MAIN_PORT=7200

# Processing Services (7300-7399)
DOCUMENT_PROCESSOR_PORT=7301
CHUNK_PROCESSOR_PORT=7302
VECTOR_PROCESSOR_PORT=7303

# ===== EXTERNAL ACCESS PORTS =====
# Main entry points for users
MAIN_WEB_PORT=80
MAIN_API_PORT=8080
ADMIN_ACCESS_PORT=8081
MONITORING_ACCESS_PORT=8082

# ===== INTERNAL COMMUNICATION PORTS =====
PC1_TO_PC2_PORT=9001
PC2_TO_PC1_PORT=9002
HEALTH_CHECK_PORT=9999
```

#### **4. shared/.env.secrets - Security Configuration**
```bash
# ===========================================
# SECURITY SECRETS - GENERATE UNIQUE VALUES
# ===========================================

# Database Credentials
POSTGRES_ADMIN_USER=kb_admin
POSTGRES_ADMIN_PASSWORD=KbAdm1n_2024_SecureP@ss
POSTGRES_APP_USER=kb_app
POSTGRES_APP_PASSWORD=KbApp_2024_SecureP@ss
POSTGRES_READONLY_USER=kb_readonly
POSTGRES_READONLY_PASSWORD=KbRead_2024_SecureP@ss

# Redis Security
REDIS_PASSWORD=Redis_2024_SecureP@ss
REDIS_AUTH_TOKEN=redis_auth_token_2024_very_long_random_string

# ChromaDB Security
CHROMA_AUTH_TOKEN=chroma_auth_token_2024_very_long_random_string
CHROMA_SERVER_AUTH_CREDENTIALS=chroma_admin:ChromaAdm1n_2024

# JWT Secrets
JWT_SECRET_KEY=jwt_secret_key_2024_this_should_be_very_long_and_random_string_minimum_32_chars
JWT_REFRESH_SECRET=jwt_refresh_secret_2024_another_very_long_random_string_for_refresh_tokens

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Encryption Keys
ENCRYPTION_KEY=encryption_key_2024_for_sensitive_data_32_characters_minimum
HASH_SALT=hash_salt_2024_for_password_hashing_random_string

# Admin Credentials
ADMIN_USERNAME=system_admin
ADMIN_PASSWORD=Adm1n_2024_VerySecureP@ssw0rd
ADMIN_EMAIL=admin@company.com

# Monitoring Credentials
GRAFANA_ADMIN_PASSWORD=Grafana_2024_SecureP@ss
PROMETHEUS_PASSWORD=Prometheus_2024_SecureP@ss

# File Upload Security
UPLOAD_SECRET_KEY=upload_secret_2024_for_file_validation

# Cross-Service Communication
INTERNAL_API_KEY=internal_api_key_2024_for_service_to_service_communication
SERVICE_TO_SERVICE_TOKEN=service_token_2024_very_long_random_string
```

#### **5. pc1/.env.pc1 - PC1 Specific Configuration**
```bash
# ===========================================
# PC1 CONFIGURATION - DATABASE & WEB SERVER
# ===========================================

# Load shared configurations
include ../shared/.env.shared
include ../shared/.env.network  
include ../shared/.env.ports
include ../shared/.env.secrets

# PC1 Specific Settings
PC_ROLE=database_server
PC_HOSTNAME=rag-pc1-db
SERVER_NAME=RAG Database Server

# Hardware Optimization
CPU_CORES=8
MEMORY_LIMIT=32G
DISK_CACHE_SIZE=8G

# Database Configuration
POSTGRES_SHARED_BUFFERS=8GB
POSTGRES_EFFECTIVE_CACHE_SIZE=24GB
POSTGRES_WORK_MEM=256MB
POSTGRES_MAINTENANCE_WORK_MEM=2GB
POSTGRES_MAX_CONNECTIONS=200
POSTGRES_LOG_STATEMENT=all
POSTGRES_LOG_MIN_DURATION_STATEMENT=1000

# Redis Configuration
REDIS_MAXMEMORY=8gb
REDIS_MAXMEMORY_POLICY=allkeys-lru
REDIS_SAVE_INTERVAL="900 1 300 10 60 10000"
REDIS_APPENDONLY=yes

# ChromaDB Configuration
CHROMA_HOST=0.0.0.0
CHROMA_PORT=${CHROMADB_PORT}
CHROMA_PERSIST_DIRECTORY=/chroma/chroma
CHROMA_ANONYMIZED_TELEMETRY=false

# Web Server Configuration
NGINX_WORKER_PROCESSES=auto
NGINX_WORKER_CONNECTIONS=1024
NGINX_CLIENT_MAX_BODY_SIZE=100M
NGINX_PROXY_TIMEOUT=300s

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_DIRECTORY=/backups
POSTGRES_BACKUP_RETENTION=7
REDIS_BACKUP_RETENTION=3

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=${PROMETHEUS_PORT}
HEALTH_CHECK_ENABLED=true
```

#### **6. pc2/.env.pc2 - PC2 Specific Configuration**
```bash
# ===========================================
# PC2 CONFIGURATION - GPU & AI PROCESSING
# ===========================================

# Load shared configurations
include ../shared/.env.shared
include ../shared/.env.network
include ../shared/.env.ports  
include ../shared/.env.secrets

# PC2 Specific Settings
PC_ROLE=ai_server
PC_HOSTNAME=rag-pc2-gpu
SERVER_NAME=RAG AI Processing Server

# Hardware Optimization
CPU_CORES=8
MEMORY_LIMIT=32G
GPU_ENABLED=true
GPU_MEMORY_LIMIT=16G

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
NVIDIA_VISIBLE_DEVICES=all
NVIDIA_DRIVER_CAPABILITIES=compute,utility
GPU_MEMORY_FRACTION=0.8
MIXED_PRECISION=true

# AI Model Configuration
MODEL_CACHE_DIR=/models/.cache
MODEL_DOWNLOAD_TIMEOUT=1800
TRANSFORMERS_CACHE=/models/transformers
HF_HOME=/models/huggingface

# Embedding Service
EMBEDDING_BATCH_SIZE=32
EMBEDDING_MAX_LENGTH=512
EMBEDDING_POOLING=mean
EMBEDDING_NORMALIZE=true

# Vietnamese NLP
PYVI_ENABLED=true
UNDERTHESEA_ENABLED=true
NLP_BATCH_SIZE=16
NLP_MAX_WORKERS=4

# RAG Pipeline Configuration
RAG_RETRIEVAL_TOP_K=10
RAG_CONTEXT_LENGTH=4096
RAG_GENERATION_MAX_TOKENS=1024
RAG_TEMPERATURE=0.7

# Performance Settings
ASYNC_WORKERS=8
QUEUE_MAX_SIZE=1000
PROCESSING_TIMEOUT=300
RETRY_ATTEMPTS=3

# External API Configuration
PC1_DATABASE_URL=postgresql://${POSTGRES_APP_USER}:${POSTGRES_APP_PASSWORD}@${PC1_INTERNAL_IP}:${POSTGRES_PORT}/knowledge_base_unified
PC1_REDIS_URL=redis://:${REDIS_PASSWORD}@${PC1_INTERNAL_IP}:${REDIS_PORT}/0
PC1_CHROMADB_URL=http://${PC1_INTERNAL_IP}:${CHROMADB_PORT}
PC1_AUTH_URL=http://${PC1_INTERNAL_IP}:${AUTH_SERVICE_PORT}
```

### **🛠️ Scripts hỗ trợ:**

#### **7. scripts/generate-secrets.sh - Tạo passwords tự động**
```bash
#!/bin/bash
# ===========================================
# SCRIPT TẠO PASSWORDS VÀ SECRETS TỰ ĐỘNG
# ===========================================

echo "Generating secure passwords and secrets..."

# Function to generate random password
generate_password() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Function to generate API key
generate_api_key() {
    echo "$(date +%s)_$(openssl rand -hex 16)"
}

# Update .env.secrets with generated values
SECRETS_FILE="../shared/.env.secrets"

# Backup original file
cp $SECRETS_FILE "$SECRETS_FILE.backup.$(date +%Y%m%d_%H%M%S)"

# Generate new secrets
POSTGRES_ADMIN_PASSWORD=$(generate_password 24)
POSTGRES_APP_PASSWORD=$(generate_password 24)
POSTGRES_READONLY_PASSWORD=$(generate_password 24)
REDIS_PASSWORD=$(generate_password 24)
REDIS_AUTH_TOKEN=$(generate_password 48)
CHROMA_AUTH_TOKEN=$(generate_password 48)
JWT_SECRET_KEY=$(generate_password 64)
JWT_REFRESH_SECRET=$(generate_password 64)
ENCRYPTION_KEY=$(generate_password 32)
HASH_SALT=$(generate_password 32)
ADMIN_PASSWORD=$(generate_password 20)
GRAFANA_ADMIN_PASSWORD=$(generate_password 20)
PROMETHEUS_PASSWORD=$(generate_password 20)
UPLOAD_SECRET_KEY=$(generate_password 32)
INTERNAL_API_KEY=$(generate_api_key)
SERVICE_TO_SERVICE_TOKEN=$(generate_password 64)

# Update secrets file
cat > $SECRETS_FILE << EOF
# ===========================================
# AUTO-GENERATED SECURITY SECRETS
# Generated on: $(date)
# ===========================================

# Database Credentials
POSTGRES_ADMIN_USER=kb_admin
POSTGRES_ADMIN_PASSWORD=$POSTGRES_ADMIN_PASSWORD
POSTGRES_APP_USER=kb_app
POSTGRES_APP_PASSWORD=$POSTGRES_APP_PASSWORD
POSTGRES_READONLY_USER=kb_readonly
POSTGRES_READONLY_PASSWORD=$POSTGRES_READONLY_PASSWORD

# Redis Security
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_AUTH_TOKEN=$REDIS_AUTH_TOKEN

# ChromaDB Security
CHROMA_AUTH_TOKEN=$CHROMA_AUTH_TOKEN
CHROMA_SERVER_AUTH_CREDENTIALS=chroma_admin:$CHROMA_AUTH_TOKEN

# JWT Secrets
JWT_SECRET_KEY=$JWT_SECRET_KEY
JWT_REFRESH_SECRET=$JWT_REFRESH_SECRET

# API Keys (Update manually)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Encryption Keys
ENCRYPTION_KEY=$ENCRYPTION_KEY
HASH_SALT=$HASH_SALT

# Admin Credentials
ADMIN_USERNAME=system_admin
ADMIN_PASSWORD=$ADMIN_PASSWORD
ADMIN_EMAIL=admin@company.com

# Monitoring Credentials
GRAFANA_ADMIN_PASSWORD=$GRAFANA_ADMIN_PASSWORD
PROMETHEUS_PASSWORD=$PROMETHEUS_PASSWORD

# File Upload Security
UPLOAD_SECRET_KEY=$UPLOAD_SECRET_KEY

# Cross-Service Communication
INTERNAL_API_KEY=$INTERNAL_API_KEY
SERVICE_TO_SERVICE_TOKEN=$SERVICE_TO_SERVICE_TOKEN
EOF

echo "✅ Secrets generated successfully!"
echo "📝 Backup saved as: $SECRETS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
echo "⚠️  Remember to update API keys manually!"
```

#### **8. scripts/validate-config.sh - Kiểm tra cấu hình**
```bash
#!/bin/bash
# ===========================================
# SCRIPT VALIDATE CONFIGURATION
# ===========================================

echo "🔍 Validating environment configuration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Error counter
ERRORS=0

# Function to check port conflicts
check_port_conflicts() {
    echo "📋 Checking port conflicts..."
    
    # Load ports configuration
    source ../shared/.env.ports
    
    # Extract all ports
    PORTS=(
        $POSTGRES_PORT $REDIS_PORT $CHROMADB_PORT
        $AUTH_SERVICE_PORT $SESSION_SERVICE_PORT
        $WEB_INTERFACE_PORT $ADMIN_PANEL_PORT
        $ANALYTICS_API_PORT $ADMIN_TOOLS_PORT $MONITORING_PORT
        $NGINX_HTTP_PORT $NGINX_HTTPS_PORT $API_GATEWAY_PORT
        $PROMETHEUS_PORT $GRAFANA_PORT $ALERTMANAGER_PORT
        $EMBEDDING_SERVICE_PORT $LLM_SERVICE_PORT $VIETNAMESE_NLP_PORT
        $DATA_PREPARATION_PORT $QUALITY_CONTROL_PORT $DATA_INGESTION_PORT
        $RETRIEVAL_ROUTER_PORT $SYNTHESIS_ENGINE_PORT $GENERATION_ENGINE_PORT $RAG_API_MAIN_PORT
        $DOCUMENT_PROCESSOR_PORT $CHUNK_PROCESSOR_PORT $VECTOR_PROCESSOR_PORT
    )
    
    # Check for duplicates
    SORTED_PORTS=($(printf '%s\n' "${PORTS[@]}" | sort -n))
    UNIQUE_PORTS=($(printf '%s\n' "${PORTS[@]}" | sort -n | uniq))
    
    if [ ${#SORTED_PORTS[@]} -ne ${#UNIQUE_PORTS[@]} ]; then
        echo -e "${RED}❌ Port conflicts detected!${NC}"
        # Find duplicates
        printf '%s\n' "${PORTS[@]}" | sort | uniq -d | while read port; do
            echo -e "${RED}   Duplicate port: $port${NC}"
        done
        ((ERRORS++))
    else
        echo -e "${GREEN}✅ No port conflicts found${NC}"
    fi
}

# Function to check required variables
check_required_vars() {
    echo "📋 Checking required environment variables..."
    
    # List of critical variables
    REQUIRED_VARS=(
        "PC1_INTERNAL_IP"
        "PC2_INTERNAL_IP"
        "POSTGRES_ADMIN_PASSWORD"
        "REDIS_PASSWORD"
        "JWT_SECRET_KEY"
        "ADMIN_PASSWORD"
    )
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}❌ Missing required variable: $var${NC}"
            ((ERRORS++))
        else
            echo -e "${GREEN}✅ $var is set${NC}"
        fi
    done
}

# Function to check password strength
check_password_strength() {
    echo "📋 Checking password strength..."
    
    # Load secrets
    source ../shared/.env.secrets
    
    # Check password length
    if [ ${#POSTGRES_ADMIN_PASSWORD} -lt 16 ]; then
        echo -e "${YELLOW}⚠️  POSTGRES_ADMIN_PASSWORD is shorter than 16 characters${NC}"
    fi
    
    if [ ${#JWT_SECRET_KEY} -lt 32 ]; then
        echo -e "${RED}❌ JWT_SECRET_KEY must be at least 32 characters${NC}"
        ((ERRORS++))
    fi
}

# Function to check network connectivity
check_network() {
    echo "📋 Checking network configuration..."
    
    source ../shared/.env.network
    
    # Validate IP format
    if [[ ! $PC1_INTERNAL_IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        echo -e "${RED}❌ Invalid PC1_INTERNAL_IP format: $PC1_INTERNAL_IP${NC}"
        ((ERRORS++))
    fi
    
    if [[ ! $PC2_INTERNAL_IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        echo -e "${RED}❌ Invalid PC2_INTERNAL_IP format: $PC2_INTERNAL_IP${NC}"
        ((ERRORS++))
    fi
}

# Function to generate validation report
generate_report() {
    echo ""
    echo "📊 Validation Report"
    echo "===================="
    
    if [ $ERRORS -eq 0 ]; then
        echo -e "${GREEN}✅ All checks passed! Configuration is valid.${NC}"
        exit 0
    else
        echo -e "${RED}❌ Found $ERRORS error(s). Please fix before deployment.${NC}"
        exit 1
    fi
}

# Main validation flow
main() {
    # Load all environment files
    source ../shared/.env.shared
    source ../shared/.env.network
    source ../shared/.env.ports
    source ../shared/.env.secrets
    
    check_port_conflicts
    check_required_vars
    check_password_strength
    check_network
    generate_report
}

main "$@"
```

#### **9. scripts/sync-env.sh - Đồng bộ cấu hình giữa 2 PC**
```bash
#!/bin/bash
# ===========================================
# SCRIPT ĐỒNG BỘ CONFIGURATION GIỮA 2 PC
# ===========================================

PC1_USER="admin"
PC1_IP="192.168.1.100"
PC2_USER="admin"  
PC2_IP="192.168.1.101"

echo "🔄 Syncing environment configuration between PC1 and PC2..."

# Function to sync to PC1
sync_to_pc1() {
    echo "📤 Syncing to PC1 ($PC1_IP)..."
    
    # Create directory structure
    ssh $PC1_USER@$PC1_IP "mkdir -p ~/rag-deployment/environment-config/{shared,pc1,scripts}"
    
    # Copy shared configurations
    scp ../shared/* $PC1_USER@$PC1_IP:~/rag-deployment/environment-config/shared/
    
    # Copy PC1 specific configurations
    scp ../pc1/* $PC1_USER@$PC1_IP:~/rag-deployment/environment-config/pc1/
    
    # Copy scripts
    scp ../scripts/* $PC1_USER@$PC1_IP:~/rag-deployment/environment-config/scripts/
    
    # Set permissions
    ssh $PC1_USER@$PC1_IP "chmod +x ~/rag-deployment/environment-config/scripts/*.sh"
}

# Function to sync to PC2
sync_to_pc2() {
    echo "📤 Syncing to PC2 ($PC2_IP)..."
    
    # Create directory structure
    ssh $PC2_USER@$PC2_IP "mkdir -p ~/rag-deployment/environment-config/{shared,pc2,scripts}"
    
    # Copy shared configurations
    scp ../shared/* $PC2_USER@$PC2_IP:~/rag-deployment/environment-config/shared/
    
    # Copy PC2 specific configurations
    scp ../pc2/* $PC2_USER@$PC2_IP:~/rag-deployment/environment-config/pc2/
    
    # Copy scripts
    scp ../scripts/* $PC2_USER@$PC2_IP:~/rag-deployment/environment-config/scripts/
    
    # Set permissions
    ssh $PC2_USER@$PC2_IP "chmod +x ~/rag-deployment/environment-config/scripts/*.sh"
}

# Main sync function
main() {
    # Validate configuration first
    echo "🔍 Validating configuration before sync..."
    ./validate-config.sh
    
    if [ $? -eq 0 ]; then
        sync_to_pc1
        sync_to_pc2
        
        echo "✅ Configuration synced successfully!"
        echo "📝 Next steps:"
        echo "   1. SSH to PC1: ssh $PC1_USER@$PC1_IP"
        echo "   2. SSH to PC2: ssh $PC2_USER@$PC2_IP"
        echo "   3. Run deployment on each PC"
    else
        echo "❌ Configuration validation failed. Please fix errors first."
        exit 1
    fi
}

main "$@"
```

### **🚀 Hướng dẫn sử dụng:**

```bash
# 1. Tạo cấu hình ban đầu
cd environment-config/scripts
chmod +x *.sh

# 2. Tạo passwords tự động
./generate-secrets.sh

# 3. Cập nhật IP addresses (sửa .env.network)
nano ../shared/.env.network

# 4. Validate cấu hình
./validate-config.sh

# 5. Đồng bộ lên 2 PC
./sync-env.sh
```

**✅ Advantages của hệ thống này:**
- **No Conflicts**: Tất cả ports được quản lý tập trung
- **Consistent**: Cùng một secrets trên cả 2 PC
- **Secure**: Auto-generated strong passwords
- **Validated**: Scripts kiểm tra lỗi tự động
- **Maintainable**: Dễ update và debug
- **Scalable**: Có thể thêm PC3, PC4 dễ dàng

Hệ thống này đảm bảo 100% không có port conflicts và password mismatches giữa các modules!
