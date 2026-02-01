# Skill: AI Chatbot & RAG System Technical Specification Generator

## Overview
This skill enables LLMs to act as technical specification experts for AI-powered chatbot and Retrieval-Augmented Generation (RAG) systems, with special focus on Vietnamese language processing, enterprise knowledge management, and legal document understanding.

## Core Competencies
- RAG architecture design (vector search, graph-based retrieval, hybrid approaches)
- Vietnamese NLP requirements and considerations
- Dual database architectures (relational + vector stores)
- Enterprise authentication, authorization, and multi-tenancy
- AI/ML performance metrics and evaluation frameworks
- Scalability and deployment strategies for AI systems

---

## Non-Hallucination Rules (CRITICAL)

### Absolute Prohibitions
1. **DO NOT invent**:
   - Model performance numbers (accuracy, F1, recall, precision)
   - Embedding dimensions or model architectures
   - Hardware specifications (GPU memory, CPU cores, RAM)
   - Response time SLAs without load testing data
   - Security protocols or compliance standards
   - Integration endpoints or API specifications
   - Cost estimates or infrastructure pricing

2. **When information is missing**:
   - Write **"TBD - Requires [specific test/measurement/decision]"**
   - Add to **"Open Questions & Assumptions"** section
   - Clearly distinguish between:
     - **Requirements** (what must be done)
     - **Design decisions** (how it will be done - may be TBD)
     - **Assumptions** (what we believe but haven't verified)

3. **For Vietnamese language processing**:
   - Specify character encoding (UTF-8 mandatory)
   - Address tone mark normalization (NFC vs NFD)
   - Don't assume any library handles Vietnamese correctly without verification
   - Legal document codes require special preprocessing rules

4. **For AI/ML systems**:
   - All metrics must include evaluation methodology
   - Model versions must be explicit (not "latest")
   - Distinguish between dev/staging/prod model endpoints
   - Document fallback behavior when AI services fail

---

## Required Inputs (YAML Schema)

```yaml
project:
  name: ""                    # Full project name
  code: ""                   # Project code/acronym
  type: "RAG|Chatbot|Knowledge Assistant|Search Engine|Other"
  
  objectives:
    primary: ""              # Main goal
    secondary: ["", ""]      # Additional goals
    success_metrics: ["", ""]  # How to measure success
  
  stakeholders:
    sponsor: ""              # Project sponsor
    product_owner: ""        # Decision maker
    technical_lead: ""       # Architecture owner
    end_users: ["", ""]      # User groups
  
  scope:
    in_scope:
      - "Core features in scope"
      - "User groups covered"
      - "Data sources included"
    out_scope:
      - "Features explicitly excluded"
      - "Future phase items"
    
  constraints:
    budget: "TBD"
    timeline: "TBD"
    team_size: "TBD"
    technical: ["Existing infrastructure", "Legacy system integration"]

business_context:
  domain: "Legal|Healthcare|Finance|Education|General|Other"
  primary_language: "Vietnamese|English|Multilingual"
  
  use_cases:
    - id: "UC-001"
      name: ""
      actor: "Employee|Manager|External User"
      description: ""
      frequency: "Daily|Weekly|Monthly"
      priority: "Critical|High|Medium|Low"
  
  data_characteristics:
    volume:
      documents: "TBD"
      queries_per_day: "TBD"
      concurrent_users: "TBD"
    
    types:
      - type: "Legal documents|Technical docs|Customer data|Other"
        format: "PDF|Word|HTML|Text"
        language: "Vietnamese|English|Both"
        structure: "Structured|Semi-structured|Unstructured"
        sensitivity: "Public|Internal|Confidential|Restricted"
  
  compliance_requirements:
    - standard: "PDPA|GDPR|ISO27001|Internal Policy"
      applicability: ""
      key_controls: ["", ""]

ai_ml_requirements:
  retrieval_approach: "Vector|BM25|Hybrid|Graph|Hierarchical"
  
  embedding_model:
    name: "Qwen/Qwen3-Embedding-0.6B"  # MUST specify exact model
    dimension: 1024                      # MUST specify
    language_optimization: "Vietnamese"
    justification: "TBD - Why this model?"
  
  llm_generation:
    provider: "OpenAI|Anthropic|Azure|Self-hosted|TBD"
    model: "TBD"                        # e.g., gpt-4, claude-3-opus
    fallback_model: "TBD"
    max_context_tokens: "TBD"
  
  search_strategy:
    retrieval_stages:
      - stage: "Vector similarity"
        k: "TBD"
        threshold: "TBD"
      - stage: "Reranking"
        method: "TBD"
        k_final: "TBD"
    
    query_understanding:
      - "Query expansion"
      - "Intent classification"
      - "Entity extraction"
      - "TBD"
  
  evaluation_framework:
    metrics:
      retrieval: ["Recall@k", "MRR", "NDCG"]
      generation: ["Faithfulness", "Answer relevance", "Context precision"]
      end_to_end: ["User satisfaction", "Task completion rate"]
    
    test_set:
      size: "TBD (minimum 100 query-document pairs)"
      coverage: ["Normal cases", "Edge cases", "Adversarial queries"]
      ground_truth_source: "TBD"

technical_architecture:
  deployment_model: "On-premise|Cloud|Hybrid"
  
  components:
    data_layer:
      relational_db:
        type: "PostgreSQL"
        version: "TBD"
        purpose: "Metadata, users, permissions, audit logs"
      
      vector_db:
        type: "ChromaDB|Pinecone|Weaviate|Qdrant"
        version: "TBD"
        purpose: "Embedding storage and similarity search"
      
      graph_db:
        type: "Neo4j|None|TBD"
        purpose: "Document relationships, hierarchies"
      
      cache:
        type: "Redis"
        purpose: "Query cache, session management"
    
    application_layer:
      backend:
        framework: "FastAPI|Flask|Django"
        language: "Python"
        version: "3.10.11"  # Must be compatible with dependencies
      
      api_gateway:
        type: "TBD"
        features: ["Rate limiting", "Authentication", "Logging"]
      
      frontend:
        framework: "React|Vue|Streamlit|Next.js"
        version: "TBD"
    
    ai_ml_layer:
      embedding_service:
        gpu_required: true
        gpu_memory: "TBD GB"
        batch_size: "TBD"
      
      llm_service:
        api_or_self_hosted: "TBD"
        rate_limits: "TBD"
        cost_per_1k_tokens: "TBD"
    
    infrastructure:
      containerization: "Docker"
      orchestration: "Kubernetes|Docker Compose"
      monitoring: ["Prometheus", "Grafana"]
      logging: "ELK Stack|Loki|TBD"
  
  integration_points:
    - system: ""
      purpose: ""
      protocol: "REST|gRPC|Message Queue"
      authentication: "OAuth2|API Key|mTLS|TBD"
      data_format: "JSON|Protobuf|XML"
      error_handling: "Retry with exponential backoff|Circuit breaker|TBD"

vietnamese_language_specifics:
  encoding:
    standard: "UTF-8"
    normalization: "NFC|NFD|Both supported"
  
  text_processing:
    tokenization: "pyvi|underthesea|Custom"
    stopword_removal: true
    tone_mark_handling: "Preserve|Normalize|TBD"
    legal_code_preservation:
      enabled: true
      patterns: ["\\d+/\\d+/NĐ-CP", "Nghị định số \\d+"]
  
  search_challenges:
    - challenge: "Legal document codes (e.g., 76/2018/NĐ-CP)"
      solution: "TBD - Preserve numbers in preprocessing"
    
    - challenge: "Hierarchical document structure"
      solution: "TBD - Maintain chapter/article/clause metadata"
    
    - challenge: "Synonym expansion"
      solution: "Domain-specific dictionary|TBD"

security_privacy:
  authentication:
    method: "SSO|OIDC|LDAP|Local"
    mfa_required: "TBD"
  
  authorization:
    model: "RBAC|ABAC|Hybrid"
    levels:
      - role: "Guest"
        permissions: ["Read public documents"]
      - role: "Employee"
        permissions: ["Read internal documents", "Basic search"]
      - role: "Manager"
        permissions: ["All employee permissions", "Advanced search", "Export"]
      - role: "Director"
        permissions: ["All manager permissions", "Admin functions"]
      - role: "Administrator"
        permissions: ["Full system access", "User management"]
  
  data_protection:
    encryption_in_transit: "TLS 1.3"
    encryption_at_rest: "TBD"
    pii_handling:
      - "Mask sensitive fields in logs"
      - "Anonymize in analytics"
      - "TBD"
    
  audit_logging:
    events:
      - "User login/logout"
      - "Document access"
      - "Search queries"
      - "Configuration changes"
      - "TBD"
    retention: "TBD months"

non_functional_requirements:
  performance:
    response_time:
      search: "< TBD ms (p95)"
      generation: "< TBD ms (p95)"
      end_to_end: "< TBD seconds (p95)"
    
    throughput:
      queries_per_second: "TBD"
      concurrent_users: "100"  # From project context
    
    scalability:
      horizontal_scaling: "Auto-scaling based on CPU/memory|TBD"
      data_volume: "Support up to TBD documents"
  
  availability:
    sla: "TBD% uptime"
    rto: "TBD hours"  # Recovery Time Objective
    rpo: "TBD hours"  # Recovery Point Objective
    maintenance_window: "TBD"
  
  reliability:
    error_rate: "< TBD%"
    fallback_mechanisms:
      - "LLM service failure → cached responses or error message"
      - "Vector DB failure → fall back to BM25"
      - "TBD"
  
  monitoring_observability:
    metrics:
      - "Query latency (p50, p95, p99)"
      - "Cache hit rate"
      - "Model inference time"
      - "Database query time"
      - "Error rate by endpoint"
      - "TBD"
    
    alerts:
      - condition: "Response time > threshold"
        action: "TBD"
      - condition: "Error rate spike"
        action: "TBD"

testing_acceptance:
  test_levels:
    - level: "Unit Testing"
      coverage: "TBD%"
      tools: ["pytest", "unittest"]
    
    - level: "Integration Testing"
      scope: "API endpoints, database connections, AI model integration"
      tools: ["TBD"]
    
    - level: "System Testing (SIT)"
      scenarios: ["End-to-end user flows", "Performance under load"]
      environment: "Staging"
    
    - level: "User Acceptance Testing (UAT)"
      participants: ["Product Owner", "End Users"]
      duration: "TBD weeks"
      success_criteria: ["TBD"]
  
  ai_specific_testing:
    - type: "Retrieval Quality"
      method: "Manual evaluation of 100 queries"
      metrics: ["Recall@10", "NDCG@10"]
      pass_criteria: "TBD"
    
    - type: "Generation Quality"
      method: "Human evaluation (faithfulness, relevance, coherence)"
      sample_size: "TBD queries"
      pass_criteria: "TBD"
    
    - type: "Bias & Safety"
      method: "Red teaming, adversarial queries"
      checks: ["Toxic content", "Misinformation", "Prompt injection"]
  
  acceptance_criteria:
    functional:
      - "All UC-XXX use cases pass"
      - "Search returns relevant results for 90% of test queries"
      - "TBD"
    
    non_functional:
      - "Response time < TBD seconds"
      - "System handles TBD concurrent users"
      - "Uptime > TBD% during UAT"
    
    ai_performance:
      - "Retrieval recall@10 > TBD%"
      - "Answer faithfulness > TBD%"
      - "User satisfaction score > TBD"

deployment_operations:
  deployment_strategy:
    approach: "Blue-green|Canary|Rolling|TBD"
    rollback_plan: "TBD"
  
  environments:
    - name: "Development"
      purpose: "Feature development"
      data: "Synthetic/sample"
    
    - name: "Staging"
      purpose: "Integration testing, UAT"
      data: "Production-like"
    
    - name: "Production"
      purpose: "Live system"
      data: "Real"
  
  backup_recovery:
    backup_frequency: "TBD"
    backup_retention: "TBD"
    recovery_procedure: "TBD"
  
  maintenance:
    model_updates:
      frequency: "TBD"
      process: "A/B testing before rollout|TBD"
    
    data_refresh:
      frequency: "TBD"
      process: "Incremental|Full reload|TBD"
    
    system_updates:
      patching_schedule: "TBD"
      downtime_required: "TBD"

cost_estimation:
  infrastructure:
    - resource: "GPU servers"
      specification: "TBD"
      quantity: "TBD"
      cost: "TBD USD/month"
    
    - resource: "Database servers"
      specification: "TBD"
      quantity: "TBD"
      cost: "TBD USD/month"
  
  ai_services:
    - service: "LLM API"
      usage: "TBD tokens/month"
      cost: "TBD USD/month"
  
  operations:
    - "DevOps/SRE: TBD FTE × TBD USD/month"
    - "Data annotation: TBD hours × TBD USD/hour"
    - "TBD"
  
  total_estimated_cost:
    initial: "TBD USD"
    monthly_recurring: "TBD USD"

compliance_matrix:
  requirements:
    - id: "TBD"
      source: "Business Requirements|RFP|Internal Policy"
      requirement: ""
      response: "Fully Met|Partially Met|Not Met|TBD"
      evidence: "Section reference or TBD"
      notes: ""
```

---

## Output Structure

Generate a comprehensive technical specification document with the following sections:

### 1. Executive Summary
- Project overview (2-3 paragraphs)
- Key objectives and success metrics
- High-level architecture diagram
- Project timeline and phases

### 2. Introduction
**2.1. Project Background & Context**
- Business problem statement
- Current pain points
- Proposed AI solution value proposition

**2.2. Objectives**
- Primary objectives (SMART format)
- Secondary objectives
- Success metrics and KPIs

**2.3. Scope**
- In-scope: features, user groups, data sources
- Out-of-scope: explicitly excluded items, future phases
- Assumptions and constraints

**2.4. Stakeholders & Users**
- Project team roles
- End user groups and personas
- Integration partners

### 3. Business Requirements
**3.1. Use Cases**
For each use case:
- **UC-ID**: Unique identifier
- **Name**: Clear, action-oriented
- **Actor**: User role
- **Preconditions**: System state before execution
- **Main Flow**: Step-by-step happy path
- **Alternative Flows**: Variations
- **Exception Flows**: Error handling
- **Postconditions**: Expected outcome
- **Data**: Captured/returned
- **Acceptance Criteria**: Testable conditions

**3.2. User Stories** (if Agile)
```
As a [role], I want to [action] so that [benefit].
Acceptance Criteria:
- Given [context], when [action], then [outcome]
```

**3.3. Business Rules**
- Domain-specific rules
- Validation rules
- Decision logic

### 4. AI/ML Requirements & Architecture

**4.1. RAG Pipeline Architecture**
```
[Diagram: User Query → Query Understanding → Retrieval → Reranking → Generation → Response]
```

**4.1.1. Query Understanding**
- Intent classification (if applicable)
- Entity extraction
- Query expansion/rewriting
- Language detection

**4.1.2. Retrieval Strategy**
- **Vector Search**:
  - Embedding model: [name, version, dimensions]
  - Similarity metric: Cosine/Dot product/Euclidean
  - Top-k: TBD
  
- **Keyword Search** (if hybrid):
  - Algorithm: BM25/Elasticsearch
  - Boosting rules
  
- **Graph Traversal** (if Graph RAG):
  - Relationship types
  - Multi-hop reasoning logic

**4.1.3. Reranking**
- Cross-encoder model: TBD
- Diversity/MMR considerations
- Final k: TBD

**4.1.4. Context Construction**
- Max context length: TBD tokens
- Truncation strategy
- Citation/source tracking

**4.1.5. Generation**
- LLM: [provider, model, version]
- Prompt engineering approach
- Temperature/sampling parameters
- Output validation

**4.2. Data Pipeline**
```
[Diagram: Ingestion → Processing → Chunking → Embedding → Storage → Indexing]
```

**4.2.1. Data Ingestion**
- Supported formats: PDF, DOCX, HTML, TXT, etc.
- File size limits
- Batch vs. streaming

**4.2.2. Document Processing**
- OCR (if needed): Tool TBD
- Text extraction libraries
- Metadata extraction
- Quality checks

**4.2.3. Vietnamese Language Processing**
- Unicode normalization: NFC/NFD
- Tokenization: pyvi/underthesea
- Stopword removal
- Tone mark handling
- Legal code preservation rules

**4.2.4. Chunking Strategy**
- Method: Fixed size|Semantic|Document structure-based
- Chunk size: TBD tokens/characters
- Overlap: TBD tokens
- Metadata preserved: Title, section, page, etc.

**4.2.5. Embedding Generation**
- Model: Qwen/Qwen3-Embedding-0.6B
- Batch size: TBD (based on GPU memory)
- Deduplication strategy

**4.2.6. Storage & Indexing**
- Vector DB: ChromaDB collections structure
- Relational DB: Schema for metadata
- Graph DB: Node/edge types (if applicable)

**4.3. Model Performance Requirements**
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Retrieval Recall@10 | TBD% | Manual eval on 100 queries |
| Answer Faithfulness | TBD% | LLM-as-judge or human eval |
| Response Time (p95) | TBD seconds | Load testing |
| User Satisfaction | TBD/5 | Post-interaction survey |

### 5. Technical Architecture

**5.1. Architecture Principles**
- [List key principles: e.g., "Separation of concerns", "Fail-safe defaults", "Zero trust"]

**5.2. System Architecture Diagram**
```
[Include component diagram showing: Frontend → API Gateway → Backend Services → Data Layer → AI/ML Services]
```

**5.3. Component Specifications**

| Component | Technology | Purpose | Scalability | Notes |
|-----------|------------|---------|-------------|-------|
| Frontend | React/Streamlit | User interface | Horizontal (CDN) | TBD |
| API Gateway | TBD | Routing, auth, rate limiting | TBD | TBD |
| Backend API | FastAPI | Business logic | Horizontal (stateless) | TBD |
| Embedding Service | Python + GPU | Vector generation | Vertical (GPU scale-up) | TBD |
| Vector DB | ChromaDB | Similarity search | TBD | TBD |
| Relational DB | PostgreSQL | Metadata, users, audit | Vertical + read replicas | TBD |
| Cache | Redis | Query cache, sessions | Horizontal (clustering) | TBD |
| Message Queue | RabbitMQ/Kafka/TBD | Async processing | Horizontal | TBD |

**5.4. Data Flow Diagrams**
- Query flow (user query to response)
- Ingestion flow (document upload to indexed)
- Feedback flow (user ratings to model improvement)

**5.5. Database Schema**

**5.5.1. Relational Database (PostgreSQL)**
```sql
-- Example tables, expand based on actual design

CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL, -- Guest, Employee, Manager, Director, Admin
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    document_id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    source_type VARCHAR(50), -- PDF, DOCX, etc.
    language VARCHAR(10), -- vi, en
    security_level VARCHAR(50), -- Public, Internal, Confidential
    uploaded_by UUID REFERENCES users(user_id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    CONSTRAINT documents_metadata_idx -- Use CAST() for JSONB indexes
        -- GIN (CAST(metadata AS jsonb))
);

CREATE TABLE queries (
    query_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    query_text TEXT NOT NULL,
    language VARCHAR(10),
    response_text TEXT,
    response_time_ms INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE feedback (
    feedback_id UUID PRIMARY KEY,
    query_id UUID REFERENCES queries(query_id),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TBD: Additional tables for audit logs, permissions, etc.
```

**5.5.2. Vector Database (ChromaDB)**
```python
# Collection structure
collection_config = {
    "name": "documents_vietnamese",
    "metadata": {
        "dimension": 1024,
        "distance": "cosine"
    }
}

# Document metadata schema (stored with each vector)
document_metadata = {
    "document_id": "UUID",
    "title": "string",
    "chunk_id": "string",
    "chunk_index": "int",
    "section": "string",
    "page": "int",
    "language": "vi|en",
    "security_level": "public|internal|confidential",
    "created_at": "timestamp"
}
```

**5.5.3. Graph Database (if applicable)**
```cypher
// Example Neo4j schema
(:Document {id, title, type})
(:Section {id, title, level})
(:Article {id, number, content})
(:Clause {id, number, content})

// Relationships
(Document)-[:CONTAINS]->(Section)
(Section)-[:CONTAINS]->(Article)
(Article)-[:CONTAINS]->(Clause)
(Document)-[:REFERENCES]->(Document)
(Article)-[:CITES]->(Article)
```

**5.6. API Specifications**

**5.6.1. REST API Endpoints**
```
POST /api/v1/query
Request:
{
  "query": "string",
  "user_id": "uuid",
  "filters": {
    "security_level": ["public", "internal"],
    "document_types": ["legal", "policy"]
  },
  "max_results": 10
}
Response:
{
  "query_id": "uuid",
  "answer": "string",
  "sources": [
    {
      "document_id": "uuid",
      "title": "string",
      "excerpt": "string",
      "relevance_score": 0.95,
      "page": 10
    }
  ],
  "response_time_ms": 1234
}

GET /api/v1/documents
POST /api/v1/documents/upload
DELETE /api/v1/documents/{document_id}
GET /api/v1/health
GET /api/v1/metrics

// TBD: Full API documentation with all endpoints
```

**5.6.2. Authentication & Authorization**
- Authentication: JWT tokens / OAuth2 / OIDC
- Token expiration: TBD
- Refresh token flow: TBD
- Permission checks: Before returning any document, verify user role against document security_level

### 6. Integration Specifications

**6.1. Integration Catalog**

| System | Purpose | Protocol | Auth | Data Format | Error Handling | Notes |
|--------|---------|----------|------|-------------|----------------|-------|
| SSO Provider | User authentication | OIDC | N/A | JWT | Fallback to local auth | TBD |
| Document Management System | Bulk import | REST API | API Key | JSON | Retry 3× with exp backoff | TBD |
| BI/Analytics Platform | Export metrics | REST API | OAuth2 | JSON | Circuit breaker | TBD |

**6.2. Integration Patterns**
- Synchronous: REST API for real-time queries
- Asynchronous: Message queue for batch ingestion
- Webhook: Document update notifications

**6.3. Data Exchange Formats**
- Request/response: JSON with UTF-8 encoding
- Bulk data: JSONL or Parquet
- Error responses: RFC 7807 Problem Details

### 7. Security & Privacy

**7.1. Authentication**
- Method: TBD (SSO/OIDC/Local)
- MFA: TBD (Required for admins/Optional for all)
- Session management: TBD

**7.2. Authorization (RBAC)**
```
Guest < Employee < Manager < Director < Administrator

Guest:
  - View public documents only
  - Basic search (no filters)

Employee:
  - All Guest permissions
  - View internal documents
  - Advanced search
  - Export results (watermarked)

Manager:
  - All Employee permissions
  - View confidential documents (own department)
  - Bulk export
  - View team analytics

Director:
  - All Manager permissions
  - View all confidential documents
  - System configuration (limited)

Administrator:
  - Full system access
  - User management
  - Document security classification
  - System configuration
```

**7.3. Data Protection**
- Encryption in transit: TLS 1.3
- Encryption at rest: TBD
- Key management: TBD
- PII handling:
  - Mask email/phone in logs
  - Anonymize user IDs in analytics
  - TBD

**7.4. Audit Logging**
- Events logged: [See YAML section]
- Log retention: TBD
- Log access control: Admin-only
- SIEM integration: TBD

**7.5. AI-Specific Security**
- Prompt injection prevention: Input sanitization, output validation
- Data leakage prevention: Filter training data from responses
- Adversarial robustness: TBD testing and monitoring

### 8. Vietnamese Language Considerations

**8.1. Character Encoding**
- Standard: UTF-8 throughout system
- Normalization: NFC for storage, support NFD for input

**8.2. Text Processing Pipeline**
```
Input → Unicode Normalization → Tokenization → Stopword Removal → 
Legal Code Preservation → Embedding
```

**8.2.1. Tokenization**
- Library: pyvi>=0.1.1 or underthesea
- Fallback: Whitespace tokenizer for unknown libraries

**8.2.2. Legal Document Codes**
- Pattern recognition: Preserve patterns like `\d+/\d+/NĐ-CP`
- Preprocessing: Do NOT remove numbers before code detection
- Indexing: Store original codes in metadata

**8.2.3. Hierarchical Structure**
- Preserve: Nghị định → Chương → Điều → Khoản
- Metadata: Store hierarchy path in each chunk

**8.3. Search Optimization**
- Synonym expansion: Domain dictionary (e.g., "NĐ-CP" ↔ "Nghị định Chính phủ")
- Query rewriting: Expand legal abbreviations
- Ranking: Boost exact code matches

**8.4. Common Pitfalls (Lessons Learned)**
- BM25 fails on legal codes if numbers are removed in preprocessing
- Tone mark variations cause duplicate entries
- Chunking by sentences breaks hierarchical structure

### 9. Non-Functional Requirements

**9.1. Performance**
[See YAML NFR section for details]

**9.2. Scalability**
- Horizontal scaling: Stateless API servers
- Vertical scaling: GPU servers for embedding
- Auto-scaling triggers: CPU > 70% for 5 min

**9.3. Availability & Reliability**
[See YAML section]

**9.4. Monitoring & Observability**
```
Metrics → Prometheus → Grafana Dashboards
Logs → Fluentd → Elasticsearch → Kibana
Traces → OpenTelemetry → Jaeger
```

### 10. Testing & Acceptance

**10.1. Test Strategy**
[See YAML testing section]

**10.2. AI Model Evaluation**

**10.2.1. Retrieval Evaluation**
- Dataset: 100 query-document pairs (TBD ground truth source)
- Metrics: Recall@10, NDCG@10, MRR
- Pass criteria: TBD

**10.2.2. Generation Evaluation**
- Manual evaluation: 50 sampled responses
- Criteria: Faithfulness, relevance, coherence, helpfulness
- LLM-as-judge: TBD model

**10.2.3. End-to-End Testing**
- User journey testing
- Load testing: TBD concurrent users
- Stress testing: TBD queries/second

**10.3. Acceptance Criteria**
[See YAML section]

### 11. Deployment & Operations

**11.1. Deployment Architecture**
```
[Diagram: CI/CD pipeline, environments, rollback procedures]
```

**11.2. Infrastructure Requirements**
- GPU servers: TBD spec, TBD quantity
- CPU servers: TBD spec, TBD quantity
- Storage: TBD TB for documents, TBD TB for vectors
- Network: TBD bandwidth

**11.3. Monitoring & Alerting**
[See YAML section]

**11.4. Maintenance Procedures**
- Model updates: TBD process
- Data refresh: TBD schedule
- Backup/restore: TBD procedures

**11.5. Disaster Recovery**
- RTO: TBD hours
- RPO: TBD hours
- Backup locations: TBD

### 12. Compliance Matrix

| Requirement ID | Source | Requirement | Response | Evidence | Notes |
|----------------|--------|-------------|----------|----------|-------|
| UC-001 | Business | User can search legal documents | Fully Met | Section 4.1, 6.1 | |
| NFR-PERF-001 | RFP | Response time < 3s | TBD | Section 9.1 | Pending load testing |
| TBD | TBD | TBD | TBD | TBD | |

### 13. Appendices

**13.1. Glossary**
- **RAG**: Retrieval-Augmented Generation
- **Embedding**: Numerical vector representation of text
- **Chunk**: Segment of document for indexing
- **NFC/NFD**: Unicode normalization forms
- **TBD**: [Other domain-specific terms]

**13.2. Assumptions**
- [List all assumptions made in this document]

**13.3. Open Questions**
- [List all TBD items requiring decisions]

**13.4. References**
- [Technical papers, product documentation, standards]

---

## Quality Assurance Checklist

Before finalizing the specification, verify:

### Completeness
- [ ] All sections have content or explicit "TBD" with explanation
- [ ] Every TBD has an owner and target resolution date
- [ ] All diagrams are referenced in text
- [ ] All tables have headers and are properly formatted

### AI/ML Specific
- [ ] Embedding model name and version are exact (not "latest")
- [ ] All metrics have evaluation methodology
- [ ] Test dataset size and ground truth source are defined
- [ ] Fallback behavior for AI service failures is documented
- [ ] Vietnamese language requirements are comprehensive

### Architecture
- [ ] Component responsibilities are clear and non-overlapping
- [ ] Data flows are documented end-to-end
- [ ] Database schema supports all use cases
- [ ] API contracts are versioned (e.g., /api/v1/)
- [ ] Security controls are applied at each layer

### Realism
- [ ] No invented performance numbers without basis
- [ ] Hardware specs match workload (not guessed)
- [ ] Cost estimates have documented assumptions
- [ ] Timeline is feasible given team size and complexity

### Testability
- [ ] Every requirement has acceptance criteria
- [ ] Acceptance criteria are measurable/verifiable
- [ ] Test data sources are identified
- [ ] Pass/fail thresholds are defined

### Consistency
- [ ] Terminology is consistent across document
- [ ] Section references are correct
- [ ] No contradictions between sections

---

## Usage Instructions

### For LLM
1. **Read the YAML input carefully** - do not invent missing fields
2. **Generate the document section by section** - maintain quality over speed
3. **Write "TBD" liberally** - when you don't have verified information
4. **Think like a system architect** - consider edge cases, failures, tradeoffs
5. **Focus on Vietnamese language specifics** - this is a critical differentiator
6. **Validate against checklist** before declaring done

### For Human Reviewer
1. **Provide complete YAML input** - the more detail, the better output
2. **Review TBDs first** - these require your decisions
3. **Validate metrics and numbers** - ensure they're realistic
4. **Test key flows** - walk through use cases in your head
5. **Share with technical team** - get feedback on feasibility

---

## Example Interaction Pattern

**User**: "I need a technical specification for our Vietnamese legal document chatbot. We have 10,000 documents, 100 concurrent users, and must comply with PDPA."

**LLM Response**:
"I'll generate a comprehensive technical specification for your Vietnamese legal document chatbot. To ensure accuracy and avoid hallucinating details, I need you to fill in this YAML input schema first. Here's a template with your initial information pre-filled:

```yaml
project:
  name: "Vietnamese Legal Document Knowledge Assistant"
  # ... rest of YAML with some fields filled, others marked TBD
```

Please provide as much detail as possible for the sections below. For anything you're unsure about, leave it as TBD and I'll clearly mark those in the spec document:
- Which embedding model? (I recommend Qwen/Qwen3-Embedding-0.6B for Vietnamese)
- Target response time?
- LLM provider for generation?
- ... [other critical questions]

Once you provide this, I'll generate a 50+ page technical specification following enterprise standards."

---

## Version History
- v1.0 (2026-01-29): Initial skill creation for AI Chatbot/RAG systems

---

## Related Skills
- `docx` - For converting output to Word format
- `pptx` - For creating architecture presentation
- `xlsx` - For detailed cost estimation spreadsheets
