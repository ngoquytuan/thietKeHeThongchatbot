Tôi sẽ tạo file `scripts/migrations/01_init_database.sql` hoàn chỉnh và đúng thứ tự để bạn có thể sử dụng trực tiếp:

```sql
-- Enhanced Database Initialization Script
-- Compatible with PostgreSQL 15+
-- Optimized for Vietnamese chatbot system with hybrid search capabilities

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create custom enum types
DO $$ BEGIN
    CREATE TYPE access_level_enum AS ENUM (
        'public', 'employee_only', 'manager_only', 'director_only', 'system_admin'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE document_type_enum AS ENUM (
        'policy', 'procedure', 'technical_guide', 'report', 
        'manual', 'specification', 'template', 'form', 
        'presentation', 'training_material', 'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE document_status_enum AS ENUM (
        'draft', 'review', 'approved', 'published', 'archived', 'deprecated'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE userlevel AS ENUM (
        'GUEST', 'EMPLOYEE', 'MANAGER', 'DIRECTOR', 'SYSTEM_ADMIN'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE userstatus AS ENUM (
        'ACTIVE', 'INACTIVE', 'SUSPENDED', 'PENDING'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Table 1: Users (Base table)
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(32) NOT NULL,
    user_level userlevel NOT NULL DEFAULT 'EMPLOYEE',
    department VARCHAR(100),
    position VARCHAR(100),
    status userstatus NOT NULL DEFAULT 'ACTIVE',
    is_active BOOLEAN NOT NULL DEFAULT true,
    email_verified BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    last_activity TIMESTAMP WITH TIME ZONE,
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    preferences JSONB DEFAULT '{}',
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 2: User Sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_jti VARCHAR(255) UNIQUE NOT NULL,
    device_info VARCHAR(500),
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    logged_out_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- Table 3: Documents Metadata (Enhanced version)
CREATE TABLE IF NOT EXISTS documents_metadata_v2 (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Basic information
    title VARCHAR(500) NOT NULL,
    content TEXT,
    document_type document_type_enum NOT NULL,
    access_level access_level_enum NOT NULL DEFAULT 'employee_only',
    department_owner VARCHAR(100) NOT NULL,
    author VARCHAR(255) NOT NULL,
    status document_status_enum DEFAULT 'draft',
    
    -- Vietnamese language support
    language_detected VARCHAR(10) DEFAULT 'vi',
    vietnamese_segmented BOOLEAN DEFAULT false,
    diacritics_normalized BOOLEAN DEFAULT false,
    tone_marks_preserved BOOLEAN DEFAULT true,
    
    -- FlashRAG support
    flashrag_collection VARCHAR(100) DEFAULT 'default_collection',
    jsonl_export_ready BOOLEAN DEFAULT false,
    
    -- Search support
    search_tokens TSVECTOR,
    keyword_density JSONB DEFAULT '{}',
    heading_structure JSONB DEFAULT '{}',
    
    -- Metadata
    embedding_model_primary VARCHAR(100) DEFAULT 'text-embedding-ada-002',
    chunk_count INTEGER DEFAULT 0,
    file_size_bytes BIGINT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 4: Enhanced Document Chunks
CREATE TABLE IF NOT EXISTS document_chunks_enhanced (
    chunk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    
    -- Content data
    chunk_content TEXT NOT NULL,
    chunk_position INTEGER NOT NULL,
    chunk_size_tokens INTEGER,
    
    -- Semantic chunking metadata
    semantic_boundary BOOLEAN DEFAULT false,
    overlap_with_prev INTEGER DEFAULT 0,
    overlap_with_next INTEGER DEFAULT 0,
    heading_context TEXT,
    
    -- Quality and method
    chunk_method VARCHAR(20) DEFAULT 'semantic',
    chunk_quality_score DECIMAL(3,2) CHECK (chunk_quality_score BETWEEN 0.00 AND 1.00),
    
    -- Vector storage references
    embedding_model VARCHAR(100) DEFAULT 'text-embedding-ada-002',
    embedding_dimensions INTEGER DEFAULT 1536,
    
    -- BM25 support
    bm25_tokens TSVECTOR,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 5: BM25 Support Index
CREATE TABLE IF NOT EXISTS document_bm25_index (
    bm25_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    chunk_id UUID NOT NULL REFERENCES document_chunks_enhanced(chunk_id) ON DELETE CASCADE,
    
    -- BM25 data
    term VARCHAR(255) NOT NULL,
    term_frequency INTEGER NOT NULL,
    document_frequency INTEGER NOT NULL,
    bm25_score DECIMAL(8,4),
    
    -- Metadata
    language VARCHAR(10) DEFAULT 'vi',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(chunk_id, term, language)
);

-- Table 6: RAG Pipeline Sessions
CREATE TABLE IF NOT EXISTS rag_pipeline_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Query information
    original_query TEXT NOT NULL,
    processed_query TEXT,
    query_language VARCHAR(10) DEFAULT 'vi',
    
    -- Pipeline metadata
    pipeline_type VARCHAR(50) NOT NULL DEFAULT 'standard',
    pipeline_method VARCHAR(50) NOT NULL DEFAULT 'hybrid',
    
    -- Performance metrics
    chunks_retrieved INTEGER,
    processing_time_ms INTEGER,
    response_quality_score DECIMAL(3,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 7: Vietnamese Text Analysis
CREATE TABLE IF NOT EXISTS vietnamese_text_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES document_chunks_enhanced(chunk_id) ON DELETE CASCADE,
    
    -- Text data
    original_text TEXT NOT NULL,
    processed_text TEXT,
    
    -- Analysis results
    word_segmentation JSONB DEFAULT '{}',
    pos_tagging JSONB DEFAULT '{}',
    
    -- Vietnamese features
    compound_words TEXT[] DEFAULT '{}',
    technical_terms TEXT[] DEFAULT '{}',
    proper_nouns TEXT[] DEFAULT '{}',
    
    -- Quality metrics
    readability_score DECIMAL(3,2),
    formality_level VARCHAR(20),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 8: Search Analytics
CREATE TABLE IF NOT EXISTS search_analytics (
    search_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    session_id VARCHAR(255),
    
    -- Query data
    query TEXT NOT NULL,
    query_normalized TEXT,
    query_language VARCHAR(10) DEFAULT 'vi',
    search_method VARCHAR(50) NOT NULL,
    filters_applied JSONB DEFAULT '{}',
    
    -- Request parameters
    limit_requested INTEGER NOT NULL DEFAULT 10,
    offset_requested INTEGER DEFAULT 0,
    
    -- Results
    results_count INTEGER NOT NULL,
    has_results BOOLEAN NOT NULL,
    top_score DOUBLE PRECISION,
    avg_score DOUBLE PRECISION,
    
    -- Performance
    processing_time_ms INTEGER NOT NULL,
    semantic_search_time_ms INTEGER,
    bm25_search_time_ms INTEGER,
    
    -- User interaction
    clicked_results JSONB DEFAULT '{}',
    user_satisfaction INTEGER CHECK (user_satisfaction BETWEEN 1 AND 5),
    
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Table 9: User Activity Summary
CREATE TABLE IF NOT EXISTS user_activity_summary (
    summary_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Activity metrics
    login_count INTEGER DEFAULT 0,
    search_count INTEGER DEFAULT 0,
    document_views INTEGER DEFAULT 0,
    downloads INTEGER DEFAULT 0,
    session_count INTEGER DEFAULT 0,
    total_session_duration_minutes DOUBLE PRECISION DEFAULT 0,
    avg_session_duration_minutes DOUBLE PRECISION,
    unique_queries INTEGER DEFAULT 0,
    search_success_rate DOUBLE PRECISION,
    most_used_search_method VARCHAR(50),
    
    -- Usage data
    documents_accessed JSONB DEFAULT '{}',
    departments_accessed JSONB DEFAULT '{}',
    avg_search_time_ms DOUBLE PRECISION,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 10: User Events
CREATE TABLE IF NOT EXISTS user_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    session_id VARCHAR(255),
    
    -- Event data
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) NOT NULL,
    event_data JSONB DEFAULT '{}',
    
    -- Context
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    processing_time_ms INTEGER
);

-- Table 11: System Metrics
CREATE TABLE IF NOT EXISTS system_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metric_type VARCHAR(100) NOT NULL,
    
    -- Performance metrics
    response_time_ms DOUBLE PRECISION,
    memory_usage_mb DOUBLE PRECISION,
    cpu_usage_percent DOUBLE PRECISION,
    gpu_usage_percent DOUBLE PRECISION,
    gpu_memory_mb DOUBLE PRECISION,
    
    -- Database metrics
    active_connections INTEGER,
    database_size_mb DOUBLE PRECISION,
    query_count INTEGER,
    slow_query_count INTEGER,
    cache_hit_rate DOUBLE PRECISION,
    cache_size_mb DOUBLE PRECISION,
    
    -- API metrics
    endpoint VARCHAR(255),
    http_status_code INTEGER,
    error_count INTEGER,
    
    -- Additional data
    metric_metadata JSONB DEFAULT '{}'
);

-- Table 12: Document Usage Stats
CREATE TABLE IF NOT EXISTS document_usage_stats (
    stats_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Usage metrics
    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    search_hits INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    
    -- Engagement metrics
    avg_view_duration_seconds DOUBLE PRECISION,
    total_view_duration_seconds DOUBLE PRECISION DEFAULT 0,
    bounce_rate DOUBLE PRECISION,
    avg_search_rank DOUBLE PRECISION,
    avg_relevance_score DOUBLE PRECISION,
    
    -- Feedback metrics
    like_count INTEGER DEFAULT 0,
    dislike_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 13: Report Generation
CREATE TABLE IF NOT EXISTS report_generation (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requested_by UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Report configuration
    report_type VARCHAR(100) NOT NULL,
    report_format VARCHAR(20) NOT NULL,
    date_range_start TIMESTAMP WITH TIME ZONE NOT NULL,
    date_range_end TIMESTAMP WITH TIME ZONE NOT NULL,
    filters JSONB DEFAULT '{}',
    departments JSONB DEFAULT '{}',
    users_included JSONB DEFAULT '{}',
    
    -- Generation status
    status VARCHAR(50) DEFAULT 'pending',
    file_path VARCHAR(500),
    file_size_bytes INTEGER,
    
    -- Timestamps
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    generation_time_seconds DOUBLE PRECISION,
    error_message TEXT,
    
    -- Usage tracking
    download_count INTEGER DEFAULT 0,
    last_downloaded_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Create performance indexes
-- Documents indexes
CREATE INDEX IF NOT EXISTS idx_documents_v2_language ON documents_metadata_v2(language_detected);
CREATE INDEX IF NOT EXISTS idx_documents_v2_status ON documents_metadata_v2(status);
CREATE INDEX IF NOT EXISTS idx_documents_v2_collection ON documents_metadata_v2(flashrag_collection);
CREATE INDEX IF NOT EXISTS idx_documents_v2_search ON documents_metadata_v2 USING GIN(search_tokens);
CREATE INDEX IF NOT EXISTS idx_documents_v2_department ON documents_metadata_v2(department_owner);
CREATE INDEX IF NOT EXISTS idx_documents_v2_type ON documents_metadata_v2(document_type);

-- Chunks indexes
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_document ON document_chunks_enhanced(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_position ON document_chunks_enhanced(chunk_position);
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_semantic ON document_chunks_enhanced(semantic_boundary) WHERE semantic_boundary = true;
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_quality ON document_chunks_enhanced(chunk_quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_bm25 ON document_chunks_enhanced USING GIN(bm25_tokens);

-- BM25 indexes
CREATE INDEX IF NOT EXISTS idx_bm25_term ON document_bm25_index(term);
CREATE INDEX IF NOT EXISTS idx_bm25_chunk ON document_bm25_index(chunk_id);
CREATE INDEX IF NOT EXISTS idx_bm25_score ON document_bm25_index(bm25_score DESC);
CREATE INDEX IF NOT EXISTS idx_bm25_language ON document_bm25_index(language);

-- Pipeline indexes
CREATE INDEX IF NOT EXISTS idx_pipeline_sessions_created ON rag_pipeline_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_sessions_type ON rag_pipeline_sessions(pipeline_type, pipeline_method);
CREATE INDEX IF NOT EXISTS idx_pipeline_sessions_quality ON rag_pipeline_sessions(response_quality_score DESC);

-- Analytics indexes
CREATE INDEX IF NOT EXISTS idx_search_analytics_user_timestamp ON search_analytics(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_search_analytics_method_timestamp ON search_analytics(search_method, timestamp);
CREATE INDEX IF NOT EXISTS idx_search_analytics_performance ON search_analytics(processing_time_ms, results_count);

-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_department ON users(department);
CREATE INDEX IF NOT EXISTS idx_users_level ON users(user_level);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status, is_active);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active, expires_at);

-- System metrics indexes
CREATE INDEX IF NOT EXISTS idx_system_metrics_type_timestamp ON system_metrics(metric_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_system_metrics_endpoint_timestamp ON system_metrics(endpoint, timestamp);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp DESC);

-- Document usage indexes
CREATE INDEX IF NOT EXISTS idx_document_usage_stats_doc_date ON document_usage_stats(document_id, date);
CREATE INDEX IF NOT EXISTS idx_document_usage_stats_date ON document_usage_stats(date DESC);
CREATE INDEX IF NOT EXISTS idx_document_usage_stats_view_count ON document_usage_stats(view_count DESC);

-- Insert sample Vietnamese documents
INSERT INTO documents_metadata_v2 (
    title, content, document_type, access_level, department_owner, author, status, jsonl_export_ready
) VALUES 
(
    'Quy trình xin nghỉ phép',
    'Quy trình xin nghỉ phép tại công ty bao gồm các bước sau: 1. Nhân viên điền đơn xin nghỉ phép qua hệ thống HR. 2. Gửi đơn cho quản lý trực tiếp để phê duyệt. 3. Quản lý phê duyệt trong vòng 2 ngày làm việc. 4. HR cập nhật vào hệ thống và thông báo cho nhân viên. 5. Nhân viên nhận thông báo kết quả và lập kế hoạch nghỉ phép.',
    'procedure',
    'employee_only',
    'HR',
    'HR Department',
    'approved',
    true
),
(
    'Chính sách làm việc từ xa',
    'Chính sách làm việc từ xa (Work From Home - WFH) được áp dụng như sau: - Nhân viên có thể làm việc từ xa tối đa 3 ngày/tuần, tùy thuộc vào tính chất công việc. - Cần đăng ký trước ít nhất 1 ngày thông qua hệ thống internal. - Đảm bảo môi trường làm việc ổn định với internet tốc độ cao và không gian yên tĩnh. - Tham gia đầy đủ các cuộc họp online theo lịch trình. - Báo cáo tiến độ công việc hàng ngày cho team lead. - Đảm bảo availability trong giờ hành chính từ 8:30-17:30.',
    'policy',
    'employee_only',
    'HR',
    'Management Team',
    'approved',
    true
),
(
    'Hướng dẫn sử dụng hệ thống ERP',
    'Hướng dẫn chi tiết sử dụng hệ thống ERP công ty: 1. Đăng nhập hệ thống - Sử dụng tài khoản company email làm username - Mật khẩu được cấp ban đầu cần đổi ngay lần đầu đăng nhập - Kích hoạt 2FA để bảo mật tài khoản 2. Module quản lý nhân sự - Cập nhật thông tin cá nhân trong profile - Đăng ký nghỉ phép qua Leave Management - Xem bảng lương và các khoản phụ cấp - Tải về payslip hàng tháng 3. Module quản lý dự án - Tạo task mới với mô tả chi tiết - Cập nhật tiến độ thực hiện hàng ngày - Báo cáo hàng tuần cho project manager - Export timesheet cuối tháng cho accounting',
    'technical_guide',
    'employee_only',
    'IT',
    'IT Support Team',
    'approved',
    true
),
(
    'Quy định về bảo mật thông tin',
    'Quy định về bảo mật thông tin công ty: 1. Phân loại độ bảo mật - Public: Thông tin công khai - Internal: Chỉ dành cho nhân viên công ty - Confidential: Thông tin nhạy cảm, hạn chế truy cập - Restricted: Thông tin tối mật, cần approval đặc biệt 2. Trách nhiệm nhân viên - Không chia sẻ thông tin công ty ra bên ngoài - Sử dụng VPN khi truy cập từ xa - Khóa máy tính khi rời khỏi chỗ làm việc - Báo cáo ngay các sự cố bảo mật 3. Xử lý vi phạm - Cảnh cáo lần đầu - Kỷ luật lao động cho lần thứ hai - Chấm dứt hợp đồng nếu vi phạm nghiêm trọng',
    'policy',
    'employee_only',
    'IT',
    'Security Team',
    'approved',
    true
),
(
    'Quy trình onboarding nhân viên mới',
    'Quy trình onboarding nhân viên mới gồm 5 giai đoạn: Giai đoạn 1 - Chuẩn bị trước ngày làm việc (1 tuần trước): HR chuẩn bị hồ sơ, tạo tài khoản email và các hệ thống cần thiết, chuẩn bị workspace và thiết bị làm việc. Giai đoạn 2 - Ngày đầu tiên: Đón tiếp và giới thiệu văn hóa công ty, tour văn phòng, gặp gỡ team members, cung cấp employee handbook. Giai đoạn 3 - Tuần đầu tiên: Training về company policies, security guidelines, sử dụng các tools và systems, gặp gỡ stakeholders liên quan. Giai đoạn 4 - Tháng đầu tiên: Giao việc cụ thể với mentor hỗ trợ, feedback sessions định kỳ, đánh giá progress và điều chỉnh nếu cần. Giai đoạn 5 - 3 tháng đầu: Performance review chính thức, feedback 360 degrees, lập kế hoạch phát triển cá nhân, confirm vào vị trí chính thức.',
    'procedure',
    'manager_only',
    'HR',
    'Talent Acquisition Team',
    'approved',
    true
)
ON CONFLICT DO NOTHING;

-- Create sample users
INSERT INTO users (
    username, email, full_name, password_hash, salt, user_level, department, status, is_active, email_verified
) VALUES 
(
    'admin',
    'admin@company.com',
    'System Administrator',
    '$2b$12$encrypted_password_hash_placeholder',
    'salt_placeholder',
    'SYSTEM_ADMIN',
    'IT',
    'ACTIVE',
    true,
    true
),
(
    'demo_user',
    'demo@company.com', 
    'Demo User',
    '$2b$12$encrypted_password_hash_placeholder',
    'salt_placeholder',
    'EMPLOYEE',
    'R&D',
    'ACTIVE',
    true,
    true
),
(
    'hr_manager',
    'hr.manager@company.com',
    'HR Manager',
    '$2b$12$encrypted_password_hash_placeholder', 
    'salt_placeholder',
    'MANAGER',
    'HR',
    'ACTIVE',
    true,
    true
)
ON CONFLICT DO NOTHING;

-- Update search tokens for documents
UPDATE documents_metadata_v2 
SET search_tokens = to_tsvector('simple', title || ' ' || COALESCE(content, ''))
WHERE search_tokens IS NULL;

-- Create sample pipeline sessions for testing
INSERT INTO rag_pipeline_sessions (
    original_query, processed_query, pipeline_type, pipeline_method,
    chunks_retrieved, processing_time_ms, response_quality_score
) VALUES 
(
    'Quy trình xin nghỉ phép như thế nào?',
    'quy trình xin nghỉ phép',
    'standard',
    'hybrid',
    3,
    150,
    0.85
),
(
    'Chính sách làm việc từ xa của công ty',
    'chính sách làm việc từ xa',
    'standard', 
    'hybrid',
    2,
    120,
    0.78
),
(
    'Cách sử dụng hệ thống ERP',
    'hướng dẫn sử dụng ERP',
    'standard',
    'dense',
    4,
    200,
    0.92
)
ON CONFLICT DO NOTHING;

-- Success notification
DO $$ BEGIN
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Enhanced Database Architecture initialized successfully!';
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Features included:';
    RAISE NOTICE '✓ Vietnamese language support with specialized processing';
    RAISE NOTICE '✓ Hybrid search (Vector + BM25) capability';
    RAISE NOTICE '✓ Enhanced document chunking with semantic boundaries';
    RAISE NOTICE '✓ FlashRAG compatibility for advanced RAG pipelines';
    RAISE NOTICE '✓ Comprehensive analytics and monitoring';
    RAISE NOTICE '✓ User management with role-based access control';
    RAISE NOTICE '✓ Performance optimized indexes';
    RAISE NOTICE '✓ Sample Vietnamese documents loaded';
    RAISE NOTICE '';
    RAISE NOTICE 'Database is ready for chatbot deployment!';
    RAISE NOTICE 'Total tables created: 13';
    RAISE NOTICE 'Total indexes created: 25+';
    RAISE NOTICE 'Sample documents: 5 Vietnamese business documents';
    RAISE NOTICE 'Sample users: 3 test accounts';
    RAISE NOTICE '====================================';
END $$;
```

Lưu file này vào `scripts/migrations/01_init_database.sql`. File này đã được tối ưu để:

- Thứ tự tạo tables đúng dependencies
- Loại bỏ duplicate constraints
- Thêm sample data phong phú
- Includes tất cả indexes cần thiết
- Compatible với Docker PostgreSQL
- Có notification để xác nhận setup thành công

Bây giờ bạn có thể chạy `docker-compose up -d` và sẽ có database hoàn chỉnh với enhanced architecture!
