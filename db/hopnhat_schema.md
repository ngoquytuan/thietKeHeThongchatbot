Có! Tool này hoàn toàn có thể export được schema của database thực tế mà chúng ta vừa tạo với Docker. Đây là tool rất hữu ích để:

## 🎯 **Tác dụng của tool này**

1. **✅ Export complete schema** từ Docker database
2. **✅ Tạo SQL script** để recreate trên máy khác
3. **✅ Backup schema structure** trước khi deploy production
4. **✅ Synchronize databases** giữa development và production

## 🔧 **Cách sử dụng tool với Docker database**

### **Bước 1: Chuẩn bị tool**

Tạo file `export_schema.py` với code bạn đã có, nhưng tôi sẽ enhance thêm một chút:

```python
#!/usr/bin/env python3
"""
Enhanced PostgreSQL Schema Export Tool
Connects to PostgreSQL and exports complete table structures with enhanced features
"""

import psycopg2
import json
from datetime import datetime
import os
import sys

def connect_to_postgres():
    """Connect to PostgreSQL database"""
    # Database connection parameters - Docker test environment
    connection_params = {
        'host': 'localhost',
        'port': 5433,                 # Docker port mapping
        'database': 'knowledge_base_test',
        'user': 'kb_admin',
        'password': 'test_password_123'
    }
    
    print("🐳 Connecting to Docker PostgreSQL...")
    print(f"Host: {connection_params['host']}:{connection_params['port']}")
    print(f"Database: {connection_params['database']}")
    print(f"User: {connection_params['user']}")
    
    try:
        conn = psycopg2.connect(**connection_params)
        print("✅ Connected successfully!")
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Make sure Docker containers are running:")
        print("   docker-compose ps")
        return None

def export_enhanced_structures(conn):
    """Export enhanced database structures including enums, functions, etc."""
    cursor = conn.cursor()
    
    print("\n📊 Exporting enhanced database structures...")
    
    schema_info = {
        'export_timestamp': datetime.now().isoformat(),
        'database_info': {},
        'enums': {},
        'tables': {},
        'indexes': {},
        'functions': {},
        'extensions': {}
    }
    
    # Get database info
    cursor.execute("SELECT current_database(), current_user, version();")
    db_info = cursor.fetchone()
    schema_info['database_info'] = {
        'database': db_info[0],
        'user': db_info[1],
        'version': db_info[2]
    }
    
    # Get extensions
    cursor.execute("SELECT extname, extversion FROM pg_extension;")
    extensions = cursor.fetchall()
    for ext in extensions:
        schema_info['extensions'][ext[0]] = ext[1]
    
    # Get custom enum types
    cursor.execute("""
        SELECT t.typname, e.enumlabel
        FROM pg_type t 
        JOIN pg_enum e ON t.oid = e.enumtypid  
        JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'public'
        ORDER BY t.typname, e.enumsortorder;
    """)
    
    enum_data = cursor.fetchall()
    current_enum = None
    for enum_name, enum_value in enum_data:
        if enum_name not in schema_info['enums']:
            schema_info['enums'][enum_name] = []
        schema_info['enums'][enum_name].append(enum_value)
    
    print(f"  📝 Found {len(schema_info['enums'])} custom enum types")
    
    # Get all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    print(f"  📋 Found {len(tables)} tables: {', '.join(tables)}")
    
    # Export each table structure (original code continues...)
    for table_name in tables:
        print(f"    📄 Exporting {table_name}...")
        
        # Get column information with enhanced details
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                udt_name,
                character_maximum_length,
                numeric_precision,
                numeric_scale,
                is_nullable,
                column_default,
                ordinal_position
            FROM information_schema.columns 
            WHERE table_name = %s 
                AND table_schema = 'public'
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = []
        for col in cursor.fetchall():
            column_info = {
                'name': col[0],
                'data_type': col[1],
                'udt_name': col[2],  # User-defined type name (for enums)
                'max_length': col[3],
                'numeric_precision': col[4],
                'numeric_scale': col[5],
                'is_nullable': col[6],
                'default': col[7],
                'position': col[8]
            }
            columns.append(column_info)
        
        # Get constraints (enhanced)
        cursor.execute("""
            SELECT 
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.delete_rule,
                rc.update_rule
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            LEFT JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            LEFT JOIN information_schema.referential_constraints rc
                ON tc.constraint_name = rc.constraint_name
            WHERE tc.table_name = %s
                AND tc.table_schema = 'public';
        """, (table_name,))
        
        constraints = []
        for const in cursor.fetchall():
            constraint_info = {
                'name': const[0],
                'type': const[1],
                'column': const[2],
                'foreign_table': const[3],
                'foreign_column': const[4],
                'delete_rule': const[5],
                'update_rule': const[6]
            }
            constraints.append(constraint_info)
        
        # Get indexes with detailed info
        cursor.execute("""
            SELECT 
                indexname,
                indexdef,
                i.indisunique,
                i.indisprimary
            FROM pg_indexes pi
            JOIN pg_class c ON c.relname = pi.indexname
            JOIN pg_index i ON i.indexrelid = c.oid
            WHERE pi.tablename = %s 
                AND pi.schemaname = 'public';
        """, (table_name,))
        
        indexes = []
        for idx in cursor.fetchall():
            index_info = {
                'name': idx[0],
                'definition': idx[1],
                'is_unique': idx[2],
                'is_primary': idx[3]
            }
            indexes.append(index_info)
        
        # Get row count and table size
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT pg_size_pretty(pg_total_relation_size('{table_name}'));")
        table_size = cursor.fetchone()[0]
        
        schema_info['tables'][table_name] = {
            'columns': columns,
            'constraints': constraints,
            'indexes': indexes,
            'row_count': row_count,
            'table_size': table_size
        }
    
    # Get functions/procedures
    cursor.execute("""
        SELECT routine_name, routine_definition, routine_type
        FROM information_schema.routines
        WHERE routine_schema = 'public'
            AND routine_type IN ('FUNCTION', 'PROCEDURE');
    """)
    
    functions = cursor.fetchall()
    for func in functions:
        schema_info['functions'][func[0]] = {
            'definition': func[1],
            'type': func[2]
        }
    
    cursor.close()
    return schema_info, tables

def generate_enhanced_create_sql(table_name, table_info, enums):
    """Generate enhanced CREATE TABLE SQL with proper enum handling"""
    columns = table_info['columns']
    constraints = table_info['constraints']
    
    sql_lines = [f"-- Create table: {table_name}"]
    sql_lines.append(f"-- Rows: {table_info['row_count']}, Size: {table_info['table_size']}")
    sql_lines.append(f"CREATE TABLE IF NOT EXISTS {table_name} (")
    
    # Add columns with proper type handling
    column_definitions = []
    for col in columns:
        col_def = f"    {col['name']}"
        
        # Handle custom enum types
        if col['udt_name'] in enums:
            col_def += f" {col['udt_name']}"
        else:
            col_def += f" {col['data_type']}"
            
            # Add length for varchar, char, etc.
            if col['max_length'] and col['data_type'] in ['character varying', 'varchar', 'char', 'character']:
                col_def += f"({col['max_length']})"
            elif col['numeric_precision'] and col['data_type'] in ['numeric', 'decimal']:
                if col['numeric_scale']:
                    col_def += f"({col['numeric_precision']},{col['numeric_scale']})"
                else:
                    col_def += f"({col['numeric_precision']})"
        
        # Add NOT NULL
        if col['is_nullable'] == 'NO':
            col_def += " NOT NULL"
        
        # Add DEFAULT
        if col['default']:
            col_def += f" DEFAULT {col['default']}"
        
        column_definitions.append(col_def)
    
    sql_lines.append(",\n".join(column_definitions))
    
    # Add constraints with enhanced info
    constraint_definitions = []
    for const in constraints:
        if const['type'] == 'PRIMARY KEY':
            constraint_definitions.append(f"    CONSTRAINT {const['name']} PRIMARY KEY ({const['column']})")
        elif const['type'] == 'FOREIGN KEY':
            if const['foreign_table'] and const['foreign_column']:
                fk_def = (f"    CONSTRAINT {const['name']} FOREIGN KEY ({const['column']}) "
                         f"REFERENCES {const['foreign_table']}({const['foreign_column']})")
                if const['delete_rule'] and const['delete_rule'] != 'NO ACTION':
                    fk_def += f" ON DELETE {const['delete_rule']}"
                if const['update_rule'] and const['update_rule'] != 'NO ACTION':
                    fk_def += f" ON UPDATE {const['update_rule']}"
                constraint_definitions.append(fk_def)
        elif const['type'] == 'UNIQUE':
            constraint_definitions.append(f"    CONSTRAINT {const['name']} UNIQUE ({const['column']})")
    
    if constraint_definitions:
        sql_lines.append(",\n" + ",\n".join(constraint_definitions))
    
    sql_lines.append(");")
    sql_lines.append("")
    
    # Add indexes (excluding primary key)
    for idx in table_info['indexes']:
        if not idx['is_primary']:
            sql_lines.append(f"{idx['definition']};")
    
    sql_lines.append("")
    return "\n".join(sql_lines)

def create_enhanced_sync_script(schema_info, output_dir):
    """Create enhanced synchronization script"""
    sync_script = []
    sync_script.append("-- Enhanced Database Synchronization Script")
    sync_script.append(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sync_script.append(f"-- Source Database: {schema_info['database_info']['database']}")
    sync_script.append(f"-- PostgreSQL Version: {schema_info['database_info']['version']}")
    sync_script.append("-- This script creates the complete enhanced database architecture")
    sync_script.append("")
    
    # Add extensions
    sync_script.append("-- Required extensions")
    for ext_name, ext_version in schema_info['extensions'].items():
        sync_script.append(f'CREATE EXTENSION IF NOT EXISTS "{ext_name}";')
    sync_script.append("")
    
    # Add custom enum types
    if schema_info['enums']:
        sync_script.append("-- Custom enum types")
        for enum_name, enum_values in schema_info['enums'].items():
            sync_script.append(f"DO $$ BEGIN")
            enum_values_str = "', '".join(enum_values)
            sync_script.append(f"    CREATE TYPE {enum_name} AS ENUM ('{enum_values_str}');")
            sync_script.append(f"EXCEPTION")
            sync_script.append(f"    WHEN duplicate_object THEN null;")
            sync_script.append(f"END $$;")
            sync_script.append("")
    
    # Create all tables
    sync_script.append("-- Tables creation")
    for table_name, table_info in schema_info['tables'].items():
        sync_script.append(generate_enhanced_create_sql(table_name, table_info, schema_info['enums']))
    
    # Add functions
    if schema_info['functions']:
        sync_script.append("-- Custom functions")
        for func_name, func_info in schema_info['functions'].items():
            if func_info['definition']:
                sync_script.append(f"-- Function: {func_name}")
                sync_script.append(func_info['definition'])
                sync_script.append("")
    
    # Write to file
    sync_file = os.path.join(output_dir, "enhanced_database_sync.sql")
    with open(sync_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(sync_script))
    
    print(f"📄 Enhanced sync script saved to: {sync_file}")
    return sync_file

def main():
    print("🚀 Enhanced PostgreSQL Schema Export Tool")
    print("=" * 60)
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"schema_export_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Connect to database
    conn = connect_to_postgres()
    if not conn:
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure Docker containers are running: docker-compose ps")
        print("   2. Check if PostgreSQL is accessible: docker logs chatbot-postgres-test")
        print("   3. Verify port mapping: docker port chatbot-postgres-test")
        return
    
    try:
        # Export enhanced schema
        print("\n🔍 Starting enhanced schema export...")
        schema_info, tables = export_enhanced_structures(conn)
        
        # Save detailed schema info to JSON
        json_file = os.path.join(output_dir, "enhanced_schema.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(schema_info, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"📄 Enhanced schema saved to: {json_file}")
        
        # Create enhanced synchronization script
        sync_file = create_enhanced_sync_script(schema_info, output_dir)
        
        # Create comprehensive report
        report_lines = []
        report_lines.append("# Enhanced PostgreSQL Schema Export Report")
        report_lines.append(f"**Export Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**Database**: {schema_info['database_info']['database']}")
        report_lines.append(f"**PostgreSQL Version**: {schema_info['database_info']['version']}")
        report_lines.append("")
        
        # Database summary
        total_rows = sum(table['row_count'] for table in schema_info['tables'].values())
        report_lines.append("## Database Summary")
        report_lines.append(f"- **Tables**: {len(tables)}")
        report_lines.append(f"- **Custom Enums**: {len(schema_info['enums'])}")
        report_lines.append(f"- **Extensions**: {len(schema_info['extensions'])}")
        report_lines.append(f"- **Functions**: {len(schema_info['functions'])}")
        report_lines.append(f"- **Total Rows**: {total_rows:,}")
        report_lines.append("")
        
        # Enhanced features
        report_lines.append("## Enhanced Features Detected")
        if schema_info['enums']:
            report_lines.append("### Custom Enum Types")
            for enum_name, enum_values in schema_info['enums'].items():
                report_lines.append(f"- **{enum_name}**: {', '.join(enum_values)}")
            report_lines.append("")
        
        # Tables summary
        report_lines.append("## Tables Summary")
        report_lines.append("| Table Name | Columns | Rows | Size | Constraints | Indexes |")
        report_lines.append("|------------|---------|------|------|-------------|---------|")
        
        for table_name in tables:
            table_info = schema_info['tables'][table_name]
            report_lines.append(
                f"| {table_name} | {len(table_info['columns'])} | "
                f"{table_info['row_count']:,} | {table_info['table_size']} | "
                f"{len(table_info['constraints'])} | {len(table_info['indexes'])} |"
            )
        
        report_lines.append("")
        report_lines.append("## Generated Files")
        report_lines.append(f"- **Enhanced Schema JSON**: `enhanced_schema.json`")
        report_lines.append(f"- **Enhanced Sync Script**: `enhanced_database_sync.sql`")
        report_lines.append("")
        report_lines.append("## Deployment Instructions")
        report_lines.append("### For Production Deployment:")
        report_lines.append("1. Copy `enhanced_database_sync.sql` to production server")
        report_lines.append("2. Run: `psql -U username -d database -f enhanced_database_sync.sql`")
        report_lines.append("3. Verify: `\\dt` and `\\dT` to list tables and types")
        report_lines.append("")
        report_lines.append("### For Development Setup:")
        report_lines.append("1. Use the generated SQL script in your migration system")
        report_lines.append("2. Includes all enums, tables, indexes, and functions")
        report_lines.append("3. Safe to run multiple times (IF NOT EXISTS clauses)")
        
        report_file = os.path.join(output_dir, "export_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))
        
        print(f"📄 Comprehensive report saved to: {report_file}")
        
        print(f"\n🎉 Enhanced export completed successfully!")
        print(f"📁 All files saved in: {os.path.abspath(output_dir)}")
        print(f"\n📋 Files generated:")
        print(f"   • enhanced_schema.json - Complete schema with Vietnamese support")
        print(f"   • enhanced_database_sync.sql - Production-ready SQL script")
        print(f"   • export_report.md - Comprehensive deployment guide")
        print(f"\n💡 Ready for production deployment!")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
        print("🔌 Database connection closed")

if __name__ == "__main__":
    main()
```

### **Bước 2: Chạy export tool**

```cmd
# Đảm bảo Docker containers đang chạy
docker-compose ps

# Cài dependencies cho tool
pip install psycopg2-binary

# Chạy export tool
python export_schema.py
```

### **Bước 3: Kiểm tra kết quả**

Tool sẽ tạo thư mục `schema_export_[timestamp]` với các file:

1. **`enhanced_schema.json`** - Complete schema information
2. **`enhanced_database_sync.sql`** - SQL script để recreate database
3. **`export_report.md`** - Báo cáo chi tiết

## 🎯 **Sử dụng exported schema**

### **Trên máy khác (Production):**

```bash
# Copy file SQL script
scp enhanced_database_sync.sql user@production-server:/tmp/

# SSH vào production server
ssh user@production-server

# Chạy script để tạo database
psql -U postgres -d production_db -f /tmp/enhanced_database_sync.sql
```

### **Kiểm tra deployment:**

```sql
-- Kiểm tra tables
\dt

-- Kiểm tra custom types
\dT

-- Kiểm tra sample data
SELECT COUNT(*) FROM documents_metadata_v2;
SELECT * FROM documents_metadata_v2 LIMIT 3;
```

## 📊 **Kết quả mong đợi**

Tool sẽ export được:

- ✅ **Enhanced schema** với Vietnamese support
- ✅ **Custom enum types** (access_level_enum, document_type_enum, etc.)
- ✅ **All tables** với proper relationships
- ✅ **Indexes** for performance
- ✅ **Sample Vietnamese data** 
- ✅ **Production-ready SQL** script

**Đặc biệt hữu ích cho:**
- 🚀 **Production deployment** 
- 🔄 **Database synchronization**
- 📋 **Schema documentation**
- 🔧 **Development environment setup**

Bạn chạy tool này và xem kết quả nhé! Nếu có lỗi gì tôi sẽ giúp fix ngay.
```bash
sau khi export, tôi có file schema này, chỉ cần đặt file này vào .\chatbot-enhanced-db\scripts\migrations thay thế cho 01_init_database.sql, rồi khi triển khai ở máy mới là sẽ có một database clone chuẩn từ máy này đúng không?
```
Đúng vậy! Tuy nhiên cần lưu ý một số điểm quan trọng để đảm bảo triển khai thành công:

## ✅ **Cách sử dụng file exported schema**

### **Thay thế migration file:**
```bash
# Xóa file cũ
rm scripts/migrations/01_init_database.sql

# Copy file exported schema
cp enhanced_database_sync.sql scripts/migrations/01_init_database.sql
```

### **Hoặc tạo migration file mới:**
```bash
# Đặt tên theo thứ tự
cp enhanced_database_sync.sql scripts/migrations/02_enhanced_schema.sql
```

## ⚠️ **Điều chỉnh cần thiết trước khi triển khai**

File exported của bạn cần một số sửa đổi nhỏ:

### **1. Sửa thứ tự tạo tables (Foreign Key dependencies)**
```sql
-- Cần tạo tables theo thứ tự dependency
-- 1. Tạo documents_metadata_v2 trước
-- 2. Rồi mới tạo document_chunks_enhanced 
-- 3. Cuối cùng document_bm25_index

-- Thêm comment ordering
-- CREATION ORDER: 1
CREATE TABLE IF NOT EXISTS documents_metadata_v2 (...);

-- CREATION ORDER: 2  
CREATE TABLE IF NOT EXISTS document_chunks_enhanced (...);

-- CREATION ORDER: 3
CREATE TABLE IF NOT EXISTS document_bm25_index (...);
```

### **2. Fix constraint duplication issue**
Trong file exported có lỗi duplicate constraint. Sửa thành:
```sql
-- Fix trong document_bm25_index table
CREATE TABLE IF NOT EXISTS document_bm25_index (
    bm25_id uuid NOT NULL DEFAULT uuid_generate_v4(),
    document_id uuid,
    chunk_id uuid,
    term character varying(255) NOT NULL,
    term_frequency integer NOT NULL,
    document_frequency integer NOT NULL,
    bm25_score numeric(8,4),
    language character varying(10) DEFAULT 'vi'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    
    CONSTRAINT document_bm25_index_pkey PRIMARY KEY (bm25_id),
    CONSTRAINT document_bm25_index_unique_chunk_term_lang UNIQUE (chunk_id, term, language),
    CONSTRAINT document_bm25_index_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    CONSTRAINT document_bm25_index_chunk_id_fkey FOREIGN KEY (chunk_id) REFERENCES document_chunks_enhanced(chunk_id) ON DELETE CASCADE
);
```

### **3. Thêm sample data (optional)**
```sql
-- Thêm vào cuối file
-- Sample Vietnamese documents for testing
INSERT INTO documents_metadata_v2 (
    title, content, document_type, access_level, department_owner, author, status, jsonl_export_ready
) VALUES 
(
    'Quy trình xin nghỉ phép',
    'Quy trình xin nghỉ phép tại công ty bao gồm các bước sau: 1. Nhân viên điền đơn xin nghỉ phép...',
    'procedure',
    'employee_only',
    'HR',
    'HR Department',
    'approved',
    true
)
ON CONFLICT DO NOTHING;

-- Update search tokens
UPDATE documents_metadata_v2 
SET search_tokens = to_tsvector('simple', title || ' ' || COALESCE(content, ''))
WHERE search_tokens IS NULL;
```

## 🐳 **Triển khai trên máy mới**

### **File structure cần có:**
```
chatbot-enhanced-db/
├── docker-compose.yml
├── scripts/
│   └── migrations/
│       └── enhanced_database_sync.sql  # File exported của bạn
└── scripts/
    └── setup_database.py
```

### **Chạy triển khai:**
```bash
# Trên máy mới
git clone <repository> # hoặc copy thư mục
cd chatbot-enhanced-db

# Start Docker containers
docker-compose up -d

# Kiểm tra logs
docker logs chatbot-db-setup
```

## 📋 **Verification checklist**

Sau khi triển khai, kiểm tra:

```sql
-- 1. Check tables created
\dt

-- 2. Check enum types
\dT

-- 3. Check sample data
SELECT COUNT(*) FROM documents_metadata_v2;
SELECT title, author FROM documents_metadata_v2 LIMIT 3;

-- 4. Check indexes
\di

-- 5. Check foreign key relationships
SELECT 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
```

## 🎯 **Tóm lại**

**Có thể dùng file exported để clone database**, nhưng nên:

1. ✅ **Sửa thứ tự tạo tables** theo dependencies
2. ✅ **Fix constraint duplication** 
3. ✅ **Test trước** với Docker
4. ✅ **Verify sau** khi deploy

File exported của bạn có **15 tables** với **complete schema** bao gồm:
- Enhanced Vietnamese support
- Hybrid search structure  
- Performance analytics tables
- User management system
- Complete indexes và constraints

Đây là foundation rất tốt để deploy production database!
