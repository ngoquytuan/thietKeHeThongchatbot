# FR03.3 — Kiến trúc Database & Luồng Dữ liệu

**Ngày:** 2026-06-03 | **Session:** 047 / DA381271  
**Stack:** Python 3.10 · FastAPI · PostgreSQL 15 · ChromaDB 1.5 · Redis 7

---

## 1. Kiến trúc Tổng quan

Toàn bộ các thành phần trong ứng dụng và kết nối đến 3 databases.

```mermaid
graph LR
    Client([🖥️ Client\nAPI / Notebook])

    subgraph APP["FastAPI Application  :8000"]
        direction TB
        JSONMW["JSONSanitization\nMiddleware"]
        CompatGuard["CompatibilityGuard\n(startup check)"]

        subgraph SEARCH["Search Layer"]
            CacheOrch["CachedSearch\nOrchestrator"]
            SearchOrch["SearchOrchestrator"]
            QueryClf["QueryClassifier\n(intent detection)"]
            SemEng["SemanticEngine\n~250ms"]
            KwEng["KeywordEngine\n~150ms"]
            BM25["BM25Indexer\n~150ms"]
            SubEng["SubstringEngine\n~100ms"]
            MetaEng["MetadataEngine\n~50ms"]
            HybridR["HybridRanker\n(fusion)"]
            Reranker["CrossEncoder\nReranker (GPU)\nBAAI/bge-reranker-v2-m3"]
        end

        subgraph SERVICES["Service Layer"]
            CitSvc["CitationService"]
            ImportProc["SimpleImport\nProcessor"]
            DelSvc["DeletionService"]
            AnalyticsSvc["SearchLogger\n(async queue)"]
            HealthSvc["DBHealthCheck"]
        end

        Embed["EmbeddingSingleton\nQwen3-Embedding-0.6B\n1024-dim (GPU)"]
    end

    PG[("🐘 PostgreSQL\nchatbotR5\n:15432")]
    Chroma[("🟣 ChromaDB\nHTTP Server\n:8000")]
    Redis[("🔴 Redis\n:6379")]

    Client --> JSONMW --> SEARCH
    Client --> SERVICES

    CacheOrch <-->|"GET/SET\nv2:search:{hash}"| Redis
    CacheOrch --> SearchOrch
    SearchOrch --> QueryClf
    SearchOrch --> SemEng & KwEng
    SearchOrch --> BM25 & SubEng & MetaEng
    SemEng & KwEng --> HybridR
    HybridR --> Reranker

    SemEng -->|"collection.query()\nvector similarity"| Chroma
    KwEng -->|"collection.get()\nwhere_document filter"| Chroma
    SemEng & KwEng & CitSvc -->|"embed()"| Embed

    BM25 -->|"SELECT bm25_index\nJOIN chunks"| PG
    SubEng -->|"ILIKE 7-field\nweighted scoring"| PG
    MetaEng -->|"JSONB queries\nlaw_id/article/type"| PG

    CitSvc --> PG & Chroma
    ImportProc -->|"INSERT docs\n+ chunks"| PG
    ImportProc -->|"upsert()\n45-field metadata"| Chroma
    DelSvc --> PG & Chroma
    AnalyticsSvc -->|"INSERT search_logs\nsearch_errors"| PG
    HealthSvc -->|"system_health_check()"| PG
    HealthSvc -->|"list_collections()"| Chroma
    HealthSvc -->|"ping()"| Redis
```

---

## 2. Luồng Search Request (Query Time)

Path đầy đủ từ client đến kết quả, bao gồm Redis cache và async logging.

```mermaid
sequenceDiagram
    participant C as Client
    participant MW as JSONMiddleware
    participant CO as CachedSearchOrch
    participant Redis as Redis
    participant SO as SearchOrchestrator
    participant QC as QueryClassifier
    participant SE as SemanticEngine
    participant KW as KeywordEngine
    participant BM as BM25Indexer
    participant Chroma as ChromaDB
    participant PG as PostgreSQL
    participant RR as Reranker (GPU)
    participant SL as SearchLogger

    C->>MW: POST /api/v1/search/{engine}
    MW->>CO: sanitized request

    CO->>Redis: GET v2:search:{sha256(query+filters)}
    alt Cache HIT (TTL 5min)
        Redis-->>CO: cached SearchResponse
        CO-->>C: SearchResponse (cache_hit=true, ~5ms)
    else Cache MISS
        Redis-->>CO: nil
        CO->>SO: search(query, top_k, filters)
        SO->>QC: classify(query)
        QC-->>SO: QueryType + extracted metadata

        par Hybrid / Semantic path
            SO->>SE: embed + cosine search
            SE->>SE: Qwen3 embed(query) → 1024-dim
            SE->>Chroma: collection.query(embedding, where_metadata)
            Chroma-->>SE: top-N chunks + similarity scores
        and Hybrid / Keyword path
            SO->>KW: keyword search
            KW->>Chroma: collection.get(where_document=OR filter)
            Chroma-->>KW: matching chunks (text match)
        end

        Note over SO: BM25 path (standalone or fallback)
        SO->>BM: bm25_search(tokens)
        BM->>PG: SELECT bm25_score JOIN document_chunks_enhanced\nWHERE bm25_tokens @@ to_tsquery()
        PG-->>BM: ranked chunks

        SO->>SO: HybridRanker.combine_results()\nintent boost + score fusion

        opt reranker enabled
            SO->>RR: rerank(query, candidates)
            RR-->>SO: reranked list (CrossEncoder score)
        end

        SO-->>CO: final SearchResponse
        CO->>Redis: SET v2:search:{hash} EX 300
        CO-->>C: SearchResponse

        CO->>SL: log_search_request (async, non-blocking)
        SL->>PG: INSERT INTO search_logs (queue-based)
    end
```

---

## 3. Luồng Import Pipeline (Document Ingestion)

Từ file JSON/JSONL đến PostgreSQL + ChromaDB, kèm BM25 indexing.

```mermaid
flowchart TD
    Files["📁 {NAME}_document.json\n{NAME}_passages.jsonl"]

    subgraph Import["Import Pipeline"]
        direction TB
        Cmd["import_new_exports.py\n(CLI entry point)"]
        SIP["SimpleImportProcessor\n.initialize()"]
        VNA["VietnameseTextAnalyzer\n(underthesea)"]
        EmbedSvc["EmbeddingSingleton\nQwen3 embed chunks"]
        Sanitize["ChromaMetadataSanitizer\nbuild_chroma_metadata_v14()\n45-field schema"]
        BM25Build["BM25Indexer\nbuild_bm25_index_with_global_terms()\nincremental=True"]
        Resolver["CollectionResolver\nroute by collection_label\n→ qwen3_v14_*"]
        JobTrack["data_ingestion_jobs\nstatus=completed"]
    end

    subgraph PG["🐘 PostgreSQL (chatbotR5)"]
        PGDocs["documents_metadata_v2\n(JSONB + 45 flat cols)"]
        PGChunks["document_chunks_enhanced\n(content + bm25_tokens tsvector)"]
        PGBm25["document_bm25_index\n(pre-computed BM25 scores)"]
        PGStats["bm25_collection_stats\n(global IDF / avg_doc_length)"]
        Trigger["fn_sync_flat_columns\ntrigger V14.11\nauto-sync content_type\norigin / scope"]
        Jobs["data_ingestion_jobs"]
    end

    subgraph Chroma["🟣 ChromaDB Collections"]
        C1["qwen3_v14_luat"]
        C2["qwen3_v14_nghi_dinh"]
        C3["qwen3_v14_thong_tu"]
        C4["qwen3_v14_noi_bo"]
    end

    Redis["🔴 Redis\ncache invalidation"]

    Files --> Cmd --> SIP
    SIP -->|"1 · parse metadata"| VNA
    SIP -->|"2 · INSERT document"| PGDocs
    PGDocs --> Trigger
    Trigger -->|"auto-compute\ncontent_type / origin / scope"| PGDocs

    SIP -->|"3 · INSERT chunks\nbm25_tokens auto via trigger"| PGChunks

    SIP -->|"4 · embed passages"| EmbedSvc
    SIP -->|"5 · sanitize metadata"| Sanitize
    Sanitize --> Resolver
    Resolver -->|"6 · collection.upsert()\nvectors + 45-field meta"| C1 & C2 & C3 & C4

    SIP -->|"7 · index BM25"| BM25Build
    BM25Build -->|"UPSERT scores"| PGBm25
    BM25Build -->|"UPDATE global stats"| PGStats

    SIP -->|"8 · track job"| Jobs

    SIP -.->|"invalidate\nsearch cache"| Redis

    style Trigger fill:#fff3cd,stroke:#ffc107
    style BM25Build fill:#d1ecf1,stroke:#0c5460
```

---

## 4. Schema PostgreSQL — Quan hệ các bảng chính

```mermaid
erDiagram
    documents_metadata_v2 {
        uuid    document_id       PK
        jsonb   metadata          "45+ fields: law_id, signer,\nbooost_keywords, heading_structure..."
        varchar document_type     "trigger-synced from metadata"
        varchar content_type      "GOVERNANCE/RECORD/PROCEDURE/..."
        varchar origin            "EXTERNAL / INTERNAL"
        varchar scope             "COMPANY_WIDE / PROJECT"
        varchar status            "active / draft / archived"
        timestamp created_at
        timestamp updated_at
    }

    document_chunks_enhanced {
        uuid    chunk_id          PK
        uuid    pg_document_id    FK
        text    content           "full chunk text"
        tsvector bm25_tokens      "GIN index — BM25 pre-filter"
        int     chunk_position
        varchar collection_name   "matches ChromaDB collection"
        timestamp created_at
    }

    document_bm25_index {
        uuid    chunk_id          FK
        varchar term
        float   bm25_score        "pre-computed TF-IDF score"
        varchar collection_name
    }

    bm25_collection_stats {
        varchar collection_name   PK
        float   avg_doc_length
        int     total_docs
        jsonb   idf_cache         "term → IDF values"
        timestamp last_updated
    }

    graph_documents {
        uuid    id                PK
        varchar law_id            "e.g. 86/2015/QH13"
        varchar doc_type          "luat / nghi_dinh / thong_tu"
        int     hierarchy_level   "0=luat, 2=nghi_dinh, 3=thong_tu"
        uuid    document_fk       FK
    }

    graph_edges {
        uuid    id                PK
        uuid    source_id         FK
        uuid    target_id         FK
        varchar relationship_type "DELEGATES_TO/BASED_ON/\nIMPLEMENTS/RELATED_TO"
        float   weight
        timestamp created_at
    }

    graph_changelog {
        uuid    id                PK
        varchar change_type
        uuid    document_id
        jsonb   change_detail
        timestamp changed_at
        varchar changed_by
    }

    data_ingestion_jobs {
        uuid    job_id            PK
        uuid    document_id       FK
        varchar status            "pending/running/completed/failed"
        varchar chunking_method   "semantic_boundary"
        int     chunks_created
        timestamp created_at
        timestamp completed_at
    }

    search_logs {
        uuid    log_id            PK
        text    query
        varchar engine
        int     results_count
        float   latency_ms
        jsonb   engine_timings
        timestamp created_at
    }

    search_errors {
        uuid    error_id          PK
        text    query
        text    error_message
        varchar engine
        timestamp created_at
    }

    deletion_audit_log {
        uuid    id                PK
        uuid    document_id       FK
        varchar deletion_type     "soft / hard"
        int     deleted_chunks
        varchar status
        timestamp deleted_at
    }

    documents_metadata_v2    ||--o{  document_chunks_enhanced  : "has chunks"
    document_chunks_enhanced ||--o{  document_bm25_index       : "BM25 indexed"
    document_chunks_enhanced }o--||  bm25_collection_stats     : "contributes to stats"
    graph_documents          ||--o{  graph_edges               : "source_id"
    graph_documents          ||--o{  graph_edges               : "target_id"
    graph_documents          }o--||  documents_metadata_v2     : "links to doc"
    graph_edges              }o--||  graph_changelog           : "audited"
    documents_metadata_v2    ||--o{  data_ingestion_jobs       : "import tracked"
    documents_metadata_v2    ||--o{  deletion_audit_log        : "deletion tracked"
```

---

## 5. ChromaDB — Collections & Metadata Schema

```mermaid
graph TD
    ChromaHTTP["🟣 ChromaDB HTTP Server\n/api/v2"]

    subgraph Collections["4 Collections (qwen3_v14_*)"]
        C1["qwen3_v14_luat\nLuật (Quốc hội)"]
        C2["qwen3_v14_nghi_dinh\nNghị định (Chính phủ)"]
        C3["qwen3_v14_thong_tu\nThông tư (Bộ)"]
        C4["qwen3_v14_noi_bo\nVăn bản nội bộ"]
    end

    subgraph Meta["45-Field Metadata Schema (V14.8)"]
        direction LR
        MID["IDs\ndocument_id · pg_document_id\nchunk_id · chunk_position"]
        MLAW["Law Identity\nlaw_id · law_type · year\nlaw_number · collection_label"]
        MORG["Organization\norganization · department\nsigner · access_level(int)"]
        MDATE["Dates\nissue_date · effective_date\nexpired_date"]
        MKW["Search Quality\nboost_keywords_json\nsubject · rank_level\ndoc_type_group"]
        MGRAPH["Graph RAG\nreference_docs\nrelated_laws\ncompliance_frameworks"]
        MENCL["Classification\ncontent_type · origin · scope\nstatus · heading_structure"]
    end

    ChromaHTTP --> Collections
    Collections --> Meta

    Embed["Qwen3-Embedding-0.6B\n1024-dim float16\nGPU (GTX1650)"]
    Embed -->|"generate vectors"| Collections

    style MID fill:#e8f4fd,stroke:#3498db
    style MLAW fill:#eafaf1,stroke:#2ecc71
    style MORG fill:#fef9e7,stroke:#f1c40f
    style MKW fill:#f9ebea,stroke:#e74c3c
    style MGRAPH fill:#f5eef8,stroke:#9b59b6
```

---

## 6. Redis — Cache Key Patterns & TTL

```mermaid
graph LR
    Redis[("🔴 Redis\nCACHE_VERSION = v2\nPrefix: v2:{type}:{hash}")]

    Redis --> SR["v2 · search · sha256\nTTL **5 min**\nSearchResponse JSON\n(query + filters + top_k)"]
    Redis --> UC["v2 · user_context · dept\nTTL **30 min**\nUser session data"]
    Redis --> PQ["v2 · popular_queries · hash\nTTL **1 hour**\nFrequently repeated queries"]
    Redis --> DS["v2 · document_stats · doc_id\nTTL **10 min**\nDoc-level aggregations"]
    Redis --> MT["v2 · metadata · hash\nTTL **1 hour**\nMetadata lookups (rarely change)"]
    Redis --> SM["v2 · system_metrics · ts\nTTL **15 min**\nHealth / monitoring data"]
    Redis --> DC["v2 · department_cache · dept\nTTL **2 hours**\nOrg structure (slow change)"]
    Redis --> AN["v2 · analytics · hash\nTTL **30 min**\nAnalytics aggregations"]

    CacheInv["⚠️ Cache Invalidation\nTriggered on:\n• Document import\n• Document delete\n• force_refresh=true"]

    CacheInv -.->|"DEL v2:search:*"| Redis

    style SR fill:#fdecea,stroke:#e74c3c
    style PQ fill:#fff3e0,stroke:#ff9800
    style MT fill:#e8f5e9,stroke:#4caf50
    style DC fill:#e3f2fd,stroke:#2196f3
```

---

## Tóm tắt — Mỗi Engine dùng Database nào

| Engine | PostgreSQL | ChromaDB | Redis |
|--------|-----------|----------|-------|
| **Semantic** | ✗ | ✅ cosine similarity (vectors) | ✅ cache output |
| **Keyword** | ✗ | ✅ where_document text filter | ✅ cache output |
| **BM25** | ✅ document_bm25_index + chunks | ✗ | ✅ cache output |
| **Substring** | ✅ ILIKE 7-field weighted | ✗ | ✅ cache output |
| **Metadata** | ✅ JSONB queries (law_id/type/year) | ✗ | ✅ cache output |
| **Hybrid** | ✅ BM25 fallback | ✅ semantic + keyword | ✅ cache output |
| **Citation** | ✅ chunk lookup + scoring | ✅ chunk content | ✗ |
| **Import** | ✅ docs + chunks + BM25 index | ✅ upsert vectors | ✅ invalidate |
| **Delete** | ✅ soft/hard delete + audit | ✅ delete vectors | ✅ invalidate |
| **Analytics** | ✅ search_logs + errors | ✗ | ✗ |
| **Graph RAG** | ✅ graph_documents + edges | ✗ | ✗ |

---

*Generated: Session 047 / DA381271 — 2026-06-03*  
*Source: FR03.3R6/src/ live read (main.py, search_orchestrator, redis_cache_manager, bm25_indexer, semantic_engine, keyword_engine, simple_import_processor, citation_service)*
