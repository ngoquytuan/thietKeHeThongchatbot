Ngày tạo: 11-September-2025

---
Dựa trên thông tin từ tài liệu dự án và **checklist hiện tại** (Done FR01-FR08, testing từng module và tích hợp), tôi đánh giá sơ đồ khối architecture hiện tại và đưa ra **phiên bản cập nhật** phù hợp với trạng thái thực tế của dự án.

## **🔍 ĐÁNH GIÁ SƠ ĐỒ KHỐI HIỆN TẠI**

Sau khi xem xét tài liệu hiện có, sơ đồ khối cần **cập nhật** những điểm sau:

### **❌ Các phần đã lạc hậu:**
1. **Embedding Model**: Đã chuyển từ multiple models sang **Qwen/Qwen3-Embedding-0.6B** (đã test và chọn)
2. **Implementation Status**: Đã hoàn thành FR01-FR08, đang ở giai đoạn testing integration
3. **Database Schema**: Đã nâng cấp lên enhanced metadata v2 với Vietnamese language support
4. **Technology Stack**: Cập nhật các version mới (PostgreSQL 15, ChromaDB 1.0.0, Redis 7)
5. **Deployment Status**: Đã có Docker Compose production-ready và monitoring stack

---

# **📊 SƠ ĐỒ KHỐI KIẾN TRÚC - PHIÊN BẢN CẬP NHẬT 2025**

## **1. 🏗️ KIẾN TRÚC TỔNG QUAN - CẬP NHẬT**

```mermaid
graph TB
    %% Người dùng theo phân cấp
    subgraph "👥 NGƯỜI DÙNG (4 CẤP ĐỘ)"
        Guest[🌐 Guest User<br/>Truy cập công khai]
        Employee[👤 Employee<br/>Nhân viên nội bộ]
        Manager[👨‍💼 Manager<br/>Trưởng phòng]
        Director[🏢 Director<br/>Giám đốc]
        Admin[⚙️ System Admin<br/>Quản trị hệ thống]
    end
    
    %% Load Balancer
    LB[⚖️ Load Balancer<br/>nginx/HAProxy<br/>🟢 PRODUCTION READY]
    
    %% API Gateway với Authentication
    subgraph "🚪 API GATEWAY LAYER"
        Gateway[🌐 API Gateway<br/>Kong/Nginx]
        Auth[🔐 JWT Authentication<br/>FR-06.1 ✅ COMPLETE]
        RateLimit[📊 Rate Limiting<br/>Per User Level]
        RBAC[🛡️ RBAC Authorization<br/>4-Level Hierarchy]
    end
    
    %% Application Services (ĐÃ HOÀN THÀNH)
    subgraph "💼 APPLICATION SERVICES"
        subgraph "🤖 RAG CORE ENGINE - FR-04 ✅"
            QueryProcessor[🔍 Query Processor<br/>Vietnamese NLP]
            Retriever[📚 Document Retriever<br/>Hybrid Search]
            ContextBuilder[🧩 Context Builder<br/>Permission Aware]
            LLMOrchestrator[🎯 LLM Orchestrator<br/>Multi-Model Support]
        end
        
        subgraph "📊 BUSINESS SERVICES"
            UserMgmt[👤 User Management<br/>FR-02.2 ✅ COMPLETE]
            DocMgmt[📄 Document Management<br/>FR-03.1/3.2/3.3 ✅]
            AnalyticsSvc[📈 Analytics Service<br/>FR-07 ✅ COMPLETE]
            SystemMgmt[⚙️ System Management<br/>FR-08 ✅ COMPLETE]
        end
        
        subgraph "🔧 DATA PROCESSING - FR-03 ✅"
            DataIngestion[📥 Data Ingestion<br/>Multi-format Support]
            EmbeddingGen[🔢 Embedding Generator<br/>Qwen3-0.6B Model]
            QualityCheck[✅ Quality Control<br/>Vietnamese Text Analysis]
            ChunkProcessor[✂️ Semantic Chunking<br/>3-7 Chunks Algorithm]
        end
    end
    
    %% Caching Layer
    subgraph "⚡ CACHE LAYER"
        Redis[🔴 Redis Cluster<br/>Session + Query Cache<br/>Version 7]
        EmbedCache[💾 Embedding Cache<br/>Vector Storage Cache]
    end
    
    %% Storage Layer với enhanced schema
    subgraph "🗄️ ENHANCED STORAGE LAYER"
        subgraph "🔢 Vector Storage"
            ChromaDB[🔢 ChromaDB 1.0.0<br/>Qwen Embeddings 1024-dim]
            VectorIndex[📇 FAISS Index<br/>IndexFlatIP Optimized]
        end
        
        subgraph "🗃️ Relational Storage - FR-02.1 v2 ✅"
            PostgreSQL[(🐘 PostgreSQL 15<br/>Enhanced Schema v2<br/>Vietnamese Language Support)]
            ReadReplica[(📖 Read Replica<br/>Load Balancing)]
            BackupDB[(💾 Automated Backup<br/>Point-in-time Recovery)]
        end
        
        subgraph "📁 File Storage"
            ObjectStore[☁️ MinIO S3-Compatible<br/>Document Storage]
            ProcessedFiles[🗂️ Processed Files<br/>Chunked + Embeddings]
        end
        
        subgraph "🔍 Search Engine"
            FullTextIndex[📝 Full-text Search<br/>PostgreSQL + tsvector]
            ElasticSearch[🔍 Elasticsearch<br/>Advanced Search Optional]
        end
    end
    
    %% External Services
    subgraph "🌐 EXTERNAL SERVICES"
        LLMServices[🧠 LLM Services<br/>OpenAI/Claude/Local Models]
        EmbeddingAPI[📡 Embedding API<br/>Qwen Model Endpoint]
        MonitoringExt[📊 External Monitoring<br/>Grafana Cloud Optional]
    end
    
    %% Infrastructure Layer với monitoring
    subgraph "🗄️ INFRASTRUCTURE & MONITORING"
        subgraph "🐳 Container Platform"
            K8s[☸️ Kubernetes<br/>Production Option]
            Docker[🐋 Docker Compose<br/>✅ CURRENT DEPLOYMENT]
        end
        
        subgraph "📊 Monitoring Stack - FR-08 ✅"
            Prometheus[📊 Prometheus<br/>Metrics Collection]
            Grafana[📈 Grafana<br/>Dashboards + Alerts]
            ELKStack[📋 ELK Stack<br/>Centralized Logging]
        end
        
        subgraph "🔒 Security & Backup"
            Vault[🔐 HashiCorp Vault<br/>Secrets Management]
            BackupSvc[💾 Backup Service<br/>Automated Schedules]
        end
    end
    
    %% Presentation Layer
    subgraph "🖥️ PRESENTATION LAYER - FR-05 ✅"
        WebUI[🌐 Web Interface<br/>Next.js 18.x]
        ChatInterface[💬 Chat Interface<br/>Real-time Messaging]
        AdminDashboard[🔧 Admin Dashboard<br/>System Management]
        Analytics[📊 Analytics Dashboard<br/>Streamlit Dashboard]
    end
    
    %% Connections
    Guest --> LB
    Employee --> LB
    Manager --> LB
    Director --> LB
    Admin --> LB
    
    LB --> Gateway
    Gateway --> Auth
    Auth --> RBAC
    RBAC --> RateLimit
    
    RateLimit --> QueryProcessor
    RateLimit --> UserMgmt
    RateLimit --> DocMgmt
    RateLimit --> AnalyticsSvc
    RateLimit --> SystemMgmt
    
    %% RAG Flow
    QueryProcessor --> Retriever
    Retriever --> ChromaDB
    Retriever --> PostgreSQL
    Retriever --> Redis
    
    Retriever --> ContextBuilder
    ContextBuilder --> LLMOrchestrator
    LLMOrchestrator --> LLMServices
    
    %% Data Processing Flow
    DocMgmt --> DataIngestion
    DataIngestion --> ChunkProcessor
    ChunkProcessor --> QualityCheck
    QualityCheck --> EmbeddingGen
    EmbeddingGen --> ChromaDB
    EmbeddingGen --> PostgreSQL
    
    %% Storage connections
    UserMgmt --> PostgreSQL
    DocMgmt --> ObjectStore
    AnalyticsSvc --> PostgreSQL
    SystemMgmt --> PostgreSQL
    
    PostgreSQL --> ReadReplica
    PostgreSQL --> BackupDB
    ChromaDB --> VectorIndex
    
    %% Cache connections
    QueryProcessor -.-> Redis
    Retriever -.-> EmbedCache
    Auth -.-> Redis
    
    %% Monitoring connections
    Prometheus -.-> QueryProcessor
    Prometheus -.-> PostgreSQL
    Prometheus -.-> ChromaDB
    Grafana --> Prometheus
    ELKStack -.-> Gateway
    
    %% External connections
    EmbeddingGen --> EmbeddingAPI
    LLMOrchestrator --> LLMServices
    
    %% UI connections
    WebUI --> Gateway
    ChatInterface --> Gateway
    AdminDashboard --> Gateway
    Analytics --> Gateway
    
    %% Styling
    classDef completed fill:#e8f5e8,stroke:#388e3c,stroke-width:3px
    classDef inProgress fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef userLayer fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef gatewayLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef storageLayer fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef externalLayer fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    classDef infraLayer fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    classDef presentationLayer fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class QueryProcessor,Retriever,ContextBuilder,LLMOrchestrator,UserMgmt,DocMgmt,AnalyticsSvc,SystemMgmt,DataIngestion,EmbeddingGen,QualityCheck,ChunkProcessor,Auth,RBAC completed
    class Gateway,RateLimit,WebUI,ChatInterface,AdminDashboard,Analytics inProgress
    class Guest,Employee,Manager,Director,Admin userLayer
    class Gateway,Auth,RateLimit,RBAC gatewayLayer
    class ChromaDB,VectorIndex,PostgreSQL,ReadReplica,BackupDB,ObjectStore,ProcessedFiles,FullTextIndex storageLayer
    class LLMServices,EmbeddingAPI,MonitoringExt externalLayer
    class K8s,Docker,Prometheus,Grafana,ELKStack,Vault,BackupSvc infraLayer
    class WebUI,ChatInterface,AdminDashboard,Analytics presentationLayer
```

---

## **2. 🎯 TRẠNG THÁI IMPLEMENTATION HIỆN TẠI**

### **✅ ĐÃ HOÀN THÀNH (FR01-FR08)**
1. **FR-01.2**: Enhanced Database System với PostgreSQL 15 + ChromaDB 1.0.0
2. **FR-02.1**: Dual Database Architecture với Vietnamese optimization  
3. **FR-02.2**: Unified Management API
4. **FR-03.1**: Document Processing Tool (Production Ready)
5. **FR-03.2**: Quality Control Service
6. **FR-03.3**: Database Integration Service
7. **FR-04.1**: RAG Core Engine với Hybrid Search
8. **FR-05.1**: Chat Interface
9. **FR-06.1**: Authentication & Authorization (JWT + RBAC)
10. **FR-07**: Analytics & Reporting với Streamlit Dashboard
11. **FR-08**: System Management & Monitoring

### **🔄 ĐANG TESTING & INTEGRATION**
- Integration testing giữa các modules
- Performance optimization
- End-to-end workflow validation
- Security penetration testing

---

## **3. 🛠️ CÔNG NGHỆ ĐÃ CẬP NHẬT**

### **🔢 Embedding & AI Models**
- **Embedding Model**: `Qwen/Qwen3-Embedding-0.6B` (đã test và chọn)
- **Dimension**: 1024 dimensions
- **Performance**: MRR = 0.7812, Hit_Rate@1 = 68.75%
- **Vietnamese Processing**: `pyvi>=0.1.1` + `underthesea`

### **🗄️ Database & Storage**
- **PostgreSQL**: Version 15 với enhanced Vietnamese schema v2
- **ChromaDB**: Version 1.0.0 với Qwen embeddings
- **Redis**: Version 7 cluster mode
- **Backup**: Automated point-in-time recovery

### **🐳 Deployment & Infrastructure**
- **Container**: Docker Compose production-ready
- **Monitoring**: Prometheus + Grafana stack hoàn chỉnh
- **Security**: JWT authentication + 4-level RBAC
- **Logging**: ELK stack với structured logging

---

## **4. 🔄 DATA FLOW CẬP NHẬT**

### **📝 Query Processing Flow:**
```
User Question (4 levels) → JWT Auth + RBAC → 
Query Processor (Vietnamese NLP) → 
Hybrid Retriever (Vector + Full-text) → 
Permission Filter → Context Builder → 
LLM Orchestrator → Response với Citations
```

### **📄 Document Processing Flow:**
```
Upload Document → FR-03.1 Processing Tool → 
Quality Control (FR-03.2) → Semantic Chunking (3-7 chunks) → 
Qwen Embedding Generation → ChromaDB + PostgreSQL (FR-03.3) → 
Full-text Indexing
```

### **📊 Analytics Flow:**
```
User Activities → Search Analytics → User Activity Summary → 
Document Usage Stats → FR-07 Analytics → 
Grafana Dashboard + Streamlit Reports
```

---

## **5. 🎯 ĐIỂM KHÁC BIỆT CHÍNH VỚI PHIÊN BẢN CŨ**

1. **✅ Embedding Model**: Đã chọn Qwen thay vì multiple options
2. **✅ Implementation Status**: 100% complete modules thay vì chỉ thiết kế
3. **✅ Database Schema**: Enhanced v2 với Vietnamese optimization
4. **✅ Monitoring**: Production-ready Prometheus + Grafana thay vì conceptual
5. **✅ Authentication**: Complete JWT + 4-level RBAC implementation
6. **✅ Document Processing**: Breakthrough trong semantic chunking algorithm
7. **✅ Deployment**: Docker Compose production-ready thay vì Kubernetes concept

Sơ đồ khối này phản ánh **trạng thái thực tế** của dự án sau khi hoàn thành FR01-FR08, sẵn sàng cho giai đoạn testing tích hợp và deployment production.
