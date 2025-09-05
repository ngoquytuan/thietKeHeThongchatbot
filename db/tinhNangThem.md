✅ Context refinement tracking (LongLLMLingua ready)
✅ Knowledge graph structure (cho advanced RAG)

## 🎯 **CONTEXT REFINEMENT TRACKING (LongLLMLingua Ready)**

### **📋 Bảng: context_refinement_log**

```sql
CREATE TABLE context_refinement_log (
    refinement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_session_id UUID,
    
    -- Original context data
    original_chunks UUID[],                    -- Array IDs của chunks gốc
    original_token_count INTEGER,             -- Số tokens ban đầu
    original_context_length INTEGER,          -- Độ dài context gốc
    
    -- Refined context data  
    refined_content TEXT,                      -- Nội dung đã được refine
    refined_token_count INTEGER,              -- Số tokens sau khi refine
    refined_context_length INTEGER,           -- Độ dài context sau refine
    compression_ratio DECIMAL(5,2),           -- Tỷ lệ nén (0.65 = giảm 35%)
    
    -- Refinement metadata
    refinement_method VARCHAR(50),            -- 'longlmllingua', 'selective_context'
    quality_score DECIMAL(3,2),              -- Điểm chất lượng (0.00-1.00)
    processing_time_ms INTEGER,              -- Thời gian xử lý
    model_used VARCHAR(100),                 -- Model được dùng để refine
    
    -- LongLLMLingua specific parameters
    compression_target DECIMAL(3,2),         -- Target compression ratio
    preserve_first_sentences INTEGER,        -- Số câu đầu được giữ nguyên
    preserve_last_sentences INTEGER,         -- Số câu cuối được giữ nguyên
    dynamic_context_length BOOLEAN,          -- Có dùng dynamic length không
    
    -- Quality tracking cho feedback loop
    user_satisfaction INTEGER CHECK (user_satisfaction BETWEEN 1 AND 5),
    answer_quality INTEGER CHECK (answer_quality BETWEEN 1 AND 5),
    context_relevance INTEGER CHECK (context_relevance BETWEEN 1 AND 5),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **🔍 Sample Data - Context Refinement Examples**

```sql
-- Ví dụ 1: LongLLMLingua compression
INSERT INTO context_refinement_log (
    query_session_id,
    original_chunks,
    original_token_count,
    original_context_length,
    refined_content,
    refined_token_count,
    refined_context_length,
    compression_ratio,
    refinement_method,
    quality_score,
    processing_time_ms,
    model_used,
    compression_target,
    preserve_first_sentences,
    preserve_last_sentences,
    user_satisfaction,
    answer_quality,
    context_relevance
) VALUES (
    'sess_001',
    ARRAY['chunk_001', 'chunk_002', 'chunk_003']::UUID[],
    1200,
    8500,
    'Quy trình xin nghỉ phép: 1. Nhân viên điền đơn 2. Gửi quản lý phê duyệt 3. HR cập nhật hệ thống 4. Thông báo kết quả',
    780,
    5200,
    0.65,  -- Giảm 35% tokens
    'longlmllingua',
    0.88,
    340,
    'longllmlingua-2.0',
    0.65,
    2,
    1,
    4,
    5,
    4
);

-- Ví dụ 2: Selective context filtering
INSERT INTO context_refinement_log (
    query_session_id,
    original_chunks,
    original_token_count,
    refined_content,
    refined_token_count,
    compression_ratio,
    refinement_method,
    quality_score,
    processing_time_ms,
    user_satisfaction,
    answer_quality
) VALUES (
    'sess_002',
    ARRAY['chunk_004', 'chunk_005', 'chunk_006', 'chunk_007']::UUID[],
    1500,
    'Chính sách WFH: Tối đa 3 ngày/tuần, đăng ký trước 1 ngày, đảm bảo môi trường ổn định',
    890,
    0.59,
    'selective_context',
    0.92,
    120,
    5,
    5
);
```

### **📊 Context Refinement Analytics**

```sql
-- Query để phân tích hiệu quả context refinement
SELECT 
    refinement_method,
    COUNT(*) as total_refinements,
    AVG(compression_ratio) as avg_compression,
    AVG(quality_score) as avg_quality,
    AVG(processing_time_ms) as avg_processing_time,
    AVG(user_satisfaction) as avg_user_satisfaction,
    AVG(answer_quality) as avg_answer_quality
FROM context_refinement_log 
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY refinement_method
ORDER BY avg_user_satisfaction DESC;
```

---

## 🕸️ **KNOWLEDGE GRAPH STRUCTURE (Advanced RAG)**

### **📋 Bảng: knowledge_graph_edges**

```sql
CREATE TABLE knowledge_graph_edges (
    edge_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_chunk_id UUID REFERENCES document_chunks_enhanced(chunk_id) ON DELETE CASCADE,
    target_chunk_id UUID REFERENCES document_chunks_enhanced(chunk_id) ON DELETE CASCADE,
    
    -- Relationship metadata
    relationship_type VARCHAR(50) NOT NULL,   -- 'references', 'contradicts', 'supports', 'elaborates', 'defines'
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score BETWEEN 0.00 AND 1.00),
    extraction_method VARCHAR(50) NOT NULL,  -- 'trace', 'manual', 'llm_extracted', 'rule_based'
    
    -- Relationship details
    relationship_description TEXT,            -- Mô tả chi tiết mối quan hệ
    evidence_text TEXT,                      -- Text evidence hỗ trợ relationship
    extraction_context JSONB,               -- Context khi extract relationship
    
    -- Graph traversal optimization
    hop_distance INTEGER DEFAULT 1,          -- Khoảng cách trong graph (1, 2, 3...)
    path_weight DECIMAL(5,3),               -- Trọng số cho path-finding algorithms
    
    -- Quality and validation
    human_verified BOOLEAN DEFAULT false,    -- Đã được human verify chưa
    verification_date TIMESTAMP WITH TIME ZONE,
    verified_by UUID,                       -- User ID của người verify
    
    -- Usage tracking cho optimization
    times_traversed INTEGER DEFAULT 0,      -- Số lần relationship được dùng
    last_traversed TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraint: không cho phép self-loops
    CONSTRAINT no_self_loops CHECK (source_chunk_id != target_chunk_id)
);
```

### **🔍 Sample Data - Knowledge Graph Examples**

```sql
-- Ví dụ 1: Reference relationship
INSERT INTO knowledge_graph_edges (
    source_chunk_id,
    target_chunk_id,
    relationship_type,
    confidence_score,
    extraction_method,
    relationship_description,
    evidence_text,
    extraction_context,
    hop_distance,
    path_weight,
    human_verified,
    times_traversed
) VALUES (
    'chunk_001',  -- Chunk về "quy trình xin nghỉ phép"
    'chunk_015',  -- Chunk về "mẫu đơn xin nghỉ phép"
    'references',
    0.95,
    'llm_extracted',
    'Quy trình xin nghỉ phép tham chiếu đến mẫu đơn cụ thể',
    'Nhân viên cần điền mẫu đơn xin nghỉ phép theo form chuẩn của công ty',
    '{"extraction_model": "gpt-4", "confidence_threshold": 0.9, "context_window": 512}',
    1,
    0.950,
    true,
    25
);

-- Ví dụ 2: Contradicts relationship
INSERT INTO knowledge_graph_edges (
    source_chunk_id,
    target_chunk_id,
    relationship_type,
    confidence_score,
    extraction_method,
    relationship_description,
    evidence_text,
    hop_distance,
    path_weight,
    human_verified
) VALUES (
    'chunk_008',  -- Chunk về "chính sách cũ"
    'chunk_023',  -- Chunk về "chính sách mới"
    'contradicts',
    0.88,
    'rule_based',
    'Chính sách mới thay thế và mâu thuẫn với chính sách cũ',
    'Chính sách mới quy định tối đa 3 ngày WFH/tuần, khác với quy định cũ là 2 ngày',
    1,
    0.880,
    true
);

-- Ví dụ 3: Elaborates relationship
INSERT INTO knowledge_graph_edges (
    source_chunk_id,
    target_chunk_id,
    relationship_type,
    confidence_score,
    extraction_method,
    relationship_description,
    evidence_text,
    hop_distance,
    path_weight
) VALUES (
    'chunk_005',  -- Chunk tổng quan về ERP
    'chunk_012',  -- Chunk chi tiết về module HR
    'elaborates',
    0.92,
    'semantic_similarity',
    'Module HR là phần chi tiết của hệ thống ERP tổng thể',
    'Module quản lý nhân sự bao gồm các chức năng cập nhật thông tin, đăng ký nghỉ phép, xem lương',
    1,
    0.920
);
```

### **📊 Knowledge Graph Analytics**

```sql
-- Query để phân tích knowledge graph structure
SELECT 
    relationship_type,
    COUNT(*) as edge_count,
    AVG(confidence_score) as avg_confidence,
    AVG(times_traversed) as avg_usage,
    COUNT(CASE WHEN human_verified = true THEN 1 END) as verified_count
FROM knowledge_graph_edges 
GROUP BY relationship_type
ORDER BY edge_count DESC;

-- Tìm chunks có nhiều connections nhất (hub nodes)
SELECT 
    c.chunk_id,
    c.chunk_content,
    COUNT(kg.edge_id) as connection_count,
    AVG(kg.confidence_score) as avg_confidence
FROM document_chunks_enhanced c
JOIN knowledge_graph_edges kg ON (c.chunk_id = kg.source_chunk_id OR c.chunk_id = kg.target_chunk_id)
GROUP BY c.chunk_id, c.chunk_content
ORDER BY connection_count DESC
LIMIT 10;
```

### **🔍 Advanced RAG Query với Knowledge Graph**

```sql
-- Function để tìm related chunks thông qua knowledge graph
CREATE OR REPLACE FUNCTION find_related_chunks(
    input_chunk_id UUID,
    max_hops INTEGER DEFAULT 2,
    min_confidence DECIMAL DEFAULT 0.7
)
RETURNS TABLE(
    related_chunk_id UUID,
    relationship_path TEXT[],
    total_confidence DECIMAL,
    hop_count INTEGER
) AS $$
BEGIN
    -- Recursive CTE để traverse knowledge graph
    RETURN QUERY
    WITH RECURSIVE knowledge_path AS (
        -- Base case: direct connections
        SELECT 
            kg.target_chunk_id as chunk_id,
            ARRAY[kg.relationship_type] as path,
            kg.confidence_score as confidence,
            1 as hops
        FROM knowledge_graph_edges kg
        WHERE kg.source_chunk_id = input_chunk_id
        AND kg.confidence_score >= min_confidence
        
        UNION ALL
        
        -- Recursive case: indirect connections
        SELECT 
            kg.target_chunk_id,
            kp.path || kg.relationship_type,
            kp.confidence * kg.confidence_score,
            kp.hops + 1
        FROM knowledge_path kp
        JOIN knowledge_graph_edges kg ON kp.chunk_id = kg.source_chunk_id
        WHERE kp.hops < max_hops
        AND kg.confidence_score >= min_confidence
    )
    SELECT 
        chunk_id,
        path,
        confidence,
        hops
    FROM knowledge_path
    ORDER BY confidence DESC, hops ASC;
END;
$$ LANGUAGE plpgsql;
```

### **🚀 Knowledge Graph Usage trong RAG Pipeline**

```python
# Ví dụ cách sử dụng knowledge graph trong RAG
async def enhanced_retrieval_with_kg(query: str, top_k: int = 5):
    # 1. Vector search để tìm chunks ban đầu
    initial_chunks = await vector_search(query, k=top_k)
    
    # 2. Mở rộng với knowledge graph
    expanded_chunks = []
    for chunk in initial_chunks:
        # Tìm related chunks qua knowledge graph
        related = await find_related_chunks(
            chunk.id, 
            max_hops=2, 
            min_confidence=0.8
        )
        expanded_chunks.extend(related)
    
    # 3. Ranking lại based on vector similarity + graph confidence
    final_chunks = rank_chunks(initial_chunks + expanded_chunks)
    
    return final_chunks
```

---

## 📈 **BENEFITS CỦA 2 FEATURES NÀY**

### **🎯 Context Refinement Tracking:**
- ✅ **Optimize context length** cho LLM calls (giảm cost 30-50%)
- ✅ **Track quality metrics** để improve refinement algorithms
- ✅ **A/B testing** different refinement methods
- ✅ **User feedback loop** để continuous improvement

### **🕸️ Knowledge Graph Structure:**
- ✅ **Advanced RAG** với multi-hop reasoning
- ✅ **Conflict detection** giữa documents
- ✅ **Comprehensive answers** bằng cách traverse relationships
- ✅ **Trace-based refinement** cho high-quality context

### **🚀 Combined Power:**
- **Step 1**: Vector search tìm relevant chunks
- **Step 2**: Knowledge graph expand với related chunks
- **Step 3**: Context refinement compress context optimally
- **Step 4**: LLM generates high-quality answer với minimal tokens

**Result**: Accuracy cao hơn, cost thấp hơn, user experience tốt hơn! 🎉
