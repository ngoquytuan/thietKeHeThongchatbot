# Manual Database Deployment Guide

## Issue Analysis: Why 02_analytics_admin_tables.sql Wasn't Deployed

### Root Cause
The `02_analytics_admin_tables.sql` script was **NOT automatically deployed** because:

1. **Docker Compose Configuration**: Only `01_init_database_V4.sql` is mounted to `/docker-entrypoint-initdb.d/`
   ```yaml
   volumes:
     - ./scripts/01_init_database_V4.sql:/docker-entrypoint-initdb.d/01_init_database.sql
     # ❌ 02_analytics_admin_tables.sql is NOT mounted
   ```

2. **PostgreSQL Auto-Init**: PostgreSQL only runs scripts in `/docker-entrypoint-initdb.d/` during container initialization
3. **Missing Volume Mount**: The analytics/admin script was never copied to the container's init directory

### Result
- ✅ **18 tables** from `01_init_database_V4.sql` were created
- ❌ **8 additional tables** from `02_analytics_admin_tables.sql` were missing

---

## Manual Database Deployment Steps

### Prerequisites
- Ubuntu PC with Docker installed
- SSH access to deployment server
- Database container running (fr02-postgres-v2)

### Step 1: Connect to Ubuntu Server
```bash
ssh abc@192.168.22.172
cd Documents/Database_18Sep_11AM
```

### Step 2: Verify Current Database State
```bash
# Check current table count
docker exec fr02-postgres-v2 psql -U kb_admin -d knowledge_base_v2 -c \
  "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';"

# List current tables
docker exec fr02-postgres-v2 psql -U kb_admin -d knowledge_base_v2 -c \
  "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
```

**Expected Initial State**: 18 tables from FR01/FR02 (main schema)

### Step 3: Deploy FR01/FR02 Core Schema (if needed)
If database is empty or incomplete:

```bash
# Copy main init script to container
docker cp scripts/01_init_database_V4.sql fr02-postgres-v2:/tmp/01_init_database_V4.sql

# Execute main schema
docker exec fr02-postgres-v2 psql -U kb_admin -d knowledge_base_v2 -f /tmp/01_init_database_V4.sql
```

**Expected Result**: 18 core tables created

### Step 4: Deploy Analytics/Admin Tables (FR07/FR08)
```bash
# Copy analytics/admin script to container
docker cp scripts/02_analytics_admin_tables.sql fr02-postgres-v2:/tmp/02_analytics_admin_tables.sql

# Execute analytics/admin schema
docker exec fr02-postgres-v2 psql -U kb_admin -d knowledge_base_v2 -f /tmp/02_analytics_admin_tables.sql
```

**Expected Result**: 8 additional tables + 4 views created

### Step 5: Verify Complete Deployment
```bash
# Verify final table count
docker exec fr02-postgres-v2 psql -U kb_admin -d knowledge_base_v2 -c \
  "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';"

# List all tables
docker exec fr02-postgres-v2 psql -U kb_admin -d knowledge_base_v2 -c \
  "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
```

**Expected Final State**: 26 total tables

---

## Complete Table Schema Overview

### FR01/FR02 Core Tables (18 tables)
1. `schema_migrations` - Schema version tracking
2. `users` - User management
3. `user_sessions` - User session tracking
4. `user_events` - User activity events
5. `documents_metadata_v2` - Document metadata
6. `document_chunks_enhanced` - Document chunks
7. `document_bm25_index` - Full-text search index
8. `vietnamese_text_analysis` - Vietnamese language processing
9. `data_ingestion_jobs` - Data pipeline jobs
10. `chunk_processing_logs` - Chunk processing logs
11. `processing_errors` - Error tracking
12. `pipeline_metrics` - Pipeline performance metrics
13. `rag_pipeline_sessions` - RAG session tracking
14. `search_analytics` - Search analytics (basic)
15. `user_activity_summary` - User activity summaries
16. `document_usage_stats` - Document usage statistics
17. `system_metrics` - System metrics (basic)
18. `report_generation` - Report generation tracking

### FR07/FR08 Analytics/Admin Tables (8 additional)
19. `analytics_cache` - Analytics query cache
20. `admin_actions` - Admin action logs
21. `system_health_log` - System health monitoring
22. `backup_status` - Backup operation tracking
23. `vw_chunking_performance` - Chunking performance view
24. `vw_document_processing_stats` - Document processing view
25. `vw_ingestion_job_summary` - Job summary view
26. `vw_pipeline_performance` - Pipeline performance view

---

## Troubleshooting

### Issue: Script Execution Errors
If you encounter errors during script execution:

```bash
# Check PostgreSQL logs
docker logs fr02-postgres-v2 --tail 50

# Check database connection
docker exec fr02-postgres-v2 pg_isready -U kb_admin -d knowledge_base_v2

# Connect to database manually
docker exec -it fr02-postgres-v2 psql -U kb_admin -d knowledge_base_v2
```

### Issue: Permission Errors
```bash
# Fix file permissions
chmod 644 scripts/01_init_database_V4.sql
chmod 644 scripts/02_analytics_admin_tables.sql

# Verify container user
docker exec fr02-postgres-v2 whoami
```

### Issue: Missing Dependencies
If scripts fail due to missing extensions:
```sql
-- Connect to database and run:
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "unaccent";
```

---

## Alternative: Fix Docker Compose (Permanent Solution)

To prevent this issue in future deployments, update `docker-compose.yml`:

```yaml
postgres:
  # ... other config ...
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./config/postgres.conf:/etc/postgresql/postgresql.conf
    - ./scripts/01_init_database_V4.sql:/docker-entrypoint-initdb.d/01_init_database.sql
    - ./scripts/02_analytics_admin_tables.sql:/docker-entrypoint-initdb.d/02_analytics_admin_tables.sql  # ADD THIS LINE
    - chatbot_storage:/opt/chatbot-storage
```

**Note**: This only works for fresh deployments. For existing containers, use the manual steps above.

---

## Verification Commands

### Quick Health Check
```bash
# Database accessibility
docker exec fr02-postgres-v2 pg_isready -U kb_admin -d knowledge_base_v2

# Table count verification
docker exec fr02-postgres-v2 psql -U kb_admin -d knowledge_base_v2 -c \
  "SELECT 'Core Tables: ' || COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name NOT LIKE 'vw_%';"

# View count verification
docker exec fr02-postgres-v2 psql -U kb_admin -d knowledge_base_v2 -c \
  "SELECT 'Views: ' || COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'vw_%';"
```

### Test Analytics Tables
```bash
# Test analytics cache table
docker exec fr02-postgres-v2 psql -U kb_admin -d knowledge_base_v2 -c \
  "SELECT COUNT(*) as analytics_cache_count FROM analytics_cache;"

# Test admin actions table
docker exec fr02-postgres-v2 psql -U kb_admin -d knowledge_base_v2 -c \
  "SELECT COUNT(*) as admin_actions_count FROM admin_actions;"
```

---

## Summary

The `02_analytics_admin_tables.sql` was not deployed because it was not included in the Docker Compose volume mounts. This guide provides step-by-step manual deployment to ensure all 26 database tables are properly created for full FR07 (Analytics) and FR08 (Admin) functionality.

**Total Expected Tables**: 26 (18 core + 8 analytics/admin)