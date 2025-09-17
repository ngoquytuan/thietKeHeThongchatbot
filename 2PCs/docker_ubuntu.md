Bạn đúng rồi! Khi chuyển từ Windows sang Ubuntu có một số điều cần điều chỉnh. Đây là phiên bản **docker-compose.yml cho Ubuntu**:

## 🐧 **DOCKER-COMPOSE.YML CHO UBUNTU**

```yaml
#FR01.2 - Ubuntu Version

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: fr02-postgres-v2
    environment:
      POSTGRES_DB: knowledge_base_v2
      POSTGRES_USER: kb_admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C.UTF-8"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./config/postgres.conf:/etc/postgresql/postgresql.conf
      - ./scripts/01_init_database_V4.sql:/docker-entrypoint-initdb.d/01_init_database.sql
      # SHARED STORAGE cho file gốc (Ubuntu path)
      - chatbot_storage:/opt/chatbot-storage
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kb_admin -d knowledge_base_v2"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    networks:
      - fr02-network

  # PgBouncer Connection Pool
  pgbouncer:
    image: pgbouncer/pgbouncer:latest
    container_name: fr02-pgbouncer
    environment:
      DATABASES_HOST: postgres
      DATABASES_PORT: 5432
      DATABASES_USER: kb_admin
      DATABASES_PASSWORD: ${POSTGRES_PASSWORD}
      DATABASES_DBNAME: knowledge_base_v2
      POOL_MODE: transaction
      SERVER_RESET_QUERY: DISCARD ALL
      MAX_CLIENT_CONN: 1000
      DEFAULT_POOL_SIZE: 25
      MIN_POOL_SIZE: 5
      RESERVE_POOL_SIZE: 3
      MAX_DB_CONNECTIONS: 100
    ports:
      - "6432:5432"
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - fr02-network

  # ChromaDB Vector Database
  chroma:
    image: chromadb/chroma:1.0.0
    container_name: fr02-chroma-v2
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
      - ./config/chroma-config.yaml:/chroma/config.yaml
    environment:
      # Ubuntu: 0.0.0.0 vẫn ổn cho Docker containers
      - CHROMA_SERVER_HOST=0.0.0.0
      - CHROMA_SERVER_PORT=8000
      - CHROMA_SERVER_CORS_ALLOW_ORIGINS=["*"]
      - PERSIST_DIRECTORY=/chroma/chroma
      - CHROMA_SERVER_AUTH_CREDENTIALS_PROVIDER=chromadb.auth.token.TokenAuthCredentialsProvider
      - CHROMA_SERVER_AUTH_CREDENTIALS=${CHROMA_AUTH_TOKEN}
      - CHROMA_SERVER_AUTH_TOKEN_TRANSPORT_HEADER=X-Chroma-Token
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/api/v2/heartbeat || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    networks:
      - fr02-network

  # Redis Cache Cluster
  redis-master:
    image: redis:7-alpine
    container_name: fr02-redis-master
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./config/redis-master.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "redis-cli ping | grep PONG"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - fr02-network

  redis-replica:
    image: redis:7-alpine
    container_name: fr02-redis-replica
    ports:
      - "6380:6379"
    volumes:
      - redis_replica_data:/data
      - ./config/redis-replica.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    depends_on:
      - redis-master
    restart: unless-stopped
    networks:
      - fr02-network

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: fr02-prometheus
    ports:
      - "9090:9090"
    volumes:
      - prometheus_data:/prometheus
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./config/alert_rules.yml:/etc/prometheus/alert_rules.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    restart: unless-stopped
    networks:
      - fr02-network

  # Grafana Dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: fr02-grafana
    ports:
      - "3009:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=redis-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - prometheus
    restart: unless-stopped
    networks:
      - fr02-network

  # PostgreSQL Exporter
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: fr02-postgres-exporter
    environment:
      DATA_SOURCE_NAME: "postgresql://kb_admin:${POSTGRES_PASSWORD}@postgres:5432/knowledge_base_v2?sslmode=disable"
    ports:
      - "9187:9187"
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - fr02-network

  # Redis Exporter
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: fr02-redis-exporter
    environment:
      REDIS_ADDR: "redis://redis-master:6379"
    ports:
      - "9121:9121"
    depends_on:
      - redis-master
    restart: unless-stopped
    networks:
      - fr02-network

  # Node Exporter
  node-exporter:
    image: prom/node-exporter:latest
    container_name: fr02-node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
    networks:
      - fr02-network

  # Adminer Database Web Interface
  adminer:
    image: adminer:latest
    container_name: fr02-adminer
    ports:
      - "8081:8080"
    environment:
      - ADMINER_DEFAULT_SERVER=postgres
      - ADMINER_DESIGN=pepa-linha
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - fr02-network

  # NGINX Load Balancer
  nginx:
    image: nginx:alpine
    container_name: fr02-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./config/ssl:/etc/nginx/ssl
    depends_on:
      - chroma
      - postgres
    restart: unless-stopped
    networks:
      - fr02-network

  # API Service để serve files
  fr02-file-api:
    build:
      context: ./api
      dockerfile: Dockerfile
    container_name: fr02-file-api
    ports:
      - "8002:8000"
    environment:
      - DATABASE_URL=postgresql://kb_admin:${POSTGRES_PASSWORD}@postgres:5432/knowledge_base_v2
      - STORAGE_BASE_PATH=/opt/chatbot-storage
    volumes:
      # Ubuntu: Mount thư mục từ host system
      - chatbot_storage:/opt/chatbot-storage
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - fr02-network

volumes:
  postgres_data:
    driver: local
  chroma_data:
    driver: local
  redis_data:
    driver: local
  redis_replica_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
  
  # 🐧 UBUNTU SHARED VOLUME cho file storage
  chatbot_storage:
    driver: local
    driver_opts:
      type: none
      o: bind
      # Ubuntu: Sử dụng thư mục trong /opt (system-wide) hoặc home directory
      device: /opt/chatbot-storage

networks:
  fr02-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 📝 **CÁC THAY ĐỔI CHỦ YẾU**

### **1. Địa chỉ IP và Host:**
```yaml
# ✅ 0.0.0.0 trong Docker vẫn ổn trên Ubuntu
- CHROMA_SERVER_HOST=0.0.0.0  # Không cần đổi thành localhost

# ✅ Healthcheck sử dụng localhost (bên trong container)
test: ["CMD-SHELL", "curl -f http://localhost:8000/api/v2/heartbeat || exit 1"]
```

**Giải thích:**
- `0.0.0.0` trong Docker container có nghĩa là bind tất cả network interfaces
- Đây là cách đúng để container có thể nhận requests từ bên ngoài
- `localhost`/`127.0.0.1` chỉ dùng cho healthcheck bên trong container

### **2. Storage Volume Path:**
```yaml
# ❌ Windows path (cũ)
device: D:\chatbot-storage

# ✅ Ubuntu path (mới)
device: /opt/chatbot-storage
```

## 🗂️ **TẠO THƯ MỤC STORAGE TRÊN UBUNTU**

```bash
# Tạo script setup storage
cat > setup_storage.sh << 'EOF'
#!/bin/bash

# Tạo thư mục storage chính
sudo mkdir -p /opt/chatbot-storage

# Tạo cấu trúc thư mục
sudo mkdir -p /opt/chatbot-storage/{documents,processed,temp,logs,exports,imports}

# Tạo thư mục cho từng department
sudo mkdir -p /opt/chatbot-storage/documents/{HR,Finance,IT,Marketing,Operations,General}

# Tạo thư mục backup
sudo mkdir -p /opt/chatbot-storage/backups/{daily,weekly,monthly}

# Set permissions (cho phép Docker access)
sudo chown -R $USER:$USER /opt/chatbot-storage
sudo chmod -R 755 /opt/chatbot-storage

# Tạo symbolic link cho dễ access
ln -sf /opt/chatbot-storage ~/chatbot-storage

echo "✅ Storage directory created: /opt/chatbot-storage"
ls -la /opt/chatbot-storage/
EOF

chmod +x setup_storage.sh
./setup_storage.sh
```

## 🔧 **SCRIPT KHỞI TẠO UBUNTU**

```bash
#!/bin/bash
# setup_docker_ubuntu.sh - Chuẩn bị môi trường Docker trên Ubuntu

# Tạo project directory
mkdir -p ~/chatbot-ai/docker-deployment
cd ~/chatbot-ai/docker-deployment

# Download hoặc copy docker-compose.yml (phiên bản Ubuntu)
# Copy file cấu hình từ Windows project

# Tạo .env file
cat > .env << 'EOF'
# Database
POSTGRES_PASSWORD=changeme123_ubuntu
CHROMA_AUTH_TOKEN=changeme-chroma-token-ubuntu
GRAFANA_PASSWORD=admin123_ubuntu

# Network
DOCKER_SUBNET=172.20.0.0/16

# Storage (Ubuntu paths)
STORAGE_BASE_PATH=/opt/chatbot-storage
LOG_PATH=/opt/chatbot-storage/logs
BACKUP_PATH=/opt/chatbot-storage/backups
EOF

# Tạo config directories
mkdir -p {config/{grafana/{dashboards,datasources},ssl},scripts,api}

# Set permissions
sudo chown -R $USER:$USER ~/chatbot-ai/docker-deployment

echo "✅ Docker environment setup completed"
echo "📁 Project directory: ~/chatbot-ai/docker-deployment"
echo "💾 Storage directory: /opt/chatbot-storage"
```

## 📋 **CÁC LỰA CHỌN THƯ MỤC STORAGE**

### **Option 1: System-wide (/opt) - Khuyến nghị**
```yaml
device: /opt/chatbot-storage
```
- ✅ **Ưu điểm:** Persistent, professional, dễ backup
- ✅ **Phù hợp:** Production deployment
- ✅ **Permission:** Dễ quản lý với Docker

### **Option 2: Home directory (~)**
```yaml
device: /home/${USER}/chatbot-storage
# hoặc
device: ${HOME}/chatbot-storage
```
- ✅ **Ưu điểm:** Không cần sudo, dễ access
- ⚠️ **Nhược điểm:** Phụ thuộc user, khó share

### **Option 3: Dedicated mount point**
```yaml
device: /data/chatbot-storage
```
- ✅ **Ưu điểm:** Tách biệt hoàn toàn, có thể là separate disk
- ⚠️ **Cần setup:** Mount point configuration

## 🚀 **DEPLOYMENT COMMANDS**

```bash
# 1. Setup storage
./setup_storage.sh

# 2. Start services
cd ~/chatbot-ai/docker-deployment
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f

# 5. Check storage access
docker exec fr02-postgres-v2 ls -la /opt/chatbot-storage/
```

## ✅ **TÓM TẮT KHÁC BIỆT UBUNTU vs WINDOWS**

| Thành phần | Windows | Ubuntu |
|------------|---------|---------|
| **Storage Path** | `D:\chatbot-storage` | `/opt/chatbot-storage` |
| **Host IP** | `0.0.0.0` (OK) | `0.0.0.0` (OK) |
| **Path Separator** | `\` | `/` |
| **Permissions** | Auto | Manual setup |
| **User Access** | Current user | `chown/chmod` |

**Chính thư mục `/opt/chatbot-storage` là lựa chọn tốt nhất cho Ubuntu!** 🎯
