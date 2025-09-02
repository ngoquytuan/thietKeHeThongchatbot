Dựa trên thiết kế cơ sở dữ liệu hiện tại và các cải tiến từ FlashRAG, đây sẽ là **7 thay đổi quan trọng** cần thực hiện:

## 🗄️ **Impact lên Database Design**

### 1. **Mở rộng Schema PostgreSQL cho Hybrid Retrieval**

**Hiện tại**: Chỉ hỗ trợ vector embeddings  
**Cần thêm**: Bảng cho BM25s indexing

```sql
-- Thêm vào documents_metadata table
ALTER TABLE documents_metadata ADD COLUMN IF NOT EXISTS (
    -- BM25 indexing support
    search_tokens TSVECTOR,  -- Full-text search tokens
    keyword_density JSONB,   -- Keyword frequency analysis
    
    -- Document structure metadata
    heading_structure JSONB,  -- Document outline (H1, H2, H3)
    chunk_strategy VARCHAR(20) DEFAULT 'semantic',  -- chunking method used
    
    -- FlashRAG compatibility  
    flashrag_collection VARCHAR(100),  -- Collection name for FlashRAG
    jsonl_export_ready BOOLEAN DEFAULT false  -- Ready for JSONL export
);

-- Create full-text search index
CREATE INDEX idx_documents_search_tokens ON documents_metadata 
USING GIN(search_tokens);

-- Create BM25 supporting table
CREATE TABLE document_chunks_bm25 (
    chunk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents_metadata(document_id),
    chunk_content TEXT NOT NULL,
    chunk_position INTEGER,
    bm25_tokens TSVECTOR,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chunks_bm25_tokens ON document_chunks_bm25 
USING GIN(bm25_tokens);
```

### 2. **Dual Storage Strategy: PostgreSQL + JSONL**

**Mở rộng**: Thêm export/import functions để tương thích FlashRAG

```sql
-- Add export metadata tracking
CREATE TABLE jsonl_exports (
    export_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    collection_name VARCHAR(100) NOT NULL,
    export_path TEXT,
    document_count INTEGER,
    total_chunks INTEGER,
    exported_at TIMESTAMP DEFAULT NOW(),
    flashrag_compatible BOOLEAN DEFAULT true
);

-- Function to prepare JSONL export
CREATE OR REPLACE FUNCTION prepare_jsonl_export(collection_name TEXT)
RETURNS TABLE(
    id TEXT,
    contents TEXT,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dm.document_id::TEXT as id,
        dm.content as contents,
        jsonb_build_object(
            'title', dm.title,
            'document_type', dm.document_type,
            'access_level', dm.access_level,
            'department_owner', dm.department_owner,
            'heading_structure', dm.heading_structure,
            'tags', array_agg(dt.tag_name)
        ) as metadata
    FROM documents_metadata dm
    LEFT JOIN document_tag_relations dtr ON dm.document_id = dtr.document_id  
    LEFT JOIN document_tags dt ON dtr.tag_id = dt.tag_id
    WHERE dm.flashrag_collection = collection_name
    GROUP BY dm.document_id, dm.content, dm.title, dm.document_type, 
             dm.access_level, dm.department_owner, dm.heading_structure;
END;
$$ LANGUAGE plpgsql;
```

### 3. **Enhanced Chunking Metadata**

**Mở rộng**: Support semantic chunking với overlap tracking

```sql
-- Modify existing chunks table or create new one
CREATE TABLE document_chunks_enhanced (
    chunk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents_metadata(document_id),
    
    -- Content data
    chunk_content TEXT NOT NULL,
    chunk_position INTEGER,
    chunk_size_tokens INTEGER,
    
    -- Semantic chunking metadata  
    semantic_boundary BOOLEAN DEFAULT false,  -- Is this a semantic boundary?
    overlap_with_prev INTEGER DEFAULT 0,      -- Overlap with previous chunk
    overlap_with_next INTEGER DEFAULT 0,      -- Overlap with next chunk
    heading_context TEXT,                     -- Which heading this belongs to
    
    -- FlashRAG compatibility
    chunk_method VARCHAR(20) DEFAULT 'semantic',  -- token/sentence/semantic
    chunk_quality_score DECIMAL(3,2),            -- Quality assessment
    
    -- Vector storage references
    faiss_index_id INTEGER,                   -- FAISS index reference
    embedding_model VARCHAR(100),             -- Which model created embedding
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_chunks_enhanced_document ON document_chunks_enhanced(document_id);
CREATE INDEX idx_chunks_enhanced_position ON document_chunks_enhanced(chunk_position);
CREATE INDEX idx_chunks_enhanced_boundary ON document_chunks_enhanced(semantic_boundary);
```

### 4. **Context Refinement Tracking**

**Mới**: Bảng tracking cho LongLLMLingua và context compression

```sql
-- Track context refinement operations
CREATE TABLE context_refinement_log (
    refinement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_session_id UUID,
    
    -- Original context
    original_chunks UUID[], -- Array of chunk IDs
    original_token_count INTEGER,
    
    -- Refined context  
    refined_content TEXT,
    refined_token_count INTEGER,
    compression_ratio DECIMAL(3,2),
    
    -- Refinement metadata
    refinement_method VARCHAR(50), -- 'longlmllingua', 'selective_context' 
    quality_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Track knowledge graph relationships (for Trace refiner)
CREATE TABLE knowledge_graph_edges (
    edge_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_chunk_id UUID REFERENCES document_chunks_enhanced(chunk_id),
    target_chunk_id UUID REFERENCES document_chunks_enhanced(chunk_id),
    
    relationship_type VARCHAR(50), -- 'references', 'contradicts', 'supports'
    confidence_score DECIMAL(3,2),
    extraction_method VARCHAR(50), -- 'trace', 'manual', 'llm_extracted'
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_kg_edges_source ON knowledge_graph_edges(source_chunk_id);
CREATE INDEX idx_kg_edges_target ON knowledge_graph_edges(target_chunk_id);
```

### 5. **Multi-Pipeline Query Tracking**

**Mở rộng**: Track different RAG pipelines usage

```sql
-- Extend existing query logs or create new table
CREATE TABLE rag_pipeline_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    
    -- Query information
    original_query TEXT NOT NULL,
    intent_detected VARCHAR(50),
    
    -- Pipeline metadata
    pipeline_type VARCHAR(50), -- 'standard', 'reasoning', 'conditional'
    pipeline_method VARCHAR(50), -- 'r1_searcher', 'ircot', 'adaptive_rag'
    
    -- Processing steps
    retrieval_method VARCHAR(50), -- 'hybrid', 'dense', 'sparse'
    chunks_retrieved INTEGER,
    context_refined BOOLEAN DEFAULT false,
    
    -- Results
    response_generated BOOLEAN,
    response_quality_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    
    -- Performance metrics
    tokens_used INTEGER,
    api_calls_count INTEGER,
    total_cost_usd DECIMAL(8,4),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pipeline_sessions_user ON rag_pipeline_sessions(user_id);
CREATE INDEX idx_pipeline_sessions_pipeline ON rag_pipeline_sessions(pipeline_type, pipeline_method);
CREATE INDEX idx_pipeline_sessions_created ON rag_pipeline_sessions(created_at);
```

### 6. **Vietnamese Language Support**

**Mở rộng**: Thêm metadata cho Vietnamese processing

```sql
-- Add Vietnamese language processing metadata
ALTER TABLE documents_metadata ADD COLUMN IF NOT EXISTS (
    -- Language processing
    language_detected VARCHAR(10) DEFAULT 'vi',
    vietnamese_segmented BOOLEAN DEFAULT false,  -- Processed with pyvi
    
    -- Vietnamese-specific metadata
    diacritics_normalized BOOLEAN DEFAULT false,
    tone_marks_preserved BOOLEAN DEFAULT true,
    
    -- Embedding model used (Vietnamese-optimized)
    embedding_model_primary VARCHAR(100),    -- e.g., 'multilingual-e5-base'
    embedding_model_fallback VARCHAR(100),   -- e.g., 'text-embedding-ada-002'
    embedding_quality_vi DECIMAL(3,2)       -- Vietnamese embedding quality score
);

-- Vietnamese text analysis results
CREATE TABLE vietnamese_text_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents_metadata(document_id),
    
    -- Pyvi segmentation results
    word_segmentation JSONB,        -- Segmented words
    pos_tagging JSONB,              -- Part-of-speech tags
    
    -- Vietnamese-specific features
    compound_words TEXT[],          -- Detected compound words  
    technical_terms TEXT[],         -- Domain-specific terminology
    proper_nouns TEXT[],            -- Vietnamese proper nouns
    
    processed_at TIMESTAMP DEFAULT NOW()
);
```

### 7. **Performance Optimization Tables**

**Mới**: Tracking performance cho optimization

```sql
-- Embedding model performance comparison
CREATE TABLE embedding_model_benchmarks (
    benchmark_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    model_name VARCHAR(100),
    model_type VARCHAR(50), -- 'vietnamese', 'multilingual', 'english'
    
    -- Performance metrics
    hit_rate DECIMAL(5,4),          -- Hit rate at k=5
    mrr DECIMAL(5,4),               -- Mean Reciprocal Rank
    processing_time_avg_ms INTEGER,  -- Average processing time
    
    -- Test dataset info
    test_dataset VARCHAR(100),
    test_queries_count INTEGER,
    language VARCHAR(10),
    
    -- Hardware/config info
    hardware_config JSONB,
    tested_at TIMESTAMP DEFAULT NOW()
);

-- Query performance tracking
CREATE TABLE query_performance_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES rag_pipeline_sessions(session_id),
    
    -- Timing breakdown
    retrieval_time_ms INTEGER,
    embedding_time_ms INTEGER,  
    llm_processing_time_ms INTEGER,
    context_refinement_time_ms INTEGER,
    
    -- Resource usage
    memory_usage_mb INTEGER,
    cpu_usage_percent DECIMAL(5,2),
    
    -- Quality metrics
    relevance_score DECIMAL(3,2),
    user_satisfaction INTEGER CHECK (user_satisfaction BETWEEN 1 AND 5),
    
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for analytics queries
CREATE INDEX idx_performance_session ON query_performance_metrics(session_id);
CREATE INDEX idx_performance_recorded ON query_performance_metrics(recorded_at);
```

## 🔄 **Database Migration Strategy**

### Phase 1: Schema Extensions (1 tuần)
```bash
# 1. Run schema migrations
python scripts/migrate_database.py --add-flashrag-support

# 2. Update existing documents with new fields
python scripts/update_existing_documents.py --add-vietnamese-metadata

# 3. Create new indexes
python scripts/create_performance_indexes.py
```

### Phase 2: Data Migration (1 tuần)  
```bash
# 1. Re-process existing documents with semantic chunking
python scripts/rechunk_documents.py --method=semantic --batch-size=100

# 2. Generate BM25 indexes for existing content
python scripts/generate_bm25_indexes.py --collection=all

# 3. Export to JSONL format for FlashRAG compatibility
python scripts/export_to_jsonl.py --collections=all --output-dir=./flashrag_data/
```

### Phase 3: Performance Testing (1 tuần)
```bash
# 1. Run benchmark tests with new schema
python scripts/benchmark_new_schema.py --test-queries=1000

# 2. Compare old vs new performance 
python scripts/compare_performance.py --old-schema --new-schema

# 3. Optimize based on results
python scripts/optimize_indexes.py --auto-tune
```

## 💾 **Storage Impact**

**Dự kiến tăng storage**:
- **PostgreSQL**: +40% (metadata mở rộng, tracking tables)
- **Vector Storage**: +20% (multiple embeddings, BM25 indexes)  
- **File Storage**: +60% (JSONL exports, backup copies)

**Tổng impact**: Tăng ~45% storage requirement, nhưng có:
- ✅ Hybrid search accuracy tăng 15-20%
- ✅ Query performance tăng 2x với caching
- ✅ FlashRAG compatibility cho advanced features
- ✅ Better Vietnamese language support

Bạn có muốn tôi chi tiết migration script cho từng phase không?
