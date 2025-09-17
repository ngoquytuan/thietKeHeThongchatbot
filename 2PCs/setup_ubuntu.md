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

---
Tôi sẽ tạo script setup hoàn chỉnh cho Ubuntu dựa trên requirements của dự án. Đây là script triển khai tự động:Dựa trên requirements của dự án, tôi sẽ tạo script setup hoàn chỉnh cho Ubuntu:

## 🛠️ **SCRIPT SETUP UBUNTU CHO DỰ ÁN CHATBOT AI**

### **Script 1: setup_ubuntu_base.sh - Cài đặt cơ bản**

```bash
#!/bin/bash

# =============================================================================
# Ubuntu Setup Script for Chatbot AI Project
# Compatible with: Ubuntu 20.04/22.04 LTS
# Target: PC1 (Database Hub) & PC2 (AI Engine)
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

# Function: Update system
update_system() {
    print_header "1. UPDATING SYSTEM PACKAGES"
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl wget git vim nano htop tree unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release
    print_status "System updated successfully"
}

# Function: Install essential utilities
install_utilities() {
    print_header "2. INSTALLING ESSENTIAL UTILITIES"
    
    # SSH Server (for remote management)
    sudo apt install -y openssh-server
    sudo systemctl enable ssh
    sudo systemctl start ssh
    
    # System monitoring tools
    sudo apt install -y htop btop neofetch iotop nethogs
    
    # Network tools
    sudo apt install -y net-tools nmap traceroute
    
    # Development tools
    sudo apt install -y build-essential cmake pkg-config
    
    # Text processing tools
    sudo apt install -y jq yq
    
    print_status "Essential utilities installed"
}

# Function: Install Python 3.10.11 (Required for underthesea, pyvi)
install_python() {
    print_header "3. INSTALLING PYTHON 3.10.11"
    
    # Add deadsnakes PPA for Python versions
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    
    # Install Python 3.10.11 and required packages
    sudo apt install -y python3.10 python3.10-venv python3.10-dev python3.10-distutils
    
    # Install pip for Python 3.10
    curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.10
    
    # Create symlinks
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
    
    # Verify installation
    python3.10 --version
    pip3.10 --version
    
    print_status "Python 3.10.11 installed successfully"
}

# Function: Install Docker & Docker Compose
install_docker() {
    print_header "4. INSTALLING DOCKER & DOCKER COMPOSE"
    
    # Remove old Docker versions
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    # Install Docker Compose standalone
    DOCKER_COMPOSE_VERSION="v2.23.0"
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_status "Docker & Docker Compose installed"
    print_warning "Please logout and login again to use Docker without sudo"
}

# Function: Install NVIDIA drivers and CUDA (for PC2 only)
install_nvidia_cuda() {
    print_header "5. INSTALLING NVIDIA DRIVERS & CUDA (Optional - PC2 only)"
    
    read -p "Is this PC2 (AI Engine) with NVIDIA GPU? (y/N): " install_gpu
    if [[ $install_gpu =~ ^[Yy]$ ]]; then
        # Check if NVIDIA GPU exists
        if command -v nvidia-smi &> /dev/null; then
            print_status "NVIDIA drivers already installed"
        else
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
        fi
        
        # Install NVIDIA Container Toolkit for Docker
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
            && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
            && curl -s -L https://nvidia.github.io/libnvidia-container/experimental/$distribution/libnvidia-container.list | \
                sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
                sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
        
        sudo apt update
        sudo apt install -y nvidia-docker2
        sudo systemctl restart docker
        
        print_status "NVIDIA drivers and CUDA installed"
        print_warning "Please reboot the system to complete GPU setup"
    else
        print_status "Skipping NVIDIA/CUDA installation"
    fi
}

# Function: Setup network configuration
setup_network() {
    print_header "6. NETWORK CONFIGURATION"
    
    # Get current IP
    CURRENT_IP=$(hostname -I | awk '{print $1}')
    print_status "Current IP: $CURRENT_IP"
    
    read -p "Configure static IP? (y/N): " setup_static
    if [[ $setup_static =~ ^[Yy]$ ]]; then
        read -p "Enter static IP (e.g., 192.168.1.201): " static_ip
        read -p "Enter gateway (e.g., 192.168.1.1): " gateway
        read -p "Enter DNS servers (e.g., 8.8.8.8,8.8.4.4): " dns_servers
        
        # Backup current netplan
        sudo cp /etc/netplan/*.yaml /etc/netplan/backup-$(date +%Y%m%d).yaml 2>/dev/null || true
        
        # Create new netplan configuration
        INTERFACE=$(ip route | grep default | awk '{print $5}' | head -1)
        
        sudo tee /etc/netplan/01-network-manager-all.yaml > /dev/null <<EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    $INTERFACE:
      dhcp4: false
      addresses:
        - $static_ip/24
      gateway4: $gateway
      nameservers:
        addresses: [${dns_servers//,/, }]
EOF
        
        print_status "Static IP configured. Apply with: sudo netplan apply"
    fi
}

# Function: Configure firewall
setup_firewall() {
    print_header "7. FIREWALL CONFIGURATION"
    
    # Enable UFW
    sudo ufw --force enable
    
    # SSH access
    sudo ufw allow ssh
    
    # Common ports for the project
    sudo ufw allow 80/tcp comment 'HTTP'
    sudo ufw allow 443/tcp comment 'HTTPS'
    sudo ufw allow 5432/tcp comment 'PostgreSQL'
    sudo ufw allow 6379/tcp comment 'Redis'
    sudo ufw allow 8000/tcp comment 'ChromaDB'
    sudo ufw allow 3000/tcp comment 'Frontend'
    sudo ufw allow 8501/tcp comment 'Streamlit'
    sudo ufw allow from 192.168.1.0/24 comment 'LAN access'
    
    # Show status
    sudo ufw status verbose
    
    print_status "Firewall configured"
}

# Main execution
main() {
    print_header "UBUNTU SETUP FOR CHATBOT AI PROJECT"
    
    update_system
    install_utilities
    install_python
    install_docker
    install_nvidia_cuda
    setup_network
    setup_firewall
    
    print_header "SETUP COMPLETED"
    print_status "Next steps:"
    echo "1. Reboot the system: sudo reboot"
    echo "2. Run setup_python_env.sh to setup Python environment"
    echo "3. Run setup_databases.sh to setup databases"
    echo "4. Configure your project-specific settings"
    
    print_warning "Please reboot before proceeding with Python environment setup"
}

# Run main function
main "$@"
```

### **Script 2: setup_python_env.sh - Môi trường Python**

```bash
#!/bin/bash

# =============================================================================
# Python Environment Setup for Chatbot AI Project
# Requirements: Python 3.10.11, Vietnamese NLP, GPU support
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

# Create project structure
create_project_structure() {
    print_header "1. CREATING PROJECT STRUCTURE"
    
    # Create main directories
    mkdir -p ~/chatbot-ai/{PC1,PC2,shared}
    mkdir -p ~/chatbot-ai/PC1/{FR02,FR05,FR07,FR08}
    mkdir -p ~/chatbot-ai/PC2/{FR03,FR04}
    mkdir -p ~/chatbot-ai/shared/{docs,scripts,configs}
    
    print_status "Project structure created in ~/chatbot-ai/"
}

# Setup Python virtual environment
setup_python_env() {
    print_header "2. SETTING UP PYTHON VIRTUAL ENVIRONMENT"
    
    cd ~/chatbot-ai
    
    # Create virtual environment with Python 3.10
    python3.10 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    print_status "Virtual environment created and activated"
}

# Install base requirements
install_base_requirements() {
    print_header "3. INSTALLING BASE PYTHON PACKAGES"
    
    # Create requirements.txt
    cat > ~/chatbot-ai/requirements.txt << 'EOF'
# =============================================================================
# Python Requirements for Chatbot AI Project
# Compatible with: Python 3.10.11
# =============================================================================

# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6

# Embedding & AI Models (Qwen/Qwen3-Embedding-0.6B required)
sentence-transformers>=2.2.2
transformers>=4.35.0
torch>=2.0.0
torchvision>=0.15.0
torchaudio>=2.0.0

# Vietnamese NLP (Required: Python 3.10.11)
pyvi>=0.1.1
underthesea>=6.7.0
regex>=2022.7.9
unicodedata2>=15.0.0

# Vector Databases
chromadb==1.0.0
faiss-cpu==1.7.4

# Traditional Databases
asyncpg==0.29.0
sqlalchemy[asyncio]==2.0.23
alembic==1.12.1

# Caching & Session
redis==5.0.1
python-redis-lock==4.0.0

# Text Processing
tiktoken==0.5.1
langchain-text-splitters==0.0.1
textstat==0.7.3

# Data Science & ML
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
scipy>=1.9.0

# Web & API
httpx>=0.25.0
websockets>=12.0
aiofiles==23.2.1

# Monitoring & Logging
prometheus-client==0.19.0
loguru==0.7.2
tenacity==8.2.3

# Visualization & Reporting
streamlit>=1.28.0
plotly>=5.15.0
matplotlib>=3.7.0
seaborn>=0.12.0

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

# Security
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.6
EOF

    # Install packages
    source venv/bin/activate
    pip install -r requirements.txt
    
    print_status "Base requirements installed"
}

# Install GPU-specific packages (for PC2)
install_gpu_packages() {
    print_header "4. GPU PACKAGES INSTALLATION"
    
    read -p "Install GPU-optimized packages for PC2? (y/N): " install_gpu
    if [[ $install_gpu =~ ^[Yy]$ ]]; then
        source venv/bin/activate
        
        # Install PyTorch with CUDA 11.8 support
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        
        # Install GPU-accelerated packages
        pip install faiss-gpu==1.7.4
        pip install accelerate>=0.24.0
        pip install bitsandbytes>=0.41.0
        
        # Install CUDA-specific utilities
        pip install nvidia-ml-py3>=7.352.0
        
        print_status "GPU packages installed"
        
        # Test GPU availability
        python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU Count: {torch.cuda.device_count()}'); print(f'GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"No GPU\"}')"
    else
        print_status "Skipping GPU packages"
    fi
}

# Download and test embedding models
setup_embedding_models() {
    print_header "5. DOWNLOADING EMBEDDING MODELS"
    
    source venv/bin/activate
    
    # Create model test script
    cat > ~/chatbot-ai/test_models.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for embedding models
"""
import torch
from sentence_transformers import SentenceTransformer
import time

def test_embedding_model(model_name):
    print(f"\n🧪 Testing model: {model_name}")
    try:
        start_time = time.time()
        model = SentenceTransformer(model_name)
        load_time = time.time() - start_time
        
        # Test Vietnamese text
        test_texts = [
            "Quy trình mua hàng của công ty như thế nào?",
            "Hướng dẫn sử dụng hệ thống quản lý nhân sự",
            "Company procurement process guidelines"
        ]
        
        start_time = time.time()
        embeddings = model.encode(test_texts)
        encode_time = time.time() - start_time
        
        print(f"✅ Model loaded successfully")
        print(f"   Load time: {load_time:.2f}s")
        print(f"   Encode time: {encode_time:.2f}s")
        print(f"   Embedding dim: {embeddings.shape[1]}")
        print(f"   Device: {model.device}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Testing Embedding Models for Vietnamese Chatbot")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    # Test models according to project requirements
    models = [
        "Qwen/Qwen2.5-7B-Instruct",  # Primary choice
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",  # Backup
        "intfloat/multilingual-e5-base"  # Alternative
    ]
    
    for model_name in models:
        test_embedding_model(model_name)
        print("-" * 50)

if __name__ == "__main__":
    main()
EOF

    chmod +x ~/chatbot-ai/test_models.py
    
    print_status "Model test script created. Run: python test_models.py"
}

# Create environment files
create_env_files() {
    print_header "6. CREATING ENVIRONMENT CONFIGURATION"
    
    # PC1 Environment (Database Hub)
    cat > ~/chatbot-ai/PC1/.env << 'EOF'
# =============================================================================
# PC1 Environment - Database & Frontend Hub
# =============================================================================

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=knowledge_base_v2
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme123

# Vector Database
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION=knowledge_base_v2

# Cache Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
CACHE_TTL=3600

# API Configuration
API_V1_STR=/api/v1
SECRET_KEY=changeme-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
PROJECT_NAME=Chatbot AI - Database Hub

# Frontend Configuration
FRONTEND_PORT=3000
STREAMLIT_PORT=8501
ADMIN_PORT=8080

# Network Configuration
PC2_HOST=192.168.1.202
PC2_API_PORT=8085

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/pc1.log
EOF

    # PC2 Environment (AI Engine)
    cat > ~/chatbot-ai/PC2/.env << 'EOF'
# =============================================================================
# PC2 Environment - AI Processing Engine
# =============================================================================

# GPU Configuration
DEVICE=cuda
BATCH_SIZE=16
MAX_GPU_MEMORY=0.8

# Embedding Models
EMBEDDING_MODEL=Qwen/Qwen2.5-7B-Instruct
EMBEDDING_DIMENSION=1024
MODEL_CACHE_DIR=./models

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

# Cache (to PC1)
REDIS_HOST=192.168.1.201
REDIS_PORT=6379
REDIS_PASSWORD=

# AI Processing Configuration
MAX_WORKERS=4
RETRY_ATTEMPTS=3
PROCESSING_TIMEOUT=300

# Storage Configuration
STORAGE_PATH=/opt/chatbot-storage
TEMP_PATH=/tmp/chatbot

# API Configuration
API_V1_STR=/api/v1
RAG_API_PORT=8085
PROCESSING_API_PORT=8080

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/pc2.log
EOF

    print_status "Environment files created"
}

# Create helper scripts
create_helper_scripts() {
    print_header "7. CREATING HELPER SCRIPTS"
    
    # Environment activation script
    cat > ~/chatbot-ai/activate.sh << 'EOF'
#!/bin/bash
# Activate chatbot AI environment
echo "🤖 Activating Chatbot AI Environment"
cd ~/chatbot-ai
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
echo "✅ Environment activated"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Virtual env: $VIRTUAL_ENV"
EOF

    # System check script
    cat > ~/chatbot-ai/check_system.sh << 'EOF'
#!/bin/bash
# System health check for Chatbot AI
echo "🔍 System Health Check"
echo "======================="

# Python environment
echo "Python version: $(python3.10 --version 2>/dev/null || echo 'Not installed')"
echo "Pip version: $(pip3.10 --version 2>/dev/null || echo 'Not installed')"

# Docker
echo "Docker version: $(docker --version 2>/dev/null || echo 'Not installed')"
echo "Docker Compose version: $(docker-compose --version 2>/dev/null || echo 'Not installed')"

# NVIDIA (if available)
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA Driver: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits)"
    echo "CUDA Version: $(nvcc --version 2>/dev/null | grep release | awk '{print $6}' | cut -c9-)"
else
    echo "NVIDIA: Not available"
fi

# Network connectivity
echo "Network status:"
ping -c 1 8.8.8.8 &>/dev/null && echo "  ✅ Internet: Connected" || echo "  ❌ Internet: Disconnected"

# Disk space
echo "Disk usage:"
df -h / | awk 'NR==2 {print "  Root: " $3 "/" $2 " (" $5 " used)"}'

# Memory
echo "Memory usage:"
free -h | awk 'NR==2 {print "  RAM: " $3 "/" $2 " (" int($3/$2*100) "% used)"}'

echo "======================="
echo "✅ System check completed"
EOF

    chmod +x ~/chatbot-ai/activate.sh
    chmod +x ~/chatbot-ai/check_system.sh
    
    print_status "Helper scripts created"
}

# Main execution
main() {
    print_header "PYTHON ENVIRONMENT SETUP"
    
    create_project_structure
    setup_python_env
    install_base_requirements
    install_gpu_packages
    setup_embedding_models
    create_env_files
    create_helper_scripts
    
    print_header "PYTHON ENVIRONMENT SETUP COMPLETED"
    print_status "Next steps:"
    echo "1. Activate environment: source ~/chatbot-ai/activate.sh"
    echo "2. Test models: cd ~/chatbot-ai && python test_models.py"
    echo "3. Check system: bash ~/chatbot-ai/check_system.sh"
    echo "4. Run database setup: bash setup_databases.sh"
    
    echo ""
    echo "📁 Project structure created in: ~/chatbot-ai/"
    echo "🔧 Environment files: PC1/.env and PC2/.env"
    echo "🧪 Test script: test_models.py"
}

main "$@"
```

### **Script 3: setup_databases.sh - Cơ sở dữ liệu**

```bash
#!/bin/bash

# =============================================================================
# Database Setup for Chatbot AI Project
# Includes: PostgreSQL, Redis, ChromaDB
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

# Setup PostgreSQL
setup_postgresql() {
    print_header "1. SETTING UP POSTGRESQL"
    
    # Create Docker Compose for databases
    mkdir -p ~/chatbot-ai/databases
    
    cat > ~/chatbot-ai/databases/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: chatbot-postgres
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
    command: postgres -c 'max_connections=200' -c 'shared_buffers=256MB' -c 'effective_cache_size=1GB'

  redis:
    image: redis:7-alpine
    container_name: chatbot-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru

  chromadb:
    image: chromadb/chroma:latest
    container_name: chatbot-chromadb
    ports:
      - "8000:8000"
    volumes:
      - chromadb_data:/chroma/chroma
    environment:
      - CHROMA_SERVER_AUTHN_CREDENTIALS=admin:changeme123
      - CHROMA_SERVER_AUTHN_PROVIDER=chromadb.auth.basic.BasicAuthenticationServerProvider
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  chromadb_data:

networks:
  default:
    name: chatbot-network
EOF

    # Create database initialization script
    mkdir -p ~/chatbot-ai/databases/init
    
    cat > ~/chatbot-ai/databases/init/01-create-extensions.sql << 'EOF'
-- Create necessary extensions for Vietnamese text processing
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create Vietnamese collation
CREATE COLLATION IF NOT EXISTS vietnamese (provider = icu, locale = 'vi-VN');

-- Set timezone
SET timezone = 'Asia/Ho_Chi_Minh';
EOF

    print_status "PostgreSQL configuration created"
}

# Start database services
start_databases() {
    print_header "2. STARTING DATABASE SERVICES"
    
    cd ~/chatbot-ai/databases
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for databases to be ready..."
    sleep 10
    
    # Check PostgreSQL
    until docker exec chatbot-postgres pg_isready -U postgres -d knowledge_base_v2; do
        print_warning "Waiting for PostgreSQL..."
        sleep 2
    done
    
    # Check Redis
    until docker exec chatbot-redis redis-cli ping | grep -q PONG; do
        print_warning "Waiting for Redis..."
        sleep 2
    done
    
    # Check ChromaDB
    until curl -s http://localhost:8000/api/v1/heartbeat | grep -q "true"; do
        print_warning "Waiting for ChromaDB..."
        sleep 2
    done
    
    print_status "All database services are ready"
}

# Create database schema
create_schema() {
    print_header "3. CREATING DATABASE SCHEMA"
    
    cat > ~/chatbot-ai/databases/schema.sql << 'EOF'
-- =============================================================================
-- Knowledge Base Database Schema v2.1
-- Compatible with FR-01.2 requirements
-- =============================================================================

-- Document types enum
CREATE TYPE document_type_enum AS ENUM (
    'policy', 'procedure', 'manual', 'form', 
    'report', 'presentation', 'spreadsheet', 'other'
);

-- Document status enum
CREATE TYPE document_status_enum AS ENUM (
    'active', 'draft', 'archived', 'deleted'
);

-- Department enum
CREATE TYPE department_enum AS ENUM (
    'HR', 'Finance', 'IT', 'Marketing', 'Operations', 'General'
);

-- Access level enum
CREATE TYPE access_level_enum AS ENUM (
    'public', 'internal', 'confidential', 'restricted'
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    department department_enum NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'employee',
    access_level access_level_enum NOT NULL DEFAULT 'internal',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents metadata table
CREATE TABLE IF NOT EXISTS documents_metadata_v2 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    file_path VARCHAR(1000),
    file_size BIGINT,
    file_hash VARCHAR(64),
    document_type document_type_enum NOT NULL,
    department department_enum NOT NULL,
    access_level access_level_enum NOT NULL DEFAULT 'internal',
    status document_status_enum NOT NULL DEFAULT 'active',
    language VARCHAR(10) DEFAULT 'vi',
    author VARCHAR(255),
    version VARCHAR(20) DEFAULT '1.0',
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    chunk_count INTEGER DEFAULT 0,
    embedding_status VARCHAR(50) DEFAULT 'pending'
);

-- Document chunks table
CREATE TABLE IF NOT EXISTS document_chunks_v2 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_length INTEGER NOT NULL,
    token_count INTEGER,
    chunk_type VARCHAR(50) DEFAULT 'paragraph',
    metadata JSONB,
    embedding_vector FLOAT8[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

-- Data ingestion jobs table
CREATE TABLE IF NOT EXISTS data_ingestion_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    total_documents INTEGER DEFAULT 0,
    processed_documents INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(id)
);

-- System metrics table
CREATE TABLE IF NOT EXISTS system_health_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT8 NOT NULL,
    metric_unit VARCHAR(20),
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_documents_department ON documents_metadata_v2(department);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents_metadata_v2(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents_metadata_v2(status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents_metadata_v2(created_at);
CREATE INDEX IF NOT EXISTS idx_documents_access_level ON documents_metadata_v2(access_level);
CREATE INDEX IF NOT EXISTS idx_documents_title_gin ON documents_metadata_v2 USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_documents_content_gin ON documents_metadata_v2 USING gin(to_tsvector('english', content));

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks_v2(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_content_gin ON document_chunks_v2 USING gin(to_tsvector('english', content));

CREATE INDEX IF NOT EXISTS idx_jobs_status ON data_ingestion_jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON data_ingestion_jobs(created_at);

CREATE INDEX IF NOT EXISTS idx_metrics_name_time ON system_health_metrics(metric_name, collected_at);

-- Create sample data
INSERT INTO users (username, email, full_name, department, role, access_level) VALUES
('admin', 'admin@company.com', 'System Administrator', 'IT', 'admin', 'restricted'),
('john.doe', 'john.doe@company.com', 'John Doe', 'IT', 'manager', 'confidential'),
('jane.smith', 'jane.smith@company.com', 'Jane Smith', 'HR', 'employee', 'internal')
ON CONFLICT (username) DO NOTHING;

-- Update timestamps trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents_metadata_v2
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
EOF

    # Apply schema
    docker exec -i chatbot-postgres psql -U postgres -d knowledge_base_v2 < ~/chatbot-ai/databases/schema.sql
    
    print_status "Database schema created successfully"
}

# Test database connections
test_connections() {
    print_header "4. TESTING DATABASE CONNECTIONS"
    
    # Test PostgreSQL
    if docker exec chatbot-postgres psql -U postgres -d knowledge_base_v2 -c "SELECT COUNT(*) FROM users;" > /dev/null; then
        print_status "✅ PostgreSQL: Connected and working"
    else
        print_error "❌ PostgreSQL: Connection failed"
    fi
    
    # Test Redis
    if docker exec chatbot-redis redis-cli ping | grep -q PONG; then
        print_status "✅ Redis: Connected and working"
    else
        print_error "❌ Redis: Connection failed"
    fi
    
    # Test ChromaDB
    if curl -s http://localhost:8000/api/v1/heartbeat | grep -q "true"; then
        print_status "✅ ChromaDB: Connected and working"
        
        # Create default collection
        curl -X POST "http://localhost:8000/api/v1/collections" \
             -H "Content-Type: application/json" \
             -d '{
                 "name": "knowledge_base_v2",
                 "metadata": {"description": "Main knowledge base collection"}
             }' || true
    else
        print_error "❌ ChromaDB: Connection failed"
    fi
}

# Create database management scripts
create_management_scripts() {
    print_header "5. CREATING DATABASE MANAGEMENT SCRIPTS"
    
    # Database backup script
    cat > ~/chatbot-ai/databases/backup.sh << 'EOF'
#!/bin/bash
# Database backup script
BACKUP_DIR="~/chatbot-ai/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

echo "🔄 Creating database backup..."

# PostgreSQL backup
docker exec chatbot-postgres pg_dump -U postgres knowledge_base_v2 > "$BACKUP_DIR/postgres_$(date +%H%M%S).sql"

# Redis backup
docker exec chatbot-redis redis-cli --rdb - > "$BACKUP_DIR/redis_$(date +%H%M%S).rdb"

echo "✅ Backup completed: $BACKUP_DIR"
EOF

    # Database restore script
    cat > ~/chatbot-ai/databases/restore.sh << 'EOF'
#!/bin/bash
# Database restore script
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE=$1

echo "🔄 Restoring database from: $BACKUP_FILE"

if [[ $BACKUP_FILE == *.sql ]]; then
    # PostgreSQL restore
    docker exec -i chatbot-postgres psql -U postgres -d knowledge_base_v2 < "$BACKUP_FILE"
elif [[ $BACKUP_FILE == *.rdb ]]; then
    # Redis restore
    docker cp "$BACKUP_FILE" chatbot-redis:/data/dump.rdb
    docker restart chatbot-redis
fi

echo "✅ Restore completed"
EOF

    # Database status script
    cat > ~/chatbot-ai/databases/status.sh << 'EOF'
#!/bin/bash
# Database status check
echo "📊 Database Status Check"
echo "========================"

# PostgreSQL status
echo "PostgreSQL:"
docker exec chatbot-postgres psql -U postgres -d knowledge_base_v2 -c "
    SELECT 
        'Documents' as table_name, COUNT(*) as count 
    FROM documents_metadata_v2
    UNION ALL
    SELECT 
        'Chunks' as table_name, COUNT(*) as count 
    FROM document_chunks_v2
    UNION ALL
    SELECT 
        'Users' as table_name, COUNT(*) as count 
    FROM users;
"

# Redis status
echo -e "\nRedis:"
docker exec chatbot-redis redis-cli info memory | grep used_memory_human
docker exec chatbot-redis redis-cli dbsize

# ChromaDB status
echo -e "\nChromaDB:"
curl -s http://localhost:8000/api/v1/collections | jq .

echo "========================"
EOF

    chmod +x ~/chatbot-ai/databases/*.sh
    
    print_status "Database management scripts created"
}

# Main execution
main() {
    print_header "DATABASE SETUP FOR CHATBOT AI"
    
    setup_postgresql
    start_databases
    create_schema
    test_connections
    create_management_scripts
    
    print_header "DATABASE SETUP COMPLETED"
    print_status "Database services:"
    echo "  📄 PostgreSQL: localhost:5432 (knowledge_base_v2)"
    echo "  🔄 Redis: localhost:6379"
    echo "  🧠 ChromaDB: localhost:8000"
    echo ""
    print_status "Management commands:"
    echo "  📊 Status: bash ~/chatbot-ai/databases/status.sh"
    echo "  💾 Backup: bash ~/chatbot-ai/databases/backup.sh"
    echo "  🔄 Restore: bash ~/chatbot-ai/databases/restore.sh <file>"
    echo "  🛑 Stop: cd ~/chatbot-ai/databases && docker-compose down"
    echo "  ▶️  Start: cd ~/chatbot-ai/databases && docker-compose up -d"
}

main "$@"
```

## 🚀 **HƯỚNG DẪN TRIỂN KHAI**

### **Bước 1: Chạy script cài đặt cơ bản**
```bash
# Download và chạy script cài đặt cơ bản
curl -sSL https://raw.githubusercontent.com/your-repo/setup_ubuntu_base.sh -o setup_ubuntu_base.sh
chmod +x setup_ubuntu_base.sh
sudo ./setup_ubuntu_base.sh

# Reboot sau khi cài đặt
sudo reboot
```

### **Bước 2: Thiết lập môi trường Python**
```bash
# Download và chạy script Python
curl -sSL https://raw.githubusercontent.com/your-repo/setup_python_env.sh -o setup_python_env.sh
chmod +x setup_python_env.sh
./setup_python_env.sh
```

### **Bước 3: Cài đặt cơ sở dữ liệu**
```bash
# Download và chạy script database
curl -sSL https://raw.githubusercontent.com/your-repo/setup_databases.sh -o setup_databases.sh
chmod +x setup_databases.sh
./setup_databases.sh
```

### **Bước 4: Kiểm tra hệ thống**
```bash
# Kích hoạt môi trường
source ~/chatbot-ai/activate.sh

# Kiểm tra hệ thống
bash ~/chatbot-ai/check_system.sh

# Test models
cd ~/chatbot-ai && python test_models.py

# Kiểm tra databases
bash ~/chatbot-ai/databases/status.sh
```

## 📋 **CHECKLIST SAU KHI CÀI ĐẶT**

- [ ] Python 3.10.11 đã được cài đặt
- [ ] Virtual environment đã được tạo
- [ ] Docker và Docker Compose hoạt động
- [ ] NVIDIA drivers và CUDA (cho PC2)
- [ ] PostgreSQL, Redis, ChromaDB đang chạy
- [ ] Vietnamese NLP packages (pyvi, underthesea) hoạt động
- [ ] Embedding models download thành công
- [ ] Network configuration đúng
- [ ] Firewall rules được cấu hình
- [ ] SSH access hoạt động

Bạn có muốn tôi tạo thêm script deployment cho từng module cụ thể (FR02, FR03, v.v.) không?
