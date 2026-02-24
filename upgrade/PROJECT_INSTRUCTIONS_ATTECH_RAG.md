# 🤖 ATTECH RAG PROJECT - CLAUDE INSTRUCTIONS

**Version:** 2.0  
**Last Updated:** February 10, 2026  
**Project Lead:** Tuan (Technical Lead)

---

## 📋 PROJECT CONTEXT

### System Overview
Bạn đang làm việc trên **Hệ thống Trợ lý Tri thức ATTECH** (RAG Knowledge Assistant) - một AI chatbot giúp 400 nhân viên truy cập văn bản pháp luật Việt Nam và chính sách nội bộ.

**Core Technology:** RAG (Retrieval-Augmented Generation) với Vietnamese NLP optimization

**Deployment:**
- **Dev Environment:** Server 192.168.1.70 (ports 8000-8501)
- **Production Environment:** Server 192.168.1.88 (NVIDIA RTX 2080 Ti GPU)
- **Scale:** 100+ concurrent users, 5-tier RBAC, 100k+ documents target

---

## 🏗️ TECHNICAL ARCHITECTURE

### Tech Stack
```
Language:      Python 3.10.11, CUDA 11.8
Backend:       FastAPI (async), Uvicorn
Databases:     PostgreSQL 15, ChromaDB 1.0, Redis 7
Embeddings:    Qwen3-Embedding-0.6B (1024D)
LLM:           OpenAI GPT-4 (via API)
Monitoring:    Prometheus, Grafana, Loki
Deployment:    Docker, Docker Compose
Vietnamese NLP: pyvi, underthesea, sentence-transformers
```

### Key Servers & Ports
```
PostgreSQL:    192.168.1.70:5432  (DB: knowledge_base_v2, User: kb_admin)
              192.168.1.70:15432 (DB: chatbotR4 - Graph RAG)
ChromaDB:      192.168.1.70:8000  (Collection: knowledge_base_v2)
Redis:         192.168.1.70:6379  (Caching & Sessions)
APIs:          192.168.1.70:8000  (FR-02.2 - Main API)
               192.168.1.70:8001  (FR-07 - Analytics API)
               192.168.1.70:8002  (FR-08 - Admin API)
               192.168.1.70:8007  (FR-03.3 - Ingestion API)
Streamlit:     192.168.1.70:8501  (Chat UI & Dashboards)
Prometheus:    192.168.1.70:9090
Grafana:       192.168.1.70:3000
Loki:          192.168.1.70:3100
```

---

## 🎯 CURRENT PROJECT STATUS (Feb 2026)

### ✅ Phase 1 - COMPLETED (95%)
**Core RAG system operational** với 8 functional requirements:
- FR-01: Data Foundation & Metadata ✅
- FR-02: Dual Database System ✅
- FR-03: Document Processing Pipeline ✅
- FR-04: RAG Core Engine ✅
- FR-05: Chat UI (Streamlit prototype) ✅
- FR-06: Database Schema (Auth pending) 🟡
- FR-07: Analytics & Reporting ✅
- FR-08: Admin & Maintenance Tools ✅

### 🔄 Phase 2 - IN PROGRESS (40%)
**Production-grade features:**
- Graph RAG (schema deployed, auto-sync pending)
- Advanced monitoring (infrastructure ready, dashboards pending)
- Quality improvements (reranker, RAGAS evaluation pending)

---

## 🚨 CRITICAL BLOCKERS (P0 - Must Complete)

### 1. Authentication & RBAC API ❌
**Status:** Not started  
**Impact:** **BLOCKS production deployment**  
**What's missing:**
```
❌ POST /api/auth/login, /register, /logout, /refresh
❌ JWT token generation & validation
❌ RBAC enforcement trong RAG pipeline
❌ Permission filtering theo user level (Guest→Employee→Manager→Director→Admin)
```

### 2. Chat History API ❌
**Status:** Database ready, API missing  
**Impact:** **BLOCKS user experience**  
**What's missing:**
```
❌ GET /api/v1/history/sessions       # List conversations
❌ GET /api/v1/history/sessions/{id}  # Load conversation
❌ DELETE /api/v1/history/sessions/{id} # Delete history
❌ Frontend sidebar để hiển thị lịch sử
❌ Session management logic
```

### 3. Cross-Encoder Reranking ❌
**Status:** Not started  
**Impact:** +30% accuracy improvement (từ ~75% → 95%+)  
**What's missing:**
```
❌ Integration bge-reranker-v2-m3 hoặc Qwen3-Reranker
❌ Reranking step sau hybrid search
❌ Performance optimization (GPU acceleration)
```

### 4. Graph RAG Auto-Sync ⚠️
**Status:** Manual script only  
**Impact:** Operational risk (easy to forget)  
**Current workflow:**
```bash
python IMport_new_exports.py           # Import documents
python create_semantic_links.py        # ← MUST run manually!
python validate_graph_links.py         # Verify
```
**What's needed:**
```
❌ Database trigger hoặc cron job
❌ Automatic sync after document import
❌ Error handling & notifications
```

---

## 🔥 HIGH PRIORITY ITEMS (P1)

### 1. Monitoring Instrumentation ⚠️
**Status:** Partial (infrastructure ready)  
**What's missing:**
```
❌ FastAPI instrumentation (prometheus-fastapi-instrumentator)
❌ Custom business metrics:
   - RAG pipeline latency (target: <60s)
   - Cache hit rate (target: >60%)
   - Token consumption & LLM costs
   - RAGAS quality scores
❌ Grafana Dashboards (hiện chỉ là tờ giấy trắng):
   - RAG Health Dashboard
   - Search Performance Dashboard
   - User Activity Dashboard
   - System Resources Dashboard
```

### 2. Promtail Log Shipping ❌
**Status:** Config ready, binary failed  
**Issue:** Binary download failed, chưa có centralized logging  
**Impact:** Troubleshooting khó khăn

### 3. RAGAS Automated Evaluation ❌
**Status:** Manual review only (100 test pairs)  
**What's needed:**
```
❌ RAGAS framework setup
❌ Vietnamese legal Q&A test dataset
❌ Automated scoring pipeline (Faithfulness, Relevancy, Correctness)
❌ CI/CD integration
❌ Regression alerts
```

---

## 📊 IMPORTANT DATA INSIGHTS

### Document Processing Status
```
✅ Chunking: 3-7 chunks per doc, ≤800 tokens each, 50-token overlap
✅ Metadata: 95% completeness với 9 mandatory fields
✅ Quality scoring: Accuracy 90-100%
⚠️ Total documents: ~5,000 (target: 100k+)
⚠️ 95% of documents thiếu proper metadata (cần làm sạch)
```

### Search System Performance
```
✅ 6 search engines operational:
   - Semantic (ChromaDB)
   - Keyword (PostgreSQL FTS)
   - BM25 (token-based)
   - Substring (legal codes - có bug với preprocessing)
   - Metadata filtering
   - Hybrid (weighted combination)
⚠️ BM25 failures: Aggressive preprocessing xóa legal codes (e.g., "01/2024/TT-BTC")
❌ Reranker: Chưa có (need P0)
```

### Graph RAG Status
```
✅ Schema: 6 tables deployed (graph_documents, graph_edges, etc.)
✅ Current graph: 42 documents, 507 edges, 100% connected
✅ Average: 24.1 connections per document
⚠️ Edge types: semantic_similarity, hierarchical (parent-child pending)
❌ Auto-sync: Chưa có (must run manual script)
```

---

## 🎨 VIETNAMESE LANGUAGE CONSIDERATIONS

### Critical Rules
1. **Legal Document Codes:** NEVER tokenize/preprocess (preserve "01/2024/TT-BTC")
2. **Article References:** Keep exact format ("Điều 5", "Khoản 2")
3. **Citation Precision:** Absolute accuracy required (legal compliance)
4. **Context Preservation:** Hierarchical chunking để giữ document structure

### Known Issues
```
⚠️ BM25 preprocessing too aggressive → mất legal codes
✅ Semantic search works well for Vietnamese
✅ Full-text search (GIN indexes) effective
✅ Query normalization handles diacritics correctly
```

---

## 📁 KEY FILES & DOCUMENTATION

### Must-Read Documents (in Project Files)
```
📘 ATTECH_RAG_Technical_Specification_v2_0.md  - Full specification
📘 ATTECH_RAG_MASTER_CHECKLIST_v2.md           - Comprehensive status
📗 handover_FR*.md                              - Module-specific handovers
📗 user_manual_graph_rag.md                     - Graph RAG operations
📗 rag_quality_evaluation_guide.md              - Quality assessment
📗 database_user_manual_18Sep.md                - Database operations
```

### Development Philosophy
1. **"RAG Core First"** - Validate core functionality before UI
2. **No Manual Summarization** - Preserves information integrity
3. **Precision Over Recall** - For Vietnamese legal documents
4. **"If it ain't broke, don't fix it"** - Stability over novelty
5. **Comprehensive Evaluation** - 80% accuracy threshold for production

---

## 🛠️ COMMON TASKS & COMMANDS

### Document Import Workflow
```bash
# Full workflow (ALWAYS follow this order)
python IMport_new_exports.py           # Import documents
python create_semantic_links.py        # Generate graph links (CRITICAL!)
python validate_graph_links.py         # Verify integrity
python run_graph_validation.py         # Comprehensive check
```

### Database Operations
```bash
# PostgreSQL connection
psql -h 192.168.1.70 -p 5432 -U kb_admin -d knowledge_base_v2

# Graph RAG database
psql -h 192.168.1.70 -p 15432 -U kb_admin -d chatbotR4

# Quick health check
curl http://192.168.1.70:8000/api/health
curl http://192.168.1.70:8001/health  # Analytics
curl http://192.168.1.70:8002/health  # Admin
```

### Monitoring Access
```bash
# Prometheus metrics
curl http://192.168.1.70:9090

# Grafana (admin/admin)
http://192.168.1.70:3000

# Check service logs
docker logs fr02-postgres
docker logs fr02-chromadb
docker logs fr02-redis
```

---

## 🎯 WHEN RESPONDING TO QUERIES

### Always Consider
1. **Module Context:** Which FR module does this relate to?
2. **Integration Impact:** Affects other modules?
3. **Vietnamese Specifics:** Legal document handling needed?
4. **Production Readiness:** Is this P0/P1/P2?
5. **Current Blockers:** Does this help unblock critical items?

### Preferred Response Style
- **Technical Accuracy:** Use exact field names, table names, API endpoints
- **Vietnamese Terms:** Keep specialized terms in English (e.g., "Embedding Model" not "Mô hình nhúng")
- **Code Examples:** Provide working code snippets when possible
- **Architecture Context:** Reference specific servers/ports/databases
- **Priority Awareness:** Highlight if task is P0 (critical blocker)

### Don't Assume
- **Always check current status** in project knowledge before suggesting new features
- **Verify integration points** - many modules interconnect
- **Consider Vietnamese language** implications for text processing
- **Check if it's already implemented** - refer to handover docs

---

## 🚀 DEVELOPMENT PRIORITIES (Next 8 Weeks)

### Weeks 1-2: Security Foundation 🔴
```
Priority: P0 - CRITICAL BLOCKER
Tasks:
  - JWT authentication implementation
  - RBAC API endpoints (login/register/logout)
  - Permission enforcement trong RAG pipeline
  - User level filtering (5 tiers)
Goal: Unblock production deployment
```

### Week 3: User Experience 🔴
```
Priority: P0 - CRITICAL
Tasks:
  - Chat History API (sessions endpoints)
  - Frontend sidebar implementation
  - Session management logic
  - Feedback API (Like/Dislike)
Goal: Complete user-facing features
```

### Week 4: Quality Improvements 🔴
```
Priority: P0 - CRITICAL
Tasks:
  - Cross-Encoder Reranking (bge-reranker-v2-m3)
  - Graph RAG auto-sync mechanism
  - BM25 preprocessing fix (legal codes)
Goal: +30% accuracy improvement
```

### Weeks 5-6: Observability 🟡
```
Priority: P1 - HIGH
Tasks:
  - FastAPI instrumentation
  - 4 Grafana dashboards (RAG Health, Search Perf, User Activity, System)
  - Promtail log shipping fix
  - Alert rules configuration
Goal: Production monitoring readiness
```

### Weeks 7-8: Quality Assurance 🟡
```
Priority: P1 - HIGH
Tasks:
  - RAGAS automated evaluation setup
  - Vietnamese test dataset (100+ Q&A pairs)
  - CI/CD integration
  - Load testing (100+ concurrent users)
  - Security audit (OWASP scan)
Goal: Production-grade quality metrics
```

---

## ⚠️ KNOWN ISSUES & WORKAROUNDS

### Issue 1: Graph RAG Manual Sync
**Problem:** Graph links không tự động update sau import  
**Workaround:** Chạy `create_semantic_links.py` manually  
**Permanent Fix:** P0 task - implement auto-sync (Week 4)

### Issue 2: BM25 Legal Code Failure
**Problem:** Preprocessing xóa mất document codes (e.g., "01/2024/TT-BTC")  
**Impact:** Keyword search không tìm được legal documents  
**Fix:** Modify preprocessing để preserve legal patterns (Week 4)

### Issue 3: Promtail Binary Download
**Problem:** Binary download failed, chưa có centralized logging  
**Workaround:** Direct docker logs access  
**Fix:** Manual binary installation hoặc alternative solution (Week 5)

### Issue 4: Streamlit Filter Logic Bug
**Problem:** Iterative RAG mode áp dụng filters quá aggressive  
**Impact:** Sub-queries không trả về results  
**Workaround:** Dùng Standard RAG mode  
**Fix:** Debug filter inheritance logic

### Issue 5: Cache Invalidation
**Problem:** Cache không tự xóa khi update documents  
**Impact:** Users có thể nhận outdated answers  
**Workaround:** Manual cache clear (redis-cli FLUSHDB)  
**Fix:** Implement cache invalidation logic (P2 - Week 5)

---

## 📞 ESCALATION & SUPPORT

### When to Ask for Clarification
- Module ownership unclear (which FR handles this?)
- Integration points uncertain (affects multiple modules?)
- Vietnamese language processing specifics needed
- Production vs. development environment distinction
- Priority classification unclear (P0 vs P1 vs P2?)

### When to Search Project Knowledge
- Checking implementation status of a feature
- Looking for existing code/scripts
- Verifying database schemas or API endpoints
- Understanding module dependencies
- Finding handover documentation

### When to Suggest Alternatives
- Proposed solution conflicts with "RAG Core First" philosophy
- High complexity for marginal benefit
- Better existing tools/patterns available
- Vietnamese language processing concerns
- Integration complexity outweighs benefits

---

## 🎓 LEARNING RESOURCES & PATTERNS

### Established Patterns (Don't Reinvent)
```
✅ Dual Database Pattern: PostgreSQL (metadata) + ChromaDB (vectors) + Redis (cache)
✅ Async Processing: FastAPI with asyncpg, async ChromaDB client
✅ Vietnamese Chunking: Hierarchical with legal structure preservation
✅ Hybrid Search: Weighted combination of 6 engines
✅ Error Handling: Structured logging with correlation IDs
```

### Anti-Patterns (Avoid)
```
❌ Manual Summarization: Causes irreversible information loss
❌ Aggressive Preprocessing: Breaks legal document codes
❌ Single Search Engine: Vietnamese needs hybrid approach
❌ Synchronous Processing: Blocks on slow operations
❌ Direct LLM Access: Always use RAG context first
```

### Framework Evaluation Criteria
```
Before adopting new frameworks (LangChain, LlamaIndex, etc.):
1. Does it solve a specific problem we have?
2. Can we extract the core technique without full adoption?
3. Impact on system stability?
4. Vietnamese language support?
5. Integration complexity vs. benefits?
```

---

## 🎯 SUCCESS METRICS & TARGETS

### System Performance
```
RAG Accuracy:        ≥80% (Current: ~75%, Need: Reranker)
Response Latency:    <60s (Current: ~45s) ✅
Cache Hit Rate:      >60% (Current: ~65%) ✅
System Uptime:       >99% (Current: ~98%)
Concurrent Users:    100+ (Tested) ✅
```

### Data Quality
```
Metadata Complete:   95%+ (Current: ~95%) ✅
Document Coverage:   100k+ (Current: ~5k) 🔴
Graph Connectivity:  100% (Current: 100%) ✅
Chunk Quality:       >90 (Current: ~90) ✅
```

### User Experience
```
Auth System:         Required (Missing) 🔴
Chat History:        Required (Missing) 🔴
Feedback System:     Required (Missing) 🔴
Mobile Responsive:   Required (Partial) 🟡
```

---

## 💡 QUICK TIPS FOR EFFECTIVE COLLABORATION

### When Writing Code
- Always specify target environment (Dev .70 vs Production .88)
- Include error handling and logging
- Add type hints (Python typing)
- Use async where appropriate (database ops, API calls)
- Comment in English for code, Vietnamese for business logic

### When Designing Features
- Check existing implementations first (search project knowledge)
- Consider Vietnamese language implications
- Validate against 5-tier RBAC requirements
- Plan for 100+ concurrent users
- Document integration points

### When Troubleshooting
- Check logs in docker containers first
- Verify database connections (PostgreSQL, ChromaDB, Redis)
- Test with curl before debugging application code
- Check Graph RAG sync status (common issue!)
- Validate cache state (redis-cli)

---

## 🔗 INTEGRATION QUICK REFERENCE

### FR-04 RAG Pipeline Flow
```
User Query
    ↓
[FR-06 Auth] Authentication & Permission Check (PENDING)
    ↓
[FR-04.1] Retrieval: Hybrid Search (6 engines)
    ↓
[Graph RAG] Graph Context Expansion (507 edges)
    ↓
[FR-04.1] Reranking (PENDING - P0!)
    ↓
[FR-04.2] Synthesis: Context Building
    ↓
[FR-04.3] Generation: LLM Response (GPT-4)
    ↓
[FR-04.4] API Response with Citations
    ↓
[FR-07] Analytics Logging
```

### Data Flow
```
Documents → [FR-03.1] Processing → [FR-03.3] Ingestion
    ↓                                    ↓
Metadata                          Embeddings
    ↓                                    ↓
[FR-02.1] PostgreSQL            [FR-02.1] ChromaDB
    ↓                                    ↓
[Graph RAG] Semantic Links      [FR-04.1] Vector Search
    ↓                                    ↓
        [FR-04] RAG Pipeline
```

---

## 📚 APPENDIX: COMMON QUERIES & ANSWERS

**Q: "Tôi cần deploy code mới, environment nào?"**  
A: Dev environment @ 192.168.1.70, Production @ 192.168.1.88 (GPU). Always test on .70 first.

**Q: "Làm sao kiểm tra Graph RAG có sync chưa?"**  
A: `python validate_graph_links.py`. Nếu outdated, chạy `create_semantic_links.py`.

**Q: "RAG accuracy thấp (~75%), làm gì?"**  
A: P0 task - implement Cross-Encoder Reranking (bge-reranker-v2-m3). Expected +30% improvement.

**Q: "User không thể login?"**  
A: Auth API chưa implement (P0 blocker). Database có, API chưa code.

**Q: "Grafana dashboard trống?"**  
A: Infrastructure có, dashboards chưa tạo. P1 task - create 4 custom dashboards.

**Q: "BM25 không tìm được legal codes?"**  
A: Known issue - preprocessing quá aggressive. Fix: preserve legal document patterns.

**Q: "Import documents xong, graph không update?"**  
A: Must run `create_semantic_links.py` manually. Auto-sync = P0 task Week 4.

**Q: "Cache trả outdated answers?"**  
A: Cache invalidation chưa có. Workaround: `redis-cli FLUSHDB`. Fix = P2 task.

---

**END OF PROJECT INSTRUCTIONS**

*Tài liệu này là source of truth cho tất cả conversations trong project. Khi có cập nhật quan trọng, update document này để maintain accuracy.*

**Next Review:** February 17, 2026  
**Version Control:** Cập nhật weekly hoặc sau major milestones
