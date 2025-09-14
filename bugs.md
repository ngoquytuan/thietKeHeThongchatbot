---
Xử lý bug tại FR03.3/refactor_FR03.3.md

---

Bạn đã chỉ ra một **thiếu sót quan trọng** trong schema hiện tại! Schema FR-02.1 v2.0 hiện tại **chưa có trường lưu đường dẫn file gốc**. Đây là vấn đề cần bổ sung ngay.

## 🚨 **VẤN ĐỀ HIỆN TẠI**

Schema `documents_metadata_v2` thiếu các trường quan trọng cho file management:
- Đường dẫn file gốc
- Metadata về file export package  
- Liên kết traceability

## 🔧 **GIẢI PHÁP: ENHANCED SCHEMA UPDATE**

### **1. Bổ sung trường File Management vào documents_metadata_v2**
```sql
-- CẬP NHẬT SCHEMA documents_metadata_v2
ALTER TABLE documents_metadata_v2 ADD COLUMN IF NOT EXISTS original_file_info JSONB DEFAULT '{}';
ALTER TABLE documents_metadata_v2 ADD COLUMN IF NOT EXISTS export_package_info JSONB DEFAULT '{}';
ALTER TABLE documents_metadata_v2 ADD COLUMN IF NOT EXISTS file_access_info JSONB DEFAULT '{}';

-- Update existing records with file information
UPDATE documents_metadata_v2 SET 
    original_file_info = '{
        "original_file_path": null,
        "original_filename": null,
        "file_size_bytes": 0,
        "file_hash": null,
        "mime_type": null,
        "created_at": null
    }'::jsonb,
    export_package_info = '{
        "fr03_1_package_path": null,
        "package_timestamp": null,
        "package_hash": null,
        "export_version": "1.0"
    }'::jsonb,
    file_access_info = '{
        "storage_tier": "warm",
        "access_count": 0,
        "last_accessed": null,
        "retention_policy": "7_years"
    }'::jsonb
WHERE original_file_info = '{}';
```

### **2. File Storage Management Strategy**

#### **Storage Architecture**
```bash
/opt/chatbot-storage/
├── original/                    # File gốc được giữ lại
│   └── {YYYY}/{MM}/{DD}/       # Phân chia theo ngày
│       └── {DEPT}_{TYPE}_{TIMESTAMP}/
│           ├── original_file.pdf           # File gốc
│           ├── file_metadata.json         # Metadata chi tiết
│           └── access_log.json            # Log truy cập
├── packages/                   # FR03.1 export packages
│   └── {YYYY}/{MM}/{DD}/
│       └── {DEPT}_{TYPE}_{TIMESTAMP}.zip  # Complete package
└── temp/                       # Temporary processing files
    └── processing_{job_id}/
```

#### **File Information Structure**
```json
// original_file_info trong PostgreSQL
{
  "original_file_path": "/opt/chatbot-storage/original/2025/09/12/HR_POLICY_20250912_143022/employee_handbook.pdf",
  "original_filename": "employee_handbook.pdf", 
  "file_size_bytes": 2847392,
  "file_hash": "sha256:abc123def456...",
  "mime_type": "application/pdf",
  "upload_timestamp": "2025-09-12T14:30:22Z",
  "uploaded_by": "hr.manager@company.com",
  "file_accessible": true,
  "preservation_status": "preserved"
}

// export_package_info
{
  "fr03_1_package_path": "/opt/chatbot-storage/packages/2025/09/12/HR_POLICY_20250912_143022.zip",
  "package_timestamp": "2025-09-12T14:35:45Z",
  "package_hash": "sha256:def789abc012...", 
  "package_size_bytes": 1245678,
  "export_version": "1.0",
  "processing_job_id": "uuid-of-job",
  "package_accessible": true
}

// file_access_info
{
  "storage_tier": "warm",           // hot, warm, cold
  "access_count": 15,
  "last_accessed": "2025-09-12T16:22:10Z",
  "retention_policy": "7_years", 
  "backup_locations": [
    "/backup/chatbot/2025/09/12/HR_POLICY_20250912_143022/",
    "s3://chatbot-backup/original/2025/09/12/"
  ],
  "legal_hold": false,
  "scheduled_deletion": null
}
```

## 🔄 **CẬP NHẬT QUY TRÌNH FR03.3**

### **Enhanced Import Process với File Management**
```python
async def import_document_with_file_tracking(extracted_dir: str, job_id: str, 
                                           original_zip_path: str, conn: asyncpg.Connection):
    """Enhanced import with original file preservation"""
    
    metadata_file = f"{extracted_dir}/FOR_DATABASE/document_metadata_v2.json"
    manifest_file = f"{extracted_dir}/manifest.json"
    
    # Read metadata và manifest
    with open(metadata_file, 'r', encoding='utf-8') as f:
        document_data = json.load(f)
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Preserve original file
    original_file_path = await preserve_original_file(extracted_dir, job_id, manifest)
    package_storage_path = await archive_export_package(original_zip_path, job_id)
    
    # Enhanced document metadata with file information
    enhanced_insert_query = """
        INSERT INTO documents_metadata_v2 (
            document_id, title, content, document_type, access_level,
            department_owner, author, status, language_detected,
            vietnamese_segmented, diacritics_normalized, tone_marks_preserved,
            search_text_normalized, indexable_content, extracted_emails,
            extracted_phones, extracted_dates, embedding_model_primary,
            chunk_count, file_size_bytes, search_tokens, 
            original_file_info, export_package_info, file_access_info,
            created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, 
            $15, $16, $17, $18, $19, $20, to_tsvector('simple', $13), 
            $21, $22, $23, $24, $25
        )
        RETURNING document_id
    """
    
    # Prepare file information
    original_file_info = {
        "original_file_path": original_file_path,
        "original_filename": manifest.get('original_filename', 'unknown'),
        "file_size_bytes": manifest.get('file_size_bytes', 0),
        "file_hash": manifest.get('file_hash', ''),
        "mime_type": manifest.get('mime_type', 'application/octet-stream'),
        "upload_timestamp": manifest.get('created_at', datetime.now().isoformat()),
        "uploaded_by": manifest.get('author_email', ''),
        "file_accessible": True,
        "preservation_status": "preserved"
    }
    
    export_package_info = {
        "fr03_1_package_path": package_storage_path,
        "package_timestamp": datetime.now().isoformat(),
        "package_hash": calculate_file_hash(original_zip_path),
        "package_size_bytes": os.path.getsize(original_zip_path),
        "export_version": "1.0",
        "processing_job_id": job_id,
        "package_accessible": True
    }
    
    file_access_info = {
        "storage_tier": "warm",
        "access_count": 0,
        "last_accessed": None,
        "retention_policy": "7_years",
        "backup_locations": [],
        "legal_hold": False,
        "scheduled_deletion": None
    }
    
    # Execute insert with file information
    document_id = await conn.fetchval(
        enhanced_insert_query,
        uuid.UUID(document_data['document_id']),
        document_data['title'],
        document_data.get('content', ''),
        document_data['document_type'], 
        document_data['access_level'],
        document_data['department_owner'],
        document_data['author'],
        document_data.get('status', 'approved'),
        document_data.get('language_detected', 'vi'),
        document_data.get('vietnamese_segmented', True),
        document_data.get('diacritics_normalized', True),
        document_data.get('tone_marks_preserved', True),
        document_data.get('search_text_normalized', ''),
        document_data.get('indexable_content', ''),
        document_data.get('extracted_emails', []),
        document_data.get('extracted_phones', []),
        document_data.get('extracted_dates', []),
        document_data.get('embedding_model_primary', 'Qwen/Qwen3-Embedding-0.6B'),
        document_data.get('chunk_count', 0),
        document_data.get('file_size_bytes', 0),
        json.dumps(original_file_info),
        json.dumps(export_package_info), 
        json.dumps(file_access_info),
        datetime.now(),
        datetime.now()
    )
    
    return document_id

async def preserve_original_file(extracted_dir: str, job_id: str, manifest: dict) -> str:
    """Preserve original file to long-term storage"""
    
    # Find original file in extracted package
    original_dir = f"{extracted_dir}/original"
    original_files = list(Path(original_dir).glob("*"))
    
    if not original_files:
        raise ValueError("No original file found in package")
    
    original_file = original_files[0]  # Take first file
    
    # Create storage path with date organization
    now = datetime.now()
    storage_date_path = f"{now.year:04d}/{now.month:02d}/{now.day:02d}"
    
    # Extract package name from manifest
    package_name = manifest.get('package_name', f"UNKNOWN_{job_id}")
    
    storage_dir = f"/opt/chatbot-storage/original/{storage_date_path}/{package_name}"
    os.makedirs(storage_dir, exist_ok=True)
    
    # Copy original file
    preserved_file_path = f"{storage_dir}/{original_file.name}"
    shutil.copy2(original_file, preserved_file_path)
    
    # Create file metadata
    file_metadata = {
        "original_filename": original_file.name,
        "preserved_at": datetime.now().isoformat(),
        "file_size": os.path.getsize(preserved_file_path),
        "file_hash": calculate_file_hash(preserved_file_path),
        "processing_job_id": job_id,
        "package_source": manifest.get('package_name', ''),
        "preservation_method": "copy"
    }
    
    with open(f"{storage_dir}/file_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(file_metadata, f, ensure_ascii=False, indent=2)
    
    # Initialize access log
    access_log = {
        "created_at": datetime.now().isoformat(),
        "access_history": []
    }
    
    with open(f"{storage_dir}/access_log.json", 'w', encoding='utf-8') as f:
        json.dump(access_log, f, ensure_ascii=False, indent=2)
    
    return preserved_file_path

async def archive_export_package(zip_path: str, job_id: str) -> str:
    """Archive FR03.1 export package"""
    
    now = datetime.now()
    archive_date_path = f"{now.year:04d}/{now.month:02d}/{now.day:02d}"
    
    zip_filename = os.path.basename(zip_path)
    archive_dir = f"/opt/chatbot-storage/packages/{archive_date_path}"
    os.makedirs(archive_dir, exist_ok=True)
    
    archived_package_path = f"{archive_dir}/{zip_filename}"
    shutil.copy2(zip_path, archived_package_path)
    
    return archived_package_path
```

## 📂 **API ĐỂ TRUY CẬP FILE GỐC**

### **File Access API trong FR-02.1**
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
import mimetypes

@app.get("/api/documents/{document_id}/original")
async def get_original_file(
    document_id: str, 
    current_user: User = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """Download original file cho document"""
    
    # Get file information from database
    file_info = await conn.fetchrow("""
        SELECT original_file_info, file_access_info, access_level, title
        FROM documents_metadata_v2 
        WHERE document_id = $1
    """, uuid.UUID(document_id))
    
    if not file_info:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check access permissions
    if not check_document_access(current_user, file_info['access_level']):
        raise HTTPException(status_code=403, detail="Access denied")
    
    original_file_info = json.loads(file_info['original_file_info'])
    file_path = original_file_info.get('original_file_path')
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Original file not accessible")
    
    # Log file access
    await log_file_access(document_id, current_user.user_id, conn)
    
    # Determine mime type
    mime_type = original_file_info.get('mime_type')
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(file_path)
    
    return FileResponse(
        file_path, 
        media_type=mime_type,
        filename=original_file_info.get('original_filename', 'document')
    )

@app.get("/api/documents/{document_id}/package")
async def get_export_package(
    document_id: str,
    current_user: User = Depends(get_current_admin_user),  # Admin only
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """Download FR03.1 export package (admin only)"""
    
    file_info = await conn.fetchrow("""
        SELECT export_package_info, title
        FROM documents_metadata_v2 
        WHERE document_id = $1
    """, uuid.UUID(document_id))
    
    if not file_info:
        raise HTTPException(status_code=404, detail="Document not found")
    
    export_info = json.loads(file_info['export_package_info'])
    package_path = export_info.get('fr03_1_package_path')
    
    if not package_path or not os.path.exists(package_path):
        raise HTTPException(status_code=404, detail="Export package not accessible")
    
    return FileResponse(
        package_path,
        media_type='application/zip',
        filename=f"{file_info['title']}_export_package.zip"
    )

async def log_file_access(document_id: str, user_id: str, conn: asyncpg.Connection):
    """Log file access for auditing"""
    
    # Update access count và last accessed
    await conn.execute("""
        UPDATE documents_metadata_v2 
        SET file_access_info = jsonb_set(
            jsonb_set(
                file_access_info, 
                '{access_count}', 
                ((file_access_info->>'access_count')::int + 1)::text::jsonb
            ),
            '{last_accessed}',
            to_jsonb($1::text)
        )
        WHERE document_id = $2
    """, datetime.now().isoformat(), uuid.UUID(document_id))
    
    # Log in separate audit table nếu cần
    await conn.execute("""
        INSERT INTO user_events (user_id, event_type, event_data)
        VALUES ($1, 'file_access', $2)
    """, uuid.UUID(user_id), json.dumps({
        'document_id': document_id,
        'access_type': 'original_file_download',
        'timestamp': datetime.now().isoformat()
    }))
```

## 📋 **SUMMARY**

**Sau khi cập nhật:**

1. **PostgreSQL quản lý metadata** của file gốc qua trường `original_file_info`
2. **File system lưu trữ** file gốc tại `/opt/chatbot-storage/original/`
3. **API endpoints** cho phép download file gốc với proper authentication
4. **Audit logging** theo dõi việc truy cập file
5. **Traceability đầy đủ** từ document ID → file gốc → export package

Bạn cần chạy migration để bổ sung các trường file management vào schema hiện tại!
