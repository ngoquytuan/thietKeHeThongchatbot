-- Enhanced Database Initialization Script v2.0
-- Compatible with PostgreSQL 15+
-- Optimized for Vietnamese chatbot system with hybrid search capabilities
-- Updated for FR03.1 chunking enhancements

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "unaccent";

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

DO $$ BEGIN
    CREATE TYPE chunking_method_enum AS ENUM (
        'fixed_size', 'sentence_based', 'semantic_boundary', 'paragraph_based', 'hybrid'
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

-- Table 3: Enhanced Documents Metadata (FR03.1 compatible)
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

    -- FR03.1 Search preparation fields
    search_text_normalized TEXT,
    indexable_content TEXT,

    -- FR03.1 Extracted information
    extracted_emails TEXT[] DEFAULT '{}',
    extracted_phones TEXT[] DEFAULT '{}',
    extracted_dates DATE[] DEFAULT '{}',

    -- FlashRAG support
    flashrag_collection VARCHAR(100) DEFAULT 'default_collection',
    jsonl_export_ready BOOLEAN DEFAULT false,

    -- Search support
    search_tokens TSVECTOR,
    keyword_density JSONB DEFAULT '{}',
    heading_structure JSONB DEFAULT '{}',

    -- Metadata
    embedding_model_primary VARCHAR(100) DEFAULT 'Qwen/Qwen3-Embedding-0.6B',
    chunk_count INTEGER DEFAULT 0,
    file_size_bytes BIGINT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 4: Enhanced Document Chunks (FR03.1 enhancements)
CREATE TABLE IF NOT EXISTS document_chunks_enhanced (
    chunk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,

    -- Content data
    chunk_content TEXT NOT NULL,
    chunk_position INTEGER NOT NULL,
    chunk_size_tokens INTEGER,

    -- FR03.1 Enhanced semantic chunking metadata
    semantic_boundary BOOLEAN DEFAULT false,
    overlap_with_prev INTEGER DEFAULT 0,
    overlap_with_next INTEGER DEFAULT 0,
    overlap_source_prev INTEGER REFERENCES document_chunks_enhanced(chunk_position),
    overlap_source_next INTEGER REFERENCES document_chunks_enhanced(chunk_position),
    is_final_part BOOLEAN DEFAULT false,
    heading_context TEXT,

    -- FR03.1 Quality and method enhancements
    chunk_method chunking_method_enum DEFAULT 'semantic_boundary',
    chunk_quality_score DECIMAL(3,2) CHECK (chunk_quality_score BETWEEN 0.00 AND 1.00),

    -- Vector storage references
    embedding_model VARCHAR(100) DEFAULT 'Qwen/Qwen3-Embedding-0.6B',
    embedding_dimensions INTEGER DEFAULT 1024,

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

-- Table 7: Enhanced Vietnamese Text Analysis (FR03.1 updates)
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

    -- FR03.1 Quality metrics enhancements
    readability_score DECIMAL(3,2),
    formality_level VARCHAR(20),
    language_quality_score DECIMAL(4,1),
    diacritics_density DECIMAL(4,3),
    token_diversity DECIMAL(4,3),

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

-- NEW Table 14: FR03.3 Data Ingestion Jobs (Support for Pipeline)
CREATE TABLE IF NOT EXISTS data_ingestion_jobs (
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,

    -- Job configuration
    job_name VARCHAR(255) NOT NULL,
    job_type VARCHAR(50) NOT NULL DEFAULT 'document_processing',
    source_path VARCHAR(1000),
    target_collection VARCHAR(100) DEFAULT 'default_collection',

    -- Processing parameters
    chunking_method chunking_method_enum DEFAULT 'semantic_boundary',
    chunk_size_tokens INTEGER DEFAULT 512,
    overlap_tokens INTEGER DEFAULT 50,
    embedding_model VARCHAR(100) DEFAULT 'Qwen/Qwen3-Embedding-0.6B',

    -- Job status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    documents_processed INTEGER DEFAULT 0,
    chunks_created INTEGER DEFAULT 0,

    -- Performance metrics
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_time_seconds DOUBLE PRECISION,
    estimated_completion_time TIMESTAMP WITH TIME ZONE,

    -- Results
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    error_log TEXT[],

    -- Resource usage
    memory_peak_mb DOUBLE PRECISION,
    cpu_time_seconds DOUBLE PRECISION,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- NEW Table 15: FR03.3 Chunk Processing Logs
CREATE TABLE IF NOT EXISTS chunk_processing_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES data_ingestion_jobs(job_id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES document_chunks_enhanced(chunk_id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,

    -- Processing details
    stage VARCHAR(50) NOT NULL, -- 'chunking', 'embedding', 'storage', 'indexing'
    status VARCHAR(20) NOT NULL, -- 'pending', 'processing', 'completed', 'failed'

    -- Performance metrics
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_time_ms INTEGER,

    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    -- Stage-specific data
    stage_metadata JSONB DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create performance indexes
-- Documents indexes (enhanced for FR03.1)
CREATE INDEX IF NOT EXISTS idx_documents_v2_language ON documents_metadata_v2(language_detected);
CREATE INDEX IF NOT EXISTS idx_documents_v2_status ON documents_metadata_v2(status);
CREATE INDEX IF NOT EXISTS idx_documents_v2_collection ON documents_metadata_v2(flashrag_collection);
CREATE INDEX IF NOT EXISTS idx_documents_v2_search ON documents_metadata_v2 USING GIN(search_tokens);
CREATE INDEX IF NOT EXISTS idx_documents_v2_department ON documents_metadata_v2(department_owner);
CREATE INDEX IF NOT EXISTS idx_documents_v2_type ON documents_metadata_v2(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_v2_search_text ON documents_metadata_v2 USING GIN(to_tsvector('vietnamese', search_text_normalized));
CREATE INDEX IF NOT EXISTS idx_documents_v2_extracted_emails ON documents_metadata_v2 USING GIN(extracted_emails);

-- Enhanced Chunks indexes (FR03.1)
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_document ON document_chunks_enhanced(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_position ON document_chunks_enhanced(chunk_position);
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_semantic ON document_chunks_enhanced(semantic_boundary) WHERE semantic_boundary = true;
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_quality ON document_chunks_enhanced(chunk_quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_bm25 ON document_chunks_enhanced USING GIN(bm25_tokens);
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_method ON document_chunks_enhanced(chunk_method);
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_overlap_prev ON document_chunks_enhanced(overlap_source_prev);
CREATE INDEX IF NOT EXISTS idx_chunks_enhanced_overlap_next ON document_chunks_enhanced(overlap_source_next);

-- BM25 indexes
CREATE INDEX IF NOT EXISTS idx_bm25_term ON document_bm25_index(term);
CREATE INDEX IF NOT EXISTS idx_bm25_chunk ON document_bm25_index(chunk_id);
CREATE INDEX IF NOT EXISTS idx_bm25_score ON document_bm25_index(bm25_score DESC);
CREATE INDEX IF NOT EXISTS idx_bm25_language ON document_bm25_index(language);

-- Pipeline indexes
CREATE INDEX IF NOT EXISTS idx_pipeline_sessions_created ON rag_pipeline_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_sessions_type ON rag_pipeline_sessions(pipeline_type, pipeline_method);
CREATE INDEX IF NOT EXISTS idx_pipeline_sessions_quality ON rag_pipeline_sessions(response_quality_score DESC);

-- FR03.3 Data Ingestion indexes
CREATE INDEX IF NOT EXISTS idx_data_ingestion_jobs_status ON data_ingestion_jobs(status);
CREATE INDEX IF NOT EXISTS idx_data_ingestion_jobs_user_created ON data_ingestion_jobs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_data_ingestion_jobs_type_status ON data_ingestion_jobs(job_type, status);
CREATE INDEX IF NOT EXISTS idx_chunk_processing_logs_job ON chunk_processing_logs(job_id, stage);
CREATE INDEX IF NOT EXISTS idx_chunk_processing_logs_status ON chunk_processing_logs(status, stage);

-- Enhanced Vietnamese analysis indexes
CREATE INDEX IF NOT EXISTS idx_vietnamese_analysis_quality ON vietnamese_text_analysis(language_quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_vietnamese_analysis_diacritics ON vietnamese_text_analysis(diacritics_density DESC);

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

-- Insert sample Vietnamese documents (updated for FR03.1)
INSERT INTO documents_metadata_v2 (
    title, content, document_type, access_level, department_owner, author, status, 
    jsonl_export_ready, search_text_normalized, indexable_content,
    extracted_emails, extracted_phones
) VALUES 
(
    'Quy trình xin nghỉ phép',
    'Quy trình xin nghỉ phép tại công ty bao gồm các bước sau: 1. Nhân viên điền đơn xin nghỉ phép qua hệ thống HR. 2. Gửi đơn cho quản lý trực tiếp để phê duyệt. 3. Quản lý phê duyệt trong vòng 2 ngày làm việc. 4. HR cập nhật vào hệ thống và thông báo cho nhân viên. 5. Nhân viên nhận thông báo kết quả và lập kế hoạch nghỉ phép.',
    'procedure',
    'employee_only',
    'HR',
    'HR Department',
    'approved',
    true,
    'quy trinh xin nghi phep nhan vien hr he thong phe duyet quan ly',
    'Quy trình xin nghỉ phép tại công ty nhân viên HR hệ thống phê duyệt quản lý',
    '{"hr@company.com"}',
    '{"0123456789"}'
),
(
    'Chính sách làm việc từ xa',
    'Chính sách làm việc từ xa (Work From Home - WFH) được áp dụng như sau: - Nhân viên có thể làm việc từ xa tối đa 3 ngày/tuần, tùy thuộc vào tính chất công việc. - Cần đăng ký trước ít nhất 1 ngày thông qua hệ thống internal. - Đảm bảo môi trường làm việc ổn định với internet tốc độ cao và không gian yên tĩnh. - Tham gia đầy đủ các cuộc họp online theo lịch trình. - Báo cáo tiến độ công việc hàng ngày cho team lead. - Đảm bảo availability trong giờ hành chính từ 8:30-17:30.',
    'policy',
    'employee_only',
    'HR',
    'Management Team',
    'approved',
    true,
    'chinh sach lam viec tu xa work from home wfh nhan vien dang ky he thong',
    'Chính sách làm việc từ xa WFH nhân viên đăng ký hệ thống internet meeting',
    '{}',
    '{}'
),
(
    'Hướng dẫn sử dụng hệ thống ERP',
    'Hướng dẫn chi tiết sử dụng hệ thống ERP công ty: 1. Đăng nhập hệ thống - Sử dụng tài khoản company email làm username - Mật khẩu được cấp ban đầu cần đổi ngay lần đầu đăng nhập - Kích hoạt 2FA để bảo mật tài khoản 2. Module quản lý nhân sự - Cập nhật thông tin cá nhân trong profile - Đăng ký nghỉ phép qua Leave Management - Xem bảng lương và các khoản phụ cấp - Tải về payslip hàng tháng 3. Module quản lý dự án - Tạo task mới với mô tả chi tiết - Cập nhật tiến độ thực hiện hàng ngày - Báo cáo hàng tuần cho project manager - Export timesheet cuối tháng cho accounting',
    'technical_guide',
    'employee_only',
    'IT',
    'IT Support Team',
    'approved',
    true,
    'huong dan su dung he thong erp dang nhap tai khoan email mat khau 2fa module nhan su du an',
    'Hướng dẫn sử dụng hệ thống ERP đăng nhập tài khoản email mật khẩu 2FA module nhân sự dự án',
    '{"support@company.com", "it.help@company.com"}',
    '{"0987654321"}'
),
(
    'Quy định về bảo mật thông tin',
    'Quy định về bảo mật thông tin công ty: 1. Phân loại độ bảo mật - Public: Thông tin công khai - Internal: Chỉ dành cho nhân viên công ty - Confidential: Thông tin nhạy cảm, hạn chế truy cập - Restricted: Thông tin tối mật, cần approval đặc biệt 2. Trách nhiệm nhân viên - Không chia sẻ thông tin công ty ra bên ngoài - Sử dụng VPN khi truy cập từ xa - Khóa máy tính khi rời khỏi chỗ làm việc - Báo cáo ngay các sự cố bảo mật 3. Xử lý vi phạm - Cảnh cáo lần đầu - Kỷ luật lao động cho lần thứ hai - Chấm dứt hợp đồng nếu vi phạm nghiêm trọng',
    'policy',
    'employee_only',
    'IT',
    'Security Team',
    'approved',
    true,
    'quy dinh bao mat thong tin cong ty phan loai nhan vien vpn vi pham',
    'Quy định bảo mật thông tin công ty phân loại nhân viên VPN vi phạm security',
    '{"security@company.com"}',
    '{"0912345678"}'
),
(
    'Quy trình onboarding nhân viên mới',
    'Quy trình onboarding nhân viên mới gồm 5 giai đoạn: Giai đoạn 1 - Chuẩn bị trước ngày làm việc (1 tuần trước): HR chuẩn bị hồ sơ, tạo tài khoản email và các hệ thống cần thiết, chuẩn bị workspace và thiết bị làm việc. Giai đoạn 2 - Ngày đầu tiên: Đón tiếp và giới thiệu văn hóa công ty, tour văn phòng, gặp gỡ team members, cung cấp employee handbook. Giai đoạn 3 - Tuần đầu tiên: Training về company policies, security guidelines, sử dụng các tools và systems, gặp gỡ stakeholders liên quan. Giai đoạn 4 - Tháng đầu tiên: Giao việc cụ thể với mentor hỗ trợ, feedback sessions định kỳ, đánh giá progress và điều chỉnh nếu cần. Giai đoạn 5 - 3 tháng đầu: Performance review chính thức, feedback 360 degrees, lập kế hoạch phát triển cá nhân, confirm vào vị trí chính thức.',
    'procedure',
    'manager_only',
    'HR',
    'Talent Acquisition Team',
    'approved',
    true,
    'quy trinh onboarding nhan vien moi hr tai khoan email workspace training feedback review',
    'quy trinh onboarding nhan vien moi hr tai khoan email workspace training feedback review',
    'Quy trình onboarding nhân viên mới HR tài khoản email workspace training feedback review',
    '{"hr.onboarding@company.com", "talent@company.com"}',
    '{"0901234567"}'
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
),
(
    'data_engineer',
    'data.engineer@company.com',
    'Data Pipeline Engineer',
    '$2b$12$encrypted_password_hash_placeholder',
    'salt_placeholder',
    'EMPLOYEE',
    'IT',
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

-- Create sample data ingestion jobs for FR03.3 testing
INSERT INTO data_ingestion_jobs (
    job_name, job_type, source_path, target_collection, chunking_method,
    chunk_size_tokens, overlap_tokens, status, progress_percentage,
    documents_processed, chunks_created, success_count
) VALUES 
(
    'Initial HR Documents Upload',
    'document_processing',
    '/data/upload/hr_documents/',
    'hr_knowledge_base',
    'semantic_boundary',
    512,
    50,
    'completed',
    100.00,
    5,
    47,
    5
),
(
    'Technical Documentation Batch',
    'document_processing',
    '/data/upload/tech_docs/',
    'technical_knowledge_base',
    'hybrid',
    768,
    75,
    'processing',
    65.50,
    8,
    123,
    7
),
(
    'Policy Updates Q1 2025',
    'document_processing',
    '/data/upload/policies_q1/',
    'policy_knowledge_base',
    'paragraph_based',
    400,
    40,
    'pending',
    0.00,
    0,
    0,
    0
)
ON CONFLICT DO NOTHING;

-- Create sample Vietnamese text analysis records
INSERT INTO vietnamese_text_analysis (
    document_id, original_text, processed_text, 
    readability_score, formality_level, language_quality_score,
    diacritics_density, token_diversity
) VALUES 
(
    (SELECT document_id FROM documents_metadata_v2 WHERE title = 'Quy trình xin nghỉ phép' LIMIT 1),
    'Quy trình xin nghỉ phép tại công ty bao gồm các bước sau',
    'quy trình xin nghỉ phép tại công ty bao gồm các bước sau',
    0.85,
    'formal',
    8.5,
    0.654,
    0.789
),
(
    (SELECT document_id FROM documents_metadata_v2 WHERE title = 'Chính sách làm việc từ xa' LIMIT 1),
    'Chính sách làm việc từ xa (Work From Home - WFH)',
    'chính sách làm việc từ xa work from home wfh',
    0.78,
    'semi_formal',
    7.8,
    0.612,
    0.834
)
ON CONFLICT DO NOTHING;

-- Create functions for Vietnamese text processing support
CREATE OR REPLACE FUNCTION normalize_vietnamese_text(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Basic Vietnamese text normalization
    RETURN lower(
        regexp_replace(
            regexp_replace(input_text, '[àáạảãâầấậẩẫăằắặẳẵ]', 'a', 'gi'),
            '[èéẹẻẽêềếệểễ]', 'e', 'gi'
        )
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create function to extract contact information
CREATE OR REPLACE FUNCTION extract_emails_from_text(input_text TEXT)
RETURNS TEXT[] AS $$
DECLARE
    email_pattern TEXT := '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}';
    result TEXT[];
BEGIN
    SELECT array_agg(DISTINCT match)
    INTO result
    FROM regexp_matches(input_text, email_pattern, 'gi') AS match;

    RETURN COALESCE(result, '{}');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create function to extract phone numbers
CREATE OR REPLACE FUNCTION extract_phones_from_text(input_text TEXT)
RETURNS TEXT[] AS $$
DECLARE
    phone_pattern TEXT := '(\+84|0)[0-9]{8,10}';
    result TEXT[];
BEGIN
    SELECT array_agg(DISTINCT match)
    INTO result
    FROM regexp_matches(input_text, phone_pattern, 'gi') AS match;

    RETURN COALESCE(result, '{}');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Update existing documents with extracted information
UPDATE documents_metadata_v2 
SET 
    search_text_normalized = normalize_vietnamese_text(COALESCE(content, title)),
    indexable_content = title || ' ' || COALESCE(content, ''),
    extracted_emails = extract_emails_from_text(COALESCE(content, '')),
    extracted_phones = extract_phones_from_text(COALESCE(content, ''))
WHERE search_text_normalized IS NULL OR extracted_emails IS NULL;

-- Create triggers for automatic updates
CREATE OR REPLACE FUNCTION update_document_search_fields()
RETURNS TRIGGER AS $$
BEGIN
    -- Auto-update search fields when document content changes
    NEW.search_text_normalized := normalize_vietnamese_text(COALESCE(NEW.content, NEW.title));
    NEW.indexable_content := NEW.title || ' ' || COALESCE(NEW.content, '');
    NEW.extracted_emails := extract_emails_from_text(COALESCE(NEW.content, ''));
    NEW.extracted_phones := extract_phones_from_text(COALESCE(NEW.content, ''));
    NEW.updated_at := NOW();
    NEW.search_tokens := to_tsvector('simple', NEW.title || ' ' || COALESCE(NEW.content, ''));

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_document_search_fields
    BEFORE INSERT OR UPDATE ON documents_metadata_v2
    FOR EACH ROW
    EXECUTE FUNCTION update_document_search_fields();

-- Create trigger for automatic chunk BM25 token updates
CREATE OR REPLACE FUNCTION update_chunk_bm25_tokens()
RETURNS TRIGGER AS $$
BEGIN
    NEW.bm25_tokens := to_tsvector('simple', NEW.chunk_content);
    NEW.updated_at := NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_chunk_bm25_tokens
    BEFORE INSERT OR UPDATE ON document_chunks_enhanced
    FOR EACH ROW
    EXECUTE FUNCTION update_chunk_bm25_tokens();

-- Create performance monitoring views
CREATE OR REPLACE VIEW vw_document_processing_stats AS
SELECT 
    d.document_type,
    d.department_owner,
    COUNT(*) as total_documents,
    AVG(d.chunk_count) as avg_chunks_per_doc,
    SUM(d.chunk_count) as total_chunks,
    AVG(EXTRACT(EPOCH FROM d.updated_at - d.created_at)) as avg_processing_time_seconds,
    COUNT(CASE WHEN d.status = 'approved' THEN 1 END) as approved_count,
    COUNT(CASE WHEN d.jsonl_export_ready THEN 1 END) as export_ready_count
FROM documents_metadata_v2 d
GROUP BY d.document_type, d.department_owner;

CREATE OR REPLACE VIEW vw_chunking_performance AS
SELECT 
    c.chunk_method,
    c.embedding_model,
    COUNT(*) as total_chunks,
    AVG(c.chunk_size_tokens) as avg_chunk_size,
    AVG(c.chunk_quality_score) as avg_quality_score,
    COUNT(CASE WHEN c.semantic_boundary THEN 1 END) as semantic_boundary_count,
    AVG(c.overlap_with_prev + c.overlap_with_next) as avg_overlap_total
FROM document_chunks_enhanced c
WHERE c.chunk_quality_score IS NOT NULL
GROUP BY c.chunk_method, c.embedding_model;

CREATE OR REPLACE VIEW vw_ingestion_job_summary AS
SELECT 
    dij.job_type,
    dij.chunking_method,
    dij.status,
    COUNT(*) as job_count,
    AVG(dij.progress_percentage) as avg_progress,
    AVG(dij.processing_time_seconds) as avg_processing_time,
    SUM(dij.documents_processed) as total_docs_processed,
    SUM(dij.chunks_created) as total_chunks_created,
    AVG(dij.success_count::DECIMAL / NULLIF(dij.documents_processed, 0) * 100) as success_rate_percentage
FROM data_ingestion_jobs dij
GROUP BY dij.job_type, dij.chunking_method, dij.status;

-- Success notification
DO $$ BEGIN
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Enhanced Database Architecture v2.0 initialized successfully!';
    RAISE NOTICE '====================================';
    RAISE NOTICE 'NEW FR03.1 Features included:';
    RAISE NOTICE '✓ Enhanced chunking support with overlap tracking';
    RAISE NOTICE '✓ Advanced Vietnamese text analysis with quality metrics';
    RAISE NOTICE '✓ Automatic contact information extraction';
    RAISE NOTICE '✓ Search text normalization and indexable content fields';
    RAISE NOTICE '✓ FR03.3 Data ingestion pipeline support tables';
    RAISE NOTICE '✓ Chunk processing logs and job tracking';
    RAISE NOTICE '✓ Performance monitoring views';
    RAISE NOTICE '✓ Automatic trigger functions for search optimization';
    RAISE NOTICE '';
    RAISE NOTICE 'EXISTING Features enhanced:';
    RAISE NOTICE '✓ Vietnamese language support with specialized processing';
    RAISE NOTICE '✓ Hybrid search (Vector + BM25) capability';
    RAISE NOTICE '✓ Enhanced document chunking with semantic boundaries';
    RAISE NOTICE '✓ FlashRAG compatibility for advanced RAG pipelines';
    RAISE NOTICE '✓ Comprehensive analytics and monitoring';
    RAISE NOTICE '✓ User management with role-based access control';
    RAISE NOTICE '✓ Performance optimized indexes';
    RAISE NOTICE '✓ Sample Vietnamese documents loaded';
    RAISE NOTICE '';
    RAISE NOTICE 'Database is ready for enhanced chatbot deployment!';
    RAISE NOTICE 'Total tables created: 15 (2 new tables added)';
    RAISE NOTICE 'Total indexes created: 30+';
    RAISE NOTICE 'Total views created: 3 performance monitoring views';
    RAISE NOTICE 'Total functions created: 4 utility functions';
    RAISE NOTICE 'Total triggers created: 2 automatic update triggers';
    RAISE NOTICE 'Sample documents: 5 Vietnamese business documents';
    RAISE NOTICE 'Sample users: 4 test accounts';
    RAISE NOTICE 'Sample jobs: 3 data ingestion test jobs';
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Ready for FR03.3 Data Ingestion Pipeline integration!';
END $$;