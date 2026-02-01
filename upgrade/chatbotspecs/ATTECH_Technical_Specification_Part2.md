## 4. YÊU CẦU AI/ML VÀ KIẾN TRÚC RAG

### 4.1. Tổng quan về Retrieval-Augmented Generation (RAG)

**Định nghĩa:**
RAG (Retrieval-Augmented Generation) là kỹ thuật kết hợp tìm kiếm thông tin (Information Retrieval) với mô hình ngôn ngữ lớn (Large Language Model) để sinh ra câu trả lời chính xác, có nguồn gốc, và giảm thiểu hallucination.

**Lý do Chọn RAG thay vì Fine-tuning:**
1. **Cập nhật Dữ liệu Dễ dàng:** Thêm documents mới không cần retrain model
2. **Tính Minh bạch:** Có thể truy vết nguồn gốc câu trả lời (citations)
3. **Chi phí Thấp hơn:** Không cần GPU clusters để fine-tune LLMs
4. **Linh hoạt:** Có thể switch LLM providers dễ dàng
5. **Kiểm soát Chất lượng:** Quality control tại retrieval stage

### 4.2. RAG Pipeline Architecture

Hệ thống RAG của ATTECH sử dụng **Hybrid Approach** kết hợp 3 phương pháp retrieval:

```mermaid
graph LR
    subgraph "INPUT LAYER"
        Query[👤 User Query]
    end
    
    subgraph "QUERY PROCESSING"
        QueryAnalysis[🔍 Query Analysis<br/>- Intent classification<br/>- Entity extraction<br/>- Legal code detection]
        QueryExpansion[📝 Query Expansion<br/>- Synonym dictionary<br/>- Legal abbreviations<br/>- Vietnamese variants]
    end
    
    subgraph "RETRIEVAL ENGINES - Parallel Execution"
        VectorSearch[🔢 Vector Similarity<br/>ChromaDB<br/>Qwen Embeddings<br/>Top 20 results]
        BM25Search[📄 BM25 Full-Text<br/>PostgreSQL<br/>Legal code preserved<br/>Top 20 results]
        GraphSearch[🕸️ Graph Traversal<br/>Document relationships<br/>Multi-hop reasoning<br/>Phase 2]
    end
    
    subgraph "RANKING & FUSION"
        HybridRanking[⚖️ Hybrid Ranking<br/>0.7*semantic + 0.3*keyword<br/>Diversity boost<br/>Top 10 final]
        Reranking[🎯 Reranking<br/>Cross-encoder optional<br/>Intent-based boost<br/>Top 5-8 final]
    end
    
    subgraph "SYNTHESIS & GENERATION"
        ContextAssembly[📋 Context Assembly<br/>Chunk selection<br/>Prompt construction<br/>Token management]
        LLMGeneration[🤖 LLM Generation<br/>Multi-provider<br/>Citation injection<br/>Grounding check]
    end
    
    subgraph "OUTPUT LAYER"
        Response[💬 Final Response<br/>Answer + Citations<br/>+ Related docs]
    end
    
    Query --> QueryAnalysis
    QueryAnalysis --> QueryExpansion
    QueryExpansion --> VectorSearch
    QueryExpansion --> BM25Search
    QueryExpansion --> GraphSearch
    
    VectorSearch --> HybridRanking
    BM25Search --> HybridRanking
    GraphSearch --> HybridRanking
    
    HybridRanking --> Reranking
    Reranking --> ContextAssembly
    ContextAssembly --> LLMGeneration
    LLMGeneration --> Response
```

### 4.3. Embedding Model Specification

#### 4.3.1. Selected Model

**Model:** Qwen/Qwen3-Embedding-0.6B  
**Version:** 0.6B parameters  
**Embedding Dimension:** 1024  
**Language Optimization:** Vietnamese  

**Lý do Chọn (từ FR-01.1 Testing):**
- ✅ Hiệu suất tốt nhất cho Vietnamese legal documents (tested extensively)
- ✅ 1024-dimensional embeddings: balance giữa accuracy và speed
- ✅ Hỗ trợ Unicode tốt (NFC/NFD normalization)
- ✅ Open-source, có thể self-host
- ✅ Inference speed: ~0.1s per query trên GPU

**Hardware Requirements:**
- **GPU:** NVIDIA RTX 3060 12GB hoặc tương đương
- **CUDA:** Version 11.8
- **VRAM:** Minimum 8GB, recommended 12GB
- **Batch Size:** 8-16 documents/batch (optimal for consumer GPU)

#### 4.3.2. Embedding Generation Process

```python
# Pseudocode for embedding generation
def generate_embedding(text: str) -> List[float]:
    """
    Generate 1024-dimensional embedding for Vietnamese text.
    """
    # 1. Preprocess text
    text = unicode_normalize(text, form="NFC")
    text = remove_excessive_whitespace(text)
    
    # 2. Tokenize (Qwen tokenizer)
    tokens = tokenizer.encode(text, max_length=512, truncation=True)
    
    # 3. Generate embedding
    with torch.no_grad():
        embedding = model.encode(tokens)  # Shape: (1024,)
    
    # 4. Normalize (for cosine similarity)
    embedding = embedding / np.linalg.norm(embedding)
    
    return embedding.tolist()
```

**Performance Metrics (từ actual testing):**
- **Throughput:** ~100 embeddings/second trên RTX 3060
- **Latency:** ~10ms per embedding (single)
- **Batch Processing:** ~0.5s for 50 embeddings
- **GPU Memory:** ~3GB VRAM utilized

### 4.4. Search Strategy Chi tiết

#### 4.4.1. Stage 1: Vector Similarity Search (ChromaDB)

**Mục đích:** Tìm các document chunks có semantic similarity cao với query.

**Process:**
```
1. Generate query embedding (1024-dim)
2. ChromaDB.query(
     collection="knowledge_base_v1",
     query_embedding=query_embedding,
     n_results=20,
     where={
         "access_level": user_accessible_levels,  // Permission filter
         "department_owner": user_departments      // Department filter
     }
   )
3. Return top 20 chunks với cosine similarity scores
```

**Scoring:**
- **Metric:** Cosine similarity
- **Threshold:** > 0.5 (lower = less relevant)
- **Weighting:** 0.7 trong hybrid ranking (70%)

**Optimization:**
- **Index Type:** HNSW (Hierarchical Navigable Small World)
- **Index Parameters:** 
  - ef_construction=200
  - M=16
- **Max Elements:** 500,000 chunks capacity

#### 4.4.2. Stage 2: BM25 Full-Text Search (PostgreSQL)

**Mục đích:** Tìm exact matches và keyword-based relevance, đặc biệt cho legal codes.

**Process:**
```sql
-- BM25 search với legal code preservation
SELECT 
    chunk_id,
    document_id,
    content,
    metadata,
    ts_rank_cd(
        to_tsvector('vietnamese', content_normalized),
        to_tsquery('vietnamese', query_normalized),
        32  -- Cover density ranking
    ) * bm25_score AS final_score
FROM document_chunks_enhanced
WHERE 
    to_tsvector('vietnamese', content_normalized) @@ to_tsquery('vietnamese', query_normalized)
    AND access_level = ANY(user_accessible_levels)
    AND (department_owner = user_department OR department_owner = 'all_departments')
ORDER BY final_score DESC
LIMIT 20;
```

**BM25 Scoring Formula:**
```
BM25(D, Q) = Σ IDF(qi) * (f(qi, D) * (k1 + 1)) / (f(qi, D) + k1 * (1 - b + b * |D| / avgdl))

Where:
- IDF(qi): Inverse Document Frequency of term qi
- f(qi, D): Term frequency in document D
- |D|: Document length
- avgdl: Average document length in collection
- k1 = 1.5: Term frequency saturation parameter
- b = 0.75: Length normalization parameter
```

**Vietnamese Preprocessing for BM25:**
1. **Tokenization:** underthesea word segmentation
2. **Accent Removal:** Generate both accented và non-accented versions
3. **Legal Code Preservation:** Do NOT remove numbers before code detection
4. **Stopword Removal:** Vietnamese stopwords + domain-specific
5. **Stemming:** Not applied (Vietnamese doesn't have traditional stemming)

**Weighting:** 0.3 trong hybrid ranking (30%)

#### 4.4.3. Stage 3: Graph Traversal (Phase 2 - Planned)

**Mục đích:** Multi-hop reasoning qua document relationships.

**Graph Structure:**
```
Nodes:
- Document (law, policy, technical doc)
- Section, Chapter, Article, Clause (hierarchical)

Edges:
- CONTAINS (parent-child hierarchy)
- REFERENCES (cross-reference between documents)
- SUPERSEDES (newer version replaces older)
- RELATES_TO (semantic relationship)
```

**Traversal Strategy:**
```
1. Start with retrieved documents from Vector/BM25
2. Expand to:
   - Parent documents (for broader context)
   - Child sections (for detailed clauses)
   - Referenced documents (for related regulations)
   - Superseding documents (for latest version)
3. Apply confidence decay: 0.8^(hop_distance)
4. Return enriched context
```

**Status:** TBD - Requires implementation in Phase 2

#### 4.4.4. Hybrid Ranking & Fusion

**Fusion Strategy:** Reciprocal Rank Fusion (RRF) + Weighted Scores

```python
def hybrid_ranking(vector_results, bm25_results, alpha=0.7):
    """
    Combine results from vector và bm25 search.
    
    Args:
        vector_results: List[(chunk_id, semantic_score)]
        bm25_results: List[(chunk_id, keyword_score)]
        alpha: Weight for semantic score (default 0.7)
    
    Returns:
        List[(chunk_id, hybrid_score)]
    """
    # Normalize scores to [0, 1]
    vector_scores = normalize_scores(vector_results)
    bm25_scores = normalize_scores(bm25_results)
    
    # Combine scores
    all_chunk_ids = set([r[0] for r in vector_results] + [r[0] for r in bm25_results])
    
    hybrid_scores = []
    for chunk_id in all_chunk_ids:
        semantic = vector_scores.get(chunk_id, 0)
        keyword = bm25_scores.get(chunk_id, 0)
        
        # Weighted combination
        hybrid_score = alpha * semantic + (1 - alpha) * keyword
        
        # Diversity boost (penalize duplicate documents)
        document_id = get_document_id(chunk_id)
        if document_already_in_results(document_id, hybrid_scores):
            hybrid_score *= 0.8  # 20% penalty
        
        hybrid_scores.append((chunk_id, hybrid_score))
    
    # Sort by hybrid score descending
    hybrid_scores.sort(key=lambda x: x[1], reverse=True)
    
    return hybrid_scores[:10]  # Top 10
```

**Diversity Boost:**
- Penalize chunks from same document: 0.8x multiplier
- Encourage variety in results
- Balance between relevance và coverage

#### 4.4.5. Query Understanding và Expansion

**Intent Classification:**
```python
def classify_query_intent(query: str) -> str:
    """
    Classify user query intent for optimized search.
    """
    # Legal code pattern detection
    if re.search(r'\d+/\d+/(NĐ-CP|QĐ-TTg|TT-BTC)', query):
        return "specific_document"
    
    # How-to questions
    if any(keyword in query.lower() for keyword in ['làm thế nào', 'cách', 'quy trình']):
        return "how_to_procedure"
    
    # What-is questions
    if any(keyword in query.lower() for keyword in ['là gì', 'có nghĩa', 'định nghĩa']):
        return "what_is_information"
    
    # Comparison questions
    if any(keyword in query.lower() for keyword in ['so sánh', 'khác nhau', 'tốt hơn']):
        return "comparison"
    
    return "general"
```

**Query Expansion:**
```python
# Vietnamese Legal Domain Dictionary (excerpt)
EXPANSION_DICT = {
    "NĐ-CP": ["Nghị định Chính phủ", "Nghi dinh Chinh phu"],
    "QĐ-TTg": ["Quyết định Thủ tướng", "Quyet dinh Thu tuong"],
    "mua hàng": ["thu mua", "mua sắm", "procurement"],
    "nhân viên": ["cán bộ", "người lao động", "employee"],
    # ... 200+ entries
}

def expand_query(original_query: str) -> List[str]:
    """
    Expand query với synonyms và Vietnamese variants.
    """
    expanded_queries = [original_query]
    
    for term, synonyms in EXPANSION_DICT.items():
        if term in original_query:
            for synonym in synonyms:
                expanded_queries.append(
                    original_query.replace(term, synonym)
                )
    
    return expanded_queries[:5]  # Max 5 variants
```

### 4.5. LLM Generation Configuration

#### 4.5.1. Supported LLM Providers

Hệ thống hỗ trợ multiple LLM providers với automatic failover:

| Provider | Models | Use Case | Cost per 1K tokens |
|----------|--------|----------|-------------------|
| **OpenAI** | GPT-4, GPT-3.5-turbo | Primary production | GPT-4: $0.03 (input), $0.06 (output)<br/>GPT-3.5: $0.0015 (input), $0.002 (output) |
| **Anthropic** | Claude-3-opus, Claude-3-sonnet | Fallback, complex queries | Opus: $0.015 (input), $0.075 (output)<br/>Sonnet: $0.003 (input), $0.015 (output) |
| **Local Models** | Qwen, Llama (optional) | Development, cost optimization | $0 (self-hosted) |

**Selection Strategy:**
```python
def select_llm_provider(query_complexity, budget_mode):
    """
    Select appropriate LLM provider based on requirements.
    """
    if budget_mode == "cost_optimized":
        if query_complexity == "simple":
            return "gpt-3.5-turbo"  # Cheapest
        else:
            return "claude-3-sonnet"  # Good balance
    
    elif budget_mode == "quality_optimized":
        if query_complexity == "complex":
            return "gpt-4"  # Best quality
        else:
            return "claude-3-opus"  # High quality
    
    else:  # balanced (default)
        return "gpt-3.5-turbo"  # Most cost-effective
```

#### 4.5.2. Prompt Engineering

**System Prompt Template:**
```
Bạn là trợ lý AI chuyên về tài liệu pháp luật và chính sách nội bộ của ATTECH.

**Nhiệm vụ:**
- Trả lời câu hỏi dựa CHÍNH XÁC trên context được cung cấp
- Trích dẫn nguồn tài liệu (tên văn bản, điều, khoản, trang)
- Nếu không có thông tin trong context, hãy nói rõ "Tôi không tìm thấy thông tin về..."
- KHÔNG tự bịa đặt hoặc đoán mò thông tin

**Định dạng Trích dẫn:**
- Văn bản pháp luật: "Theo Nghị định số XX/YYYY/NĐ-CP ngày DD/MM/YYYY, Điều X, Khoản Y..."
- Chính sách nội bộ: "Theo [Tên tài liệu], Mục [X], Trang [Y]..."
- Tài liệu kỹ thuật: "[Tên sản phẩm] Datasheet, Section [X], Page [Y]"

**Ngôn ngữ:**
- Sử dụng tiếng Việt chuyên nghiệp
- Giữ nguyên thuật ngữ tiếng Anh (không dịch) nếu là thuật ngữ kỹ thuật

**Độ dài:**
- Câu trả lời ngắn gọn (2-3 đoạn văn)
- Nếu cần chi tiết, chia thành các điểm rõ ràng
```

**User Prompt Template:**
```
**Câu hỏi:** {user_query}

**Context từ Tài liệu:**

{context_chunks}

**Hãy trả lời câu hỏi dựa trên context trên, và nhớ trích dẫn nguồn.**
```

#### 4.5.3. Context Window Management

**Max Context Tokens:** 8,192 tokens (for GPT-3.5-turbo)

**Token Budget Allocation:**
```
System Prompt:      ~500 tokens
User Query:         ~100 tokens (average)
Context Chunks:     ~6,500 tokens (flexible)
Response Budget:    ~1,000 tokens (reserve)
-----------------------------------
Total:              ~8,100 tokens
```

**Chunk Selection Strategy:**
```python
def select_chunks_for_context(ranked_chunks, max_tokens=6500):
    """
    Select optimal chunks to fit within token budget.
    """
    selected_chunks = []
    total_tokens = 0
    
    for chunk in ranked_chunks:
        chunk_tokens = count_tokens(chunk.content)
        
        if total_tokens + chunk_tokens <= max_tokens:
            selected_chunks.append(chunk)
            total_tokens += chunk_tokens
        else:
            # Check if we can fit a summary
            summary = chunk.metadata.get('summary')
            summary_tokens = count_tokens(summary)
            if total_tokens + summary_tokens <= max_tokens:
                selected_chunks.append({
                    'content': summary,
                    'is_summary': True,
                    'full_chunk_id': chunk.id
                })
                total_tokens += summary_tokens
            else:
                break  # Context is full
    
    return selected_chunks, total_tokens
```

#### 4.5.4. Citation Extraction và Grounding

**Citation Format:**
```json
{
  "citation_type": "legal_document",  // or "internal_policy", "technical_doc"
  "document_id": "uuid",
  "document_title": "Nghị định số 76/2018/NĐ-CP",
  "law_id": "76/2018/NĐ-CP",
  "issue_date": "2018-05-15",
  "article": "Điều 5",
  "clause": "Khoản 2",
  "page": 12,
  "relevance_score": 0.95,
  "excerpt": "...relevant text snippet..."
}
```

**Grounding Verification:**
```python
def verify_grounding(generated_answer, retrieved_chunks):
    """
    Verify that generated answer is grounded in source documents.
    
    Returns:
        float: Grounding score [0, 1]
    """
    # Tokenize answer và source chunks
    answer_tokens = set(tokenize(generated_answer))
    source_tokens = set()
    for chunk in retrieved_chunks:
        source_tokens.update(tokenize(chunk.content))
    
    # Calculate token overlap
    overlap = len(answer_tokens & source_tokens)
    total = len(answer_tokens)
    
    grounding_score = overlap / total if total > 0 else 0.0
    
    # Threshold: 0.3 (30% overlap required)
    if grounding_score < 0.3:
        log_warning(f"Low grounding score: {grounding_score}")
    
    return grounding_score
```

### 4.6. Evaluation Framework

#### 4.6.1. Retrieval Quality Metrics

**Metric 1: Recall@10**
```
Recall@10 = (Number of relevant documents in top 10) / (Total relevant documents)

Target: > 90%
Measurement: Manual evaluation on 100 query-document pairs
```

**Metric 2: NDCG@10 (Normalized Discounted Cumulative Gain)**
```
NDCG@10 = DCG@10 / IDCG@10

Where:
DCG@10 = Σ(i=1 to 10) (2^relevance_i - 1) / log2(i + 1)
IDCG@10 = DCG for ideal ranking

Target: > 0.85
```

**Metric 3: MRR (Mean Reciprocal Rank)**
```
MRR = (1/N) * Σ(i=1 to N) (1 / rank_i)

Where rank_i = position of first relevant document for query i

Target: > 0.75
```

#### 4.6.2. Generation Quality Metrics

**Metric 4: Faithfulness**
```
Faithfulness = % of generated claims that can be verified in source documents

Measurement method:
1. Extract claims from generated answer
2. For each claim, check if supported by retrieved chunks
3. Calculate percentage of supported claims

Target: > 85%
Measurement: LLM-as-judge or human evaluation on 50 samples
```

**Metric 5: Answer Relevance**
```
Answer Relevance = Semantic similarity between (user query, generated answer)

Measurement:
1. Embed user query với Qwen model
2. Embed generated answer
3. Compute cosine similarity

Target: > 0.80
```

**Metric 6: Citation Accuracy**
```
Citation Accuracy = % of citations that are correct and verifiable

Measurement:
1. Extract all citations from generated answers
2. Verify each citation against source documents
3. Check: document ID, section, page number, quote accuracy

Target: > 95%
```

#### 4.6.3. End-to-End Metrics

**Metric 7: User Satisfaction**
```
Measurement: Post-interaction survey (5-point Likert scale)
Questions:
1. "The answer was relevant to my question" (Relevance)
2. "The answer was accurate and trustworthy" (Accuracy)
3. "I would use this system again" (Usability)

Aggregation: Average across all questions

Target: > 4.0/5.0
Sample size: 100+ user interactions
```

**Metric 8: Task Completion Rate**
```
Task Completion = % of queries where user clicked on at least one result
                  AND did not submit a refined query within 5 minutes

Target: > 90%
Measurement: Analytics tracking
```

#### 4.6.4. Test Set Specification

**Ground Truth Dataset:**
- **Size:** 100 query-document pairs minimum (expandable to 500)
- **Coverage:**
  - Normal cases: 60% (typical queries users would ask)
  - Edge cases: 25% (unusual phrasing, multi-intent, ambiguous)
  - Adversarial queries: 15% (prompt injection attempts, nonsensical)

**Annotation Process:**
1. Collect 100 real user queries from logs
2. Domain experts (legal, technical, HR) annotate:
   - Relevant documents for each query
   - Expected answer structure
   - Key points that must be covered
3. Review và consensus meeting
4. Store in PostgreSQL table: `ground_truth_queries`

**Ground Truth Source:** 
- Historical user queries (anonymized)
- Domain expert annotations
- Manual verification by Technical Lead

---

## 5. KIẾN TRÚC KỸ THUẬT

### 5.1. Tổng quan Kiến trúc Hệ thống

ATTECH RAG System sử dụng **microservices architecture** với các components được containerized bằng Docker và orchestrated bởi Docker Compose (Kubernetes cho future scaling).

```mermaid
graph TB
    subgraph "CLIENT TIER"
        Browser[🌐 Web Browser<br/>Chrome, Firefox, Edge]
        Mobile[📱 Mobile Browser<br/>Responsive Design]
    end
    
    subgraph "PRESENTATION TIER"
        Streamlit[🖥️ Streamlit UI<br/>Port 8501<br/>- Chat interface<br/>- Admin dashboard<br/>- Analytics views]
    end
    
    subgraph "APPLICATION TIER - API Gateway"
        FastAPI[🔌 FastAPI Server<br/>Port 8000<br/>- Request routing<br/>- JWT validation<br/>- Rate limiting<br/>- CORS handling]
    end
    
    subgraph "APPLICATION TIER - Core Services"
        subgraph "FR-04 RAG Engine"
            Retrieval[🔍 Retrieval Service<br/>- Hybrid search<br/>- Permission filtering<br/>- Result ranking]
            Synthesis[📋 Synthesis Service<br/>- Context assembly<br/>- Prompt generation<br/>- Token management]
            Generation[✨ Generation Service<br/>- Multi-provider LLM<br/>- Citation extraction<br/>- Grounding check]
        end
        
        AuthService[🛡️ FR-06 Auth Service<br/>- JWT tokens<br/>- Session management<br/>- RBAC enforcement]
        
        Analytics[📊 FR-07 Analytics<br/>- Usage tracking<br/>- Quality metrics<br/>- Dashboards]
        
        AdminService[⚙️ FR-08 Admin<br/>- User management<br/>- Document management<br/>- System config]
        
        IngestionPipeline[📥 FR-03 Data Ingestion<br/>- Document processing<br/>- Vietnamese NLP<br/>- Embedding generation]
    end
    
    subgraph "DATA TIER"
        PostgreSQL[(🐘 PostgreSQL 15<br/>192.168.1.95:5432<br/>- Users & permissions<br/>- Metadata<br/>- BM25 full-text<br/>- Audit logs)]
        
        ChromaDB[(🔢 ChromaDB 1.0.0<br/>192.168.1.95:8000<br/>- 1024-dim embeddings<br/>- Semantic search<br/>- HNSW index)]
        
        Redis[(⚡ Redis 7<br/>192.168.1.95:6379<br/>- Query cache<br/>- Session store<br/>- Rate limiting)]
    end
    
    subgraph "AI/ML TIER"
        EmbeddingService[🧠 Qwen Embedding Service<br/>GPU-accelerated<br/>- 1024-dim vectors<br/>- Batch processing]
        
        LLMProviders[🤖 LLM Providers<br/>- OpenAI GPT-4<br/>- Anthropic Claude<br/>- Local models<br/>API calls]
    end
    
    subgraph "MONITORING TIER"
        Prometheus[📈 Prometheus<br/>Port 9090<br/>Metrics collection]
        
        Grafana[📊 Grafana<br/>Port 3000<br/>Dashboards]
        
        Loki[📜 Loki<br/>Port 3100<br/>Log aggregation]
    end
    
    Browser --> Streamlit
    Mobile --> Streamlit
    Streamlit --> FastAPI
    
    FastAPI --> Retrieval
    FastAPI --> AuthService
    FastAPI --> Analytics
    FastAPI --> AdminService
    
    Retrieval --> Synthesis
    Synthesis --> Generation
    
    Retrieval --> PostgreSQL
    Retrieval --> ChromaDB
    Retrieval --> Redis
    
    AuthService --> PostgreSQL
    AuthService --> Redis
    
    Generation --> LLMProviders
    
    IngestionPipeline --> EmbeddingService
    IngestionPipeline --> PostgreSQL
    IngestionPipeline --> ChromaDB
    
    FastAPI -.-> Prometheus
    Prometheus --> Grafana
    FastAPI -.-> Loki
    
    classDef client fill:#e1f5ff,stroke:#01579b
    classDef presentation fill:#f3e5f5,stroke:#4a148c
    classDef application fill:#e8f5e9,stroke:#1b5e20
    classDef data fill:#fff3e0,stroke:#e65100
    classDef aiml fill:#fce4ec,stroke:#880e4f
    classDef monitoring fill:#f1f8e9,stroke:#33691e
    
    class Browser,Mobile client
    class Streamlit presentation
    class FastAPI,Retrieval,Synthesis,Generation,AuthService,Analytics,AdminService,IngestionPipeline application
    class PostgreSQL,ChromaDB,Redis data
    class EmbeddingService,LLMProviders aiml
    class Prometheus,Grafana,Loki monitoring
```

### 5.2. Database Architecture

#### 5.2.1. PostgreSQL Schema (v2.0 Enhanced)

**Connection Parameters:**
```yaml
Host: 192.168.1.95
Port: 5432
Database: knowledge_base_v2
Username: kb_admin
Password: [REDACTED - see key.md]
Connection String: postgresql://kb_admin:********@192.168.1.95:5432/knowledge_base_v2
```

**Core Tables:**

**1. users (User Management - FR-06)**
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hashed
    full_name VARCHAR(255) NOT NULL,      -- Supports Vietnamese characters
    
    -- Role & Department
    user_level VARCHAR(20) NOT NULL DEFAULT 'EMPLOYEE',  -- GUEST, EMPLOYEE, MANAGER, DIRECTOR, SYSTEM_ADMIN
    department VARCHAR(100),
    position VARCHAR(100),
    
    -- Status
    status VARCHAR(20) DEFAULT 'ACTIVE',  -- ACTIVE, INACTIVE, LOCKED
    is_active BOOLEAN NOT NULL DEFAULT true,
    email_verified BOOLEAN NOT NULL DEFAULT false,
    
    -- Security
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE,
    
    -- Preferences
    preferences JSONB DEFAULT '{}',  -- UI settings, language, etc.
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    CONSTRAINT check_user_level CHECK (user_level IN ('GUEST', 'EMPLOYEE', 'MANAGER', 'DIRECTOR', 'SYSTEM_ADMIN'))
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_level ON users(user_level);
CREATE INDEX idx_users_department ON users(department);
```

**2. documents_metadata_v2 (FR-02)**
```sql
CREATE TABLE documents_metadata_v2 (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Basic Info
    title VARCHAR(500) NOT NULL,
    source_document_id VARCHAR(255) UNIQUE,  -- External ID
    source_type VARCHAR(50),  -- PDF, DOCX, JSON, etc.
    file_path TEXT,
    file_hash VARCHAR(64),  -- MD5 or SHA256
    file_size_bytes BIGINT,
    
    -- Classification
    document_type VARCHAR(50),  -- legal, policy, technical, manual
    access_level VARCHAR(50) DEFAULT 'INTERNAL',  -- PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    department_owner VARCHAR(100) DEFAULT 'all_departments',
    
    -- Legal Document Specific
    law_id VARCHAR(100),  -- e.g., "76/2018/NĐ-CP"
    law_type VARCHAR(50),  -- e.g., "Nghị định", "Quyết định"
    issue_date DATE,
    effective_date DATE,
    expiry_date DATE,
    issuing_agency VARCHAR(200),
    signer VARCHAR(200),
    
    -- Relationships
    parent_document_id UUID REFERENCES documents_metadata_v2(document_id),
    based_on JSONB DEFAULT '[]',  -- Array of document IDs
    relates_to JSONB DEFAULT '[]',
    supersedes UUID REFERENCES documents_metadata_v2(document_id),
    superseded_by UUID REFERENCES documents_metadata_v2(document_id),
    
    -- Content Info
    language VARCHAR(10) DEFAULT 'vi',  -- vi, en
    page_count INTEGER,
    word_count INTEGER,
    
    -- Quality & Processing
    quality_score DECIMAL(3,2),  -- 0.00 to 1.00
    processing_status VARCHAR(50) DEFAULT 'PENDING',  -- PENDING, PROCESSING, COMPLETED, FAILED
    processing_error TEXT,
    
    -- Metadata
    tags TEXT[],  -- Array of tags
    keywords TEXT[],
    summary TEXT,
    custom_metadata JSONB DEFAULT '{}',  -- Flexible additional metadata
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    uploaded_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    
    -- Indexes
    CONSTRAINT check_access_level CHECK (access_level IN ('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'))
);

CREATE INDEX idx_documents_title ON documents_metadata_v2 USING gin(to_tsvector('vietnamese', title));
CREATE INDEX idx_documents_law_id ON documents_metadata_v2(law_id);
CREATE INDEX idx_documents_document_type ON documents_metadata_v2(document_type);
CREATE INDEX idx_documents_access_level ON documents_metadata_v2(access_level);
CREATE INDEX idx_documents_department_owner ON documents_metadata_v2(department_owner);
CREATE INDEX idx_documents_issue_date ON documents_metadata_v2(issue_date);
CREATE INDEX idx_documents_custom_metadata ON documents_metadata_v2 USING gin(custom_metadata);
```

**3. document_chunks_enhanced (FR-02 + FR-03)**
```sql
CREATE TABLE document_chunks_enhanced (
    chunk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    
    -- Content
    content TEXT NOT NULL,
    content_normalized TEXT,  -- Accent-removed for BM25
    chunk_index INTEGER NOT NULL,  -- Position in document
    
    -- Context
    prev_chunk_id UUID REFERENCES document_chunks_enhanced(chunk_id),
    next_chunk_id UUID REFERENCES document_chunks_enhanced(chunk_id),
    heading_context TEXT,  -- Parent section heading
    
    -- Legal Structure
    article_number VARCHAR(50),  -- e.g., "Điều 5"
    clause_number VARCHAR(50),   -- e.g., "Khoản 2"
    section_title VARCHAR(500),
    hierarchy_path VARCHAR(1000),  -- e.g., "Nghị định > Chương 1 > Điều 5 > Khoản 2"
    
    -- Tokens & Size
    token_count INTEGER,
    char_count INTEGER,
    
    -- BM25 Search
    tsv_content TSVECTOR,  -- Full-text search vector
    bm25_score REAL,       -- Pre-computed BM25 component
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Embedding Reference
    chroma_id VARCHAR(255),  -- ChromaDB ID for this chunk
    embedding_vector_exists BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_document_chunk_index UNIQUE(document_id, chunk_index)
);

-- Full-text search index
CREATE INDEX idx_chunks_tsv_content ON document_chunks_enhanced USING gin(tsv_content);

-- Trigger to automatically update tsv_content
CREATE TRIGGER tsvector_update BEFORE INSERT OR UPDATE
ON document_chunks_enhanced
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(tsv_content, 'pg_catalog.vietnamese', content_normalized);

CREATE INDEX idx_chunks_document_id ON document_chunks_enhanced(document_id);
CREATE INDEX idx_chunks_article_number ON document_chunks_enhanced(article_number);
CREATE INDEX idx_chunks_chroma_id ON document_chunks_enhanced(chroma_id);
CREATE INDEX idx_chunks_metadata ON document_chunks_enhanced USING gin(metadata);
```

**4. audit_logs (FR-06 Compliance)**
```sql
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Who
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    username VARCHAR(50),  -- Denormalized for performance
    user_role VARCHAR(20),
    
    -- What
    event_type VARCHAR(100) NOT NULL,  -- e.g., "document_access", "search_query", "user_role_changed"
    action VARCHAR(50) NOT NULL,  -- CREATE, READ, UPDATE, DELETE, SEARCH, LOGIN, etc.
    resource_type VARCHAR(50),  -- document, user, system_config, etc.
    resource_id VARCHAR(255),
    
    -- Details
    event_data JSONB DEFAULT '{}',  -- Flexible event-specific data
    query_text TEXT,  -- For search queries
    results_count INTEGER,  -- For search results
    
    -- Context
    ip_address VARCHAR(45),  -- IPv4 or IPv6
    user_agent TEXT,
    session_id VARCHAR(255),
    
    -- Outcome
    status VARCHAR(20),  -- SUCCESS, FAILURE, DENIED
    error_message TEXT,
    
    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    CONSTRAINT check_action CHECK (action IN ('CREATE', 'READ', 'UPDATE', 'DELETE', 'SEARCH', 'LOGIN', 'LOGOUT', 'ACCESS_DENIED'))
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_resource_type_id ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_event_data ON audit_logs USING gin(event_data);
```

**5. search_analytics (FR-07)**
```sql
CREATE TABLE search_analytics (
    search_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Query Info
    query_text TEXT NOT NULL,
    query_intent VARCHAR(50),  -- specific_document, how_to, what_is, comparison, general
    query_language VARCHAR(10),  -- vi, en
    
    -- User Context
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    user_role VARCHAR(20),
    department VARCHAR(100),
    session_id VARCHAR(255),
    
    -- Search Results
    retrieval_method VARCHAR(50),  -- hybrid, vector_only, bm25_only, graph
    results_count INTEGER,
    top_result_score REAL,
    results_document_ids UUID[],  -- Array of document IDs
    
    -- User Interaction
    clicked_document_id UUID REFERENCES documents_metadata_v2(document_id),
    clicked_rank INTEGER,  -- Position of clicked result (1-indexed)
    dwell_time_seconds INTEGER,  -- Time spent on clicked document
    user_feedback VARCHAR(20),  -- helpful, not_helpful, null
    
    -- Performance Metrics
    response_time_ms INTEGER,
    cache_hit BOOLEAN DEFAULT false,
    llm_provider VARCHAR(50),  -- openai, anthropic, local
    llm_tokens_used INTEGER,
    
    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
);

CREATE INDEX idx_search_analytics_user_id ON search_analytics(user_id);
CREATE INDEX idx_search_analytics_timestamp ON search_analytics(timestamp DESC);
CREATE INDEX idx_search_analytics_query_intent ON search_analytics(query_intent);
CREATE INDEX idx_search_analytics_user_feedback ON search_analytics(user_feedback);
```

#### 5.2.2. ChromaDB Configuration

**Connection Parameters:**
```yaml
Host: 192.168.1.95
Port: 8000
API Version: v2
Auth Token: [REDACTED - see key.md]
Endpoint: http://192.168.1.95:8000/api/v2/
```

**Collection Structure:**

**Main Collection: knowledge_base_v1**
```python
collection_config = {
    "name": "knowledge_base_v1",
    "metadata": {
        "description": "Main knowledge base for Vietnamese legal documents",
        "embedding_model": "Qwen/Qwen3-Embedding-0.6B",
        "embedding_dimension": 1024,
        "distance_metric": "cosine",
        "index_type": "HNSW",
        "hnsw_space": "cosine",
        "hnsw_construction_ef": 200,
        "hnsw_M": 16,
        "created_at": "2025-08-15"
    }
}

# Document metadata schema (per chunk)
document_metadata_schema = {
    "chunk_id": "UUID from PostgreSQL",
    "document_id": "UUID from PostgreSQL",
    "title": "Document title",
    "document_type": "legal|policy|technical|manual",
    "access_level": "public|internal|confidential|restricted",
    "department_owner": "Department name or all_departments",
    "law_id": "Legal code if applicable",
    "article_number": "Article number if legal doc",
    "hierarchy_path": "Full hierarchy string",
    "language": "vi|en",
    "chunk_index": "Integer position in document",
    "token_count": "Number of tokens",
    "quality_score": "0.0-1.0",
    "created_at": "ISO timestamp"
}
```

**Department-Specific Collections (Phase 2):**
```python
# Planned for optimization
department_collections = [
    "dept_hr_v2",       # HR documents only
    "dept_it_v2",       # IT technical docs
    "dept_rd_v2",       # R&D documents
    "dept_sales_v2",    # Sales & marketing
    "dept_manufacturing_v2"  # Manufacturing procedures
]
```

#### 5.2.3. Redis Configuration

**Connection Parameters:**
```yaml
Host: 192.168.1.95
Port: 6379
Database: 0
Password: None (internal network)
Connection String: redis://192.168.1.95:6379/0
```

**Data Structures:**

**1. Query Cache**
```
Key Pattern: cache:query:{query_hash}
Value: JSON string of {results, timestamp, user_role}
TTL: 3600 seconds (1 hour)
Eviction: LRU (Least Recently Used)
```

**2. Session Store**
```
Key Pattern: session:{session_id}
Value: JSON string of {user_id, role, department, login_time, last_active}
TTL: 1800 seconds (30 minutes)
Renewal: On each request
```

**3. Rate Limiting**
```
Key Pattern: ratelimit:{user_id}:{endpoint}:{time_window}
Value: Integer (request count)
TTL: 60 seconds (sliding window)
Limit: 100 requests per minute per user per endpoint
```

**4. Embedding Cache**
```
Key Pattern: embedding:{text_hash}
Value: Serialized numpy array (1024 floats)
TTL: 86400 seconds (24 hours)
Purpose: Cache frequently embedded queries/chunks
```

---

Đây là phần 2 (khoảng 25% document nữa). Tổng cộng đã hoàn thành ~50% đặc tả.

Tôi sẽ tiếp tục tạo phần 3 với:
- Mục 6: Đặc điểm Xử lý Tiếng Việt
- Mục 7: An ninh và Bảo mật
- Mục 8: Yêu cầu Phi chức năng

Bạn muốn tôi tiếp tục ngay không? 🚀