
# KIẾN TRÚC GIẢI PHÁP ĐỀ XUẤT
## PROPOSED SOLUTION ARCHITECTURE

```mermaid
graph TB
    %% User Layer
    subgraph "👥 USER LAYER"
        Web[🖥️ Web Browser]
        Mobile[📱 Mobile App]
        API_Client[🔧 API Client]
    end
    
    %% Load Balancer & API Gateway
    LB[⚖️ Load Balancer<br/>nginx/HAProxy]
    
    %% API Gateway
    subgraph "🚪 API GATEWAY LAYER"
        Gateway[🌐 API Gateway<br/>Kong/Nginx]
        Auth[🔐 Authentication<br/>JWT/OAuth2]
        RateLimit[📊 Rate Limiting]
        Logging[📝 Request Logging]
    end
    
    %% Application Layer
    subgraph "💼 APPLICATION LAYER"
        subgraph "🤖 RAG Core Engine"
            QueryProcessor[🔍 Query Processor]
            Retriever[📚 Document Retriever]
            ContextBuilder[🧩 Context Builder]
            LLMOrchestrator[🎯 LLM Orchestrator]
        end
        
        subgraph "📊 Business Logic Services"
            UserMgmt[👤 User Management]
            DocMgmt[📄 Document Management]
            PermissionSvc[🛡️ Permission Service]
            AnalyticsSvc[📈 Analytics Service]
        end
        
        subgraph "🔧 Data Processing Pipeline"
            DataIngestion[📥 Data Ingestion]
            EmbeddingGen[🔢 Embedding Generator]
            QualityCheck[✅ Quality Control]
            ChunkProcessor[✂️ Chunk Processor]
        end
    end
    
    %% Cache Layer
    subgraph "⚡ CACHE LAYER"
        Redis[🔴 Redis<br/>Session & Query Cache]
        Memcached[💾 Memcached<br/>Embedding Cache]
    end
    
    %% Storage Layer
    subgraph "🗄️ STORAGE LAYER"
        subgraph "📊 Vector Storage"
            VectorDB[🔢 Vector Database<br/>Chroma/FAISS/Weaviate]
            EmbeddingIndex[📇 Embedding Index]
        end
        
        subgraph "🗃️ Relational Storage"
            PostgreSQL[(🐘 PostgreSQL<br/>Metadata & Users)]
            ReadReplica[(📖 Read Replica)]
        end
        
        subgraph "📁 File Storage"
            ObjectStore[☁️ Object Storage<br/>MinIO/S3-compatible]
            LocalFS[💽 Local File System]
        end
    end
    
    %% External Services
    subgraph "🌐 EXTERNAL SERVICES"
        LLMService[🧠 LLM Services<br/>OpenAI/Claude/Local LLM]
        EmbeddingAPI[🔢 Embedding API<br/>OpenAI/HuggingFace]
        MonitoringExt[📊 External Monitoring<br/>DataDog/NewRelic]
    end
    
    %% Infrastructure Layer
    subgraph "🏗️ INFRASTRUCTURE LAYER"
        subgraph "🐳 Container Platform"
            Kubernetes[☸️ Kubernetes Cluster]
            Docker[🐋 Docker Containers]
        end
        
        subgraph "📊 Monitoring & Logging"
            Prometheus[📊 Prometheus<br/>Metrics]
            Grafana[📈 Grafana<br/>Dashboards]
            ELKStack[📋 ELK Stack<br/>Logs]
        end
        
        subgraph "🔒 Security & Backup"
            Vault[🔐 HashiCorp Vault<br/>Secrets]
            Backup[💾 Backup Service]
            SecurityScan[🛡️ Security Scanner]
        end
    end
    
    %% Data Flow Connections
    Web --> LB
    Mobile --> LB
    API_Client --> LB
    
    LB --> Gateway
    Gateway --> Auth
    Gateway --> RateLimit
    Gateway --> Logging
    
    Auth --> UserMgmt
    Gateway --> QueryProcessor
    Gateway --> DocMgmt
    
    %% RAG Engine Flow
    QueryProcessor --> Retriever
    Retriever --> VectorDB
    Retriever --> PostgreSQL
    Retriever --> Redis
    
    Retriever --> ContextBuilder
    ContextBuilder --> LLMOrchestrator
    LLMOrchestrator --> LLMService
    
    %% Data Processing Flow
    DocMgmt --> DataIngestion
    DataIngestion --> ChunkProcessor
    ChunkProcessor --> QualityCheck
    QualityCheck --> EmbeddingGen
    EmbeddingGen --> EmbeddingAPI
    EmbeddingGen --> VectorDB
    EmbeddingGen --> PostgreSQL
    
    %% Storage Connections
    UserMgmt --> PostgreSQL
    DocMgmt --> PostgreSQL
    DocMgmt --> ObjectStore
    PermissionSvc --> PostgreSQL
    AnalyticsSvc --> PostgreSQL
    
    PostgreSQL --> ReadReplica
    VectorDB --> EmbeddingIndex
    
    %% Cache Connections
    QueryProcessor -.-> Redis
    Retriever -.-> Memcached
    UserMgmt -.-> Redis
    
    %% Infrastructure Connections
    Kubernetes --> Docker
    Prometheus --> Grafana
    ELKStack --> Logging
    Vault --> Auth
    Backup --> PostgreSQL
    Backup --> VectorDB
    Backup --> ObjectStore
    
    %% Monitoring Connections
    Prometheus -.-> QueryProcessor
    Prometheus -.-> PostgreSQL
    Prometheus -.-> VectorDB
    ELKStack -.-> Gateway
    MonitoringExt -.-> Kubernetes
    
    %% Styling
    classDef userLayer fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef gatewayLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef appLayer fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef cacheLayer fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef storageLayer fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef externalLayer fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    classDef infraLayer fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    
    class Web,Mobile,API_Client userLayer
    class Gateway,Auth,RateLimit,Logging gatewayLayer
    class QueryProcessor,Retriever,ContextBuilder,LLMOrchestrator,UserMgmt,DocMgmt,PermissionSvc,AnalyticsSvc,DataIngestion,EmbeddingGen,QualityCheck,ChunkProcessor appLayer
    class Redis,Memcached cacheLayer
    class VectorDB,EmbeddingIndex,PostgreSQL,ReadReplica,ObjectStore,LocalFS storageLayer
    class LLMService,EmbeddingAPI,MonitoringExt externalLayer
    class Kubernetes,Docker,Prometheus,Grafana,ELKStack,Vault,Backup,SecurityScan infraLayer
```

## 🏗️ **CHI TIẾT KIẾN TRÚC CÁC TẦNG**

### 1. **👥 USER LAYER - Tầng Người dùng**
- **Web Browser**: Giao diện chính cho desktop users
- **Mobile App**: Ứng dụng di động (tùy chọn trong phase 2)
- **API Client**: Cho tích hợp với các hệ thống khác

### 2. **🚪 API GATEWAY LAYER - Tầng Cổng API**
- **Load Balancer**: Phân tải traffic đến multiple instances
- **API Gateway**: Routing, protocol translation, API versioning
- **Authentication**: JWT-based auth với session management
- **Rate Limiting**: Chống DoS, quản lý quota per user
- **Request Logging**: Audit trail cho compliance

### 3. **💼 APPLICATION LAYER - Tầng Ứng dụng**

#### 🤖 **RAG Core Engine** (Trái tim của hệ thống)
- **Query Processor**: Xử lý và normalize câu hỏi người dùng
- **Document Retriever**: Tìm kiếm semantic trong vector space
- **Context Builder**: Xây dựng context từ retrieved documents
- **LLM Orchestrator**: Điều phối LLM calls và response generation

#### 📊 **Business Logic Services**
- **User Management**: CRUD operations cho users và roles
- **Document Management**: Upload, versioning, metadata management
- **Permission Service**: Authorization logic theo RBAC model
- **Analytics Service**: Usage metrics, performance analytics

#### 🔧 **Data Processing Pipeline**
- **Data Ingestion**: Batch và real-time data import
- **Chunk Processor**: Text chunking với configurable strategies
- **Quality Control**: Duplicate detection, content validation
- **Embedding Generator**: Vector generation từ text content

### 4. **⚡ CACHE LAYER - Tầng Cache**
- **Redis**: Session storage, query results cache, user permissions cache
- **Memcached**: High-frequency embedding vectors cache

### 5. **🗄️ STORAGE LAYER - Tầng Lưu trữ**

#### 📊 **Vector Storage**
- **Vector Database**: Primary storage cho embeddings (Chroma/FAISS)
- **Embedding Index**: Optimized indices for fast similarity search

#### 🗃️ **Relational Storage**  
- **PostgreSQL**: Master database cho metadata, users, permissions
- **Read Replica**: Load balancing cho read-heavy operations

#### 📁 **File Storage**
- **Object Storage**: Scalable storage cho original documents
- **Local FS**: Temporary storage cho processing pipeline

### 6. **🌐 EXTERNAL SERVICES - Dịch vụ Ngoài**
- **LLM Services**: OpenAI GPT-4, Claude, hoặc self-hosted models
- **Embedding API**: OpenAI embeddings hoặc HuggingFace models
- **External Monitoring**: Optional cloud monitoring services

### 7. **🏗️ INFRASTRUCTURE LAYER - Tầng Hạ tầng**

#### 🐳 **Container Platform**
- **Kubernetes**: Container orchestration, auto-scaling, service mesh
- **Docker**: Application containerization

#### 📊 **Monitoring & Logging**
- **Prometheus**: Metrics collection và alerting
- **Grafana**: Visualization dashboards
- **ELK Stack**: Centralized logging và log analysis

#### 🔒 **Security & Operations**
- **HashiCorp Vault**: Secrets management
- **Backup Service**: Automated backup cho tất cả storage layers
- **Security Scanner**: Vulnerability scanning cho containers

---

## 🔄 **DATA FLOW CHÍNH**

### **Query Processing Flow:**
```
User Question → API Gateway → Query Processor → 
Document Retriever → Vector DB + Permission Check → 
Context Builder → LLM Orchestrator → External LLM → 
Response với Citations
```

### **Document Ingestion Flow:**
```
Upload Document → Data Ingestion → Quality Check → 
Chunk Processor → Embedding Generator → 
Vector DB + Metadata → PostgreSQL
```

### **Permission Flow:**
```
User Request → Authentication → Permission Service → 
PostgreSQL lookup → Allow/Deny + Filtered Results
```

---

## 🎯 **THIẾT KẾ ĐẶC BIỆT**

### **🔧 Modular & Replaceable Components:**
- Mỗi service có thể thay thế độc lập (loose coupling)
- API-first design cho future integrations
- Configuration-driven behavior

### **📈 Scalability Considerations:**
- Horizontal scaling cho stateless services
- Database partitioning strategies
- Cache layers cho performance optimization

### **🛡️ Security by Design:**
- Multi-layer authentication & authorization
- Encryption at rest và in transit
- Comprehensive audit logging
- Regular security scanning

### **🔄 High Availability:**
- Multiple replicas cho critical services
- Database replication
- Circuit breaker patterns
- Graceful degradation strategies

Kiến trúc này đảm bảo **scalability, maintainability, security** và **performance** theo yêu cầu đã đề ra trong SRS document.

Bạn nói đúng! Tôi sẽ tách thành các diagram từ tổng quát đến chi tiết để dễ theo dõi hơn.

# KIẾN TRÚC HỆ THỐNG - PHÂN CẤP DIAGRAM

## 1. 🌐 **HIGH-LEVEL ARCHITECTURE OVERVIEW**

```mermaid
graph TB
    %% Users
    Users[👥 Users<br/>Guest, Employee, Manager, Director]
    
    %% Main System Layers
    subgraph "🏢 KNOWLEDGE ASSISTANT SYSTEM"
        Presentation[🖥️ PRESENTATION LAYER<br/>Web UI + Mobile]
        
        Gateway[🚪 API GATEWAY LAYER<br/>Auth, Rate Limit, Routing]
        
        Business[💼 BUSINESS LOGIC LAYER<br/>RAG Engine + Services]
        
        Data[🗄️ DATA LAYER<br/>Vector DB + SQL + Cache]
    end
    
    %% External Dependencies  
    External[🌐 EXTERNAL SERVICES<br/>LLM APIs + Monitoring]
    
    %% Infrastructure
    Infrastructure[🏗️ INFRASTRUCTURE<br/>K8s + Docker + Security]
    
    %% Connections
    Users --> Presentation
    Presentation --> Gateway
    Gateway --> Business
    Business --> Data
    Business --> External
    Infrastructure -.-> Presentation
    Infrastructure -.-> Gateway
    Infrastructure -.-> Business
    Infrastructure -.-> Data
    
    %% Styling
    classDef userLayer fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef systemLayer fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef externalLayer fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef infraLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class Users userLayer
    class Presentation,Gateway,Business,Data systemLayer
    class External externalLayer
    class Infrastructure infraLayer
```

---

## 2. 🖥️ **PRESENTATION & API GATEWAY LAYER**

```mermaid
graph TB
    %% Users
    WebUsers[🖥️ Web Users]
    MobileUsers[📱 Mobile Users] 
    APIClients[🔧 API Clients]
    
    %% Load Balancing
    LoadBalancer[⚖️ Load Balancer<br/>nginx/HAProxy]
    
    %% API Gateway Components
    subgraph "🚪 API GATEWAY"
        APIGateway[🌐 API Gateway<br/>Kong/Nginx]
        
        subgraph "Security & Control"
            Auth[🔐 Authentication<br/>JWT + Session]
            RateLimit[📊 Rate Limiting<br/>User/IP based]
            CORS[🔄 CORS Handler]
        end
        
        subgraph "Monitoring & Logging"
            RequestLog[📝 Request Logging]
            Metrics[📊 Metrics Collection]
            HealthCheck[❤️ Health Checks]
        end
    end
    
    %% Backend Services (simplified)
    Backend[💼 Business Logic Services]
    
    %% Flow
    WebUsers --> LoadBalancer
    MobileUsers --> LoadBalancer
    APIClients --> LoadBalancer
    
    LoadBalancer --> APIGateway
    APIGateway --> Auth
    APIGateway --> RateLimit
    APIGateway --> CORS
    
    Auth --> RequestLog
    RateLimit --> Metrics
    APIGateway --> HealthCheck
    
    APIGateway --> Backend
    
    %% Styling
    classDef users fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef gateway fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef security fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef monitoring fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    
    class WebUsers,MobileUsers,APIClients users
    class LoadBalancer,APIGateway gateway
    class Auth,RateLimit,CORS security
    class RequestLog,Metrics,HealthCheck monitoring
```

---

## 3. 🤖 **RAG CORE ENGINE - BUSINESS LOGIC**

```mermaid
graph TB
    %% Input
    UserQuery[❓ User Query + Context]
    
    %% RAG Core Pipeline
    subgraph "🤖 RAG CORE ENGINE"
        subgraph "🔍 Query Processing"
            QueryParser[📝 Query Parser<br/>Intent Detection]
            QueryEnhancer[⚡ Query Enhancer<br/>Expansion + Rewrite]
        end
        
        subgraph "📚 Document Retrieval"
            SemanticSearch[🔍 Semantic Search<br/>Vector Similarity]
            KeywordSearch[🔎 Keyword Search<br/>BM25/Elasticsearch]
            HybridRanker[📊 Hybrid Ranker<br/>Combine + Rerank]
        end
        
        subgraph "🧩 Context Generation"
            PermissionFilter[🛡️ Permission Filter<br/>Access Control]
            ContextBuilder[🧩 Context Builder<br/>Relevant Chunks]
            PromptTemplate[📋 Prompt Template<br/>System + User Prompt]
        end
        
        subgraph "🎯 Response Generation"
            LLMCaller[🧠 LLM Caller<br/>API Management]
            ResponseParser[📄 Response Parser<br/>Extract Answer + Citations]
            QualityCheck[✅ Quality Validator<br/>Relevance Check]
        end
    end
    
    %% Output
    FinalResponse[✨ Final Response + References]
    
    %% Flow
    UserQuery --> QueryParser
    QueryParser --> QueryEnhancer
    QueryEnhancer --> SemanticSearch
    QueryEnhancer --> KeywordSearch
    
    SemanticSearch --> HybridRanker
    KeywordSearch --> HybridRanker
    
    HybridRanker --> PermissionFilter
    PermissionFilter --> ContextBuilder
    ContextBuilder --> PromptTemplate
    
    PromptTemplate --> LLMCaller
    LLMCaller --> ResponseParser
    ResponseParser --> QualityCheck
    QualityCheck --> FinalResponse
    
    %% External connections (dotted)
    SemanticSearch -.-> VectorDB[(🔢 Vector DB)]
    KeywordSearch -.-> SearchIndex[(🔎 Search Index)]
    PermissionFilter -.-> UserDB[(👤 User DB)]
    LLMCaller -.-> ExternalLLM[🌐 External LLM]
    
    %% Styling
    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef processing fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef retrieval fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef context fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef generation fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef output fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    classDef external fill:#f1f8e9,stroke:#689f38,stroke-width:1px
    
    class UserQuery input
    class QueryParser,QueryEnhancer processing
    class SemanticSearch,KeywordSearch,HybridRanker retrieval
    class PermissionFilter,ContextBuilder,PromptTemplate context
    class LLMCaller,ResponseParser,QualityCheck generation
    class FinalResponse output
    class VectorDB,SearchIndex,UserDB,ExternalLLM external
```

---

## 4. 🔧 **DATA PROCESSING PIPELINE**

```mermaid
graph TB
    %% Input Sources
    subgraph "📥 INPUT SOURCES"
        RawDocs[📄 Raw Documents<br/>PDF, Word, Text]
        WebUpload[🌐 Web Upload<br/>Manual Upload]
        BulkImport[📦 Bulk Import<br/>Batch Processing]
    end
    
    %% Processing Pipeline
    subgraph "🔧 DATA PROCESSING PIPELINE"
        subgraph "1️⃣ Ingestion Stage"
            DocParser[📖 Document Parser<br/>Extract Text + Metadata]
            FormatValidator[✅ Format Validator<br/>Check File Types]
            MetadataExtractor[🏷️ Metadata Extractor<br/>Auto-tag + Manual]
        end
        
        subgraph "2️⃣ Quality Control Stage"
            DuplicateDetector[🔍 Duplicate Detector<br/>Semantic + Hash]
            ContentValidator[✅ Content Validator<br/>Quality Rules]
            ComplianceCheck[🛡️ Compliance Check<br/>Security Classification]
        end
        
        subgraph "3️⃣ Processing Stage"
            TextCleaner[🧹 Text Cleaner<br/>Remove Noise]
            ChunkSplitter[✂️ Chunk Splitter<br/>Intelligent Splitting]
            EmbeddingGenerator[🔢 Embedding Generator<br/>Vector Creation]
        end
        
        subgraph "4️⃣ Storage Stage"
            IndexBuilder[📇 Index Builder<br/>Vector + Text Index]
            DatabaseWriter[💾 Database Writer<br/>Atomic Operations]
        end
    end
    
    %% Output Storage
    subgraph "🗄️ STORAGE DESTINATIONS"
        VectorStore[(🔢 Vector Database<br/>Embeddings)]
        MetadataStore[(🗃️ Metadata Store<br/>PostgreSQL)]
        FileStore[(📁 File Storage<br/>Original Documents)]
        SearchIndex[(🔎 Search Index<br/>Full-text)]
    end
    
    %% Flow
    RawDocs --> DocParser
    WebUpload --> DocParser
    BulkImport --> DocParser
    
    DocParser --> FormatValidator
    FormatValidator --> MetadataExtractor
    
    MetadataExtractor --> DuplicateDetector
    DuplicateDetector --> ContentValidator
    ContentValidator --> ComplianceCheck
    
    ComplianceCheck --> TextCleaner
    TextCleaner --> ChunkSplitter
    ChunkSplitter --> EmbeddingGenerator
    
    EmbeddingGenerator --> IndexBuilder
    IndexBuilder --> DatabaseWriter
    
    DatabaseWriter --> VectorStore
    DatabaseWriter --> MetadataStore
    DatabaseWriter --> FileStore
    DatabaseWriter --> SearchIndex
    
    %% External Services (dotted)
    EmbeddingGenerator -.-> EmbeddingAPI[🌐 Embedding API]
    ComplianceCheck -.-> SecurityRules[🛡️ Security Rules]
    
    %% Styling
    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef stage1 fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef stage2 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef stage3 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef stage4 fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef storage fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    classDef external fill:#f1f8e9,stroke:#689f38,stroke-width:1px
    
    class RawDocs,WebUpload,BulkImport input
    class DocParser,FormatValidator,MetadataExtractor stage1
    class DuplicateDetector,ContentValidator,ComplianceCheck stage2
    class TextCleaner,ChunkSplitter,EmbeddingGenerator stage3
    class IndexBuilder,DatabaseWriter stage4
    class VectorStore,MetadataStore,FileStore,SearchIndex storage
    class EmbeddingAPI,SecurityRules external
```

---

## 5. 🗄️ **DATA STORAGE ARCHITECTURE**

```mermaid
graph TB
    %% Application Layer (simplified)
    Apps[💼 Application Services]
    
    %% Cache Layer
    subgraph "⚡ CACHE LAYER"
        Redis[🔴 Redis Cluster<br/>Sessions + Query Cache]
        Memcached[💾 Memcached<br/>Embedding Cache]
    end
    
    %% Primary Storage
    subgraph "🗄️ PRIMARY STORAGE"
        subgraph "📊 Vector Storage"
            VectorDB[🔢 Vector Database<br/>Chroma/FAISS]
            VectorReplica[📊 Vector Replica<br/>Read-only Copy]
        end
        
        subgraph "🗃️ Relational Storage"
            PostgreSQL[(🐘 PostgreSQL Master<br/>Metadata + Users)]
            PGReplica[(📖 PostgreSQL Replica<br/>Read Queries)]
            PGBackup[(💾 PostgreSQL Backup<br/>Point-in-time Recovery)]
        end
        
        subgraph "🔎 Search Storage"
            Elasticsearch[(🔍 Elasticsearch<br/>Full-text Search)]
            ESReplica[(🔍 ES Replica<br/>High Availability)]
        end
    end
    
    %% File Storage
    subgraph "📁 FILE STORAGE"
        ObjectStorage[☁️ Object Storage<br/>MinIO/S3-compatible]
        LocalCache[💽 Local SSD Cache<br/>Hot Files]
        ArchiveStorage[📦 Archive Storage<br/>Cold Files]
    end
    
    %% Backup & Recovery
    subgraph "💾 BACKUP & RECOVERY"
        BackupService[🔄 Backup Service<br/>Automated Schedules]
        DisasterRecovery[🚨 Disaster Recovery<br/>Remote Site]
    end
    
    %% Connections
    Apps --> Redis
    Apps --> Memcached
    Apps --> VectorDB
    Apps --> PostgreSQL
    Apps --> Elasticsearch
    Apps --> ObjectStorage
    
    %% Replication
    VectorDB --> VectorReplica
    PostgreSQL --> PGReplica
    PostgreSQL --> PGBackup
    Elasticsearch --> ESReplica
    
    %% Storage Hierarchy
    Apps -.-> LocalCache
    LocalCache --> ObjectStorage
    ObjectStorage --> ArchiveStorage
    
    %% Backup Flows
    PostgreSQL --> BackupService
    VectorDB --> BackupService
    ObjectStorage --> BackupService
    BackupService --> DisasterRecovery
    
    %% Styling
    classDef apps fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef cache fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef vector fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef relational fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef search fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef files fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    classDef backup fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class Apps apps
    class Redis,Memcached cache
    class VectorDB,VectorReplica vector
    class PostgreSQL,PGReplica,PGBackup relational
    class Elasticsearch,ESReplica search
    class ObjectStorage,LocalCache,ArchiveStorage files
    class BackupService,DisasterRecovery backup
```

---

## 6. 🏗️ **INFRASTRUCTURE & DEPLOYMENT**

```mermaid
graph TB
    %% External Access
    Internet[🌐 Internet/Intranet]
    
    %% Network Layer
    subgraph "🔒 NETWORK SECURITY"
        Firewall[🛡️ Firewall<br/>Network Protection]
        VPN[🔐 VPN Gateway<br/>Secure Access]
        LoadBalancer[⚖️ Load Balancer<br/>Traffic Distribution]
    end
    
    %% Kubernetes Cluster
    subgraph "☸️ KUBERNETES CLUSTER"
        subgraph "🏷️ Namespaces"
            ProdNS[🟢 Production<br/>Namespace]
            StagingNS[🟡 Staging<br/>Namespace]
            MonitorNS[📊 Monitoring<br/>Namespace]
        end
        
        subgraph "⚙️ Cluster Services"
            APIServer[🎯 K8s API Server]
            Scheduler[📅 Scheduler]
            Controller[🎛️ Controller Manager]
            ETCD[(🗄️ ETCD Cluster)]
        end
    end
    
    %% Worker Nodes
    subgraph "🖥️ WORKER NODES"
        subgraph "Node 1"
            Node1[💻 Master Node<br/>Control Plane]
        end
        
        subgraph "Node 2-4"  
            Node2[💻 Worker Node<br/>App Services]
            Node3[💻 Worker Node<br/>Data Services]
            Node4[💻 Worker Node<br/>ML/AI Workloads]
        end
    end
    
    %% Storage Infrastructure
    subgraph "💾 STORAGE INFRASTRUCTURE"
        SharedStorage[🗄️ Shared Storage<br/>NFS/GlusterFS]
        LocalSSD[⚡ Local SSD<br/>High Performance]
        NetworkStorage[🌐 Network Storage<br/>Persistent Volumes]
    end
    
    %% Monitoring & Security
    subgraph "📊 MONITORING & SECURITY"
        Prometheus[📊 Prometheus<br/>Metrics Collection]
        Grafana[📈 Grafana<br/>Dashboards]
        ELKStack[📋 ELK Stack<br/>Log Management]
        Vault[🔐 HashiCorp Vault<br/>Secret Management]
        SecurityScan[🛡️ Security Scanner<br/>Vulnerability Assessment]
    end
    
    %% External Dependencies
    subgraph "🌐 EXTERNAL SERVICES"
        CloudLLM[🧠 Cloud LLM APIs<br/>OpenAI/Claude]
        CloudMonitor[📊 Cloud Monitoring<br/>Optional]
        CloudBackup[☁️ Cloud Backup<br/>Disaster Recovery]
    end
    
    %% Flow
    Internet --> Firewall
    Firewall --> VPN
    VPN --> LoadBalancer
    LoadBalancer --> APIServer
    
    APIServer --> ProdNS
    APIServer --> StagingNS
    APIServer --> MonitorNS
    
    APIServer --> Scheduler
    Scheduler --> Controller
    Controller --> ETCD
    
    Scheduler --> Node1
    Scheduler --> Node2
    Scheduler --> Node3
    Scheduler --> Node4
    
    Node2 --> SharedStorage
    Node3 --> LocalSSD
    Node4 --> NetworkStorage
    
    ProdNS -.-> Prometheus
    Prometheus --> Grafana
    ProdNS -.-> ELKStack
    APIServer -.-> Vault
    Node1 -.-> SecurityScan
    
    Node2 -.-> CloudLLM
    Prometheus -.-> CloudMonitor
    SharedStorage -.-> CloudBackup
    
    %% Styling
    classDef internet fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef network fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef k8s fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef nodes fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef storage fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef monitoring fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    classDef external fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    
    class Internet internet
    class Firewall,VPN,LoadBalancer network
    class ProdNS,StagingNS,MonitorNS,APIServer,Scheduler,Controller,ETCD k8s
    class Node1,Node2,Node3,Node4 nodes
    class SharedStorage,LocalSSD,NetworkStorage storage
    class Prometheus,Grafana,ELKStack,Vault,SecurityScan monitoring
    class CloudLLM,CloudMonitor,CloudBackup external
```

---

## 📋 **TỔNG KẾT KIẾN TRÚC**

### **🎯 Ưu điểm của kiến trúc này:**
1. **Modular Design**: Mỗi layer có thể phát triển và scale độc lập
2. **High Availability**: Multiple replicas và failover mechanisms  
3. **Security-First**: Multi-layer security với proper access controls
4. **Scalable**: Horizontal scaling cho mọi components
5. **Maintainable**: Clear separation of concerns và comprehensive monitoring

### **📈 Khả năng mở rộng:**
- **Vertical**: Tăng resources cho existing services
- **Horizontal**: Thêm replicas và worker nodes
- **Functional**: Dễ dàng thêm features mới qua API
- **Geographic**: Multi-region deployment ready

### **🔄 Data Flow tổng quan:**
```
User → Load Balancer → API Gateway → RAG Engine → 
Vector Search + Permission Check → LLM Processing → 
Response with Citations → Cache → User
```

Kiến trúc được thiết kế để đáp ứng tất cả yêu cầu trong SRS với khả năng mở rộng trong tương lai!
