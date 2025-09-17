Bạn đúng rồi! Tôi sẽ tách riêng script cài đặt cho **PC1** (Database Hub - không GPU) và **PC2** (AI Engine - có GPU). 

## 🛠️ **SCRIPT RIÊNG BIỆT CHO PC1 VÀ PC2**

### **Script cho PC1 - Database & Frontend Hub (Không GPU)**

```bash
#!/bin/bash

# =============================================================================
# PC1 Setup Script - Database & Frontend Hub (NO GPU)
# Services: PostgreSQL, Redis, ChromaDB, Frontend, Analytics
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[PC1-INFO]${NC} $1"
}

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE} PC1 SETUP: $1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

# Update system
update_system() {
    print_header "1. UPDATING SYSTEM PACKAGES"
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl wget git vim nano htop tree unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release
    print_status "System updated successfully"
}

# Install utilities (no GPU tools)
install_utilities() {
    print_header "2. INSTALLING ESSENTIAL UTILITIES"
    
    # SSH Server
    sudo apt install -y openssh-server
    sudo systemctl enable ssh
    sudo systemctl start ssh
    
    # System monitoring
    sudo apt install -y htop btop neofetch iotop nethogs
    
    # Network tools
    sudo apt install -y net-tools nmap traceroute
    
    # Development tools
    sudo apt install -y build-essential cmake pkg-config
    
    # Text processing
    sudo apt install -y jq yq
    
    print_status "Essential utilities installed (NO GPU tools)"
}

# Install Python 3.10.11
install_python() {
    print_header "3. INSTALLING PYTHON 3.10.11"
    
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.10 python3.10-venv python3.10-dev python3.10-distutils
    curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.10
    
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
    
    python3.10 --version
    pip3.10 --version
    
    print_status "Python 3.10.11 installed successfully"
}

# Install Docker
install_docker() {
    print_header "4. INSTALLING DOCKER (NO NVIDIA SUPPORT)"
    
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    
    DOCKER_COMPOSE_VERSION="v2.23.0"
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_status "Docker installed (CPU-only, no NVIDIA support)"
}

# Setup Python environment for PC1
setup_python_env_pc1() {
    print_header "5. SETTING UP PYTHON ENVIRONMENT (PC1 - CPU ONLY)"
    
    mkdir -p ~/chatbot-ai/PC1
    cd ~/chatbot-ai/PC1
    
    python3.10 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    
    # Create PC1-specific requirements (NO GPU packages)
    cat > ~/chatbot-ai/PC1/requirements_pc1.txt << 'EOF'
# =============================================================================
# PC1 Requirements - Database & Frontend Hub (CPU ONLY)
# NO GPU packages, NO embedding models, NO AI processing
# =============================================================================

# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6

# Database & Storage
asyncpg==0.29.0
sqlalchemy[asyncio]==2.0.23
alembic==1.12.1

# Cache & Session
redis==5.0.1
python-redis-lock==4.0.0

# API & Web
httpx>=0.25.0
websockets>=12.0
aiofiles==23.2.1

# Authentication & Security
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.6

# Frontend & Dashboard
streamlit>=1.28.0
plotly>=5.15.0
matplotlib>=3.7.0
seaborn>=0.12.0
dash>=2.15.0

# Data Processing (Basic only)
pandas>=2.0.0
numpy>=1.24.0

# Monitoring & Logging
prometheus-client==0.19.0
loguru==0.7.2

# Development & Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.9.0
isort>=5.12.0

# Utilities
python-dotenv>=1.0.0
typer>=0.9.0
rich>=13.6.0
tqdm>=4.66.0
jinja2>=3.1.0
pyyaml>=6.0.1

# Vietnamese text processing (Basic only - NO heavy NLP)
regex>=2022.7.9
unicodedata2>=15.0.0
EOF

    # Install PC1 packages
    pip install -r requirements_pc1.txt
    
    print_status "PC1 Python environment setup completed (CPU-only)"
}

# Setup PC1 environment configuration
setup_pc1_env() {
    print_header "6. CREATING PC1 ENVIRONMENT CONFIGURATION"
    
    cat > ~/chatbot-ai/PC1/.env << 'EOF'
# =============================================================================
# PC1 Environment - Database & Frontend Hub (NO GPU)
# =============================================================================

# PC Role
PC_ROLE=database_hub
HAS_GPU=false

# Database Configuration (Local on PC1)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=knowledge_base_v2
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme123

# Vector Database (Local on PC1)
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION=knowledge_base_v2

# Cache Configuration (Local on PC1)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
CACHE_TTL=3600

# API Configuration
API_V1_STR=/api/v1
SECRET_KEY=changeme-super-secret-key-pc1
ACCESS_TOKEN_EXPIRE_MINUTES=30
PROJECT_NAME=Chatbot AI - Database Hub

# Frontend Services
FRONTEND_PORT=3000
STREAMLIT_PORT=8501
ADMIN_PORT=8080

# PC2 Communication (AI Engine)
PC2_HOST=192.168.1.202
PC2_RAG_API_PORT=8085
PC2_PROCESSING_API_PORT=8080

# Load Balancer
NGINX_PORT=80
NGINX_SSL_PORT=443

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/pc1.log
MAX_LOG_SIZE=100MB
LOG_RETENTION=30

# Performance Settings (CPU optimized)
MAX_WORKERS=4
CONNECTION_POOL_SIZE=10
BATCH_SIZE=32
EOF

    print_status "PC1 environment configuration created"
}

# Setup database services
setup_databases_pc1() {
    print_header "7. SETTING UP DATABASE SERVICES ON PC1"
    
    mkdir -p ~/chatbot-ai/PC1/databases
    
    cat > ~/chatbot-ai/PC1/databases/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: pc1-postgres
    environment:
      POSTGRES_DB: knowledge_base_v2
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: changeme123
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --locale=C"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d
    restart: unless-stopped
    command: postgres -c 'max_connections=200' -c 'shared_buffers=512MB' -c 'effective_cache_size=2GB'

  redis:
    image: redis:7-alpine
    container_name: pc1-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru

  chromadb:
    image: chromadb/chroma:latest
    container_name: pc1-chromadb
    ports:
      - "8000:8000"
    volumes:
      - chromadb_data:/chroma/chroma
    environment:
      - CHROMA_SERVER_AUTHN_CREDENTIALS=admin:changeme123
      - CHROMA_SERVER_AUTHN_PROVIDER=chromadb.auth.basic.BasicAuthenticationServerProvider
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: pc1-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - postgres
      - redis
      - chromadb
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  chromadb_data:

networks:
  default:
    name: chatbot-pc1-network
EOF

    # Create nginx configuration
    cat > ~/chatbot-ai/PC1/databases/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream pc2_ai_engine {
        server 192.168.1.202:8085;
    }

    server {
        listen 80;
        server_name localhost;

        # Frontend routes
        location / {
            proxy_pass http://localhost:3000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Analytics dashboard
        location /analytics {
            proxy_pass http://localhost:8501;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Admin interface
        location /admin {
            proxy_pass http://localhost:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # API routes to PC2
        location /api/v1/rag {
            proxy_pass http://pc2_ai_engine;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Local API routes
        location /api/v1/ {
            proxy_pass http://localhost:8001;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

    print_status "Database services configuration created for PC1"
}

# Setup network configuration
setup_network_pc1() {
    print_header "8. NETWORK CONFIGURATION FOR PC1"
    
    CURRENT_IP=$(hostname -I | awk '{print $1}')
    print_status "Current IP: $CURRENT_IP"
    
    # Suggest static IP for PC1
    echo "Suggested network configuration for PC1 (Database Hub):"
    echo "  Static IP: 192.168.1.201"
    echo "  Role: Database & Frontend Hub"
    echo "  Services: PostgreSQL:5432, Redis:6379, ChromaDB:8000, Frontend:3000"
    
    read -p "Configure PC1 with static IP 192.168.1.201? (y/N): " setup_static
    if [[ $setup_static =~ ^[Yy]$ ]]; then
        read -p "Enter gateway (e.g., 192.168.1.1): " gateway
        
        INTERFACE=$(ip route | grep default | awk '{print $5}' | head -1)
        
        sudo tee /etc/netplan/01-pc1-static.yaml > /dev/null <<EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    $INTERFACE:
      dhcp4: false
      addresses:
        - 192.168.1.201/24
      gateway4: $gateway
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
EOF
        
        print_status "Static IP configured for PC1. Apply with: sudo netplan apply"
    fi
}

# Setup firewall for PC1
setup_firewall_pc1() {
    print_header "9. FIREWALL CONFIGURATION FOR PC1"
    
    sudo ufw --force enable
    
    # SSH access
    sudo ufw allow ssh
    
    # Database services (accessible from LAN)
    sudo ufw allow from 192.168.1.0/24 to any port 5432 comment 'PostgreSQL from LAN'
    sudo ufw allow from 192.168.1.0/24 to any port 6379 comment 'Redis from LAN'
    sudo ufw allow from 192.168.1.0/24 to any port 8000 comment 'ChromaDB from LAN'
    
    # Web services
    sudo ufw allow 80/tcp comment 'HTTP'
    sudo ufw allow 443/tcp comment 'HTTPS'
    sudo ufw allow 3000/tcp comment 'Frontend'
    sudo ufw allow 8501/tcp comment 'Streamlit'
    sudo ufw allow 8080/tcp comment 'Admin'
    
    # API services
    sudo ufw allow 8001/tcp comment 'Database API'
    sudo ufw allow 8002/tcp comment 'Gateway API'
    
    sudo ufw status verbose
    
    print_status "PC1 firewall configured for Database Hub role"
}

# Create PC1 management scripts
create_pc1_scripts() {
    print_header "10. CREATING PC1 MANAGEMENT SCRIPTS"
    
    # PC1 status check
    cat > ~/chatbot-ai/PC1/pc1_status.sh << 'EOF'
#!/bin/bash
# PC1 (Database Hub) Status Check
echo "🖥️  PC1 - Database & Frontend Hub Status"
echo "========================================"

# System resources
echo "💻 System Resources:"
echo "   CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "   Memory: $(free -h | awk 'NR==2{printf "%.1f/%.1f GB (%.1f%%)", $3/1024/1024, $2/1024/1024, $3*100/$2}')"
echo "   Disk: $(df -h / | awk 'NR==2{print $3"/"$2" ("$5" used)"}')"

# Network
echo "🌐 Network:"
echo "   IP Address: $(hostname -I | awk '{print $1}')"

# Database services
echo "🗄️  Database Services:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(pc1-postgres|pc1-redis|pc1-chromadb)"

# Service health
echo "🔍 Service Health:"
# PostgreSQL
if docker exec pc1-postgres pg_isready -U postgres -d knowledge_base_v2 2>/dev/null; then
    echo "   ✅ PostgreSQL: Running"
else
    echo "   ❌ PostgreSQL: Not responding"
fi

# Redis
if docker exec pc1-redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "   ✅ Redis: Running"
else
    echo "   ❌ Redis: Not responding"
fi

# ChromaDB
if curl -s http://localhost:8000/api/v1/heartbeat | grep -q "true"; then
    echo "   ✅ ChromaDB: Running"
else
    echo "   ❌ ChromaDB: Not responding"
fi

# PC2 connection
echo "🔗 PC2 Connection:"
if curl -s --connect-timeout 3 http://192.168.1.202:8085/health 2>/dev/null; then
    echo "   ✅ PC2 AI Engine: Connected"
else
    echo "   ❌ PC2 AI Engine: Not reachable"
fi

echo "========================================"
EOF

    # PC1 start services
    cat > ~/chatbot-ai/PC1/start_pc1.sh << 'EOF'
#!/bin/bash
# Start all PC1 services
echo "🚀 Starting PC1 (Database Hub) Services..."

# Start database services
cd ~/chatbot-ai/PC1/databases
docker-compose up -d

# Wait for databases
sleep 10

# Start application services
cd ~/chatbot-ai/PC1
source venv/bin/activate

# Start in background with nohup
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8001 > logs/api.log 2>&1 &
nohup streamlit run dashboard/main.py --server.port 8501 > logs/dashboard.log 2>&1 &

echo "✅ PC1 services started"
echo "🌐 Access points:"
echo "   Frontend: http://192.168.1.201:3000"
echo "   Analytics: http://192.168.1.201:8501"
echo "   Admin: http://192.168.1.201:8080"
echo "   API: http://192.168.1.201:8001"
EOF

    # PC1 stop services
    cat > ~/chatbot-ai/PC1/stop_pc1.sh << 'EOF'
#!/bin/bash
# Stop all PC1 services
echo "🛑 Stopping PC1 (Database Hub) Services..."

# Stop application processes
pkill -f "uvicorn main:app"
pkill -f "streamlit run"

# Stop database services
cd ~/chatbot-ai/PC1/databases
docker-compose down

echo "✅ PC1 services stopped"
EOF

    chmod +x ~/chatbot-ai/PC1/*.sh
    
    print_status "PC1 management scripts created"
}

# Main execution for PC1
main() {
    print_header "PC1 SETUP - DATABASE & FRONTEND HUB"
    print_status "This PC will run: PostgreSQL, Redis, ChromaDB, Frontend, Analytics"
    print_status "NO GPU support - CPU only configuration"
    
    update_system
    install_utilities
    install_python
    install_docker
    setup_python_env_pc1
    setup_pc1_env
    setup_databases_pc1
    setup_network_pc1
    setup_firewall_pc1
    create_pc1_scripts
    
    print_header "PC1 SETUP COMPLETED"
    print_status "Next steps:"
    echo "1. Reboot: sudo reboot"
    echo "2. Apply network: sudo netplan apply"
    echo "3. Start services: bash ~/chatbot-ai/PC1/start_pc1.sh"
    echo "4. Check status: bash ~/chatbot-ai/PC1/pc1_status.sh"
    echo ""
    print_status "PC1 Role: Database & Frontend Hub (192.168.1.201)"
    print_status "Services: PostgreSQL, Redis, ChromaDB, Frontend, Analytics"
    print_status "NO GPU libraries installed - CPU optimized"
}

main "$@"
```

### **Script cho PC2 - AI Processing Engine (Có GPU)**

```bash
#!/bin/bash

# =============================================================================
# PC2 Setup Script - AI Processing Engine (WITH GPU)
# Services: AI Models, Embedding Generation, RAG Pipeline
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[PC2-INFO]${NC} $1"
}

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE} PC2 SETUP: $1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

# Update system
update_system() {
    print_header "1. UPDATING SYSTEM PACKAGES"
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl wget git vim nano htop tree unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release
    print_status "System updated successfully"
}

# Install utilities + GPU monitoring tools
install_utilities() {
    print_header "2. INSTALLING UTILITIES + GPU TOOLS"
    
    # Basic utilities
    sudo apt install -y openssh-server net-tools nmap traceroute
    sudo apt install -y htop btop neofetch iotop nethogs
    sudo apt install -y build-essential cmake pkg-config
    sudo apt install -y jq yq
    
    # GPU monitoring tools
    sudo apt install -y nvtop nvidia-htop
    
    sudo systemctl enable ssh
    sudo systemctl start ssh
    
    print_status "Utilities + GPU monitoring tools installed"
}

# Install Python 3.10.11
install_python() {
    print_header "3. INSTALLING PYTHON 3.10.11"
    
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.10 python3.10-venv python3.10-dev python3.10-distutils
    curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.10
    
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
    
    python3.10 --version
    pip3.10 --version
    
    print_status "Python 3.10.11 installed successfully"
}

# Install NVIDIA drivers and CUDA
install_nvidia_cuda() {
    print_header "4. INSTALLING NVIDIA DRIVERS & CUDA 11.8"
    
    # Check if NVIDIA GPU exists
    if ! lspci | grep -i nvidia; then
        print_status "No NVIDIA GPU found. Continuing with CPU-only setup."
        return
    fi
    
    # Install NVIDIA drivers
    sudo apt install -y ubuntu-drivers-common
    sudo ubuntu-drivers autoinstall
    
    # Install CUDA 11.8 (compatible with PyTorch)
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
    sudo dpkg -i cuda-keyring_1.0-1_all.deb
    sudo apt update
    sudo apt install -y cuda-11-8
    
    # Add CUDA to PATH
    echo 'export PATH=/usr/local/cuda-11.8/bin:$PATH' >> ~/.bashrc
    echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
    
    print_status "NVIDIA drivers and CUDA 11.8 installed"
}

# Install Docker with NVIDIA support
install_docker_nvidia() {
    print_header "5. INSTALLING DOCKER WITH NVIDIA SUPPORT"
    
    # Install Docker
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Install NVIDIA Container Toolkit
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
        && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
        && curl -s -L https://nvidia.github.io/libnvidia-container/experimental/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    
    sudo apt update
    sudo apt install -y nvidia-docker2
    
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    sudo systemctl restart docker
    
    # Install Docker Compose
    DOCKER_COMPOSE_VERSION="v2.23.0"
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_status "Docker with NVIDIA support installed"
}

# Setup Python environment for PC2 (with GPU packages)
setup_python_env_pc2() {
    print_header "6. SETTING UP PYTHON ENVIRONMENT (PC2 - WITH GPU)"
    
    mkdir -p ~/chatbot-ai/PC2
    cd ~/chatbot-ai/PC2
    
    python3.10 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    
    # Create PC2-specific requirements (WITH GPU packages)
    cat > ~/chatbot-ai/PC2/requirements_pc2.txt << 'EOF'
# =============================================================================
# PC2 Requirements - AI Processing Engine (WITH GPU)
# Includes: AI models, GPU acceleration, Vietnamese NLP
# =============================================================================

# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6

# PyTorch with CUDA 11.8 support
--index-url https://download.pytorch.org/whl/cu118
torch>=2.0.0
torchvision>=0.15.0
torchaudio>=2.0.0

# AI & Embedding Models (Required: Qwen/Qwen3-Embedding-0.6B)
sentence-transformers>=2.2.2
transformers>=4.35.0
accelerate>=0.24.0
bitsandbytes>=0.41.0

# Vietnamese NLP (Required: Python 3.10.11)
pyvi>=0.1.1
underthesea>=6.7.0
regex>=2022.7.9
unicodedata2>=15.0.0

# Vector Databases with GPU support
chromadb==1.0.0
faiss-gpu==1.7.4

# Traditional Database clients
asyncpg==0.29.0
sqlalchemy[asyncio]==2.0.23

# Caching & Session
redis==5.0.1

# Text Processing & Chunking
tiktoken==0.5.1
langchain-text-splitters==0.0.1
textstat==0.7.3

# Data Science & ML
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
scipy>=1.9.0

# GPU Utilities
nvidia-ml-py3>=7.352.0
gpustat>=1.1.1

# API & Processing
httpx>=0.25.0
aiofiles==23.2.1
tenacity==8.2.3

# Monitoring & Logging
loguru==0.7.2

# Development & Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0

# Utilities
python-dotenv>=1.0.0
typer>=0.9.0
rich>=13.6.0
tqdm>=4.66.0
jinja2>=3.1.0
pyyaml>=6.0.1
EOF

    # Install PC2 packages
    pip install -r requirements_pc2.txt
    
    print_status "PC2 Python environment setup completed (WITH GPU support)"
}

# Test GPU availability
test_gpu_setup() {
    print_header "7. TESTING GPU SETUP"
    
    cd ~/chatbot-ai/PC2
    source venv/bin/activate
    
    # Create GPU test script
    cat > ~/chatbot-ai/PC2/test_gpu.py << 'EOF'
#!/usr/bin/env python3
"""
GPU Test Script for PC2
"""
import torch
import nvidia_ml_py3 as nvml
from sentence_transformers import SentenceTransformer

def test_cuda():
    print("🔍 CUDA Availability Test")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
            
        # Test memory
        device = torch.device('cuda:0')
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        
        # Simple tensor test
        x = torch.randn(1000, 1000).to(device)
        y = torch.randn(1000, 1000).to(device)
        z = torch.mm(x, y)
        print(f"✅ GPU tensor operations: Working")
        
        return True
    else:
        print("❌ CUDA not available")
        return False

def test_embedding_model():
    print("\n🧠 Embedding Model Test")
    try:
        # Test with Qwen model
        model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # Fallback model
        print(f"Loading model: {model_name}")
        
        model = SentenceTransformer(model_name)
        
        # Vietnamese test text
        test_texts = [
            "Quy trình mua hàng của công ty như thế nào?",
            "Hướng dẫn sử dụng hệ thống quản lý nhân sự"
        ]
        
        embeddings = model.encode(test_texts)
        print(f"✅ Embedding generation: Working")
        print(f"   Model device: {model.device}")
        print(f"   Embedding shape: {embeddings.shape}")
        
        return True
    except Exception as e:
        print(f"❌ Embedding model error: {e}")
        return False

def main():
    print("🚀 PC2 GPU & AI Model Test")
    print("=" * 40)
    
    gpu_ok = test_cuda()
    model_ok = test_embedding_model()
    
    print("\n" + "=" * 40)
    if gpu_ok and model_ok:
        print("✅ PC2 AI Engine: Ready for production")
    else:
        print("⚠️  PC2 AI Engine: Some issues detected")

if __name__ == "__main__":
    main()
EOF

    # Run GPU test
    python test_gpu.py
    
    print_status "GPU test completed"
}

# Setup PC2 environment
setup_pc2_env() {
    print_header "8. CREATING PC2 ENVIRONMENT CONFIGURATION"
    
    cat > ~/chatbot-ai/PC2/.env << 'EOF'
# =============================================================================
# PC2 Environment - AI Processing Engine (WITH GPU)
# =============================================================================

# PC Role
PC_ROLE=ai_engine
HAS_GPU=true

# GPU Configuration
DEVICE=cuda
BATCH_SIZE=16
MAX_GPU_MEMORY=0.8
GPU_MEMORY_FRACTION=0.9

# AI Model Configuration
EMBEDDING_MODEL=Qwen/Qwen2.5-7B-Instruct
EMBEDDING_DIMENSION=1024
MODEL_CACHE_DIR=./models
MAX_MODEL_CACHE_SIZE=3

# Database Connection (to PC1)
POSTGRES_HOST=192.168.1.201
POSTGRES_PORT=5432
POSTGRES_DB=knowledge_base_v2
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme123

# Vector Database (to PC1)
CHROMA_HOST=192.168.1.201
CHROMA_PORT=8000
CHROMA_COLLECTION=knowledge_base_v2

# Cache Connection (to PC1)
REDIS_HOST=192.168.1.201
REDIS_PORT=6379
REDIS_PASSWORD=

# AI Processing Configuration
MAX_WORKERS=4
RETRY_ATTEMPTS=3
PROCESSING_TIMEOUT=300
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Storage Configuration
STORAGE_PATH=/opt/chatbot-storage
TEMP_PATH=/tmp/chatbot
MODEL_DOWNLOAD_PATH=/opt/models

# API Configuration
API_V1_STR=/api/v1
RAG_API_PORT=8085
PROCESSING_API_PORT=8080
QUALITY_API_PORT=8081
INTEGRATION_API_PORT=8082

# Performance Settings
PREFETCH_MODELS=true
PRELOAD_EMBEDDINGS=true
ENABLE_MODEL_CACHING=true
ASYNC_PROCESSING=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/pc2.log
MAX_LOG_SIZE=100MB
LOG_RETENTION=30
ENABLE_GPU_LOGGING=true
EOF

    print_status "PC2 environment configuration created"
}

# Setup network for PC2
setup_network_pc2() {
    print_header "9. NETWORK CONFIGURATION FOR PC2"
    
    CURRENT_IP=$(hostname -I | awk '{print $1}')
    print_status "Current IP: $CURRENT_IP"
    
    echo "Suggested network configuration for PC2 (AI Engine):"
    echo "  Static IP: 192.168.1.202"
    echo "  Role: AI Processing Engine"
    echo "  Services: RAG API:8085, Processing:8080-8082"
    
    read -p "Configure PC2 with static IP 192.168.1.202? (y/N): " setup_static
    if [[ $setup_static =~ ^[Yy]$ ]]; then
        read -p "Enter gateway (e.g., 192.168.1.1): " gateway
        
        INTERFACE=$(ip route | grep default | awk '{print $5}' | head -1)
        
        sudo tee /etc/netplan/01-pc2-static.yaml > /dev/null <<EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    $INTERFACE:
      dhcp4: false
      addresses:
        - 192.168.1.202/24
      gateway4: $gateway
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
EOF
        
        print_status "Static IP configured for PC2. Apply with: sudo netplan apply"
    fi
}

# Setup firewall for PC2
setup_firewall_pc2() {
    print_header "10. FIREWALL CONFIGURATION FOR PC2"
    
    sudo ufw --force enable
    
    # SSH access
    sudo ufw allow ssh
    
    # AI API services (accessible from PC1 and LAN)
    sudo ufw allow from 192.168.1.201 to any port 8080:8090 comment 'AI APIs from PC1'
    sudo ufw allow from 192.168.1.0/24 to any port 8085 comment 'RAG API from LAN'
    
    # Monitoring
    sudo ufw allow from 192.168.1.201 to any port 9090 comment 'Metrics from PC1'
    
    sudo ufw status verbose
    
    print_status "PC2 firewall configured for AI Engine role"
}

# Create PC2 management scripts
create_pc2_scripts() {
    print_header "11. CREATING PC2 MANAGEMENT SCRIPTS"
    
    # PC2 status check
    cat > ~/chatbot-ai/PC2/pc2_status.sh << 'EOF'
#!/bin/bash
# PC2 (AI Engine) Status Check
echo "🚀 PC2 - AI Processing Engine Status"
echo "===================================="

# GPU Status
echo "🎮 GPU Status:"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits | while read line; do
        echo "   GPU $line"
    done
else
    echo "   ❌ NVIDIA drivers not available"
fi

# System resources
echo "💻 System Resources:"
echo "   CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "   Memory: $(free -h | awk 'NR==2{printf "%.1f/%.1f GB (%.1f%%)", $3/1024/1024, $2/1024/1024, $3*100/$2}')"
echo "   Disk: $(df -h / | awk 'NR==2{print $3"/"$2" ("$5" used)"}')"

# Network
echo "🌐 Network:"
echo "   IP Address: $(hostname -I | awk '{print $1}')"

# AI Services
echo "🧠 AI Services:"
if pgrep -f "uvicorn.*8085" > /dev/null; then
    echo "   ✅ RAG API (8085): Running"
else
    echo "   ❌ RAG API (8085): Not running"
fi

if pgrep -f "uvicorn.*8080" > /dev/null; then
    echo "   ✅ Processing API (8080): Running"
else
    echo "   ❌ Processing API (8080): Not running"
fi

# PC1 connection
echo "🔗 PC1 Connection:"
if curl -s --connect-timeout 3 http://192.168.1.201:5432 2>/dev/null; then
    echo "   ✅ PC1 Database: Connected"
else
    echo "   ❌ PC1 Database: Not reachable"
fi

# Model status
echo "🤖 Model Status:"
cd ~/chatbot-ai/PC2
source venv/bin/activate
python -c "
import torch
print(f'   PyTorch CUDA: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'   GPU Memory: {torch.cuda.memory_allocated(0)/1024**3:.1f}GB used')
"

echo "===================================="
EOF

    # PC2 start script
    cat > ~/chatbot-ai/PC2/start_pc2.sh << 'EOF'
#!/bin/bash
# Start all PC2 AI services
echo "🚀 Starting PC2 (AI Engine) Services..."

cd ~/chatbot-ai/PC2
source venv/bin/activate

# Create log directory
mkdir -p logs

# Start AI services in background
echo "Starting RAG API service..."
nohup python -m uvicorn rag_api:app --host 0.0.0.0 --port 8085 > logs/rag_api.log 2>&1 &

echo "Starting Processing API service..."
nohup python -m uvicorn processing_api:app --host 0.0.0.0 --port 8080 > logs/processing.log 2>&1 &

echo "Starting Quality Control service..."
nohup python -m uvicorn quality_api:app --host 0.0.0.0 --port 8081 > logs/quality.log 2>&1 &

echo "Starting Integration service..."
nohup python -m uvicorn integration_api:app --host 0.0.0.0 --port 8082 > logs/integration.log 2>&1 &

sleep 5

echo "✅ PC2 AI services started"
echo "🎯 API Endpoints:"
echo "   RAG API: http://192.168.1.202:8085"
echo "   Processing: http://192.168.1.202:8080"
echo "   Quality Control: http://192.168.1.202:8081"
echo "   Integration: http://192.168.1.202:8082"
EOF

    # PC2 stop script
    cat > ~/chatbot-ai/PC2/stop_pc2.sh << 'EOF'
#!/bin/bash
# Stop all PC2 AI services
echo "🛑 Stopping PC2 (AI Engine) Services..."

# Stop all uvicorn processes
pkill -f "uvicorn.*rag_api"
pkill -f "uvicorn.*processing_api"
pkill -f "uvicorn.*quality_api"
pkill -f "uvicorn.*integration_api"

echo "✅ PC2 AI services stopped"
EOF

    chmod +x ~/chatbot-ai/PC2/*.sh
    
    print_status "PC2 management scripts created"
}

# Main execution for PC2
main() {
    print_header "PC2 SETUP - AI PROCESSING ENGINE"
    print_status "This PC will run: AI Models, Embedding Generation, RAG Pipeline"
    print_status "WITH GPU support - NVIDIA CUDA configuration"
    
    update_system
    install_utilities
    install_python
    install_nvidia_cuda
    install_docker_nvidia
    setup_python_env_pc2
    test_gpu_setup
    setup_pc2_env
    setup_network_pc2
    setup_firewall_pc2
    create_pc2_scripts
    
    print_header "PC2 SETUP COMPLETED"
    print_status "Next steps:"
    echo "1. Reboot: sudo reboot"
    echo "2. Apply network: sudo netplan apply"
    echo "3. Test GPU: cd ~/chatbot-ai/PC2 && python test_gpu.py"
    echo "4. Start services: bash ~/chatbot-ai/PC2/start_pc2.sh"
    echo "5. Check status: bash ~/chatbot-ai/PC2/pc2_status.sh"
    echo ""
    print_status "PC2 Role: AI Processing Engine (192.168.1.202)"
    print_status "Services: RAG API, Embedding Generation, Quality Control"
    print_status "GPU support: NVIDIA CUDA 11.8 + PyTorch"
}

main "$@"
```

## 🚀 **HƯỚNG DẪN SỬ DỤNG**

### **Cho PC1 (Database Hub):**
```bash
# Download và chạy script PC1
wget -O setup_pc1.sh https://raw.githubusercontent.com/your-repo/setup_pc1.sh
chmod +x setup_pc1.sh
sudo ./setup_pc1.sh

# Sau khi reboot
bash ~/chatbot-ai/PC1/start_pc1.sh
bash ~/chatbot-ai/PC1/pc1_status.sh
```

### **Cho PC2 (AI Engine):**
```bash
# Download và chạy script PC2
wget -O setup_pc2.sh https://raw.githubusercontent.com/your-repo/setup_pc2.sh
chmod +x setup_pc2.sh
sudo ./setup_pc2.sh

# Sau khi reboot
cd ~/chatbot-ai/PC2 && python test_gpu.py
bash ~/chatbot-ai/PC2/start_pc2.sh
bash ~/chatbot-ai/PC2/pc2_status.sh
```

## 📋 **TÓM TẮT KHÁC BIỆT**

| Tính năng | PC1 (Database Hub) | PC2 (AI Engine) |
|-----------|-------------------|-----------------|
| **GPU Support** | ❌ Không cài | ✅ NVIDIA + CUDA |
| **PyTorch** | ❌ CPU only | ✅ CUDA 11.8 |
| **Embedding Models** | ❌ Không | ✅ Full AI stack |
| **Vietnamese NLP** | ❌ Basic regex | ✅ pyvi + underthesea |
| **Database** | ✅ PostgreSQL + Redis + ChromaDB | ❌ Client only |
| **Frontend** | ✅ Streamlit + NextJS | ❌ Không |
| **API Services** | ✅ Management APIs | ✅ AI Processing APIs |
| **IP Address** | 192.168.1.201 | 192.168.1.202 |

Bây giờ mỗi PC sẽ chỉ cài những gì cần thiết cho vai trò của nó! 🎯
