# FR-03.1 v2.0 Enhanced Deployment Guide

**Project**: FR-03.1 - Document Processing Tool v2.0 Enhanced  
**Version**: 2.0 (100% FR-02.1 v2.0 Compatible)  
**Date**: September 13, 2025  
**Status**: Production Ready

## 📋 **Deployment Overview**

This document provides comprehensive deployment instructions for FR-03.1 v2.0, supporting both Docker and non-Docker environments. The enhanced version provides 100% compatibility with FR-02.1 v2.0 database schema and advanced Vietnamese processing capabilities.

## 🎯 **Deployment Options**

### **Option 1: Docker Deployment (Recommended)** 🐳
- **Best for**: Production environments, isolated deployment
- **Requirements**: Docker, Docker Compose
- **Setup Time**: ~5 minutes
- **Maintenance**: Low

### **Option 2: Manual Deployment** 💻
- **Best for**: Development environments, custom configurations
- **Requirements**: Python 3.9+, system dependencies
- **Setup Time**: ~15 minutes
- **Maintenance**: Medium

---

## 🐳 **Docker Deployment (Recommended)**

### **Prerequisites**
- Docker 20.0+ installed
- Docker Compose 1.25+ installed  
- 4GB available RAM
- 2GB available disk space
- Port 8501 available

### **Quick Start**

1. **Navigate to Project Directory**
   ```bash
   cd FR-03.1
   ```

2. **Start the Application**
   ```bash
   docker-compose up -d
   ```

3. **Verify Deployment**
   ```bash
   # Check container status
   docker-compose ps
   
   # Check logs
   docker-compose logs fr-03-1-document-processor
   
   # Health check
   curl http://localhost:8501/_stcore/health
   ```

4. **Access Application**
   - Web Interface: http://localhost:8501
   - API Health Check: http://localhost:8501/_stcore/health

### **Docker Configuration Details**

#### **docker-compose.yml Configuration**
```yaml
version: '3.8'
services:
  fr-03-1-document-processor:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./exports:/app/exports
      - ./temp:/app/temp
      - ./logs:/app/logs
    environment:
      - PYTHONPATH=/app
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    mem_limit: 2g
    cpus: 1.0
```

#### **Dockerfile Configuration**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for Vietnamese processing
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p exports temp logs temp/cache temp/processing

# Set permissions
RUN chmod -R 755 /app

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### **Docker Management Commands**

#### **Basic Operations**
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

#### **Maintenance Operations**
```bash
# Update containers
docker-compose pull
docker-compose up -d

# Clean up old containers and images
docker system prune -f

# View resource usage
docker stats

# Access container shell (for debugging)
docker-compose exec fr-03-1-document-processor bash
```

### **Docker Monitoring**

#### **Health Checks**
```bash
# Application health
curl http://localhost:8501/_stcore/health

# Container health
docker inspect --format='{{.State.Health.Status}}' fr-03-1_fr-03-1-document-processor_1

# Resource monitoring
docker stats fr-03-1_fr-03-1-document-processor_1
```

#### **Log Analysis**
```bash
# View application logs
docker-compose logs fr-03-1-document-processor

# Follow logs in real-time
docker-compose logs -f fr-03-1-document-processor

# View last 100 lines
docker-compose logs --tail=100 fr-03-1-document-processor
```

### **Docker Troubleshooting**

#### **Common Issues**

**Issue 1: Port Already in Use**
```bash
# Check what's using port 8501
netstat -tlnp | grep 8501

# Kill process using port
sudo kill -9 <PID>

# Or use different port
docker-compose up -d -p 8502:8501
```

**Issue 2: Memory Issues**
```bash
# Check memory usage
docker stats

# Increase memory limit in docker-compose.yml
mem_limit: 4g
```

**Issue 3: Container Won't Start**
```bash
# Check container logs
docker-compose logs fr-03-1-document-processor

# Check if image built correctly
docker images | grep fr-03-1

# Rebuild container
docker-compose build --no-cache
docker-compose up -d
```

---

## 💻 **Manual Deployment (Non-Docker)**

### **Prerequisites**
- Python 3.9 or higher
- pip package manager
- 2GB available RAM
- 1GB available disk space
- Port 8501 available

### **System Dependencies**

#### **Ubuntu/Debian**
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-dev gcc curl
```

#### **CentOS/RHEL**
```bash
sudo yum update
sudo yum install -y python3-pip python3-devel gcc curl
```

#### **Windows**
- Install Python 3.9+ from python.org
- Install Visual Studio Build Tools
- Add Python to PATH

#### **macOS**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.9
```

### **Installation Steps**

1. **Create Virtual Environment**
   ```bash
   # Navigate to project directory
   cd FR-03.1
   
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # Linux/macOS:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   ```

2. **Install Python Dependencies**
   ```bash
   # Upgrade pip
   pip install --upgrade pip
   
   # Install requirements
   pip install -r requirements.txt
   ```

3. **Create Required Directories**
   ```bash
   mkdir -p exports temp logs temp/cache temp/processing
   ```

4. **Set Environment Variables**
   ```bash
   # Linux/macOS:
   export PYTHONPATH=$PWD
   export STREAMLIT_SERVER_PORT=8501
   export STREAMLIT_SERVER_ADDRESS=0.0.0.0
   
   # Windows:
   set PYTHONPATH=%CD%
   set STREAMLIT_SERVER_PORT=8501
   set STREAMLIT_SERVER_ADDRESS=0.0.0.0
   ```

5. **Start Application**
   ```bash
   streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0
   ```

6. **Verify Installation**
   - Open browser to http://localhost:8501
   - Check health endpoint: http://localhost:8501/_stcore/health
   - Test document upload functionality

### **Manual Deployment Configuration**

#### **requirements.txt** (Enhanced for v2.0)
```
streamlit==1.28.0
pandas==2.0.3
python-docx==0.8.11
PyPDF2==3.0.1
markdown==3.4.4
pyvi==0.1.1
underthesea==6.5.3
nltk==3.8.1
scikit-learn==1.3.0
numpy==1.24.3
requests==2.31.0
hashlib-compat==1.0.1
pathlib2==2.3.7
python-dotenv==1.0.0
```

#### **System Service Configuration (Linux)**
Create `/etc/systemd/system/fr031-processor.service`:
```ini
[Unit]
Description=FR-03.1 Document Processor
After=network.target

[Service]
Type=simple
User=fr031user
WorkingDirectory=/opt/fr-03-1
Environment=PYTHONPATH=/opt/fr-03-1
Environment=STREAMLIT_SERVER_PORT=8501
ExecStart=/opt/fr-03-1/venv/bin/streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl enable fr031-processor
sudo systemctl start fr031-processor
sudo systemctl status fr031-processor
```

### **Manual Deployment Monitoring**

#### **Process Management**
```bash
# Check if application is running
ps aux | grep streamlit

# Kill application
pkill -f "streamlit run"

# Start in background (Linux/macOS)
nohup streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0 > logs/app.log 2>&1 &

# Start in background (Windows)
start /B streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0
```

#### **Log Management**
```bash
# View application logs (if using systemd)
journalctl -u fr031-processor -f

# View custom logs
tail -f logs/app.log

# Rotate logs
logrotate /etc/logrotate.d/fr031-processor
```

### **Manual Deployment Troubleshooting**

#### **Common Issues**

**Issue 1: Module Not Found**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

**Issue 2: Permission Errors**
```bash
# Fix directory permissions (Linux/macOS)
chmod -R 755 exports temp logs

# Fix Python path
export PYTHONPATH=$PWD
```

**Issue 3: Vietnamese Processing Errors**
```bash
# Install Vietnamese NLP dependencies
python -c "import nltk; nltk.download('punkt')"
pip install --upgrade pyvi underthesea
```

---

## 🔧 **Configuration & Customization**

### **Application Configuration**

#### **config/settings.json**
```json
{
  "app_config": {
    "max_file_size_mb": 50,
    "supported_formats": ["pdf", "docx", "txt", "md"],
    "processing_timeout_seconds": 300,
    "max_concurrent_users": 10
  },
  "processing_config": {
    "chunk_size_tokens": 512,
    "overlap_tokens": 50,
    "quality_threshold": 0.7,
    "vietnamese_processing": true,
    "semantic_chunking": true
  },
  "export_config": {
    "include_original_file": true,
    "generate_markdown": true,
    "create_database_exports": true,
    "create_vector_exports": true,
    "create_search_exports": true
  }
}
```

#### **Environment Variables**
```bash
# Application settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
PYTHONPATH=/app

# Processing settings  
FR031_MAX_FILE_SIZE=50
FR031_PROCESSING_TIMEOUT=300
FR031_VIETNAMESE_NLP=true

# Export settings
FR031_INCLUDE_ORIGINAL=true
FR031_CREATE_DB_EXPORTS=true
FR031_CREATE_VECTOR_EXPORTS=true
```

### **Performance Tuning**

#### **Memory Optimization**
```bash
# Docker memory limits
mem_limit: 2g
memswap_limit: 2g

# Python memory settings
PYTHONHASHSEED=0
PYTHONUNBUFFERED=1
```

#### **CPU Optimization**
```bash
# Docker CPU limits
cpus: 1.0
cpu_shares: 1024

# Python workers
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=50
```

### **Security Configuration**

#### **Network Security**
```bash
# Bind to localhost only (development)
--server.address=127.0.0.1

# Use reverse proxy (production)
--server.address=0.0.0.0
```

#### **File Security**
```json
{
  "security": {
    "max_file_size": 52428800,
    "allowed_extensions": [".pdf", ".docx", ".txt", ".md"],
    "scan_uploads": true,
    "auto_cleanup": true,
    "cleanup_interval_minutes": 60
  }
}
```

---

## 📊 **Monitoring & Maintenance**

### **Application Monitoring**

#### **Health Endpoints**
```bash
# Application health
curl http://localhost:8501/_stcore/health

# Extended health check
curl -s http://localhost:8501/_stcore/health | jq
```

#### **Performance Metrics**
```bash
# Memory usage
ps -o pid,ppid,cmd,%mem,%cpu -p $(pgrep -f "streamlit")

# Disk usage
du -sh exports/ temp/ logs/

# Network connections
netstat -tulpn | grep 8501
```

### **Maintenance Tasks**

#### **Regular Maintenance**
```bash
# Clean temporary files (daily)
find temp/ -type f -mtime +1 -delete

# Rotate logs (weekly)
find logs/ -name "*.log" -mtime +7 -delete

# Clean old exports (monthly)
find exports/ -type f -mtime +30 -delete
```

#### **Database Maintenance**
```bash
# Backup configuration
cp config/settings.json config/settings.json.backup.$(date +%Y%m%d)

# Update dependencies (monthly)
pip install --upgrade -r requirements.txt
```

### **Backup & Recovery**

#### **Backup Strategy**
```bash
#!/bin/bash
# backup_fr031.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/fr031"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config/

# Backup exports (last 7 days)
find exports/ -mtime -7 -type f | tar -czf $BACKUP_DIR/exports_$DATE.tar.gz -T -

# Backup logs (last 1 day)
find logs/ -mtime -1 -type f | tar -czf $BACKUP_DIR/logs_$DATE.tar.gz -T -

echo "Backup completed: $BACKUP_DIR"
```

#### **Recovery Procedures**
```bash
# Stop application
docker-compose down  # or systemctl stop fr031-processor

# Restore configuration
tar -xzf /backup/fr031/config_YYYYMMDD_HHMMSS.tar.gz

# Restore data (if needed)
tar -xzf /backup/fr031/exports_YYYYMMDD_HHMMSS.tar.gz

# Start application
docker-compose up -d  # or systemctl start fr031-processor
```

---

## 🚀 **Production Deployment Checklist**

### **Pre-Deployment**
- [ ] System requirements verified
- [ ] Dependencies installed and tested
- [ ] Configuration files reviewed
- [ ] Security settings configured
- [ ] Backup procedures established
- [ ] Monitoring setup completed

### **Deployment**
- [ ] Application deployed successfully
- [ ] Health checks passing
- [ ] All endpoints accessible
- [ ] File upload functionality tested
- [ ] Vietnamese processing validated
- [ ] Database export format verified

### **Post-Deployment**
- [ ] Performance metrics baseline established
- [ ] Log rotation configured
- [ ] Backup schedule implemented
- [ ] Alert thresholds set
- [ ] Documentation updated
- [ ] Team training completed

### **Validation Tests**

#### **Functional Testing**
```bash
# Test document upload
curl -X POST -F "file=@test.pdf" http://localhost:8501/api/upload

# Test Vietnamese processing
curl -X POST -F "file=@vietnamese_doc.docx" http://localhost:8501/api/process

# Test export generation
curl -X GET http://localhost:8501/api/export/latest
```

#### **Performance Testing**
```bash
# Load testing (if available)
ab -n 100 -c 10 http://localhost:8501/

# Memory stress test
# Upload multiple large documents simultaneously

# Concurrent user test
# Multiple browser sessions processing documents
```

---

## 📞 **Support & Troubleshooting**

### **Common Issues**

**Issue**: Application won't start
**Solution**: Check logs, verify dependencies, check port availability

**Issue**: File upload fails
**Solution**: Check file size limits, permissions, disk space

**Issue**: Vietnamese processing errors
**Solution**: Verify NLP libraries, check language models

**Issue**: Export generation fails
**Solution**: Check disk space, permissions, processing settings

### **Log Locations**
```bash
# Docker deployment
docker-compose logs fr-03-1-document-processor

# Manual deployment
tail -f logs/app.log
tail -f logs/error.log

# System logs (Linux)
journalctl -u fr031-processor
```

### **Support Contacts**
- **Technical Issues**: Check logs and error messages first
- **Configuration Help**: Review config/settings.json
- **Performance Issues**: Monitor system resources
- **Bug Reports**: Include logs and reproduction steps

---

## 🎯 **Next Steps**

After successful deployment:

1. **Test Document Processing**: Upload various Vietnamese documents
2. **Verify Database Compatibility**: Test export formats with FR-02.1 v2.0
3. **Monitor Performance**: Track processing times and resource usage
4. **Setup Monitoring**: Configure health checks and alerts
5. **Schedule Maintenance**: Setup automated backups and cleanups
6. **Train Users**: Provide user training on enhanced features

---

**Deployment Complete!** 🚀

FR-03.1 v2.0 Enhanced is now ready for production use with 100% FR-02.1 v2.0 database compatibility and advanced Vietnamese processing capabilities.