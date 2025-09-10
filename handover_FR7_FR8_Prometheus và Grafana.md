Dựa trên kết quả tìm kiếm trong project knowledge, tôi thấy rằng **Prometheus và Grafana** xuất hiện trong nhiều module khác nhau:

## 📊 **PROMETHEUS & GRAFANA TRONG CẤU TRÚC DỰ ÁN**

### **FR-02.1: Dual Database System**
- **Prometheus**: Metrics collection cho PostgreSQL, ChromaDB, Redis
- **Grafana**: Database performance dashboards
- **Scope**: Infrastructure monitoring cho database layer

### **FR-07: Analytics & Reporting** 
- **Prometheus**: Application metrics và business metrics
- **Grafana**: Analytics dashboards cho user behavior, search patterns
- **Scope**: Business intelligence và reporting

### **FR-08: Admin & Maintenance Tools**
- **Prometheus**: System health monitoring
- **Grafana**: Admin dashboards cho system administration
- **Scope**: Administrative monitoring và maintenance

## 🎯 **PHÂN CHIA TRÁCH NHIỆM**

### **FR-02.1 (Infrastructure Monitoring)**
```yaml
# Prometheus trong FR-02.1
scrape_configs:
  - job_name: 'postgres-exporter'
  - job_name: 'redis-exporter' 
  - job_name: 'chroma-api'
  - job_name: 'node-exporter'
```

### **FR-07 (Business Analytics)**
```python
# Prometheus trong FR-07
from prometheus_client import Counter, Histogram, Gauge
search_queries_total = Counter('search_queries_total')
response_time_histogram = Histogram('response_time_seconds')
```

### **FR-08 (System Administration)**
```yaml
# Prometheus trong FR-08
admin_operations_total = Counter('admin_operations_total')
system_health_gauge = Gauge('system_health_status')
```

## 🔧 **KHUYẾN NGHỊ THIẾT KẾ**

### **Tách biệt theo Layer:**
1. **FR-02.1**: Infrastructure metrics (database, cache, storage)
2. **FR-07**: Application metrics (business logic, user analytics)  
3. **FR-08**: Administrative metrics (system health, maintenance)

### **Shared Configuration:**
- **Centralized Prometheus**: Một instance duy nhất collect từ tất cả modules
- **Dedicated Grafana Dashboards**: Mỗi module có dashboard riêng
- **Alert Manager**: Chung cho toàn hệ thống

## 📋 **CẬP NHẬT CHO FR-02.1 v2.0**

Trong tài liệu FR-02.1 v2.0, cần làm rõ:

```yaml
# FR-02.1 chỉ tập trung vào Infrastructure Monitoring
prometheus:
  role: "Infrastructure Metrics Collection"
  scope: 
    - Database performance (PostgreSQL, ChromaDB)
    - Cache performance (Redis)
    - Storage metrics
    - Network performance
  
grafana:
  role: "Infrastructure Dashboards" 
  scope:
    - Database connection pools
    - Query performance
    - Cache hit rates
    - Storage utilization
```

---


Tài liệu FR-02.1 v2.0 hiện tại đã đúng khi đặt Prometheus/Grafana trong infrastructure monitoring, nhưng nên bổ sung note về coordination với các module khác để tránh confusion.


---

# FR-07 ANALYTICS & REPORTING - HANDOVER v2.0
## TÀI LIỆU BÀN GIAO NHANH CHO TEAM PHÁT TRIỂN

---

**Phiên bản:** 2.0  
**Ngày:** 12/09/2025  
**Module:** FR-07 Analytics & Reporting  
**Trạng thái:** Ready for Integration với FR-02.1 v2.0  
**Liên hệ:** Development Team Lead  

---

## 🎯 **TÓM TẮT MODULE**

FR-07 cung cấp **Business Intelligence và User Analytics** cho hệ thống Vietnamese Chatbot, bao gồm:
- **Real-time Analytics API** cho search patterns, user behavior
- **Interactive Dashboard** với Streamlit 
- **Business Metrics Collection** qua Prometheus
- **Automated Reporting** (CSV, PDF export)

## 🔌 **INTEGRATION POINTS VỚI FR-02.1 v2.0**

### **Database Connection**
```python
# FR-07 connects to FR-02.1 PostgreSQL
DATABASE_URL = "postgresql://kb_admin:${POSTGRES_PASSWORD}@localhost:5432/knowledge_base_v2"

# Tables FR-07 cần từ FR-02.1:
- users                    # User management data
- documents_metadata_v2    # Document information  
- search_analytics         # Search queries và results
- user_activity_summary    # User behavior patterns
- system_metrics          # Performance data
```

### **API Endpoints cần từ FR-02.1**
```bash
# FR-07 sẽ call các endpoints này:
GET /api/users/activity           # User statistics
GET /api/documents/usage         # Document access patterns  
GET /api/search/analytics        # Search performance
GET /api/system/health           # System status
```

## 📊 **MONITORING COORDINATION**

### **Prometheus Metrics Separation**

#### **FR-02.1 (Infrastructure)**
```yaml
# PostgreSQL, ChromaDB, Redis metrics
- pg_connections_active
- chroma_search_duration 
- redis_memory_usage
```

#### **FR-07 (Business Analytics)**
```python
# Application và business metrics
search_queries_total = Counter('fr07_search_queries_total')
user_session_duration = Histogram('fr07_user_session_duration_seconds')
document_views_total = Counter('fr07_document_views_total')
report_generation_time = Histogram('fr07_report_generation_seconds')
```

### **Grafana Dashboard Structure**
```
Grafana Organization:
├── Infrastructure (FR-02.1)
│   ├── Database Performance
│   ├── Cache Metrics  
│   └── System Health
├── Business Analytics (FR-07)
│   ├── User Behavior
│   ├── Search Analytics
│   └── Content Performance
└── Admin Tools (FR-08)
    ├── System Administration
    └── Maintenance Tasks
```

## 🚀 **QUICK START GUIDE**

### **1. Environment Setup**
```bash
# Clone project
git clone <repository> && cd FR-07

# Environment variables
cat > .env << EOF
# Database (from FR-02.1)
DATABASE_URL=postgresql://kb_admin:${POSTGRES_PASSWORD}@localhost:5432/knowledge_base_v2
REDIS_URL=redis://localhost:6379

# FR-07 Specific
API_PORT=8001
DASHBOARD_PORT=8501
SECRET_KEY=$(openssl rand -hex 32)

# Integration URLs
FR02_API_BASE=http://localhost:8000
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000
EOF
```

### **2. Docker Deployment**
```yaml
# docker-compose.fr07.yml
version: '3.8'
services:
  fr07-analytics-api:
    build: ./analytics_module
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres  # From FR-02.1
      - redis     # From FR-02.1
    networks:
      - fr02-network  # Join FR-02.1 network
      
  fr07-dashboard:
    build: ./analytics_module
    command: streamlit run dashboard/main.py --server.port 8501
    ports:
      - "8501:8501"
    depends_on:
      - fr07-analytics-api
    networks:
      - fr02-network

networks:
  fr02-network:
    external: true  # Use network from FR-02.1
```

### **3. Start Services**
```bash
# Ensure FR-02.1 is running first
cd ../FR-02.1 && docker-compose up -d

# Start FR-07
cd ../FR-07 && docker-compose -f docker-compose.fr07.yml up -d

# Verify
curl http://localhost:8001/health
curl http://localhost:8501
```

## 📋 **INTEGRATION CHECKLIST**

### **Prerequisites**
- [ ] FR-02.1 v2.0 deployed và running
- [ ] Database `knowledge_base_v2` accessible
- [ ] Redis instance available
- [ ] Prometheus collecting metrics từ FR-02.1

### **Integration Steps**
- [ ] Configure database connection to FR-02.1 PostgreSQL
- [ ] Set up Redis connection for caching
- [ ] Register FR-07 metrics với Prometheus
- [ ] Create Grafana dashboards cho business analytics
- [ ] Test API endpoints integration
- [ ] Verify dashboard connectivity

### **Testing Integration**
```bash
# Test database connectivity
python3 -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('${DATABASE_URL}')
    result = await conn.fetchval('SELECT COUNT(*) FROM users')
    print(f'Users in database: {result}')
    await conn.close()
asyncio.run(test())
"

# Test API integration
curl -X GET "http://localhost:8001/api/analytics/search-metrics?days=7"
curl -X GET "http://localhost:8001/api/analytics/user-activity?user_level=EMPLOYEE"
```

## 🔧 **CONFIGURATION**

### **Database Schema Requirements**
```sql
-- FR-07 requires these views from FR-02.1
CREATE VIEW fr07_search_summary AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_searches,
    AVG(processing_time_ms) as avg_response_time,
    COUNT(CASE WHEN has_results THEN 1 END) as successful_searches
FROM search_analytics 
GROUP BY DATE(timestamp);

CREATE VIEW fr07_user_engagement AS
SELECT 
    user_level,
    department,
    COUNT(DISTINCT user_id) as active_users,
    AVG(search_count) as avg_searches_per_user
FROM user_activity_summary
GROUP BY user_level, department;
```

### **API Configuration**
```python
# config/fr07_config.py
class FR07Config:
    # Integration settings
    FR02_DATABASE_URL = os.getenv("DATABASE_URL")
    FR02_API_BASE = os.getenv("FR02_API_BASE", "http://localhost:8000")
    
    # FR-07 specific
    ANALYTICS_API_PORT = 8001
    DASHBOARD_PORT = 8501
    CACHE_TTL = 300  # 5 minutes
    
    # Business logic
    DEFAULT_DATE_RANGE = 30  # days
    MAX_EXPORT_RECORDS = 10000
    REPORT_GENERATION_TIMEOUT = 600  # seconds
```

## 📈 **API ENDPOINTS**

### **Core Analytics APIs**
```bash
# Search Analytics
GET /api/analytics/search-metrics?days=30
GET /api/analytics/popular-queries?limit=10
GET /api/analytics/search-performance

# User Analytics  
GET /api/analytics/user-activity?department=IT
GET /api/analytics/user-engagement?user_level=EMPLOYEE
GET /api/analytics/session-analysis

# Document Analytics
GET /api/analytics/document-usage?document_type=policy
GET /api/analytics/content-performance
GET /api/analytics/access-patterns

# System Analytics
GET /api/analytics/system-performance
GET /api/analytics/error-rates
GET /api/analytics/capacity-metrics
```

### **Export & Reports**
```bash
# Data Export
GET /api/export/search-data?format=csv&start_date=2025-01-01
GET /api/export/user-report?format=pdf&department=HR

# Automated Reports
POST /api/reports/generate
GET /api/reports/{report_id}/status
GET /api/reports/{report_id}/download
```

## 🛠️ **TROUBLESHOOTING**

### **Common Integration Issues**

#### **Database Connection Failed**
```bash
# Check FR-02.1 PostgreSQL status
docker-compose -f ../FR-02.1/docker-compose.yml ps postgres

# Test connection
psql -h localhost -p 5432 -U kb_admin -d knowledge_base_v2 -c "SELECT version();"

# Fix: Update DATABASE_URL in FR-07 .env
```

#### **Redis Connection Issues**
```bash
# Check FR-02.1 Redis status
docker-compose -f ../FR-02.1/docker-compose.yml ps redis-master

# Test connection
redis-cli -h localhost -p 6379 ping

# Fix: Update REDIS_URL in FR-07 .env
```

#### **Prometheus Metrics Conflicts**
```bash
# Check if FR-07 metrics are being collected
curl http://localhost:9090/api/v1/label/__name__/values | grep fr07

# Fix: Ensure unique metric names với fr07_ prefix
```

## 📞 **SUPPORT & CONTACTS**

### **Module Dependencies**
- **FR-02.1**: Database schema, API endpoints
- **Shared**: Prometheus instance, Grafana organization
- **Optional**: FR-05 (UI integration), FR-06 (Authentication)

### **Key Integration Points**
```python
# FR-07 Service Discovery
DEPENDENT_SERVICES = {
    "postgres": "FR-02.1 PostgreSQL Database",
    "redis": "FR-02.1 Redis Cache", 
    "prometheus": "Shared Monitoring Stack",
    "grafana": "Shared Dashboard Platform"
}
```

### **Documentation Links**
- **API Docs**: http://localhost:8001/docs
- **Dashboard**: http://localhost:8501
- **Metrics**: http://localhost:9090/targets (check fr07-* targets)
- **Grafana**: http://localhost:3000 (Business Analytics folder)

---

# FR-08 ADMIN & MAINTENANCE TOOLS - HANDOVER v2.0
## TÀI LIỆU BÀN GIAO NHANH CHO TEAM PHÁT TRIỂN

---

**Phiên bản:** 2.0  
**Ngày:** 12/09/2025  
**Module:** FR-08 Admin & Maintenance Tools  
**Trạng thái:** Ready for Integration với FR-02.1 v2.0  
**Liên hệ:** DevOps Team Lead  

---

## 🎯 **TÓM TẮT MODULE**

FR-08 cung cấp **System Administration và Maintenance** cho toàn bộ hệ thống, bao gồm:
- **Admin API** cho user management, system configuration
- **Maintenance Tools** cho database backup, cleanup
- **System Health Monitoring** với alerts và notifications
- **Administrative Dashboard** cho system operators

## 🔌 **INTEGRATION POINTS VỚI FR-02.1 v2.0**

### **Database Administrative Access**
```python
# FR-08 needs ADMIN level access to all FR-02.1 tables
DATABASE_URL = "postgresql://kb_admin:${POSTGRES_PASSWORD}@localhost:5432/knowledge_base_v2"

# Admin operations on:
- users                      # User management (CRUD)
- documents_metadata_v2      # Document administration
- data_ingestion_jobs        # Job management
- system_health_metrics      # System monitoring
- chunk_processing_logs      # Processing oversight
```

### **Administrative APIs**
```bash
# FR-08 provides admin endpoints for:
POST /api/admin/users                    # User creation/management
DELETE /api/admin/users/{user_id}        # User deletion
POST /api/admin/documents/reindex        # Document reindexing
POST /api/admin/system/backup            # System backup
GET /api/admin/system/health             # Comprehensive health check
POST /api/admin/maintenance/cleanup      # Data cleanup operations
```

## 📊 **MONITORING COORDINATION**

### **Administrative Metrics**

#### **FR-08 System Administration Metrics**
```python
# System admin operations tracking
admin_operations_total = Counter('fr08_admin_operations_total', ['operation_type', 'status'])
backup_duration_seconds = Histogram('fr08_backup_duration_seconds')
cleanup_operations_total = Counter('fr08_cleanup_operations_total', ['cleanup_type'])
system_health_score = Gauge('fr08_system_health_score')
maintenance_window_active = Gauge('fr08_maintenance_window_active')
```

### **Alert Management Integration**
```yaml
# FR-08 manages alerts for entire system
alert_groups:
  - name: fr02_infrastructure
    rules:
      - alert: DatabaseDown
        expr: pg_up{job="postgres-exporter"} == 0
        for: 5m
        labels:
          severity: critical
          module: FR-02.1
        annotations:
          summary: "PostgreSQL database is down"
          
  - name: fr07_business_metrics  
    rules:
      - alert: HighErrorRate
        expr: rate(fr07_api_errors_total[5m]) > 0.1
        for: 10m
        labels:
          severity: warning
          module: FR-07
```

## 🚀 **QUICK START GUIDE**

### **1. Environment Setup**
```bash
# Clone admin tools
git clone <repository> && cd FR-08

# Admin environment variables
cat > .env << EOF
# Database (ADMIN access to FR-02.1)
DATABASE_URL=postgresql://kb_admin:${POSTGRES_PASSWORD}@localhost:5432/knowledge_base_v2
REDIS_URL=redis://localhost:6379

# FR-08 Admin specific
ADMIN_API_PORT=8002
ADMIN_SECRET_KEY=$(openssl rand -hex 32)
BACKUP_RETENTION_DAYS=30
LOG_LEVEL=INFO

# System integration
FR02_API_BASE=http://localhost:8000
FR07_API_BASE=http://localhost:8001
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000
ALERTMANAGER_URL=http://localhost:9093

# Notification settings
SMTP_SERVER=smtp.company.com
SMTP_PORT=587
ADMIN_EMAIL=admin@company.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
EOF
```

### **2. Docker Deployment**
```yaml
# docker-compose.fr08.yml
version: '3.8'
services:
  fr08-admin-api:
    build: ./admin_tools
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - ADMIN_SECRET_KEY=${ADMIN_SECRET_KEY}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock  # Docker management
      - ./backups:/app/backups                     # Backup storage
      - ./logs:/app/logs                           # Log storage
    depends_on:
      - postgres  # From FR-02.1
      - redis     # From FR-02.1
    networks:
      - fr02-network
    restart: unless-stopped
      
  fr08-backup-scheduler:
    build: ./admin_tools
    command: python -m admin_tools.services.backup_scheduler
    volumes:
      - ./backups:/app/backups
      - postgres_data:/var/lib/postgresql/data:ro
      - chroma_data:/chroma/chroma:ro
    depends_on:
      - fr08-admin-api
    networks:
      - fr02-network
    restart: unless-stopped

  fr08-alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./config/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    networks:
      - fr02-network
    restart: unless-stopped

volumes:
  postgres_data:
    external: true  # From FR-02.1
  chroma_data:
    external: true  # From FR-02.1

networks:
  fr02-network:
    external: true  # Use FR-02.1 network
```

### **3. Start Admin Services**
```bash
# Ensure FR-02.1 và FR-07 are running
cd ../FR-02.1 && docker-compose ps
cd ../FR-07 && docker-compose -f docker-compose.fr07.yml ps

# Start FR-08 admin tools
cd ../FR-08 && docker-compose -f docker-compose.fr08.yml up -d

# Verify admin services
curl http://localhost:8002/health
curl http://localhost:9093/#/status
```

## 📋 **INTEGRATION CHECKLIST**

### **Prerequisites**
- [ ] FR-02.1 v2.0 running với admin database access
- [ ] FR-07 deployed (optional but recommended)
- [ ] Docker socket access for container management
- [ ] SMTP server configured for notifications
- [ ] Backup storage volumes mounted

### **Administrative Setup**
- [ ] Create admin user accounts với SYSTEM_ADMIN level
- [ ] Configure backup schedules và retention policies
- [ ] Set up alert notification channels (email, Slack)
- [ ] Configure maintenance windows
- [ ] Test emergency procedures
- [ ] Document recovery procedures

### **Security Configuration**
```bash
# Create admin users
curl -X POST http://localhost:8002/api/admin/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -d '{
    "username": "sysadmin",
    "email": "sysadmin@company.com", 
    "user_level": "SYSTEM_ADMIN",
    "department": "IT"
  }'

# Configure backup encryption
curl -X POST http://localhost:8002/api/admin/config/backup \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -d '{
    "encryption_enabled": true,
    "compression_level": 6,
    "retention_days": 30
  }'
```

## 🔧 **ADMINISTRATIVE OPERATIONS**

### **User Management**
```bash
# User administration
GET /api/admin/users                     # List all users
POST /api/admin/users                    # Create user
PUT /api/admin/users/{user_id}           # Update user
DELETE /api/admin/users/{user_id}        # Delete user
POST /api/admin/users/{user_id}/reset    # Reset password
POST /api/admin/users/{user_id}/lock     # Lock account
```

### **System Management**
```bash
# System operations
GET /api/admin/system/status             # Complete system status
POST /api/admin/system/backup            # Trigger manual backup
POST /api/admin/system/maintenance       # Enter maintenance mode
DELETE /api/admin/system/cache           # Clear all caches
GET /api/admin/system/logs?service=all   # Aggregate logs
```

### **Document Management**
```bash
# Document administration
POST /api/admin/documents/reindex        # Reindex all documents
POST /api/admin/documents/cleanup        # Remove orphaned documents
GET /api/admin/documents/quality         # Document quality report
POST /api/admin/documents/migrate        # Migrate document format
```

### **Maintenance Operations**
```bash
# Database maintenance
POST /api/admin/maintenance/vacuum       # Database vacuum
POST /api/admin/maintenance/reindex      # Rebuild indexes
POST /api/admin/maintenance/analyze      # Update statistics
GET /api/admin/maintenance/health        # Database health check
```

## 🚨 **ALERTING & NOTIFICATIONS**

### **Alert Configuration**
```yaml
# config/alertmanager.yml
global:
  smtp_smarthost: '${SMTP_SERVER}:${SMTP_PORT}'
  smtp_from: 'alerts@company.com'

route:
  group_by: ['alertname', 'module']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'admin-team'

receivers:
  - name: 'admin-team'
    email_configs:
      - to: '${ADMIN_EMAIL}'
        subject: '[CHATBOT] {{ .GroupLabels.module }} Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          Module: {{ .Labels.module }}
          Severity: {{ .Labels.severity }}
          {{ end }}
    
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#chatbot-alerts'
        title: '{{ .GroupLabels.module }} Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

### **System Health Monitoring**
```python
# Health check aggregation
@app.get("/api/admin/system/health")
async def system_health():
    health_status = {
        "overall": "healthy",
        "services": {
            "fr02_postgres": await check_postgres_health(),
            "fr02_chroma": await check_chroma_health(),
            "fr02_redis": await check_redis_health(),
            "fr07_analytics": await check_fr07_health(),
            "fr08_admin": "healthy"
        },
        "metrics": {
            "uptime_seconds": get_system_uptime(),
            "memory_usage_percent": get_memory_usage(),
            "disk_usage_percent": get_disk_usage(),
            "active_users": await get_active_user_count()
        }
    }
    return health_status
```

## 🔄 **BACKUP & RECOVERY**

### **Automated Backup Strategy**
```python
# Backup scheduler configuration
BACKUP_SCHEDULE = {
    "postgres": {
        "frequency": "daily",
        "time": "02:00",
        "retention_days": 30,
        "compression": True,
        "encryption": True
    },
    "chroma": {
        "frequency": "daily", 
        "time": "03:00",
        "retention_days": 14,
        "compression": True
    },
    "redis": {
        "frequency": "every_6_hours",
        "retention_hours": 72,
        "compression": False
    },
    "logs": {
        "frequency": "weekly",
        "retention_weeks": 4,
        "compression": True
    }
}
```

### **Recovery Procedures**
```bash
# Database recovery
POST /api/admin/recovery/postgres
{
  "backup_file": "postgres_backup_20250912_020000.sql.gz",
  "target_database": "knowledge_base_v2",
  "confirm_overwrite": true
}

# Vector database recovery  
POST /api/admin/recovery/chroma
{
  "backup_file": "chroma_backup_20250912_030000.tar.gz",
  "target_collection": "knowledge_base_v2",
  "verify_integrity": true
}
```

## 🛠️ **TROUBLESHOOTING**

### **Common Administrative Issues**

#### **Backup Failures**
```bash
# Check backup service status
docker-compose -f docker-compose.fr08.yml ps fr08-backup-scheduler

# Check backup logs
docker-compose -f docker-compose.fr08.yml logs fr08-backup-scheduler

# Manual backup test
curl -X POST http://localhost:8002/api/admin/system/backup \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"
```

#### **Alert Manager Not Working**
```bash
# Check AlertManager status
curl http://localhost:9093/api/v1/status

# Test alert routing
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{
    "labels": {"alertname": "TestAlert", "severity": "warning"},
    "annotations": {"summary": "Test alert from FR-08"}
  }]'
```

#### **System Health Check Failures**
```bash
# Check individual service health
curl http://localhost:8002/api/admin/system/health

# Check service dependencies
docker-compose -f ../FR-02.1/docker-compose.yml ps
docker-compose -f ../FR-07/docker-compose.fr07.yml ps

# Restart unhealthy services
docker-compose restart <service_name>
```

## 📞 **SUPPORT & CONTACTS**

### **Administrative Responsibilities**
- **User Management**: Account creation, permissions, password resets
- **System Monitoring**: Health checks, performance monitoring, alerting
- **Data Management**: Backups, cleanup, migration, recovery
- **Security**: Access control, audit logging, compliance

### **Emergency Procedures**
```bash
# System emergency stop
curl -X POST http://localhost:8002/api/admin/emergency/stop \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"

# Enter maintenance mode
curl -X POST http://localhost:8002/api/admin/system/maintenance \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -d '{"duration_minutes": 60, "reason": "Emergency maintenance"}'

# Restore from backup
curl -X POST http://localhost:8002/api/admin/recovery/full-restore \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -d '{"backup_timestamp": "20250912_020000"}'
```

### **Documentation Links**
- **Admin API**: http://localhost:8002/docs
- **System Status**: http://localhost:8002/api/admin/system/status
- **Alert Manager**: http://localhost:9093
- **Backup Status**: http://localhost:8002/api/admin/backup/status

### **Integration Dependencies**
```yaml
# FR-08 depends on:
required_services:
  - fr02-postgres      # Database administration
  - fr02-redis         # Cache management  
  - fr02-chroma        # Vector DB maintenance
  - prometheus         # Metrics collection
  - grafana           # Dashboard management

optional_integrations:
  - fr07-analytics     # Business metrics oversight
  - smtp-server        # Email notifications
  - slack-api          # Chat notifications
```

---

**🔧 Ready for immediate deployment and integration với FR-02.1 v2.0 infrastructure!**

---
