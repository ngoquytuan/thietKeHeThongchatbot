# ĐẶC TẢ KỸ THUẬT HỆ THỐNG TRỢ LÝ TRI THỨC NỘI BỘ
## VIETNAMESE LEGAL DOCUMENT KNOWLEDGE ASSISTANT SYSTEM

---

**Tên dự án:** Vietnamese Legal Document Knowledge Assistant System  
**Mã dự án:** ATTECH-RAG-KA  
**Tổ chức:** ATTECH - Công ty Kỹ thuật Quản lý Bay (30+ năm kinh nghiệm)  
**Phiên bản:** 2.0  
**Ngày:** 07 tháng 02 năm 2026  
**Trạng thái:** Production Phase 1 Hoàn thành — Phase 2 Đang triển khai  
**Cập nhật từ:** v1.0 (29/01/2026)

---

**LỜI CAM KẾT CHẤT LƯỢNG:**
Tài liệu này được soạn thảo tuân thủ nghiêm ngặt các nguyên tắc không bịa đặt số liệu (Non-Hallucination Rules). Mọi số liệu, metric, và thông số kỹ thuật đều có nguồn gốc từ các tài liệu handover chính thức (FR-01 đến FR-08), kết quả testing thực tế, hoặc được đánh dấu rõ ràng là "TBD - Cần xác định" kèm lý do.

**THAY ĐỔI CHÍNH SO VỚI v1.0:**

| # | Thay đổi | Mô tả | Mục |
|---|----------|-------|-----|
| 1 | ⭐ **Nâng cấp Embedding Model** | Qwen3-Embedding-0.6B → Qwen3-Embedding-4B (32K context, chất lượng cao hơn 15-25%) | §4.3 |
| 2 | 🔴 **Thêm Cross-Encoder Reranking** | Tầng thiếu vắng quan trọng nhất — kỳ vọng cải thiện +33-47% nDCG@10 | §4.4.5 |
| 3 | 🕸️ **Graph Retrieval-Augmented Generation vận hành** | Từ "Planned" → Operational: 42 tài liệu, 507 cạnh, 6 bảng đã triển khai | §4.4.3 |
| 4 | 📊 **Pipeline đánh giá tự động RAGAS** | Thay thế 100 cặp thủ công bằng pipeline tự động liên tục | §4.6 |
| 5 | ⚡ **pgvector trong PostgreSQL** | Bổ sung vector search native trong PostgreSQL — hợp nhất BM25 + vector + RBAC | §5.2 |
| 6 | 🔄 **Large Language Model Gateway (LiteLLM)** | Chuẩn hóa đa nhà cung cấp Large Language Model với semantic caching, failover, cost tracking | §4.5 |
| 7 | 🇻🇳 **Nâng cấp xử lý tiếng Việt** | Fallback 3 tầng, Legal Entity NER mở rộng, bảo vệ mã pháp luật cải tiến | §6 |
| 8 | 📐 **Công thức Hybrid Scoring 3 chiều** | α×semantic + β×keyword + γ×graph (trọng số thích ứng theo loại truy vấn) | §4.4.4 |
| 9 | 🏗️ **Kiến trúc hạ tầng cập nhật** | Phản ánh thực tế production: .70 Debian (13 services) + .88 DietPi (12 services) | §5.1, §10 |
| 10 | 📋 **Loại bỏ mục Ước tính Chi phí** | Tập trung thuần kỹ thuật theo yêu cầu; thay bằng Lộ trình Nâng cấp Kỹ thuật | §11 |

---

## MỤC LỤC

1. [Executive Summary](#1-executive-summary)
2. [Giới thiệu](#2-giới-thiệu)
3. [Yêu cầu Nghiệp vụ](#3-yêu-cầu-nghiệp-vụ)
4. [Yêu cầu Artificial Intelligence/Machine Learning và Kiến trúc Retrieval-Augmented Generation](#4-yêu-cầu-aiml-và-kiến-trúc-rag)
5. [Kiến trúc Kỹ thuật](#5-kiến-trúc-kỹ-thuật)
6. [Đặc điểm Xử lý Tiếng Việt](#6-đặc-điểm-xử-lý-tiếng-việt)
7. [An ninh và Bảo mật](#7-an-ninh-và-bảo-mật)
8. [Yêu cầu Phi chức năng](#8-yêu-cầu-phi-chức-năng)
9. [Kiểm thử và Nghiệm thu](#9-kiểm-thử-và-nghiệm-thu)
10. [Triển khai và Vận hành](#10-triển-khai-và-vận-hành)
11. [Lộ trình Nâng cấp Kỹ thuật](#11-lộ-trình-nâng-cấp-kỹ-thuật)
12. [Ma trận Đáp ứng Yêu cầu](#12-ma-trận-đáp-ứng-yêu-cầu)
13. [Phụ lục](#13-phụ-lục)

---

## 1. EXECUTIVE SUMMARY

### 1.1. Tổng quan Dự án

**Vietnamese Legal Document Knowledge Assistant System** là hệ thống trợ lý tri thức nội bộ sử dụng công nghệ Retrieval-Augmented Generation (RAG) được phát triển cho ATTECH — một công ty kỹ thuật quản lý bay Việt Nam với hơn 30 năm kinh nghiệm trong lĩnh vực Communication, Navigation, Surveillance / Air Traffic Management (CNS/ATM).

Hệ thống được thiết kế đặc biệt để xử lý tài liệu pháp luật tiếng Việt với cấu trúc phân cấp phức tạp và các mã tài liệu đặc thù (ví dụ: 76/2018/NĐ-CP), đồng thời hỗ trợ 400 nhân viên tại 15 phòng ban trong việc truy cập nhanh chóng các tài liệu nội bộ, chính sách, quy trình và hướng dẫn kỹ thuật.

### 1.2. Mục tiêu Chiến lược

**Mục tiêu chính:**
Xây dựng hệ thống chatbot Artificial Intelligence cấp doanh nghiệp được tối ưu hóa cho xử lý tài liệu pháp luật tiếng Việt và quản lý tri thức nội bộ.

**Mục tiêu phụ:**
- Hỗ trợ 100 người dùng đồng thời với hệ thống phân quyền 5 cấp
- Đạt độ chính xác cao trong xử lý ngôn ngữ tiếng Việt (nDCG@10 ≥ 0.85)
- Truy xuất hiệu quả các mã tài liệu pháp luật với Cross-Encoder Reranking
- Hỗ trợ multi-hop reasoning qua Graph Retrieval-Augmented Generation
- Tích hợp liền mạch với hạ tầng hiện có của ATTECH
- Pipeline đánh giá chất lượng tự động hóa liên tục

### 1.3. Các Chỉ số Thành công (KPIs) — v2.0 Cập nhật

| Chỉ số | Mục tiêu v1.0 | Mục tiêu v2.0 | Phương pháp Đo lường |
|--------|---------------|---------------|---------------------|
| **Retrieval nDCG@10** | > 0.85 | **> 0.90** | RAGAS automated pipeline + VN-MTEB benchmark |
| **Retrieval Recall@10** | > 90% | > 90% | Đánh giá trên 100+ cặp query-document |
| **Answer Faithfulness** | > 85% | **> 90%** | RAGAS faithfulness metric (tự động) |
| **Context Precision** | N/A (mới) | **> 0.85** | RAGAS context precision metric |
| **Response Time (p95)** | < 60 giây | **< 45 giây** | Load testing + Prometheus metrics |
| **Reranking Improvement** | N/A (mới) | **+30% nDCG** | A/B test trước/sau khi tích hợp Cross-Encoder |
| **Graph Completeness** | N/A (mới) | **≥ 95%** | graph_edges / expected_edges ratio |
| **Concurrent Users** | 100 users | 100 users | Stress testing, monitoring production |
| **User Satisfaction** | > 4.0/5.0 | > 4.0/5.0 | Post-interaction survey |
| **Cache Hit Rate** | > 60% | **> 70%** | Redis metrics + semantic cache monitoring |

### 1.4. Kiến trúc Tổng thể v2.0

```mermaid
graph TB
    subgraph "PRESENTATION LAYER"
        UI["🖥️ Streamlit Chat UI<br/>Real-time messaging<br/>Auto-suggestions<br/>File upload"]
    end
    
    subgraph "APPLICATION LAYER"
        API["🔌 FastAPI Gateway<br/>JWT Authentication<br/>Rate Limiting<br/>Request Routing"]
        
        subgraph "RAG CORE ENGINE v2.0"
            QueryProc["🔎 Query Processing<br/>Intent Classification<br/>Query Expansion<br/>Legal Code Detection"]
            Retrieval["🔍 FR-04.1 Retrieval<br/>Hybrid Search 3 chiều:<br/>Vector + BM25 + Graph"]
            Reranker["🎯 Cross-Encoder Reranker ⭐NEW<br/>Qwen3-Reranker<br/>+33-47% Accuracy"]
            Synthesis["📋 FR-04.2 Synthesis<br/>Context Assembly<br/>Prompt Generation"]
            Generation["✨ FR-04.3 Generation<br/>LiteLLM Gateway ⭐NEW<br/>Citation & Grounding"]
        end
        
        AuthZ["🛡️ FR-06 Auth & AuthZ<br/>5-tier RBAC<br/>Session Management<br/>Audit Logging"]
        Analytics["📊 FR-07 Analytics<br/>Usage Tracking<br/>RAGAS Quality ⭐NEW<br/>Dashboards"]
        Admin["⚙️ FR-08 Admin Tools<br/>User Management<br/>Document Management<br/>System Config"]
    end
    
    subgraph "DATA LAYER v2.0"
        Postgres[("🐘 PostgreSQL 15<br/>+ pgvector ⭐NEW<br/>Metadata + BM25<br/>+ Vector Search<br/>+ Graph Tables")]
        Chroma[("🔢 ChromaDB 1.0.0<br/>1024-dim Embeddings<br/>Semantic Search<br/>Dev/Prototyping")]
        Redis[("⚡ Redis 7<br/>Query Cache<br/>Semantic Cache ⭐NEW<br/>Session + Rate Limit")]
    end
    
    subgraph "PROCESSING LAYER"
        Ingestion["📥 FR-03.3 Data Ingestion<br/>Vietnamese NLP 3-tier ⭐NEW<br/>Hierarchical Chunking<br/>Embedding Generation"]
        QualityControl["✅ FR-03.2 Quality Control<br/>Document Validation<br/>Metadata Extraction<br/>Duplicate Detection"]
        EvalPipeline["📊 RAGAS Eval Pipeline ⭐NEW<br/>Faithfulness + Relevance<br/>Context Precision<br/>Continuous Monitoring"]
    end
    
    subgraph "AI/ML SERVICES v2.0"
        EmbedModel["🧠 Qwen3-Embedding-4B ⭐UPGRADED<br/>1024-dimensional<br/>32K context window<br/>GPU-accelerated"]
        RerankerModel["🎯 Cross-Encoder ⭐NEW<br/>bge-reranker-v2-m3<br/>hoặc Qwen3-Reranker"]
        LLMGateway["🤖 LiteLLM Gateway ⭐NEW<br/>OpenAI / Anthropic / Local<br/>Semantic Caching<br/>Auto-Failover<br/>Cost Tracking"]
    end
    
    UI --> API
    API --> QueryProc
    QueryProc --> Retrieval
    API --> AuthZ
    Retrieval --> Reranker
    Reranker --> Synthesis
    Synthesis --> Generation
    Generation --> LLMGateway
    
    Retrieval --> Postgres
    Retrieval --> Chroma
    Retrieval --> Redis
    
    API --> Admin
    API --> Analytics
    EvalPipeline --> Analytics
    
    Ingestion --> QualityControl
    QualityControl --> Postgres
    QualityControl --> Chroma
    Ingestion --> EmbedModel
    
    classDef presentation fill:#e3f2fd,stroke:#1976d2
    classDef application fill:#f3e5f5,stroke:#7b1fa2
    classDef data fill:#e8f5e9,stroke:#388e3c
    classDef aiml fill:#fff3e0,stroke:#f57c00
    classDef newFeature fill:#ffebee,stroke:#c62828
    
    class UI presentation
    class API,QueryProc,Retrieval,Reranker,Synthesis,Generation,AuthZ,Analytics,Admin application
    class Postgres,Chroma,Redis data
    class EmbedModel,RerankerModel,LLMGateway aiml
```

### 1.5. Tình trạng Triển khai Hiện tại

**Phase 1 — HOÀN THÀNH (110% completion):**
- ✅ **FR-01:** Embedding Model Selection & Optimization (Qwen3-Embedding-0.6B)
- ✅ **FR-02:** Dual Database System (PostgreSQL + ChromaDB)
- ✅ **FR-03:** Data Ingestion Pipeline & Quality Control
- ✅ **FR-04:** RAG Core Engine (Retrieval, Synthesis, Generation, API)
- ✅ **FR-05:** Chat UI with Interactive Features
- ✅ **FR-06:** Authentication & Authorization (5-tier RBAC)
- ✅ **FR-07:** Analytics & Reporting
- ✅ **FR-08:** Admin & Maintenance Tools

**Phase 2 — ĐANG TRIỂN KHAI (Target: Q1/2026):**
- 🔴 **P0:** Cross-Encoder Reranking integration
- 🔴 **P0:** RAGAS evaluation pipeline setup
- 🟡 **P1:** Embedding upgrade Qwen3 0.6B → 4B
- 🟡 **P1:** Graph Retrieval-Augmented Generation population & API integration
- 🟢 **P2:** pgvector extension & migration
- 🟢 **P2:** LiteLLM Gateway integration

**Phase 3 — LÊN KẾ HOẠCH (Target: Q2/2026):**
- 🔵 Agentic Retrieval-Augmented Generation với LangGraph multi-agent
- 🔵 vietnamese-document-embedding (dual embedding strategy)
- 🔵 Pipeline đánh giá liên tục tự động (weekly runs)

### 1.6. Các Bên liên quan Chính

| Vai trò | Tên | Trách nhiệm |
|---------|-----|-------------|
| **Nhà tài trợ** | Ban Giám đốc ATTECH | Phê duyệt ngân sách, định hướng chiến lược |
| **Product Owner** | Trưởng phòng IT | Ra quyết định sản phẩm, ưu tiên tính năng |
| **Technical Lead** | Tuan | Kiến trúc hệ thống, review kỹ thuật, coordination |
| **Người dùng cuối** | 400 nhân viên (15 phòng ban) | Sử dụng hệ thống hàng ngày |

### 1.7. Timeline

| Phase | Thời gian | Mục tiêu chính | Trạng thái |
|-------|-----------|-----------------|-----------|
| Phase 1 | 08/2025 – 12/2025 | FR-01 → FR-08 hoàn thành | ✅ Done |
| Phase 2 | 01/2026 – 03/2026 | Reranking + Graph RAG + Eval Pipeline | 🔄 In Progress |
| Phase 3 | 04/2026 – 06/2026 | Agentic RAG + Dual Embedding + Continuous Eval | 📋 Planned |

---

## 2. GIỚI THIỆU

### 2.1. Bối cảnh Dự án

#### 2.1.1. Về Tổ chức ATTECH

ATTECH (Air Traffic Equipment & Technology Company) là công ty kỹ thuật quản lý bay hàng đầu Việt Nam với hơn 30 năm kinh nghiệm trong lĩnh vực:
- **CNS/ATM Systems:** Communication, Navigation, Surveillance / Air Traffic Management
- **Airport Lighting:** Hệ thống đèn sân bay LED hiện đại
- **Mechanical Manufacturing:** Sản xuất thiết bị cơ khí chính xác
- **Aviation Services:** Hiệu chuẩn bay, huấn luyện, đào tạo

Với 400 nhân viên tại 15 phòng ban, ATTECH phục vụ các sân bay quốc tế và khu vực trên toàn Việt Nam.

#### 2.1.2. Vấn đề Nghiệp vụ Cần Giải quyết

Nhân viên ATTECH gặp các khó khăn nghiêm trọng trong việc truy cập thông tin nội bộ:

**Vấn đề 1: Khó truy cập Tài liệu Pháp luật** — Cấu trúc phân cấp phức tạp (Nghị định → Chương → Điều → Khoản), mã tài liệu đặc thù không được công cụ tìm kiếm thông thường hỗ trợ. BM25 search fails với legal codes do aggressive preprocessing loại bỏ số.

**Vấn đề 2: Thông tin Phân tán** — Chính sách nội bộ, quy trình, hướng dẫn kỹ thuật nằm rải rác trên nhiều hệ thống và định dạng khác nhau.

**Vấn đề 3: Thiếu Ngữ cảnh Liên kết** — Tìm kiếm truyền thống không thể hiện mối quan hệ giữa các văn bản (văn bản nào thay thế/bổ sung/căn cứ vào văn bản nào).

#### 2.1.3. Giải pháp Đề xuất v2.0

Hệ thống RAG với kiến trúc 3 tầng retrieval (Vector Similarity + BM25 Keyword + Graph Traversal), tích hợp Cross-Encoder Reranking và Large Language Model Gateway thống nhất, được tối ưu hóa chuyên biệt cho tiếng Việt.

### 2.2. Mục tiêu và Phạm vi

#### 2.2.1. Mục tiêu Dự án

**Bắt buộc (Must Have):**
- Tìm kiếm hybrid 3 chiều (semantic + keyword + graph) cho tài liệu pháp luật tiếng Việt
- Cross-Encoder Reranking cải thiện ≥30% nDCG@10
- Hệ thống phân quyền 5 cấp (Guest, Employee, Manager, Director, System_Admin)
- Trích dẫn nguồn chính xác (Điều, Khoản, Trang) với grounding verification
- Pipeline đánh giá chất lượng tự động (RAGAS)
- Graph Retrieval-Augmented Generation cho multi-hop reasoning giữa các văn bản

**Nên có (Should Have):**
- Large Language Model Gateway với semantic caching và auto-failover
- pgvector integration cho unified vector + metadata search
- Vietnamese-specific embedding model (dual embedding strategy)
- Continuous evaluation pipeline chạy tự động hàng tuần

**Có thể có (Could Have):**
- Agentic Retrieval-Augmented Generation với LangGraph multi-agent orchestration
- Graph visualization UI (D3.js / Cytoscape.js)
- Mobile Progressive Web App (PWA)

#### 2.2.2. Phạm vi Dự án

**Trong phạm vi:**
- Xử lý tài liệu pháp luật tiếng Việt (Nghị định, Quyết định, Thông tư)
- Chính sách nội bộ ATTECH, quy trình, hướng dẫn kỹ thuật
- Tài liệu kỹ thuật sản phẩm (CNS/ATM, đèn sân bay, cơ khí)
- Hệ thống nội bộ on-premise cho 400 nhân viên
- Hiện tại: 42 tài liệu, 507 quan hệ graph, ~100 người dùng đồng thời

**Ngoài phạm vi:**
- Dịch vụ public-facing cho khách hàng bên ngoài
- Tích hợp với hệ thống pháp luật quốc gia bên ngoài
- Tạo/soạn thảo tài liệu pháp luật mới
- Real-time collaboration giữa người dùng

#### 2.2.3. Ràng buộc Dự án

| Ràng buộc | Chi tiết |
|-----------|---------|
| **Phần cứng** | NVIDIA RTX 2080 Ti (11GB VRAM), CUDA 11.8, PyTorch 2.7.1+cu118 |
| **Ngôn ngữ** | Python 3.10.11 (bắt buộc cho underthesea, pyvi) |
| **Mã nguồn mở** | Ưu tiên Open Source ($0 license) — Apache 2.0, MIT |
| **On-premise** | Triển khai nội bộ, không sử dụng cloud infrastructure |
| **Hạ tầng phân tán** | Server .70 Debian + Server .88 DietPi |
| **VRAM Budget** | Tổng ~10GB cho Embedding (8GB) + Reranker (2GB) trên RTX 2080 Ti |

### 2.3. Giả định và Loại trừ

#### 2.3.1. Giả định
1. Người dùng có kỹ năng cơ bản sử dụng giao diện tìm kiếm
2. Tài liệu chủ yếu bằng tiếng Việt và tiếng Anh
3. Triển khai on-premise được ưu tiên vì bảo mật dữ liệu
4. GPU available cho embedding generation và reranking
5. Internet connectivity cho Large Language Model API access (có local fallback)
6. PostgreSQL 15 và Redis 7 đã sẵn sàng
7. 100 concurrent user licenses đủ cho nhu cầu hiện tại
8. Tài liệu pháp luật tuân theo định dạng chuẩn Chính phủ Việt Nam
9. Graph Retrieval-Augmented Generation tables đã được triển khai (6 bảng, 29/12/2025)
10. Giấy phép Apache 2.0 / MIT cho tất cả thành phần mới

#### 2.3.2. Loại trừ (Exclusions)
- Fine-tuning Large Language Model models (ưu tiên RAG approach)
- Neo4j / dedicated graph database (dùng PostgreSQL graph tables)
- Milvus / Qdrant (over-engineering cho 42 tài liệu, 100 users)
- Mobile native app (sử dụng responsive web thay thế)
- Real-time document collaboration
- Kubernetes orchestration (Docker Compose đủ cho quy mô hiện tại)

---

## 3. YÊU CẦU NGHIỆP VỤ

> **Ghi chú v2.0:** Phần này giữ nguyên nội dung v1.0 (7 Use Cases + Business Rules). Xem chi tiết trong v1.0 §3.1–§3.2. Dưới đây tóm tắt các Use Case và cập nhật liên quan đến v2.0.

### 3.1. Use Cases Tổng hợp

| UC ID | Tên | Actor | v2.0 Enhancement |
|-------|-----|-------|-----------------|
| UC-001 | Tìm kiếm Tài liệu Pháp luật theo Mã số | Employee+ | ⭐ Graph traversal hiện related/superseding docs |
| UC-002 | Truy vấn Chính sách Nội bộ | Employee+ | ⭐ Reranking cải thiện độ chính xác kết quả |
| UC-003 | Thông tin Kỹ thuật Sản phẩm | Employee+ | Giữ nguyên |
| UC-004 | Truy cập Tài liệu Compliance | Manager+ | ⭐ Multi-hop reasoning qua graph |
| UC-005 | Đánh giá Analytics Hệ thống | Manager+ | ⭐ RAGAS quality metrics trên dashboard |
| UC-006 | Quản lý Người dùng | Admin | Giữ nguyên |
| UC-007 | Upload Tài liệu Hàng loạt | Admin | ⭐ Auto-sync graph_documents + regenerate edges |

### 3.2. Business Rules — v2.0 Bổ sung

**Bổ sung BR-GRAPH-001: Graph Synchronization**
- Khi tài liệu mới được upload, hệ thống PHẢI sync vào `graph_documents` table
- Chạy `create_semantic_links.py` sau mỗi batch import
- Verify graph completeness ≥ 95% (zero isolated nodes)

**Bổ sung BR-RERANK-001: Reranking Quality**
- Tất cả kết quả search PHẢI qua Cross-Encoder Reranking trước khi trả về người dùng
- Reranking timeout: 2 giây — fallback về hybrid ranking nếu timeout

**Bổ sung BR-EVAL-001: Quality Monitoring**
- RAGAS evaluation pipeline PHẢI chạy tối thiểu 1 lần/tuần
- Alert nếu nDCG@10 giảm > 5% so với baseline

---

## 4. YÊU CẦU ARTIFICIAL INTELLIGENCE/MACHINE LEARNING VÀ KIẾN TRÚC RETRIEVAL-AUGMENTED GENERATION

### 4.1. Tổng quan về Retrieval-Augmented Generation (RAG)

**Định nghĩa:**
Retrieval-Augmented Generation (RAG) là kỹ thuật kết hợp tìm kiếm thông tin (Information Retrieval) với mô hình ngôn ngữ lớn (Large Language Model) để sinh ra câu trả lời chính xác, có nguồn gốc, và giảm thiểu hallucination.

**Lý do Chọn RAG thay vì Fine-tuning:**
1. **Cập nhật Dữ liệu Dễ dàng:** Thêm documents mới không cần retrain model
2. **Tính Minh bạch:** Có thể truy vết nguồn gốc câu trả lời (citations)
3. **Chi phí Thấp hơn:** Không cần GPU clusters để fine-tune Large Language Models
4. **Linh hoạt:** Có thể switch Large Language Model providers qua LiteLLM Gateway
5. **Kiểm soát Chất lượng:** Quality control tại retrieval stage + reranking stage

**Tiến hóa Kiến trúc RAG tại ATTECH:**

```mermaid
graph LR
    subgraph "v1.0 — Phase 1"
        A1["Bi-Encoder<br/>Vector + BM25"] --> B1["Hybrid Ranking<br/>0.7 sem + 0.3 kw"]
        B1 --> C1["LLM Direct<br/>OpenAI/Anthropic"]
    end
    
    subgraph "v2.0 — Phase 2 ⭐"
        A2["Bi-Encoder<br/>Vector + BM25 + Graph"] --> B2["Cross-Encoder<br/>Reranker ⭐NEW"]
        B2 --> C2["LiteLLM Gateway ⭐NEW<br/>Multi-provider + Cache"]
    end
    
    subgraph "v3.0 — Phase 3"
        A3["Multi-Agent<br/>LangGraph Planning"] --> B3["Specialized<br/>Agent Routing"]
        B3 --> C3["Verified<br/>Generation + Eval"]
    end
    
    A1 -.->|upgrade| A2
    A2 -.->|upgrade| A3
```

### 4.2. RAG Pipeline Architecture v2.0

Hệ thống RAG v2.0 sử dụng **Three-Stage Hybrid Approach** với Reranking:

```mermaid
graph TD
    subgraph "INPUT LAYER"
        Query["👤 User Query"]
    end
    
    subgraph "QUERY PROCESSING"
        QueryAnalysis["🔍 Query Analysis<br/>- Intent classification<br/>- Entity extraction<br/>- Legal code detection"]
        QueryExpansion["📝 Query Expansion<br/>- Synonym dictionary (200+)<br/>- Legal abbreviations<br/>- Vietnamese variants<br/>- Tone-removed variants"]
    end
    
    subgraph "STAGE 1: RETRIEVAL — Parallel Execution ⚡~50ms"
        VectorSearch["🔢 Vector Similarity<br/>ChromaDB + pgvector ⭐<br/>Qwen3-4B Embeddings ⭐<br/>Top 50 results"]
        BM25Search["📄 BM25 Full-Text<br/>PostgreSQL<br/>Legal code preserved<br/>Top 50 results"]
        GraphSearch["🕸️ Graph Traversal ⭐OPERATIONAL<br/>507 edges, 42 documents<br/>Multi-hop reasoning<br/>Confidence decay 0.8^hop"]
    end
    
    subgraph "STAGE 2: FUSION & RERANKING ⭐NEW ~200-400ms"
        HybridFusion["⚖️ Hybrid Fusion<br/>α×semantic + β×keyword + γ×graph<br/>Adaptive weights by intent<br/>Top 100 candidates"]
        CrossEncoder["🎯 Cross-Encoder Reranking ⭐NEW<br/>bge-reranker-v2-m3<br/>hoặc Qwen3-Reranker<br/>Top 10 final results"]
    end
    
    subgraph "STAGE 3: SYNTHESIS & GENERATION"
        ContextAssembly["📋 Context Assembly<br/>Chunk selection + token mgmt<br/>Hierarchy context injection<br/>Max 6500 tokens context"]
        LLMGeneration["🤖 LLM Generation<br/>LiteLLM Gateway ⭐NEW<br/>Citation injection<br/>Grounding verification"]
    end
    
    subgraph "EVALUATION LAYER ⭐NEW"
        RAGASEval["📊 RAGAS Evaluation<br/>Faithfulness + Relevance<br/>Context Precision<br/>Continuous monitoring"]
    end
    
    subgraph "OUTPUT LAYER"
        Response["💬 Final Response<br/>Answer + Citations<br/>+ Related docs<br/>+ Graph connections"]
    end
    
    Query --> QueryAnalysis
    QueryAnalysis --> QueryExpansion
    QueryExpansion --> VectorSearch
    QueryExpansion --> BM25Search
    QueryExpansion --> GraphSearch
    
    VectorSearch --> HybridFusion
    BM25Search --> HybridFusion
    GraphSearch --> HybridFusion
    
    HybridFusion --> CrossEncoder
    CrossEncoder --> ContextAssembly
    ContextAssembly --> LLMGeneration
    LLMGeneration --> Response
    
    LLMGeneration -.-> RAGASEval
    Response -.-> RAGASEval
```

### 4.3. Embedding Model Specification v2.0

#### 4.3.1. Selected Models

**Primary Model (UPGRADED):** Qwen/Qwen3-Embedding-4B ⭐  
**Fallback Model:** Qwen/Qwen3-Embedding-0.6B (hiện tại)  
**Future Addition (Phase 3):** vietnamese-document-embedding (PhoBERT-based)

| Thuộc tính | v1.0 (0.6B) | v2.0 (4B) ⭐ | Delta |
|-----------|------------|------------|-------|
| **Parameters** | 0.6 tỷ | 4 tỷ | +566% |
| **Embedding Dimension** | 1024 | 1024 | Không đổi (tương thích ngược) |
| **Max Context Window** | 8,192 tokens | **32,768 tokens** | +4x |
| **Vietnamese Quality** | Tốt | Rất tốt | +15-25% nDCG ước tính |
| **GPU VRAM** | ~2.2GB | ~8GB | Vẫn fit RTX 2080 Ti (11GB) |
| **Giấy phép** | Apache 2.0 | Apache 2.0 | Không đổi |
| **Inference Speed** | ~0.1s/query | ~0.3s/query | Chấp nhận được |
| **Batch Throughput** | ~100 emb/s | ~30 emb/s | Cần batch optimization |

**Lý do Nâng cấp:**
- ✅ Context window 32K tokens: xử lý toàn bộ Điều/Khoản dài mà không cắt cụt
- ✅ Cùng kiến trúc Qwen3 → migration dễ dàng, ChromaDB collection tương thích dimension
- ✅ Chất lượng embedding tốt hơn đáng kể cho tài liệu pháp luật phức tạp
- ✅ Vẫn fit trong VRAM budget: 8GB model + 2GB reranker = 10GB < 11GB RTX 2080 Ti
- ✅ Apache 2.0, self-hosted

**Kế hoạch Migration:**
```
Phase 2 (Tuần 3-6):
1. Tải Qwen3-Embedding-4B về GPU server
2. Benchmark trên 100 ground truth queries: compare nDCG@10 vs 0.6B
3. Nếu improvement ≥ 10%: re-embed toàn bộ 42 documents
4. Tạo ChromaDB collection mới: knowledge_base_v2 (giữ v1 làm rollback)
5. Cập nhật pgvector table với embeddings mới
6. Smoke test → switch traffic → monitor
```

#### 4.3.2. Embedding Generation Process v2.0

```python
# Pseudocode for embedding generation v2.0
from sentence_transformers import SentenceTransformer
import torch

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(
            'Qwen/Qwen3-Embedding-4B',  # v2.0: upgraded from 0.6B
            device='cuda',
            trust_remote_code=True
        )
        self.dimension = 1024
        self.max_length = 32768  # v2.0: 4x increase from 8192
    
    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate 1024-dimensional embedding for Vietnamese text.
        v2.0: Supports up to 32K tokens context.
        """
        # 1. Preprocess text
        text = unicode_normalize(text, form="NFC")
        text = remove_excessive_whitespace(text)
        
        # 2. Generate embedding with instruction prefix (Qwen3 feature)
        with torch.no_grad():
            embedding = self.model.encode(
                text,
                max_length=self.max_length,
                normalize_embeddings=True,  # L2 normalization for cosine
                show_progress_bar=False
            )
        
        return embedding.tolist()
    
    def generate_batch(self, texts: list[str], batch_size: int = 8) -> list[list[float]]:
        """
        Batch embedding generation.
        v2.0: batch_size=8 cho 4B model trên RTX 2080 Ti (VRAM optimization).
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,  # 8 cho 4B model (vs 16 cho 0.6B)
            max_length=self.max_length,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        return embeddings.tolist()
```

**Performance Metrics (ước tính cho Qwen3-4B trên RTX 2080 Ti):**

| Metric | v1.0 (0.6B) | v2.0 (4B) | Ghi chú |
|--------|------------|-----------|---------|
| Single query latency | ~10ms | ~30ms | Vẫn < 100ms SLA |
| Batch throughput | ~100 emb/s | ~30 emb/s | batch_size=8 |
| GPU VRAM utilized | ~2.2GB | ~8GB | Fit RTX 2080 Ti |
| Re-embedding 42 docs | ~5 phút | ~15 phút | One-time migration |

#### 4.3.3. Dual Embedding Strategy — Phase 3

```mermaid
graph TD
    Q["Truy vấn người dùng"] --> Classify{"Phân loại<br/>Ngôn ngữ & Loại"}
    
    Classify -->|"Tiếng Việt pháp luật"| VN["vietnamese-document-embedding<br/>768-dim, PhoBERT-based<br/>8096 tokens, Matryoshka"]
    Classify -->|"Đa ngôn ngữ / Kỹ thuật"| QW["Qwen3-Embedding-4B<br/>1024-dim, 32K context"]
    
    VN --> Norm["Normalize & Align<br/>Dimension Mapping"]
    QW --> Norm
    Norm --> Merge["Weighted Score Merge"]
    Merge --> Rerank["Cross-Encoder Reranking"]
```

**Ghi chú:** Dual embedding sẽ được triển khai ở Phase 3 sau khi validate Qwen3-4B hoạt động ổn định. vietnamese-document-embedding sử dụng cùng `pyvi` tokenizer mà ATTECH đã tích hợp.

### 4.4. Search Strategy v2.0

#### 4.4.1. Stage 1A: Vector Similarity Search (ChromaDB + pgvector)

**Thay đổi v2.0:** Bổ sung pgvector trong PostgreSQL song song với ChromaDB.

```python
# v2.0: Dual vector search — ChromaDB + pgvector
async def vector_search_v2(
    query_embedding: list[float],
    user_permissions: dict,
    top_k: int = 50,  # v2.0: tăng từ 20 lên 50 (reranker sẽ lọc)
    use_pgvector: bool = True  # v2.0: pgvector primary
) -> list[SearchResult]:
    
    results = []
    
    if use_pgvector:
        # pgvector: unified query với permission filter trong cùng SQL
        pg_results = await pgvector_search(
            query_embedding=query_embedding,
            access_levels=user_permissions["accessible_levels"],
            departments=user_permissions["departments"],
            top_k=top_k
        )
        results.extend(pg_results)
    else:
        # ChromaDB fallback
        chroma_results = chroma_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "access_level": {"$in": user_permissions["accessible_levels"]},
            }
        )
        results.extend(chroma_results)
    
    return results
```

**pgvector Query (v2.0 NEW):**
```sql
-- Unified vector search + BM25 + RBAC trong cùng 1 query
SELECT 
    c.chunk_id,
    c.document_id,
    c.content,
    c.hierarchy_path,
    c.article_number,
    e.embedding <=> query_embedding::vector AS vector_distance,
    1 - (e.embedding <=> query_embedding::vector) AS cosine_similarity
FROM document_chunks_enhanced c
JOIN document_embeddings_v2 e ON e.chunk_id = c.chunk_id
JOIN documents_metadata_v2 d ON d.document_id = c.document_id
WHERE 
    d.access_level = ANY($1)  -- Permission filter
    AND (d.department_owner = ANY($2) OR d.department_owner = 'all_departments')
ORDER BY e.embedding <=> query_embedding::vector ASC
LIMIT 50;
```

**Scoring:**
- **Metric:** Cosine similarity
- **Threshold:** > 0.3 (minimum relevance)
- **v2.0 Change:** Retrieve top-50 (thay vì top-20) để Cross-Encoder reranking có nhiều ứng viên hơn

#### 4.4.2. Stage 1B: BM25 Full-Text Search (PostgreSQL)

**Giữ nguyên kiến trúc v1.0** với các cải tiến:

```sql
-- v2.0: BM25 search với legal code preservation cải tiến
SELECT 
    chunk_id,
    document_id,
    content,
    metadata,
    hierarchy_path,
    ts_rank_cd(
        tsv_content,
        to_tsquery('vietnamese', $1),
        32  -- Cover density ranking
    ) AS bm25_score
FROM document_chunks_enhanced
WHERE 
    tsv_content @@ to_tsquery('vietnamese', $1)
    AND chunk_id IN (
        SELECT chunk_id FROM document_chunks_enhanced c
        JOIN documents_metadata_v2 d ON d.document_id = c.document_id
        WHERE d.access_level = ANY($2)
          AND (d.department_owner = ANY($3) OR d.department_owner = 'all_departments')
    )
ORDER BY bm25_score DESC
LIMIT 50;  -- v2.0: tăng từ 20 lên 50
```

**BM25 Parameters (giữ nguyên v1.0):**
- k1 = 1.5 (term frequency saturation)
- b = 0.75 (length normalization)

#### 4.4.3. Stage 1C: Graph Traversal ⭐ OPERATIONAL (v2.0)

**Thay đổi từ v1.0:** Từ "Phase 2 - Planned" → "Operational" với 42 documents, 507 edges.

**Graph Statistics (thực tế, 31/12/2025):**

| Metric | Giá trị |
|--------|---------|
| Total Documents | 42 |
| Total Edges | 507 |
| Average Connections per Document | 24.1 |
| Max Connections | 35 |
| Min Connections | 10 |
| Isolated Nodes | 0 (100% connected) |

**Edge Types:**

| Loại | Subtype | Số lượng | Confidence | Mô tả |
|------|---------|---------|-----------|-------|
| semantic_similarity | same_category | 226 | 0.7 | Tài liệu cùng danh mục |
| semantic_similarity | shared_keywords | 137 | 0.85 | Chia sẻ ≥2 từ khóa |
| hierarchical | same_level_peers | 144 | 0.6 | Cùng cấp hierarchy |

**Graph Traversal Algorithm:**

```python
async def graph_search_v2(
    seed_document_ids: list[str],  # Từ vector/BM25 results
    max_hops: int = 2,
    confidence_decay: float = 0.8,
    max_results: int = 20
) -> list[GraphResult]:
    """
    Multi-hop graph traversal từ seed documents.
    v2.0: Operational với 507 edges.
    
    Strategy:
    1. Bắt đầu từ documents tìm được qua vector/BM25
    2. Mở rộng qua các edge types:
       - same_category (0.7 confidence)
       - shared_keywords (0.85 confidence)  
       - same_level_peers (0.6 confidence)
    3. Confidence decay: 0.8^(hop_distance)
    4. Trả về enriched context
    """
    
    query = """
    WITH RECURSIVE graph_traversal AS (
        -- Base: seed documents
        SELECT 
            gd.graph_doc_id,
            gd.source_document_id,
            gd.title,
            0 as hop_distance,
            1.0 as accumulated_confidence
        FROM graph_documents gd
        WHERE gd.source_document_id = ANY($1)
        
        UNION ALL
        
        -- Recursive: follow edges
        SELECT 
            gd2.graph_doc_id,
            gd2.source_document_id,
            gd2.title,
            gt.hop_distance + 1,
            gt.accumulated_confidence * ge.confidence * $2  -- decay
        FROM graph_traversal gt
        JOIN graph_edges ge ON ge.source_graph_doc_id = gt.graph_doc_id
        JOIN graph_documents gd2 ON gd2.graph_doc_id = ge.target_graph_doc_id
        WHERE 
            gt.hop_distance < $3  -- max_hops
            AND ge.is_active = true
            AND gt.accumulated_confidence * ge.confidence * $2 > 0.1  -- minimum threshold
    )
    SELECT DISTINCT ON (source_document_id)
        graph_doc_id,
        source_document_id,
        title,
        hop_distance,
        accumulated_confidence
    FROM graph_traversal
    WHERE source_document_id != ALL($1)  -- Exclude seed documents
    ORDER BY source_document_id, accumulated_confidence DESC
    LIMIT $4;
    """
    
    results = await db.fetch(query, seed_document_ids, confidence_decay, max_hops, max_results)
    return [GraphResult(**r) for r in results]
```

**⚠️ QUAN TRỌNG — Graph Link Generation:**

Graph links KHÔNG tự động tạo khi thêm tài liệu mới. Workflow bắt buộc:

```bash
# Sau khi import tài liệu mới:
python IMport_new_exports.py          # Step 1: Import documents
python create_semantic_links.py        # Step 2: CRITICAL - Regenerate graph links
python validate_graph_links.py         # Step 3: Verify (optional)
```

#### 4.4.4. Hybrid Ranking & Fusion v2.0

**Thay đổi chính:** Công thức 3 chiều thích ứng (thay vì 2 chiều cố định).

```python
# v2.0: Adaptive 3-way hybrid scoring
class HybridScoringV2:
    """
    Công thức: final_score = α×semantic + β×keyword + γ×graph
    
    Trọng số thích ứng theo loại truy vấn (intent):
    - specific_document:  α=0.3, β=0.6, γ=0.1  (keyword chủ đạo)
    - how_to_procedure:   α=0.6, β=0.2, γ=0.2  (semantic chủ đạo)
    - comparison:         α=0.4, β=0.2, γ=0.4  (graph quan trọng)
    - general:            α=0.5, β=0.3, γ=0.2  (balanced)
    """
    
    INTENT_WEIGHTS = {
        "specific_document":  {"alpha": 0.3, "beta": 0.6, "gamma": 0.1},
        "how_to_procedure":   {"alpha": 0.6, "beta": 0.2, "gamma": 0.2},
        "what_is_information":{"alpha": 0.5, "beta": 0.3, "gamma": 0.2},
        "comparison":         {"alpha": 0.4, "beta": 0.2, "gamma": 0.4},
        "general":            {"alpha": 0.5, "beta": 0.3, "gamma": 0.2},
    }
    
    def compute_hybrid_score(
        self,
        query_intent: str,
        semantic_score: float,
        keyword_score: float,
        graph_score: float,
        document_id: str,
        seen_documents: set
    ) -> float:
        weights = self.INTENT_WEIGHTS.get(query_intent, self.INTENT_WEIGHTS["general"])
        
        # Weighted combination
        hybrid_score = (
            weights["alpha"] * semantic_score +
            weights["beta"] * keyword_score +
            weights["gamma"] * graph_score
        )
        
        # Diversity penalty: -20% cho duplicate documents
        if document_id in seen_documents:
            hybrid_score *= 0.8
        
        return hybrid_score
```

**So sánh v1.0 vs v2.0:**

| Khía cạnh | v1.0 | v2.0 |
|-----------|------|------|
| Công thức | 0.7×semantic + 0.3×keyword | α×semantic + β×keyword + γ×graph |
| Trọng số | Cố định | Thích ứng theo intent |
| Graph | Không có | ✅ Tích hợp (507 edges) |
| Candidates | Top 20 | Top 100 (cho reranker) |
| Diversity | 0.8× penalty | 0.8× penalty (giữ nguyên) |

#### 4.4.5. Cross-Encoder Reranking ⭐ NEW

**Đây là thay đổi quan trọng nhất trong v2.0.** Theo xu hướng 2026, Cross-Encoder Reranking là kiến trúc mặc định cho production RAG systems, cải thiện 33-47% độ chính xác.

```mermaid
graph LR
    subgraph "BEFORE v1.0"
        Q1["Query"] --> H1["Hybrid Ranking<br/>Top 20"]
        H1 --> L1["LLM<br/>(có thể chứa noise)"]
    end
    
    subgraph "AFTER v2.0 ⭐"
        Q2["Query"] --> H2["Hybrid Fusion<br/>Top 100 candidates<br/>~50ms"]
        H2 --> RE["Cross-Encoder ⭐<br/>Rerank Top 100 → Top 10<br/>~200-400ms"]
        RE --> L2["LLM<br/>(context chính xác hơn)"]
    end
```

**Model Selection:**

| Model | Ưu điểm | Nhược điểm | Phù hợp |
|-------|---------|-----------|---------|
| **bge-reranker-v2-m3** | Nhỏ gọn, multilingual, benchmark tốt | Generic, chưa tối ưu pháp luật VN | ⭐ **Khuyến nghị chính** |
| **Qwen3-Reranker** | Cùng họ Qwen, instruction-aware | Mới, ít benchmark | ⭐ **Thay thế tốt** |
| **Cohere Rerank 3** | Nhanh, API dễ dùng | API-only, cần internet | 🟡 Fallback |

**Implementation:**

```python
from sentence_transformers import CrossEncoder

class RerankerService:
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        self.model = CrossEncoder(
            model_name,
            device='cuda',
            max_length=512  # Đủ cho query + chunk pair
        )
        self.timeout_seconds = 2.0  # Fallback nếu timeout
    
    async def rerank(
        self,
        query: str,
        candidates: list[SearchResult],
        top_k: int = 10
    ) -> list[SearchResult]:
        """
        Cross-Encoder reranking: chấm điểm (query, document) pairs.
        
        Khác biệt vs Bi-Encoder:
        - Bi-Encoder: encode query và document RIÊNG → cosine similarity
        - Cross-Encoder: encode (query, document) CÙNG LÚC → relevance score trực tiếp
        → Chính xác hơn nhưng chậm hơn (O(n) thay vì O(1) retrieval)
        
        Args:
            query: User query text
            candidates: Top-100 results từ hybrid fusion
            top_k: Số kết quả cuối cùng (default 10)
        
        Returns:
            Top-K reranked results
        """
        try:
            # Tạo (query, document) pairs
            pairs = [(query, candidate.content) for candidate in candidates]
            
            # Cross-Encoder scoring
            scores = self.model.predict(
                pairs,
                batch_size=16,  # Fit in VRAM alongside embedding model
                show_progress_bar=False
            )
            
            # Combine reranker score với original hybrid score
            for candidate, reranker_score in zip(candidates, scores):
                candidate.reranker_score = float(reranker_score)
                candidate.final_score = (
                    0.7 * candidate.reranker_score +  # Cross-encoder dominates
                    0.3 * candidate.hybrid_score       # Original score as tiebreaker
                )
            
            # Sort by final_score descending
            candidates.sort(key=lambda x: x.final_score, reverse=True)
            
            return candidates[:top_k]
        
        except TimeoutError:
            # Fallback: trả về hybrid ranking results
            logger.warning("Reranker timeout — falling back to hybrid ranking")
            candidates.sort(key=lambda x: x.hybrid_score, reverse=True)
            return candidates[:top_k]
```

**Expected Impact:**

| Metric | v1.0 (no reranker) | v2.0 (with reranker) | Improvement |
|--------|-------------------|---------------------|------------|
| nDCG@10 | ~0.70 (baseline) | ~0.90 (target) | **+28-30%** |
| MRR | ~0.65 | ~0.85 | **+30%** |
| Recall@10 | 92% | 92% | Không đổi (retrieval stage) |
| Latency | ~50ms retrieval | +200-400ms reranking | Chấp nhận |

#### 4.4.6. Query Understanding và Expansion (Cập nhật)

**Intent Classification (cập nhật để phân phối trọng số hybrid):**

```python
def classify_query_intent(query: str) -> str:
    """
    Classify user query intent.
    v2.0: Kết quả được dùng để điều chỉnh trọng số hybrid scoring.
    """
    # Legal code pattern detection — HIGHEST priority
    if re.search(r'\d+/\d+/(NĐ-CP|QĐ-TTg|TT-[A-Z]+)', query):
        return "specific_document"  # α=0.3, β=0.6, γ=0.1
    
    # Comparison/relationship questions → graph-heavy
    if any(kw in query.lower() for kw in ['so sánh', 'khác nhau', 'liên quan', 'căn cứ', 'thay thế']):
        return "comparison"  # α=0.4, β=0.2, γ=0.4
    
    # How-to questions → semantic-heavy
    if any(kw in query.lower() for kw in ['làm thế nào', 'cách', 'quy trình', 'hướng dẫn']):
        return "how_to_procedure"  # α=0.6, β=0.2, γ=0.2
    
    # What-is questions
    if any(kw in query.lower() for kw in ['là gì', 'có nghĩa', 'định nghĩa']):
        return "what_is_information"  # α=0.5, β=0.3, γ=0.2
    
    return "general"  # α=0.5, β=0.3, γ=0.2
```

### 4.5. Large Language Model Generation Configuration v2.0

#### 4.5.1. LiteLLM Gateway ⭐ NEW

**Thay đổi từ v1.0:** Thay thế custom multi-provider logic bằng LiteLLM Gateway chuẩn hóa.

```mermaid
graph LR
    subgraph "v1.0 — Custom Router"
        App1["FastAPI"] --> R1["Custom Logic<br/>if/else providers"]
        R1 --> OAI1["OpenAI"]
        R1 --> ANT1["Anthropic"]
        R1 --> LOC1["Local"]
    end
    
    subgraph "v2.0 — LiteLLM Gateway ⭐"
        App2["FastAPI"] --> LIT["LiteLLM Proxy<br/>OpenAI-compatible API<br/>+ Semantic Cache<br/>+ Cost Tracking<br/>+ Auto-Failover"]
        LIT --> OAI2["OpenAI GPT-4o"]
        LIT --> ANT2["Claude 3.5 Sonnet"]
        LIT --> LOC2["Local Qwen"]
    end
```

**LiteLLM Configuration:**

```yaml
# litellm_config.yaml
model_list:
  - model_name: "gpt-4o"
    litellm_params:
      model: "openai/gpt-4o"
      api_key: "${OPENAI_API_KEY}"
      timeout: 30
      max_tokens: 2048
      
  - model_name: "claude-sonnet"
    litellm_params:
      model: "anthropic/claude-3-5-sonnet-20241022"
      api_key: "${ANTHROPIC_API_KEY}"
      timeout: 30
      max_tokens: 2048

  - model_name: "qwen-local"
    litellm_params:
      model: "openai/qwen2.5"
      api_base: "http://localhost:11434/v1"
      timeout: 60
      max_tokens: 2048

litellm_settings:
  # Semantic Caching
  cache: true
  cache_params:
    type: "redis"
    host: "192.168.1.70"
    port: 6379
    ttl: 3600  # 1 hour cache
    similarity_threshold: 0.95  # Semantic similarity for cache hit
  
  # Routing Strategy
  router_settings:
    routing_strategy: "latency-based-routing"
    allowed_fails: 2
    cooldown_time: 60
    
  # Fallback Chain
  fallback_models:
    gpt-4o: ["claude-sonnet", "qwen-local"]
    claude-sonnet: ["gpt-4o", "qwen-local"]
    qwen-local: ["gpt-4o"]

  # Cost Tracking
  success_callback: ["prometheus"]
  failure_callback: ["prometheus"]
```

**Lợi ích LiteLLM so với custom router:**

| Feature | v1.0 Custom | v2.0 LiteLLM |
|---------|------------|--------------|
| Provider support | 3 (manual code) | 100+ (built-in) |
| Failover | Manual if/else | Automatic với cooldown |
| Semantic caching | ❌ | ✅ Redis-based, similarity 0.95 |
| Cost tracking | ❌ | ✅ Per-request, per-provider |
| Rate limiting | Manual | Built-in per-model |
| API compatibility | Custom endpoint | OpenAI-compatible (drop-in) |
| Latency routing | ❌ | ✅ Automatic lowest-latency |

#### 4.5.2. Prompt Engineering (Giữ nguyên v1.0)

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

#### 4.5.3. Context Window Management (Cập nhật)

**v2.0 Change:** Tăng context budget nhờ LLM models mới hỗ trợ context window lớn hơn.

**Token Budget Allocation (GPT-4o / Claude 3.5 Sonnet):**
```
System Prompt:      ~500 tokens
User Query:         ~200 tokens (average, including expanded)
Context Chunks:     ~12,000 tokens (v2.0: tăng từ 6,500)
Graph Context:      ~1,000 tokens (v2.0: related documents info)
Response Budget:    ~2,000 tokens (reserve)
-----------------------------------
Total:              ~15,700 tokens (within 128K context)
```

#### 4.5.4. Citation Extraction và Grounding (Giữ nguyên v1.0)

Xem chi tiết trong v1.0 §4.5.4. Không có thay đổi về logic citation/grounding.

### 4.6. Evaluation Framework v2.0 ⭐ MAJOR UPGRADE

#### 4.6.1. RAGAS Automated Evaluation Pipeline ⭐ NEW

**Thay đổi từ v1.0:** Từ 100 cặp đánh giá thủ công → Pipeline tự động hóa liên tục.

```mermaid
graph TD
    subgraph "DATA LAYER"
        GT["Ground Truth Dataset<br/>100+ query-document pairs<br/>+ expected answers"]
        Prod["Production Queries<br/>(sampled daily)"]
    end
    
    subgraph "RAGAS EVALUATION PIPELINE ⭐NEW"
        Collect["Collect Samples<br/>Random 50 queries/week"]
        Run["Run RAG Pipeline<br/>query → retrieval → generation"]
        
        subgraph "RAGAS Metrics"
            Faith["Faithfulness<br/>Claims in answer vs source"]
            Relevance["Answer Relevance<br/>Query-answer semantic sim"]
            CtxPrec["Context Precision<br/>Relevant chunks in top-K"]
            CtxRecall["Context Recall<br/>Ground truth covered"]
        end
        
        Score["Aggregate Scores<br/>Weekly report"]
        Alert["Alert System<br/>If metric drops > 5%"]
    end
    
    subgraph "REPORTING"
        Grafana["Grafana Dashboard<br/>Time-series trends"]
        Report["Weekly Quality Report<br/>Auto-generated"]
    end
    
    GT --> Collect
    Prod --> Collect
    Collect --> Run
    Run --> Faith
    Run --> Relevance
    Run --> CtxPrec
    Run --> CtxRecall
    Faith --> Score
    Relevance --> Score
    CtxPrec --> Score
    CtxRecall --> Score
    Score --> Grafana
    Score --> Alert
    Score --> Report
```

**RAGAS Metrics Definition:**

| Metric | Công thức | Mục tiêu v2.0 | Đo lường |
|--------|-----------|---------------|---------|
| **Faithfulness** | % claims in answer verifiable trong source docs | > 0.90 | RAGAS faithfulness scorer |
| **Answer Relevance** | Cosine sim (query embedding, answer embedding) | > 0.85 | RAGAS answer_relevancy |
| **Context Precision** | % retrieved chunks actually relevant | > 0.85 | RAGAS context_precision |
| **Context Recall** | % ground truth info covered by retrieved chunks | > 0.90 | RAGAS context_recall |
| **nDCG@10** | Normalized Discounted Cumulative Gain | > 0.90 | Custom evaluation script |
| **MRR** | Mean Reciprocal Rank | > 0.80 | Custom evaluation script |

**Implementation:**

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

class RAGASEvaluationPipeline:
    def __init__(self):
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
    
    async def run_weekly_evaluation(self, sample_size: int = 50):
        """
        Run RAGAS evaluation on sampled queries.
        Scheduled: Every Sunday 2:00 AM
        """
        # 1. Sample queries (mix of ground truth + production)
        ground_truth_queries = await self.get_ground_truth_sample(sample_size // 2)
        production_queries = await self.get_production_sample(sample_size // 2)
        
        all_queries = ground_truth_queries + production_queries
        
        # 2. Run RAG pipeline on each query
        results = []
        for query_data in all_queries:
            rag_result = await rag_pipeline.process(query_data["query"])
            results.append({
                "question": query_data["query"],
                "answer": rag_result.answer,
                "contexts": [c.content for c in rag_result.retrieved_chunks],
                "ground_truth": query_data.get("expected_answer", ""),
            })
        
        # 3. Evaluate with RAGAS
        dataset = Dataset.from_list(results)
        scores = evaluate(dataset, metrics=self.metrics)
        
        # 4. Store results
        await self.store_evaluation_results(scores)
        
        # 5. Check alerts
        await self.check_quality_alerts(scores)
        
        return scores
    
    async def check_quality_alerts(self, scores):
        """Alert nếu metric giảm > 5% so với baseline."""
        baseline = await self.get_baseline_scores()
        for metric_name, score in scores.items():
            if baseline.get(metric_name):
                drop = baseline[metric_name] - score
                if drop > 0.05:  # 5% threshold
                    await alert_system.send(
                        severity="WARNING",
                        message=f"RAGAS {metric_name} dropped {drop:.2%}: "
                                f"{baseline[metric_name]:.2f} → {score:.2f}"
                    )
```

#### 4.6.2. VN-MTEB Benchmark (v2.0 NEW)

**Vietnamese Massive Text Embedding Benchmark** (41 datasets, 6 tasks) — baseline cho embedding quality.

```python
# Run VN-MTEB benchmark on current and new embedding model
from mteb import MTEB

def benchmark_embedding_model(model_name: str):
    """
    Benchmark embedding model trên VN-MTEB.
    So sánh Qwen3-0.6B vs Qwen3-4B.
    """
    model = SentenceTransformer(model_name, device='cuda')
    
    # Relevant tasks cho ATTECH
    tasks = [
        "ViRetrieval",        # Document retrieval
        "ViSTS",              # Semantic textual similarity
        "ViClassification",   # Text classification
    ]
    
    evaluation = MTEB(tasks=tasks)
    results = evaluation.run(model, output_folder=f"results/{model_name}")
    
    return results
```

#### 4.6.3. Ground Truth Dataset (Cập nhật)

**Ground Truth Dataset v2.0:**
- **Size:** 100 query-document pairs (maintained from v1.0) + expanding to 200
- **Coverage:**
  - Normal cases: 50% (typical queries)
  - Edge cases: 25% (unusual phrasing, multi-intent, ambiguous)
  - Graph-specific: 15% (multi-hop, relationship queries) ⭐ NEW
  - Adversarial: 10% (prompt injection attempts, nonsensical)

---

## 5. KIẾN TRÚC KỸ THUẬT

### 5.1. Tổng quan Kiến trúc Hệ thống v2.0

ATTECH RAG System v2.0 sử dụng **microservices architecture** với các components được containerized bằng Docker và orchestrated bởi Docker Compose trên hạ tầng phân tán 2 server.

```mermaid
graph TB
    subgraph "CLIENT TIER"
        Browser["🌐 Web Browser<br/>Chrome, Firefox, Edge"]
        Mobile["📱 Mobile Browser<br/>Responsive Design"]
    end
    
    subgraph "PRESENTATION TIER"
        Streamlit["🖥️ Streamlit UI<br/>Port 8501<br/>- Chat interface<br/>- Admin dashboard<br/>- Analytics views<br/>- Graph explorer ⭐NEW"]
    end
    
    subgraph "APPLICATION TIER — API Gateway"
        FastAPI["🔌 FastAPI Server<br/>Port 8000<br/>- Request routing<br/>- JWT validation<br/>- Rate limiting<br/>- CORS handling"]
    end
    
    subgraph "APPLICATION TIER — Core Services"
        subgraph "FR-04 RAG Engine v2.0"
            QueryProc2["🔎 Query Processing<br/>- Intent classification<br/>- Query expansion<br/>- Legal code detection"]
            Retrieval2["🔍 Retrieval Service<br/>- 3-way hybrid search ⭐<br/>- Permission filtering<br/>- Graph traversal ⭐"]
            RerankerSvc["🎯 Reranker Service ⭐NEW<br/>- Cross-Encoder scoring<br/>- Top-100 → Top-10<br/>- 2s timeout + fallback"]
            Synthesis2["📋 Synthesis Service<br/>- Context assembly<br/>- Graph context injection ⭐<br/>- Token management"]
            Generation2["✨ Generation Service<br/>- LiteLLM Gateway ⭐<br/>- Citation extraction<br/>- Grounding check"]
        end
        
        AuthService["🛡️ FR-06 Auth Service<br/>- JWT tokens<br/>- Session management<br/>- RBAC enforcement"]
        
        Analytics2["📊 FR-07 Analytics<br/>- Usage tracking<br/>- RAGAS metrics ⭐<br/>- Quality dashboards"]
        
        AdminService["⚙️ FR-08 Admin<br/>- User management<br/>- Document management<br/>- Graph management ⭐<br/>- System config"]
        
        IngestionPipeline["📥 FR-03 Data Ingestion<br/>- Vietnamese NLP 3-tier ⭐<br/>- Hierarchical chunking<br/>- Embedding generation<br/>- Graph sync ⭐"]
        
        EvalService["📊 Evaluation Service ⭐NEW<br/>- RAGAS pipeline<br/>- VN-MTEB benchmark<br/>- Weekly auto-evaluation"]
    end
    
    subgraph "DATA TIER — Server .70 (Debian)"
        PostgreSQL2[("🐘 PostgreSQL 15<br/>192.168.1.70:15432<br/>+ pgvector extension ⭐<br/>- Metadata + BM25 + Vector<br/>- Graph tables (6) ⭐<br/>- Users + Audit logs")]
        
        ChromaDB2[("🔢 ChromaDB 1.0.0<br/>192.168.1.70:8000<br/>- 1024-dim embeddings<br/>- Semantic search<br/>- HNSW index")]
        
        Redis2[("⚡ Redis 7<br/>192.168.1.70:6379<br/>- Query cache<br/>- Semantic cache ⭐<br/>- Session store<br/>- Rate limiting")]
    end
    
    subgraph "AI/ML TIER — Server .88 (DietPi / GPU)"
        EmbeddingService2["🧠 Qwen3-Embedding-4B ⭐<br/>GPU-accelerated<br/>- 1024-dim vectors<br/>- 32K context ⭐<br/>- Batch processing"]
        
        RerankerModel2["🎯 Cross-Encoder ⭐NEW<br/>bge-reranker-v2-m3<br/>- GPU-accelerated<br/>- ~2GB VRAM"]
        
        LiteLLMProxy["🤖 LiteLLM Proxy ⭐NEW<br/>Port 4000<br/>- OpenAI/Anthropic/Local<br/>- Semantic caching<br/>- Auto-failover<br/>- Cost tracking"]
    end
    
    subgraph "MONITORING TIER"
        Prometheus2["📈 Prometheus<br/>Port 9090<br/>Metrics collection"]
        Grafana2["📊 Grafana<br/>Port 3000<br/>Dashboards"]
        Loki2["📜 Loki<br/>Port 3100<br/>Log aggregation"]
    end
    
    Browser --> Streamlit
    Mobile --> Streamlit
    Streamlit --> FastAPI
    
    FastAPI --> QueryProc2
    QueryProc2 --> Retrieval2
    FastAPI --> AuthService
    FastAPI --> Analytics2
    FastAPI --> AdminService
    
    Retrieval2 --> RerankerSvc
    RerankerSvc --> Synthesis2
    Synthesis2 --> Generation2
    
    Retrieval2 --> PostgreSQL2
    Retrieval2 --> ChromaDB2
    Retrieval2 --> Redis2
    
    AuthService --> PostgreSQL2
    AuthService --> Redis2
    
    Generation2 --> LiteLLMProxy
    
    IngestionPipeline --> EmbeddingService2
    IngestionPipeline --> PostgreSQL2
    IngestionPipeline --> ChromaDB2
    
    RerankerSvc --> RerankerModel2
    EvalService --> Analytics2
    
    FastAPI -.-> Prometheus2
    Prometheus2 --> Grafana2
    FastAPI -.-> Loki2
    
    classDef client fill:#e1f5ff,stroke:#01579b
    classDef presentation fill:#f3e5f5,stroke:#4a148c
    classDef application fill:#e8f5e9,stroke:#1b5e20
    classDef data fill:#fff3e0,stroke:#e65100
    classDef aiml fill:#fce4ec,stroke:#880e4f
    classDef monitoring fill:#f1f8e9,stroke:#33691e
```

### 5.2. Database Architecture v2.0

#### 5.2.1. PostgreSQL Schema (v2.0 Enhanced + pgvector + Graph)

**Connection Parameters:**
```yaml
Host: 192.168.1.70
Port: 15432
Database: chatbotR4
Username: kb_admin
Password: [REDACTED - see key.md]
Connection String: postgresql://kb_admin:********@192.168.1.70:15432/chatbotR4
```

**Extensions Required (v2.0):**
```sql
-- Existing
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- v2.0 NEW: Vector search trong PostgreSQL
CREATE EXTENSION IF NOT EXISTS vector;
```

**Tổng quan Tables v2.0:**

| Nhóm | Table | Mô tả | v2.0 Status |
|------|-------|-------|-------------|
| **Core** | `users` | Quản lý người dùng, 5-tier RBAC | Giữ nguyên |
| **Core** | `documents_metadata_v2` | Metadata tài liệu, JSONB | Giữ nguyên |
| **Core** | `document_chunks_enhanced` | Chunks + BM25 + hierarchy | Giữ nguyên |
| **Core** | `audit_logs` | Audit trail | Giữ nguyên |
| **Core** | `search_analytics` | Search tracking | Giữ nguyên |
| **Vector** | `document_embeddings_v2` ⭐ | pgvector embeddings | **NEW** |
| **Graph** | `graph_documents` ⭐ | Graph nodes (42 docs) | **NEW (deployed)** |
| **Graph** | `graph_edges` ⭐ | Graph edges (507) | **NEW (deployed)** |
| **Graph** | `graph_validation_rules` ⭐ | Validation constraints | **NEW (deployed)** |
| **Graph** | `graph_validation_log` ⭐ | Violation tracking | **NEW (deployed)** |
| **Graph** | `graph_changelog` ⭐ | Graph audit trail | **NEW (deployed)** |
| **Graph** | `graph_templates` ⭐ | Structure templates | **NEW (deployed)** |
| **Eval** | `evaluation_results` ⭐ | RAGAS scores | **NEW** |

> **Ghi chú:** Core tables (users, documents_metadata_v2, document_chunks_enhanced, audit_logs, search_analytics) giữ nguyên schema v1.0. Xem chi tiết trong v1.0 §5.2.1. Dưới đây chỉ trình bày tables MỚI.

**NEW — document_embeddings_v2 (pgvector):**
```sql
-- v2.0: pgvector table cho unified vector + metadata search
CREATE TABLE document_embeddings_v2 (
    id SERIAL PRIMARY KEY,
    chunk_id UUID NOT NULL REFERENCES document_chunks_enhanced(chunk_id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents_metadata_v2(document_id) ON DELETE CASCADE,
    
    -- Vector data
    embedding vector(1024),  -- pgvector type, 1024 dimensions (Qwen3)
    embedding_model VARCHAR(100) DEFAULT 'Qwen/Qwen3-Embedding-4B',
    
    -- Metadata for filtering
    access_level VARCHAR(50),
    department_owner VARCHAR(100),
    document_type VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_chunk_embedding UNIQUE(chunk_id)
);

-- HNSW index cho cosine similarity search
CREATE INDEX idx_embeddings_hnsw ON document_embeddings_v2 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 200);

-- Composite indexes cho filtered search
CREATE INDEX idx_embeddings_access ON document_embeddings_v2(access_level);
CREATE INDEX idx_embeddings_department ON document_embeddings_v2(department_owner);
CREATE INDEX idx_embeddings_document ON document_embeddings_v2(document_id);
```

**NEW — Graph Tables (6 tables, deployed 29/12/2025):**

```sql
-- graph_documents: Document nodes
CREATE TABLE graph_documents (
    graph_doc_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_document_id UUID REFERENCES documents_metadata_v2(document_id),
    
    -- Document info (mirrored)
    law_id VARCHAR(100),
    task_code VARCHAR(100),
    document_number VARCHAR(200),
    title TEXT,
    doc_type VARCHAR(50),
    department VARCHAR(100),
    
    -- Graph properties
    hierarchy_level INTEGER,  -- 1-6 (L0-L5)
    parent_count INTEGER DEFAULT 0,
    child_count INTEGER DEFAULT 0,
    is_root_node BOOLEAN DEFAULT false,
    is_leaf_node BOOLEAN DEFAULT true,
    
    -- Metadata
    tags TEXT[],
    keywords TEXT[],
    category VARCHAR(100),
    has_validation_errors BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_graph_docs_source ON graph_documents(source_document_id);
CREATE INDEX idx_graph_docs_hierarchy ON graph_documents(hierarchy_level);
CREATE INDEX idx_graph_docs_category ON graph_documents(category);
CREATE INDEX idx_graph_docs_tags ON graph_documents USING gin(tags);

-- graph_edges: Document relationships
CREATE TABLE graph_edges (
    edge_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_graph_doc_id UUID NOT NULL REFERENCES graph_documents(graph_doc_id),
    target_graph_doc_id UUID NOT NULL REFERENCES graph_documents(graph_doc_id),
    
    -- Relationship
    relation_type VARCHAR(50) NOT NULL,    -- semantic_similarity, hierarchical
    relation_subtype VARCHAR(50),          -- same_category, shared_keywords, same_level_peers
    confidence FLOAT NOT NULL DEFAULT 0.5, -- 0.0 to 1.0
    edge_weight FLOAT DEFAULT 1.0,
    
    -- Context
    source_task_code VARCHAR(100),
    target_task_code VARCHAR(100),
    level_diff INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_suggested BOOLEAN DEFAULT false,
    verified BOOLEAN DEFAULT false,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_edge UNIQUE(source_graph_doc_id, target_graph_doc_id, relation_type)
);

CREATE INDEX idx_graph_edges_source ON graph_edges(source_graph_doc_id);
CREATE INDEX idx_graph_edges_target ON graph_edges(target_graph_doc_id);
CREATE INDEX idx_graph_edges_relation_type ON graph_edges(relation_type);
CREATE INDEX idx_graph_edges_active ON graph_edges(is_active) WHERE is_active = true;
CREATE INDEX idx_graph_edges_recursive_lookup ON graph_edges(source_graph_doc_id, target_graph_doc_id, relation_type) 
    WHERE is_active = true;
```

**NEW — evaluation_results (RAGAS):**
```sql
-- v2.0: Store RAGAS evaluation results
CREATE TABLE evaluation_results (
    eval_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Evaluation info
    eval_type VARCHAR(50) NOT NULL,   -- 'weekly_ragas', 'benchmark', 'manual'
    eval_date DATE NOT NULL,
    sample_size INTEGER,
    
    -- RAGAS Metrics
    faithfulness FLOAT,
    answer_relevancy FLOAT,
    context_precision FLOAT,
    context_recall FLOAT,
    
    -- Retrieval Metrics
    ndcg_at_10 FLOAT,
    mrr FLOAT,
    recall_at_10 FLOAT,
    
    -- Metadata
    model_config JSONB,    -- embedding model, reranker, LLM used
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_eval_date ON evaluation_results(eval_date DESC);
CREATE INDEX idx_eval_type ON evaluation_results(eval_type);
```

#### 5.2.2. ChromaDB Configuration (Giữ nguyên v1.0 + migration path)

**Connection Parameters:**
```yaml
Host: 192.168.1.70
Port: 8000
API Version: v2
```

**Collection Strategy v2.0:**
```python
# v1.0: Giữ nguyên cho backward compatibility
collection_v1 = {
    "name": "knowledge_base_v1",
    "embedding_model": "Qwen/Qwen3-Embedding-0.6B",
    "embedding_dimension": 1024,
}

# v2.0: Collection mới với Qwen3-4B embeddings
collection_v2 = {
    "name": "knowledge_base_v2",
    "embedding_model": "Qwen/Qwen3-Embedding-4B",
    "embedding_dimension": 1024,  # Same dimension → tương thích
}

# Migration: chạy song song v1 và v2, switch traffic khi verified
```

#### 5.2.3. Redis Configuration (Cập nhật Semantic Cache)

**Data Structures v2.0:**

| Key Pattern | Mô tả | TTL | v2.0 Change |
|-------------|-------|-----|-------------|
| `cache:query:{hash}` | Query result cache | 3600s | Giữ nguyên |
| `cache:semantic:{hash}` ⭐ | LiteLLM semantic cache | 3600s | **NEW** |
| `session:{id}` | Session store | 1800s | Giữ nguyên |
| `ratelimit:{user}:{endpoint}` | Rate limiting | 60s | Giữ nguyên |
| `embedding:{text_hash}` | Embedding cache | 86400s | Giữ nguyên |
| `eval:baseline:{metric}` ⭐ | RAGAS baseline scores | ∞ | **NEW** |

---

## 6. ĐẶC ĐIỂM XỬ LÝ TIẾNG VIỆT v2.0

### 6.1. Tổng quan

> **Ghi chú v2.0:** Phần này giữ nguyên nội dung cốt lõi v1.0 (Unicode Normalization, Legal Code Patterns, Hierarchical Structure, Synonym Expansion, Tone Mark Handling). Dưới đây chỉ trình bày các **cải tiến mới**.

**Cải tiến chính v2.0:**

```mermaid
graph TB
    subgraph "v1.0 Vietnamese Natural Language Processing"
        A1["underthesea"] --> B1["pyvi (backup)"]
        B1 --> C1["Manual fallback"]
    end
    
    subgraph "v2.0 Vietnamese Natural Language Processing ⭐"
        A2["Tier 1: underthesea<br/>State-of-the-art accuracy"] -->|fail| B2["Tier 2: pyvi<br/>Lighter weight, faster"]
        B2 -->|fail| C2["Tier 3: Whitespace split ⭐NEW<br/>Basic but always works"]
        
        D2["Legal Entity NER ⭐NEW<br/>Expanded patterns"]
        E2["Vietnamese Prompt Injection ⭐NEW<br/>Detection patterns"]
    end
```

### 6.2. Vietnamese Text Processing Pipeline v2.0 — 3-Tier Fallback ⭐

```python
class VietnameseNLPService:
    """
    v2.0: 3-tier fallback tokenization.
    Đảm bảo tokenization failure rate → 0%.
    """
    
    def tokenize(self, text: str) -> str:
        """
        3-tier fallback word segmentation.
        
        Tier 1: underthesea (best accuracy)
        Tier 2: pyvi (lighter, faster)
        Tier 3: whitespace split (always works)
        """
        # Tier 1: underthesea
        try:
            from underthesea import word_tokenize
            words = word_tokenize(text)
            if self._validate_tokenization(words, text):
                return " ".join(words)
        except Exception as e:
            logger.warning(f"underthesea failed: {e}")
        
        # Tier 2: pyvi
        try:
            from pyvi import ViTokenizer
            result = ViTokenizer.tokenize(text)
            if result and len(result) > 0:
                return result
        except Exception as e:
            logger.warning(f"pyvi failed: {e}")
        
        # Tier 3: Basic whitespace split (always succeeds)
        logger.warning("Both NLP libraries failed — using whitespace split")
        return text  # Return original text with natural word boundaries
    
    def _validate_tokenization(self, words: list, original: str) -> bool:
        """Validate tokenization didn't corrupt content."""
        if not words:
            return False
        rejoined = "".join(w.replace("_", " ") for w in words)
        # Character count should be similar (allow 10% tolerance)
        if abs(len(rejoined) - len(original.replace(" ", ""))) > len(original) * 0.1:
            return False
        return True
```

### 6.3. Legal Entity NER Mở rộng ⭐ NEW

```python
# v2.0: Expanded legal entity patterns
LEGAL_ENTITY_PATTERNS_V2 = {
    # v1.0 patterns (giữ nguyên)
    "nghi_dinh": r'\d+/\d{4}/NĐ-CP',
    "quyet_dinh": r'\d+/\d{4}/QĐ-TTg',
    "thong_tu": r'\d+/\d{4}/TT-[A-Z]+',
    "dieu": r'Điều\s+\d+',
    "khoan": r'Khoản\s+\d+',
    
    # v2.0 NEW patterns
    "nghi_quyet": r'\d+/\d{4}/NQ-(?:CP|QH)',           # Nghị quyết
    "chi_thi": r'\d+/\d{4}/CT-TTg',                     # Chỉ thị
    "cong_van": r'\d+/[A-Z]+-[A-Z]+',                   # Công văn
    "luat": r'Luật\s+(?:số\s+)?\d+/\d{4}/QH\d+',       # Luật
    
    # Organization entities
    "organization": r'(?:Bộ|Cục|Vụ|Sở|UBND|HĐND)\s+[A-ZĐ][a-zàáạảãâầấậẩẫăằắặẳẵ]+',
    
    # Date patterns in Vietnamese legal docs
    "legal_date": r'ngày\s+\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4}',
    
    # Financial amounts
    "currency": r'\d[\d.,]*\s*(?:đồng|VNĐ|USD|triệu|tỷ)',
}
```

### 6.4. Vietnamese Prompt Injection Detection ⭐ NEW

```python
VIETNAMESE_INJECTION_PATTERNS = [
    # Direct instruction override
    r'(?i)bỏ qua (?:hướng dẫn|lệnh|chỉ dẫn) (?:trước đó|ở trên)',
    r'(?i)quên (?:tất cả|mọi thứ) (?:đã nói|đã hướng dẫn)',
    r'(?i)bây giờ hãy (?:làm|thực hiện) (?:như sau|điều này)',
    
    # Role manipulation
    r'(?i)bạn (?:bây giờ là|hãy đóng vai|giả vờ là)',
    r'(?i)từ giờ bạn sẽ (?:là|hoạt động như)',
    
    # System prompt extraction
    r'(?i)(?:cho tôi|hiển thị|in ra) (?:system prompt|hướng dẫn hệ thống)',
    r'(?i)(?:nội dung|text) (?:trước|phía trên) (?:câu hỏi|tin nhắn) này',
]
```

### 6.5. Common Pitfalls và Lessons Learned (Cập nhật)

> **Ghi chú:** 3 pitfalls từ v1.0 giữ nguyên (BM25 fails on legal codes, Tone mark duplicates, Chunking breaks hierarchy). Bổ sung thêm:

**Pitfall 4 (v2.0): Graph Links Không Tự Động ⭐**

```python
# WRONG: Assume graph auto-updates
upload_document(new_doc)  # Document added to PostgreSQL + ChromaDB
# → graph_documents: NOT updated
# → graph_edges: NOT updated
# → New document is INVISIBLE to Graph RAG!

# CORRECT: Manual sync required
upload_document(new_doc)
sync_document_to_graph(new_doc.document_id)     # Step 2
create_semantic_links()                           # Step 3
validate_graph_links()                            # Step 4 (optional)
```

**Pitfall 5 (v2.0): Reranker VRAM Conflict ⭐**

```python
# WRONG: Load embedding + reranker simultaneously with large batch
embedding_model = load("Qwen3-4B")     # ~8GB VRAM
reranker = load("bge-reranker-v2-m3")  # ~2GB VRAM
# Total: 10GB — barely fits RTX 2080 Ti (11GB)!
# Large batch may cause OOM

# CORRECT: Manage VRAM carefully
embedding_model = load("Qwen3-4B", device='cuda')  # 8GB
reranker = load("bge-reranker-v2-m3", device='cuda')  # 2GB
# Use batch_size=8 for embedding, batch_size=16 for reranker
# Total ~10GB — leaves 1GB headroom
```

---

## 7. AN NINH VÀ BẢO MẬT

> **Ghi chú v2.0:** Phần này giữ nguyên nội dung v1.0 (Authentication, 5-Tier RBAC, Data Protection, Audit Logging, AI-Specific Security). Xem chi tiết trong v1.0 §7.1–§7.6. Dưới đây chỉ trình bày **bổ sung v2.0**.

### 7.1. Tổng quan — Bổ sung v2.0

Hệ thống ATTECH RAG v2.0 bổ sung:
1. **LiteLLM Security:** API key management cho multiple providers
2. **pgvector Access Control:** RBAC tích hợp trong SQL queries
3. **Graph Access Control:** Permission filtering trên graph traversal
4. **Vietnamese Prompt Injection:** Detection patterns mở rộng (§6.4)

### 7.2. LiteLLM Security Configuration ⭐ NEW

```yaml
# litellm_config.yaml — Security section
litellm_settings:
  # API Key Management
  api_key_management:
    rotation_schedule: "monthly"
    storage: "environment_variables"  # Never in code/config files
    
  # Request Sanitization
  request_hooks:
    pre_call:
      - "validate_input_length"      # Max 32K tokens
      - "check_prompt_injection"      # Vietnamese + English patterns
      - "redact_pii"                  # Remove PII before sending to external LLM
    
  # Response Validation
  response_hooks:
    post_call:
      - "validate_grounding"          # Check answer grounded in context
      - "check_data_leakage"          # Ensure no unauthorized data in response
```

### 7.3. Graph Access Control ⭐ NEW

```python
async def graph_search_with_rbac(
    user_permissions: dict,
    seed_document_ids: list[str],
    max_hops: int = 2
) -> list[GraphResult]:
    """
    Graph traversal WITH permission filtering.
    Chỉ trả về documents mà user có quyền truy cập.
    """
    results = await graph_search_v2(seed_document_ids, max_hops)
    
    # Filter by user permissions
    filtered = [
        r for r in results
        if check_document_access(
            r.source_document_id, 
            user_permissions["role"],
            user_permissions["department"]
        )
    ]
    
    return filtered
```

---

## 8. YÊU CẦU PHI CHỨC NĂNG (NFRs) v2.0

### 8.1. Performance Requirements — Cập nhật

| Metric | v1.0 Target | v2.0 Target | Ghi chú |
|--------|------------|------------|---------|
| **Search Response (p50)** | < 2s | < 2s | Giữ nguyên |
| **Search Response (p95)** | < 5s | < 5s | Giữ nguyên |
| **Reranking Latency** ⭐ | N/A | **< 400ms** | Cross-Encoder on GPU |
| **End-to-End (p95)** | < 60s | **< 45s** | LiteLLM caching giúp giảm |
| **Graph Traversal** ⭐ | N/A | **< 200ms** | 2-hop max, indexed |
| **Cache Hit Latency** | < 100ms | < 100ms | Giữ nguyên |
| **Semantic Cache Hit** ⭐ | N/A | **< 50ms** | Redis + cosine sim |
| **RAGAS Eval (weekly)** ⭐ | N/A | **< 30 min** | 50 queries batch |

### 8.2. Resource Utilization v2.0

| Resource | v1.0 | v2.0 | Ghi chú |
|----------|------|------|---------|
| **GPU VRAM** | ~3GB (0.6B) | **~10GB** (4B + reranker) | Fit RTX 2080 Ti (11GB) |
| **CPU Usage (avg)** | < 70% | < 70% | Giữ nguyên |
| **Memory Usage** | < 80% | < 80% | Giữ nguyên |
| **Disk (PostgreSQL)** | ~5GB | **~8GB** (+ pgvector + graph) | Capacity OK |
| **Redis Memory** | ~500MB | **~1GB** (+ semantic cache) | Cần monitor |

### 8.3. Scalability Requirements (Giữ nguyên v1.0)

Xem v1.0 §8.2. Không thay đổi: 100 concurrent users, 1M+ documents target.

### 8.4. Availability & Reliability (Giữ nguyên v1.0)

Xem v1.0 §8.3. SLA 99.5% business hours, RTO < 4h, RPO < 24h.

**Bổ sung Fallback v2.0:**

```python
FALLBACK_STRATEGIES_V2 = {
    # v1.0 strategies giữ nguyên
    "llm_failure": {
        "order": ["litellm_primary", "litellm_fallback", "cached_response", "error_message"],
        "timeout_per_provider": 30
    },
    
    # v2.0 NEW
    "reranker_failure": {
        "fallback_to": "hybrid_ranking_only",  # Skip reranking
        "message": "Using hybrid ranking (reranker unavailable)",
        "timeout": 2  # seconds
    },
    "graph_failure": {
        "fallback_to": "vector_bm25_only",
        "message": "Using vector + keyword search (graph unavailable)"
    },
    "pgvector_failure": {
        "fallback_to": "chromadb_search",
        "message": "Using ChromaDB (pgvector unavailable)"
    },
    "embedding_upgrade_failure": {
        "fallback_to": "qwen3_0.6b",  # Rollback to v1 model
        "message": "Using Qwen3-0.6B (4B model unavailable)"
    }
}
```

### 8.5. Monitoring & Observability v2.0 — Cập nhật Dashboards

**Dashboard 1: System Health (giữ nguyên v1.0)**

**Dashboard 2: RAG Quality v2.0 ⭐ UPGRADED**
```
Panels:
- RAGAS Faithfulness (time series, weekly)          ⭐ NEW
- RAGAS Context Precision (time series, weekly)     ⭐ NEW
- nDCG@10 trend (with/without reranker comparison)  ⭐ NEW
- Reranker latency p50/p95                          ⭐ NEW
- Graph traversal latency                           ⭐ NEW
- User satisfaction score (gauge)
- Search success rate (percentage)
- Citation accuracy (percentage)
```

**Dashboard 3: LiteLLM Gateway ⭐ NEW**
```
Panels:
- Token usage by provider (stacked area)
- Semantic cache hit rate (gauge)
- Provider latency comparison (box plot)
- Failover events (event log)
- Cost per query by provider (line chart)
- Error rate by provider (bar chart)
```

---

## 9. KIỂM THỬ VÀ NGHIỆM THU v2.0

### 9.1. Test Strategy — Cập nhật

> **Ghi chú:** Giữ nguyên 4 test levels từ v1.0 (Unit, Integration, Performance, Security). Bổ sung **Artificial Intelligence-Specific Testing v2.0** và **Continuous Evaluation**.

#### 9.1.1. Test Levels (Giữ nguyên v1.0)
- **Level 1:** Unit Testing (80% coverage, pytest)
- **Level 2:** Integration Testing (API, DB, LLM mocked)
- **Level 3:** Performance Testing (load, stress)
- **Level 4:** Security Testing (auth, authz, pentest)

#### 9.1.2. v2.0 Additions

| Level | Tên | Công cụ | Tần suất | Mục tiêu |
|-------|-----|---------|---------|----------|
| **Level 5** ⭐ | RAGAS Evaluation | RAGAS framework | Hàng tuần | Faithfulness > 0.90 |
| **Level 6** ⭐ | Embedding Benchmark | VN-MTEB | Khi upgrade model | nDCG@10 baseline |
| **Level 7** ⭐ | Reranker A/B Test | Custom script | Khi thay đổi reranker | +30% nDCG improvement |
| **Level 8** ⭐ | Graph Validation | validate_graph_links.py | Sau mỗi import | 0 isolated nodes |

### 9.2. Artificial Intelligence-Specific Testing v2.0

#### 9.2.1. Reranker Quality Testing ⭐ NEW

```python
class RerankerQualityTest:
    """Test Cross-Encoder Reranker effectiveness."""
    
    async def test_reranker_improvement(self, ground_truth_queries: list):
        """
        A/B test: với và không có reranker.
        Kỳ vọng: nDCG@10 improvement ≥ 30%.
        """
        results_without_reranker = []
        results_with_reranker = []
        
        for query_data in ground_truth_queries:
            # Without reranker (v1.0 style)
            hybrid_results = await hybrid_search(query_data["query"], top_k=10)
            ndcg_without = compute_ndcg(hybrid_results, query_data["relevant_docs"])
            results_without_reranker.append(ndcg_without)
            
            # With reranker (v2.0)
            candidates = await hybrid_search(query_data["query"], top_k=100)
            reranked = await reranker.rerank(query_data["query"], candidates, top_k=10)
            ndcg_with = compute_ndcg(reranked, query_data["relevant_docs"])
            results_with_reranker.append(ndcg_with)
        
        avg_without = sum(results_without_reranker) / len(results_without_reranker)
        avg_with = sum(results_with_reranker) / len(results_with_reranker)
        improvement = (avg_with - avg_without) / avg_without * 100
        
        assert improvement >= 30, f"Reranker improvement {improvement:.1f}% < 30% target"
        return {"without": avg_without, "with": avg_with, "improvement_pct": improvement}
```

#### 9.2.2. Graph Retrieval-Augmented Generation Testing ⭐ NEW

```python
class GraphRAGTest:
    """Test Graph RAG integration quality."""
    
    async def test_graph_completeness(self):
        """Graph phải 100% connected, 0 isolated nodes."""
        stats = await get_graph_stats()
        assert stats["isolated_nodes"] == 0, "Graph has isolated nodes!"
        assert stats["total_edges"] >= 500, f"Expected ≥500 edges, got {stats['total_edges']}"
        assert stats["total_documents"] == 42, f"Expected 42 docs, got {stats['total_documents']}"
    
    async def test_multi_hop_query(self):
        """Multi-hop queries phải trả về related documents."""
        # Query about a specific law
        results = await rag_pipeline.search("Nghị định liên quan đến quản lý bay")
        
        # Verify graph-enriched results include related documents
        graph_results = [r for r in results if r.source == "graph"]
        assert len(graph_results) > 0, "No graph results for multi-hop query"
    
    async def test_graph_sync_after_import(self):
        """New documents phải được sync vào graph sau import."""
        # Import test document
        doc_id = await import_document(test_doc)
        
        # Verify graph sync
        graph_doc = await get_graph_document(doc_id)
        assert graph_doc is not None, "Document not synced to graph!"
```

#### 9.2.3. Vietnamese Language Testing (Cập nhật)

```python
class VietnameseNLPTest:
    """v2.0: Test 3-tier fallback tokenization."""
    
    def test_3tier_fallback(self):
        """Tokenization phải luôn thành công qua 3 tiers."""
        test_cases = [
            "Nghị định số 76/2018/NĐ-CP",
            "Hệ thống quản lý bay CNS/ATM",
            "Điều 5, Khoản 2, Điểm a",
            "🔍 emoji + Vietnamese text",  # Edge case
            "",  # Empty string
            "A" * 100000,  # Very long text
        ]
        
        nlp = VietnameseNLPService()
        for text in test_cases:
            result = nlp.tokenize(text)
            assert result is not None, f"Tokenization returned None for: {text[:50]}"
            # No exception should be raised for any input
```

### 9.3. Acceptance Criteria v2.0

#### 9.3.1. Functional Acceptance (Giữ nguyên v1.0)

#### 9.3.2. Non-Functional Acceptance (Giữ nguyên v1.0)

#### 9.3.3. Artificial Intelligence Performance Acceptance v2.0 — Cập nhật

| Metric | v1.0 Criteria | v2.0 Criteria | Checkpoint |
|--------|-------------|-------------|-----------|
| Retrieval nDCG@10 | > 0.85 | **> 0.90** | CP1 |
| Answer Faithfulness | > 85% | **> 90% (RAGAS)** | CP0 |
| Context Precision | N/A | **> 0.85 (RAGAS)** | CP0 |
| Reranker Improvement | N/A | **+30% nDCG** | CP0 |
| Graph Completeness | N/A | **≥ 95%, 0 isolated** | CP1 |
| Response Time (p95) | < 60s | **< 45s** | CP2 |
| 3-tier Tokenization | N/A | **0% failure rate** | CP2 |

---

## 10. TRIỂN KHAI VÀ VẬN HÀNH v2.0

### 10.1. Infrastructure Requirements — Cập nhật thực tế

**Production Setup (Thực tế, Cập nhật 02/2026):**

```mermaid
graph LR
    subgraph "Server .70 — Debian (13 services)"
        PG["PostgreSQL 15<br/>+ pgvector ⭐<br/>Port 15432"]
        CH["ChromaDB 1.0.0<br/>Port 8000"]
        RD["Redis 7<br/>Port 6379"]
        API70["FastAPI Backend<br/>Port 8000"]
        ST["Streamlit UI<br/>Port 8501"]
        PROM["Prometheus<br/>Port 9090"]
        GRAF["Grafana<br/>Port 3000"]
        LOKI["Loki<br/>Port 3100"]
        LITELLM["LiteLLM Proxy ⭐<br/>Port 4000"]
        EVAL["RAGAS Evaluator ⭐<br/>Cron weekly"]
    end
    
    subgraph "Server .88 — DietPi / GPU (12 services)"
        EMB["Qwen3-Embedding-4B ⭐<br/>GPU-accelerated"]
        RERANK["Cross-Encoder ⭐<br/>bge-reranker-v2-m3"]
        ING["Data Ingestion<br/>FR-03.3 Pipeline"]
    end
    
    API70 <-->|"Internal network"| PG
    API70 <-->|"Internal network"| CH
    API70 <-->|"Internal network"| RD
    API70 <-->|"HTTP"| EMB
    API70 <-->|"HTTP"| RERANK
    API70 <-->|"HTTP"| LITELLM
```

**Server .70 — Debian (Application + Data):**
```yaml
Role: API backend, UI, databases, monitoring, LLM gateway
IP: 192.168.1.70
Services: 13 containers (Docker Compose)
Key ports:
  - 15432: PostgreSQL (+ pgvector)
  - 8000: ChromaDB / FastAPI  
  - 6379: Redis
  - 8501: Streamlit UI
  - 4000: LiteLLM Proxy (NEW)
  - 9090: Prometheus
  - 3000: Grafana
  - 3100: Loki
```

**Server .88 — DietPi (GPU Processing):**
```yaml
Role: Embedding generation, reranking, data ingestion
IP: 192.168.1.88
GPU: NVIDIA RTX 2080 Ti (11GB VRAM)
CUDA: 11.8
PyTorch: 2.7.1+cu118
Services: 12 containers
Key services:
  - Qwen3-Embedding-4B service (8GB VRAM)
  - bge-reranker-v2-m3 service (2GB VRAM)
  - Data ingestion pipeline (FR-03.3)
```

### 10.2. Deployment Strategy v2.0

#### 10.2.1. Docker Compose Configuration v2.0

```yaml
# docker-compose.v2.yml — Additions for v2.0
services:
  # --- v2.0 NEW services ---
  
  litellm-proxy:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    volumes:
      - ./litellm_config.yaml:/app/config.yaml
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - redis
    restart: always
    
  reranker-service:
    build: ./services/reranker
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - MODEL_NAME=BAAI/bge-reranker-v2-m3
      - DEVICE=cuda
      - MAX_LENGTH=512
      - BATCH_SIZE=16
    ports:
      - "8002:8002"
    restart: always
  
  ragas-evaluator:
    build: ./services/evaluator
    environment:
      - DATABASE_URL=postgresql://kb_admin:${DB_PASSWORD}@postgres:15432/chatbotR4
      - RAGAS_EVAL_SCHEDULE=0 2 * * 0  # Every Sunday 2AM
      - SAMPLE_SIZE=50
    depends_on:
      - postgres
      - fastapi
    restart: always
    
  # PostgreSQL with pgvector extension
  postgres:
    image: pgvector/pgvector:pg15
    # ... (replaces standard postgres image)
```

#### 10.2.2. Migration Plan v1.0 → v2.0

```mermaid
graph TD
    subgraph "Phase A: Foundation (Week 1)"
        A1["Install pgvector extension<br/>CREATE EXTENSION vector"]
        A2["Deploy graph tables<br/>(already done 29/12/2025)"]
        A3["Create evaluation_results table"]
        A4["Setup LiteLLM Proxy container"]
    end
    
    subgraph "Phase B: Reranker (Week 2)"
        B1["Deploy reranker service<br/>bge-reranker-v2-m3"]
        B2["Run A/B test vs hybrid only"]
        B3["Verify +30% nDCG improvement"]
        B4["Enable reranker in production"]
    end
    
    subgraph "Phase C: Embedding Upgrade (Weeks 3-4)"
        C1["Download Qwen3-Embedding-4B"]
        C2["Benchmark vs 0.6B on ground truth"]
        C3["Re-embed all 42 documents"]
        C4["Create knowledge_base_v2 collection"]
        C5["Populate pgvector table"]
        C6["Switch traffic with rollback plan"]
    end
    
    subgraph "Phase D: Graph + Eval (Weeks 5-6)"
        D1["Populate graph (create_semantic_links.py)"]
        D2["Deploy graph search API endpoint"]
        D3["Setup RAGAS weekly pipeline"]
        D4["Create Grafana dashboards"]
        D5["Run first baseline evaluation"]
    end
    
    A1 --> A2 --> A3 --> A4
    A4 --> B1 --> B2 --> B3 --> B4
    B4 --> C1 --> C2 --> C3 --> C4 --> C5 --> C6
    C6 --> D1 --> D2 --> D3 --> D4 --> D5
```

### 10.3. Operational Procedures (Cập nhật)

#### 10.3.1. Backup & Recovery (Giữ nguyên v1.0 + bổ sung)

**Bổ sung v2.0:**
```yaml
# Graph data backup
Graph Tables:
  Full Backup: Daily at 2:30AM (after PostgreSQL backup)
  Retention: 30 days
  
# pgvector data backup
pgvector Embeddings:
  Full Backup: Weekly (vectors can be regenerated)
  Retention: 4 weeks
  
# Evaluation results
Evaluation Data:
  Backup: With PostgreSQL daily backup
  Retention: Permanent (historical metrics)
  
# LiteLLM config
LiteLLM Config:
  Backup: Git repository
  Encryption: Yes (API keys)
```

#### 10.3.2. Maintenance Checklist v2.0 — Bổ sung

```
Bổ sung cho monthly maintenance:
- [ ] Verify graph integrity (validate_graph_links.py)
- [ ] Check RAGAS metric trends (không giảm > 5%)
- [ ] Review LiteLLM cost tracking
- [ ] Verify reranker VRAM usage < 90%
- [ ] Check pgvector index health (REINDEX nếu cần)
- [ ] Review semantic cache hit rate (target > 70%)
- [ ] Rotate LLM API keys nếu đến hạn
```

---

## 11. LỘ TRÌNH NÂNG CẤP KỸ THUẬT

> **Ghi chú:** Mục này thay thế mục "Ước tính Chi phí" trong v1.0 theo yêu cầu tập trung kỹ thuật.

### 11.1. Tổng quan Lộ trình

```mermaid
gantt
    title Lộ trình Nâng cấp Kỹ thuật v2.0
    dateFormat  YYYY-MM-DD
    
    section 🔴 P0 - Immediate
    Cross-Encoder Reranker        :crit, p0a, 2026-02-10, 14d
    RAGAS Evaluation Pipeline     :crit, p0b, 2026-02-10, 14d
    VN-MTEB Benchmark Baseline    :p0c, 2026-02-17, 7d
    CP0 Checkpoint                :milestone, cp0, 2026-02-24, 0d
    
    section 🟡 P1 - Phase 2 Start
    Graph RAG Population          :p1a, 2026-02-24, 14d
    Embedding Upgrade 0.6B→4B    :p1b, 2026-02-24, 21d
    Graph Search API              :p1c, 2026-03-03, 14d
    Hybrid Scoring 3-way         :p1d, 2026-03-10, 7d
    CP1 Checkpoint                :milestone, cp1, 2026-03-17, 0d
    
    section 🟢 P2 - Phase 2 Mid
    pgvector Installation         :p2a, 2026-03-17, 14d
    LiteLLM Gateway              :p2b, 2026-03-17, 14d
    Vietnamese NLP 3-tier        :p2c, 2026-03-24, 7d
    CP2 Checkpoint                :milestone, cp2, 2026-04-07, 0d
    
    section 🔵 P3 - Phase 3
    Agentic RAG (LangGraph)       :p3a, 2026-04-07, 28d
    Dual Embedding Strategy       :p3b, 2026-04-14, 21d
    Continuous Eval Pipeline      :p3c, 2026-04-21, 14d
    CP3 Checkpoint                :milestone, cp3, 2026-05-05, 0d
```

### 11.2. Chi tiết từng Phase

#### 🔴 P0 — Immediate (Tuần 1-2, Target: 24/02/2026)

| Task | Mô tả | Output | Metric thành công |
|------|--------|--------|-------------------|
| Tích hợp Cross-Encoder | Deploy bge-reranker-v2-m3 hoặc Qwen3-Reranker lên GPU server .88 | Reranker service chạy ổn định | nDCG@10 tăng ≥ 30% vs baseline |
| RAGAS Pipeline Setup | Cài đặt RAGAS, kết nối ground truth dataset, chạy evaluation đầu tiên | Baseline metrics collected | Faithfulness, Relevance, Precision scores |
| VN-MTEB Benchmark | Chạy benchmark Qwen3-0.6B trên VN-MTEB tasks | Baseline embedding quality | Scores documented |

**CP0 Checkpoint Criteria:**
- ✅ Reranker improvement ≥ 30% nDCG@10
- ✅ RAGAS baseline scores collected
- ✅ VN-MTEB baseline documented

#### 🟡 P1 — Phase 2 Start (Tuần 3-6, Target: 17/03/2026)

| Task | Mô tả | Output | Metric thành công |
|------|--------|--------|-------------------|
| Graph RAG Population | Chạy `populate_graph_correct.py` + `create_semantic_links.py` | 42 docs, 507+ edges, 0 isolated nodes | Graph completeness ≥ 95% |
| Embedding Upgrade | Qwen3-0.6B → 4B: benchmark, re-embed, migrate collection | knowledge_base_v2 collection | nDCG@10 ≥ 0.85 (hoặc +15% vs 0.6B) |
| Graph Search API | Implement `/api/v1/graph/search` endpoint | API endpoint operational | Multi-hop query trả về kết quả hợp lệ |
| Hybrid Scoring 3-way | Update scoring formula: α×sem + β×kw + γ×graph | Adaptive weights by intent | Scoring formula active |

**CP1 Checkpoint Criteria:**
- ✅ Graph populated (≥ 500 edges, 0 isolated nodes)
- ✅ Embedding upgraded, overall accuracy ≥ 80%
- ✅ Graph search API returns valid results
- ✅ 3-way hybrid scoring active

#### 🟢 P2 — Phase 2 Mid (Tuần 7-10, Target: 07/04/2026)

| Task | Mô tả | Output | Metric thành công |
|------|--------|--------|-------------------|
| pgvector Installation | Cài extension, migrate embedding data, benchmark | pgvector operational | Query parity với ChromaDB |
| LiteLLM Gateway | Deploy proxy, configure providers, enable caching | LiteLLM proxy on port 4000 | Failover < 5s, cache hit > 40% |
| Vietnamese NLP 3-tier | Implement 3-tier fallback tokenization | VietnameseNLPService v2 | Tokenization failure rate = 0% |

**CP2 Checkpoint Criteria:**
- ✅ pgvector queries có kết quả tương đương ChromaDB
- ✅ LiteLLM failover < 5s
- ✅ Tokenization failure rate = 0%

#### 🔵 P3 — Phase 3 (Tuần 11-14, Target: 05/05/2026)

| Task | Mô tả | Output | Metric thành công |
|------|--------|--------|-------------------|
| Agentic RAG | LangGraph multi-agent cho complex queries | Multi-agent pipeline | Complex queries handled correctly |
| Dual Embedding | Thêm vietnamese-document-embedding cho VN-specific | Dual model routing | VN-specific nDCG improvement |
| Continuous Eval | Automated weekly RAGAS runs + alerts | Grafana dashboard + alerts | Weekly runs, alerts active |

**CP3 Checkpoint Criteria:**
- ✅ Agentic RAG handles complex multi-hop queries
- ✅ Dual embedding shows VN improvement
- ✅ Continuous evaluation runs weekly with alerting

### 11.3. Rủi ro và Giảm thiểu

| Rủi ro | Mức độ | Giảm thiểu |
|--------|--------|-----------|
| Qwen3-4B không fit VRAM cùng Reranker | Trung bình | Chạy tuần tự (load/unload), hoặc giữ 0.6B |
| Graph links stale sau import | Cao | Cron job `create_semantic_links.py` hàng đêm |
| RAGAS evaluation chậm | Thấp | Sample 50 queries thay vì toàn bộ |
| LiteLLM proxy single point of failure | Trung bình | Fallback direct API calls nếu proxy down |
| pgvector migration data loss | Thấp | Giữ ChromaDB song song, không xóa |

---

## 12. MA TRẬN ĐÁP ỨNG YÊU CẦU (COMPLIANCE MATRIX) v2.0

| ID | Requirement | v1.0 Status | v2.0 Status | Evidence |
|----|-------------|------------|------------|----------|
| **FR-01** | Embedding Model Selection | ✅ 0.6B deployed | ⬆️ **Upgrading to 4B** | Benchmark + migration plan |
| **FR-02** | Dual Database System | ✅ PG + ChromaDB | ⬆️ **+ pgvector + Graph** | 6 graph tables deployed |
| **FR-03** | Data Ingestion Pipeline | ✅ Operational | ⬆️ **+ 3-tier NLP + graph sync** | VietnameseNLPService v2 |
| **FR-04.1** | Retrieval Engine | ✅ Hybrid 2-way | ⬆️ **Hybrid 3-way + Reranker** | Cross-Encoder integrated |
| **FR-04.2** | Synthesis Module | ✅ Context assembly | ⬆️ **+ Graph context injection** | Hierarchy + graph context |
| **FR-04.3** | Generation Engine | ✅ Multi-provider | ⬆️ **LiteLLM Gateway** | Semantic caching + failover |
| **FR-04.4** | API Endpoint | ✅ /api/v1/query | ⬆️ **+ /api/v1/graph/search** | Graph search API |
| **FR-05.1** | Chat UI | ✅ Streamlit | ⬆️ **+ Graph explorer** | Graph visualization |
| **FR-06** | Authentication & Authorization | ✅ 5-tier RBAC | ⬆️ **+ Graph access control** | RBAC on graph traversal |
| **FR-07** | Analytics & Reporting | ✅ Dashboards | ⬆️ **+ RAGAS metrics** | Quality dashboards |
| **FR-08** | Admin Tools | ✅ User/Doc mgmt | ⬆️ **+ Graph mgmt** | Graph admin panel |
| **RERANK-001** ⭐ | Cross-Encoder Reranking | ❌ Not implemented | 🔄 **P0 — Implementing** | bge-reranker-v2-m3 |
| **GRAPH-001** ⭐ | Graph RAG Operational | ⏳ Schema only | 🔄 **P1 — Populating** | 507 edges, 42 docs |
| **EVAL-001** ⭐ | Automated Evaluation | ❌ Manual only | 🔄 **P0 — Setting up** | RAGAS pipeline |
| **GATEWAY-001** ⭐ | LLM Gateway | ❌ Custom router | 🔄 **P2 — Integrating** | LiteLLM config |
| **PGVEC-001** ⭐ | pgvector Integration | ❌ Not implemented | 🔄 **P2 — Installing** | Extension + migration |

**Legend:**
- ✅ Fully Met | ⬆️ Upgrading | 🔄 In Progress | ⏳ Pending | ❌ Not Met

---

## 13. PHỤ LỤC

### 13.1. Glossary v2.0 — Bổ sung

| Thuật ngữ | Định nghĩa |
|-----------|-----------|
| **Cross-Encoder** | Mô hình chấm điểm (query, document) cùng lúc cho relevance score chính xác hơn Bi-Encoder |
| **Bi-Encoder** | Mô hình encode query và document RIÊNG thành vectors, dùng cosine similarity để so sánh |
| **RAGAS** | Retrieval Augmented Generation Assessment — framework đánh giá chất lượng RAG tự động |
| **VN-MTEB** | Vietnamese Massive Text Embedding Benchmark — 41 datasets, 6 tasks cho đánh giá embedding |
| **pgvector** | PostgreSQL extension cho vector similarity search |
| **LiteLLM** | Proxy server thống nhất 100+ Large Language Model providers qua OpenAI-compatible API |
| **Semantic Cache** | Cache dựa trên semantic similarity (không chỉ exact match) |
| **Graph Traversal** | Duyệt đồ thị theo các cạnh (edges) để tìm tài liệu liên quan |
| **nDCG@10** | Normalized Discounted Cumulative Gain tại top 10 — metric đánh giá chất lượng ranking |
| **Matryoshka Embedding** | Kỹ thuật cho phép sử dụng embeddings ở nhiều chiều khác nhau |
| **Agentic RAG** | Kiến trúc RAG với Large Language Model-powered agents tự lên kế hoạch truy vấn |
| **LangGraph** | Framework cho multi-agent orchestration dựa trên state machine |
| **(Các thuật ngữ v1.0)** | Xem v1.0 §13.1 |

### 13.2. Technology Stack v2.0 — Tổng hợp

| Layer | Component | Version | Giấy phép | v2.0 Change |
|-------|-----------|---------|-----------|-------------|
| **Runtime** | Python | 3.10.11 | PSF | Giữ nguyên |
| **Framework** | FastAPI | 0.115.9 | MIT | Giữ nguyên |
| **UI** | Streamlit | latest | Apache 2.0 | Giữ nguyên |
| **Embedding** | Qwen3-Embedding | **4B** | Apache 2.0 | ⬆️ 0.6B→4B |
| **Reranker** | bge-reranker-v2-m3 | latest | MIT | ⭐ NEW |
| **Vector DB** | ChromaDB | 1.0.0 | Apache 2.0 | Giữ nguyên |
| **Vector Ext** | pgvector | 0.7+ | PostgreSQL | ⭐ NEW |
| **Relational DB** | PostgreSQL | 15 | PostgreSQL | Giữ nguyên |
| **Cache** | Redis | 7 | BSD | Giữ nguyên |
| **LLM Gateway** | LiteLLM | latest | MIT | ⭐ NEW |
| **GPU** | PyTorch | 2.7.1+cu118 | BSD | Giữ nguyên |
| **GPU Hardware** | NVIDIA RTX 2080 Ti | 11GB VRAM | — | Giữ nguyên |
| **Evaluation** | RAGAS | latest | Apache 2.0 | ⭐ NEW |
| **Vietnamese NLP** | underthesea + pyvi | latest | MIT/GPL | Giữ nguyên |
| **Monitoring** | Prometheus + Grafana | latest | Apache 2.0 | Giữ nguyên |
| **Logging** | Loki | latest | AGPLv3 | Giữ nguyên |
| **Container** | Docker + Compose | latest | Apache 2.0 | Giữ nguyên |

### 13.3. Open Questions & Decisions v2.0

**Đã giải quyết (từ v1.0):**
- [x] Graph database choice → PostgreSQL graph tables (không cần Neo4j)
- [x] Reranker model → bge-reranker-v2-m3 hoặc Qwen3-Reranker
- [x] LLM Gateway → LiteLLM (thay vì custom router)
- [x] Evaluation framework → RAGAS (thay vì manual only)

**Còn mở:**
- [ ] Qwen3-4B VRAM co-location: Chạy song song hay tuần tự với reranker?
- [ ] Graph auto-linking: Implement cron job hay trigger-based?
- [ ] pgvector vs ChromaDB: Phase out ChromaDB hay giữ song song?
- [ ] Agentic RAG scope: Bao nhiêu agent types cho Phase 3?
- [ ] SSO integration timeline với corporate LDAP/AD?
- [ ] Mobile Progressive Web App priority?

### 13.4. References v2.0

**Technology References:**
- Qwen3-Embedding-4B: https://huggingface.co/Qwen/Qwen3-Embedding-4B
- bge-reranker-v2-m3: https://huggingface.co/BAAI/bge-reranker-v2-m3
- Qwen3-Reranker: https://huggingface.co/Qwen/Qwen3-Reranker-0.6B
- pgvector: https://github.com/pgvector/pgvector
- LiteLLM: https://docs.litellm.ai/
- RAGAS: https://docs.ragas.io/
- VN-MTEB: https://huggingface.co/spaces/mteb/leaderboard
- vietnamese-document-embedding: https://huggingface.co/dangvantuan/vietnamese-document-embedding
- LangGraph: https://langchain-ai.github.io/langgraph/

**Project Documents:**
- v1.0 Technical Specification: ATTECH_RAG_Technical_Specification_v1_0_Complete.md
- Technology Survey Report: CAP_NHAT_CONG_NGHE_RAG_2026.md
- FR-01 đến FR-08 Handover Documents: Xem project knowledge
- Graph RAG Summary: GRAPH_RAG_SUMMARY.md
- Graph RAG User Manual: user_manual_graph_rag.md
- Database Backup Schema: backup_schema_31Dec.sql

---

## DOCUMENT APPROVAL

| Vai trò | Tên | Chữ ký | Ngày |
|---------|-----|--------|------|
| **Technical Lead** | Tuan | ___________________ | ___________ |
| **Product Owner** | IT Department Manager | ___________________ | ___________ |
| **Sponsor** | Board of Directors Representative | ___________________ | ___________ |

---

**END OF DOCUMENT v2.0**

**Document Statistics:**
- **Phiên bản:** 2.0 (nâng cấp từ v1.0)
- **Tập trung:** Kỹ thuật thuần túy (đã loại bỏ mục Chi phí)
- **Thay đổi chính:** 10 nâng cấp kỹ thuật (xem bảng đầu document)
- **Tổng Sections:** 13 sections chính
- **Mermaid Diagrams:** 15+ diagrams
- **Code Examples:** 25+ code blocks
- **Tables:** 40+ tables

**Document History:**
- Version 1.0 (29/01/2026): Initial comprehensive specification (FR-01 → FR-08)
- Version 2.0 (07/02/2026): Technical upgrade based on 2026 RAG technology survey — Reranking, Graph RAG, RAGAS, pgvector, LiteLLM, Embedding upgrade, Vietnamese NLP improvements

---

**For questions or clarifications, contact:**
- Technical Lead (Tuan): [email]
- Product Owner: [email]
