# Metadata User Manual - FR-03.1 System
**Version:** 9.1.5
**Last Updated:** March 3, 2026
**System:** Vietnamese Document Metadata Extraction & Graph RAG + ChromaDB V14

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Output Files Overview](#2-output-files-overview)
3. [document.json — Flat Canonical V3 Fields](#3-documentjson--flat-canonical-v3-fields)
4. [passages.jsonl — Passages and ChromaDB V14 Metadata](#4-passagesjsonl--passages-and-chromadb-v14-metadata)
5. [PostgreSQL JSONB Canonical Structure](#5-postgresql-jsonb-canonical-structure)
6. [Graph RAG Integration](#6-graph-rag-integration)
7. [Relationship Detection Strategies](#7-relationship-detection-strategies)
8. [Best Practices](#8-best-practices)
9. [Examples](#9-examples)
10. [Validation & Quality Assurance](#10-validation--quality-assurance)
11. [Common Issues & Solutions](#11-common-issues--solutions)
12. [Developer Integration Guide](#12-developer-integration-guide)
13. [Summary](#13-summary)

---

## 1. Introduction

### 1.1 What is Metadata?

The FR-03.1 system automatically extracts structured metadata from Vietnamese documents (QMS procedures, legal documents, reports, decisions). This metadata enables:

- **Document Discovery**: Fast search and retrieval via BM25 and vector search
- **Knowledge Graph**: Automatic relationship detection between documents
- **Categorization**: Intelligent classification and routing to the correct ChromaDB collection
- **Compliance**: Track document hierarchy and dependencies
- **Analytics**: Generate insights from document relationships

### 1.2 Version Summary

Current version: **9.1.5** (March 3, 2026)

**Key changes from v3.0 (December 2025):**
- Output `document.json` is now **flat** (Canonical V3 format), not nested sections
- New `chroma_metadata` key in each passage of `passages.jsonl` — 42 pre-computed fields ready for ChromaDB V14 ingestion
- `collection_label` replaces `chromadb_primary` — business label routing, not physical collection naming
- `access_level_int` field (integer 0/1/2) added alongside string `access_level`
- `author_name` / `author_email` now reflect the **document author** (extracted from content)
- New `processed_by` / `processed_by_email` fields for the **person who uploaded** the document
- `doc_type_group` values updated with more specific classification

---

## 2. Output Files Overview

FR-03.1 exports **three files** per processed document in a ZIP archive:

| File | Format | Purpose |
|---|---|---|
| `*_document.json` | JSON (flat) | Full document metadata — primary source for PostgreSQL |
| `*_passages.jsonl` | JSONL (one passage per line) | Text chunks with ChromaDB V14 metadata per passage |
| `*_llm_metadata.json` | JSON | LLM-generated metadata summary (informational only) |

**Critical rule:** Always use `document.json` for authoritative metadata. Use `passages.jsonl[*].chroma_metadata` for ChromaDB ingestion. Do NOT use `llm_metadata.json` for database storage — it is informational only and may contain inaccuracies (e.g., `author` field still shows uploader).

### 2.1 document.json structure

```
document.json (FLAT — all fields at root level)
├── document_id              (UUID, primary key)
├── version                  ("3.0" — schema version)
├── title, description       (document title and summary)
├── document_type            (snake_case type code, e.g. "luat", "quyet_dinh")
├── doc_type_group           (derived classification, e.g. "LEGAL_NA")
├── access_level             (string: "public", "internal", "restricted")
├── access_level_int         (integer: 0, 1, 2)
├── collection_label         (business label: "LAW_PUBLIC", etc.)
├── author_name, author_email (document author — from signer or org)
├── processed_by, processed_by_email (uploader who submitted the document)
├── department_owner         (internal department code, e.g. "RND")
├── organization             (issuing organization name)
├── signer_display           (person who signed)
├── document_number          (official number, e.g. "01/2026/TT-BGTVT")
├── issue_date               (ISO date or null)
├── effective_date           (ISO date or null)
├── rank_level               (integer, 0=National Law, see §3.14)
├── rank_label               (string, e.g. "LAW", "DECREE")
├── parent_id                (parent document number or null)
├── root_id                  (root law document number or null)
├── references_json          (array of referenced document numbers)
├── keywords_json            (array of content keywords)
├── tags_json                (array of tags)
├── searchable_text          (BM25-optimized concatenated text)
├── boost_keywords_json      (top 4 keywords for search ranking boost)
├── metadata_completeness    (float 0–100)
├── quality_score            (float 0–1)
├── pages, words, passages, total_tokens, chunk_size (stats)
└── raw_metadata_json        (internal source debug data — do NOT use for retrieval)
```

### 2.2 passages.jsonl structure

Each line is one passage (JSON object):

```
passage line (JSONL)
├── id               (UUID of this passage)
├── doc_id           (UUID of parent document)
├── content          (full text of this passage)
├── position         (1-based passage number)
├── chunk_index      (0-based passage index)
├── tokens           (token count)
├── heading          (heading context, may be empty)
├── meta             (passage-level tags: dept, type, access, entities, etc.)
└── chroma_metadata  (42 V14 fields — use this directly for ChromaDB ingestion)
```

---

## 3. document.json — Flat Canonical V3 Fields

### 3.1 Identity & Classification

#### `document_id`
- **Type:** String (UUID)
- **Auto-generated:** ✅ Yes
- **Purpose:** Primary key. Unique across the entire system.
- **Example:** `"d7b01224-8b61-4a71-a440-8c1c8d21e088"`

#### `source_document_id`
- **Type:** String (UUID) or null
- **Purpose:** If this document is a revision of / supersedes another document already in the system, this field holds the `document_id` of that source document.
- **Example:** `"a1b2c3d4-5678-..."` or `null`
- **Usage:** Build a "version chain" in the knowledge graph. Documents with the same `document_number` and different `source_document_id` values represent revision history.
- **Set by:** FR-03.1 does **not** auto-populate this field. It must be set explicitly via the metadata form (Step 2) when the document is a known revision of an existing document.

#### `version`
- **Type:** String
- **Value:** `"3.0"` (Flat Canonical V3 format)

#### `document_type`
- **Type:** String (enum, snake_case)
- **Purpose:** Vietnamese document type
- **Values:**
  - `"luat"` — Luật (National Law)
  - `"bo_luat"` — Bộ luật
  - `"nghi_dinh"` — Nghị định (Government Decree)
  - `"thong_tu"` — Thông tư (Circular)
  - `"quyet_dinh"` — Quyết định (Decision)
  - `"quy_trinh"` — Quy trình (Procedure)
  - `"quy_dinh"` — Quy định (Regulation)
  - `"cong_van"` — Công văn (Official Dispatch)
  - `"bao_cao"` — Báo cáo (Report)
  - `"to_trinh"` — Tờ trình (Proposal)
  - `"bien_ban"` — Biên bản (Minutes)
  - `"thong_bao"` — Thông báo (Notice)
  - `"ke_hoach"` — Kế hoạch (Plan)
  - `"huong_dan"` — Hướng dẫn (Guidance)

#### `doc_type_group`
- **Type:** String (enum)
- **Purpose:** Higher-level classification derived from `document_type`
- **Values (updated):**

| Value | Covers |
|---|---|
| `LEGAL_NA` | luat, bo_luat, phap_lenh (National Assembly laws) |
| `LEGAL_GOV` | nghi_quyet_chinh_phu, nghi_dinh (Government decrees) |
| `LEGAL_MIN` | thong_tu, thong_tu_lien_tich, quyet_dinh_bo, chi_thi_bo (Ministry circulars) |
| `INTERNAL_POLICY` | quyet_dinh, quy_che, quy_dinh, quy_trinh, huong_dan, ke_hoach |
| `INTERNAL_ADMIN` | bao_cao, to_trinh, bien_ban, cong_van, thong_bao |
| `GENERAL` | All other types |

- **Note:** This field is now synced between both `document.json` and `chroma_metadata` using `model.doc_type_group` for consistency. Both sources now always reflect the same classified group (e.g., "LEGAL_NA" or "INTERNAL_POLICY").

---

### 3.2 Access Control

#### `access_level`
- **Type:** String (enum)
- **Values:** `"public"`, `"internal"`, `"employee_only"`, `"restricted"`, `"secret"`, `"confidential"`

#### `access_level_int`
- **Type:** Integer
- **Purpose:** Integer encoding for ChromaDB numeric pre-filtering
- **Mapping:**

| `access_level` | `access_level_int` |
|---|---|
| `"public"` | `0` |
| `"internal"`, `"employee_only"` | `1` |
| `"restricted"`, `"secret"`, `"confidential"` | `2` |

- **Usage:** Use `access_level_int` for ChromaDB `where` clause filtering (e.g., `{"access_level": {"$lte": 1}}`). Use string `access_level` for human-readable display.

---

### 3.3 Collection Label (Routing)

#### `collection_label`
- **Type:** String (enum)
- **Purpose:** Business routing label — tells chatbotR5 which physical ChromaDB collection to store this document in. FR-03.1 sets this; chatbotR5 resolves it to a physical `collection_name`.
- **Values:**

| Label | Vietnamese | Use Case |
|---|---|---|
| `LAW_PUBLIC` | Văn bản pháp luật công khai | Legal documents, public access |
| `GENERAL_PUBLIC` | Tài liệu công khai chung | Other public documents |
| `INTERNAL_REGULATION` | Quy định nội bộ | Internal policies and rules |
| `INTERNAL_TECH` | Tài liệu kỹ thuật nội bộ | Internal technical documents |
| `OTHERS` | Khác | Fallback for unclassified |

- **Important:** `collection_label` is NOT the physical ChromaDB collection name. The physical `collection_name` (e.g., `"qwen3_v14_law"`) is assigned by chatbotR5 at ingest time based on this label. Never store `collection_label` as the ChromaDB collection name.

---

### 3.4 Author vs Uploader

Two separate people are tracked:

| Field | Meaning | Source |
|---|---|---|
| `author_name` | Person who authored/issued the document | Extracted from document content (signer or organization name) |
| `author_email` | Author's email | Always `""` — not extractable from document text |
| `processed_by` | Person who uploaded the document to FR-03.1 | UI form (Step 2), from config defaults |
| `processed_by_email` | Uploader's email | UI form (Step 2) |

- **Note:** In earlier versions (before v9.0), `author_name` incorrectly contained the uploader's name from config. This is now fixed. If you see documents where `author_name` equals the uploader's name (e.g., "Ngô quý tuấn"), those were processed before v9.0 and should be re-processed or manually corrected.

---

### 3.5 Official Identity Fields

#### `document_number`
- **Type:** String
- **Purpose:** Official document number (Số văn bản). Primary unique identifier within an organization.
- **Example:** `"134/2025/QH"`, `"01/2026/TT-BGTVT"`, `"513/QĐ-KTQLB"`

#### `organization`
- **Type:** String
- **Purpose:** Issuing organization name
- **Example:** `"Ban Hành Luật Trí Tuệ Nhân Tạo"`, `"Bộ Giao thông Vận tải"`

#### `department_owner`
- **Type:** String
- **Purpose:** Internal department code that owns this document
- **Example:** `"RND"`, `"IT"`, `"HR"`, `"ADMIN"`

#### `signer_display`
- **Type:** String
- **Purpose:** Name of person who signed the document (may be empty)
- **Example:** `"Nguyễn Hoàng Giang"`

#### `issue_date`
- **Type:** String (ISO 8601) or null
- **Purpose:** Date document was issued
- **Example:** `"2025-10-06T00:00:00Z"`, `"2026-01-15"`

> [!NOTE]
> **Sentinel Values:** When the exact month/day are unknown (e.g., extracted from a year-only document number), `month` will be set to `0` and `issue_date_ts` will be set to `0`. Downstream systems should treat `0` as "Year-Only metadata".

#### `document_number` + `issue_date` together identify a document uniquely within its organization.

---

### 3.6 Subject / Task / Project

#### `subject`
- **Type:** String (may be empty)
- **Purpose:** Document subject (V/v — Về việc)
- **Example:** `"Thực hiện Chế tạo sản phẩm mẫu thuộc Nhiệm vụ KH&CN"`

#### `task_code`
- **Type:** String or null
- **Purpose:** **CRITICAL for Graph RAG** — R&D task/project code
- **Example:** `"ĐTCT.2024.05"`, `"NCPT.2025.01"`
- **Usage:** All documents with the same `task_code` are automatically linked as `SAME_PROJECT`

#### `project_code`
- **Type:** String or null
- **Purpose:** Alternative project code
- **Example:** `"ĐTCT.2024.05"`

---

### 3.7 Keywords, Tags, and Search

#### `keywords_json`
- **Type:** Array of Strings
- **Purpose:** Content keywords extracted from document
- **Example:** `["trí tuệ nhân tạo", "hệ thống trí tuệ nhân tạo", "nghiên cứu phát triển"]`

#### `tags_json`
- **Type:** Array of Strings
- **Purpose:** Additional tags for categorization
- **Example:** `["luật trí tuệ nhân tạo", "quản lý nhà nước"]`

#### `searchable_text`
- **Type:** String
- **Purpose:** Optimized text for BM25 full-text search. Concatenation of key fields.
- **Example:** `"Luật Trí tuệ nhân tạo 134/2025/QH RND hệ thống nghiên cứu..."`
- **Note:** May contain minor Vietnamese stopword noise — acceptable, slightly reduces BM25 precision

#### `boost_keywords_json`
- **Type:** Array of Strings (max 4)
- **Purpose:** Top keywords for search ranking boost
- **Example:** `["trí tuệ nhân tạo", "hệ thống trí tuệ nhân tạo", "nghiên cứu phát triển"]`

---

### 3.8 Relationships

#### `references_json`
- **Type:** Array of Strings
- **Purpose:** Document numbers referenced by this document (from "Căn cứ" clauses)
- **Example:** `["654/QĐ-CTCT", "324/QĐ-CTCT", "751/QĐ-CTCT"]`
- **Usage:** Use to build `REFERENCES` graph edges

#### `parent_id`
- **Type:** String or null
- **Purpose:** Primary parent document number
- **Example:** `"654/QĐ-CTCT"`, `null`
- **Critical:** Must be a document number or UUID — NOT a technology name or description

#### `root_id`
- **Type:** String or null
- **Purpose:** Root/top-level document in the hierarchy
- **Example:** `"51/2001/QH10"`, `null`

---

### 3.9 Hierarchy (Rank)

#### `rank_level`
- **Type:** Integer
- **Purpose:** Document authority level (0 = highest)

| `rank_level` | `rank_label` | Document Types |
|---|---|---|
| `0` | `LAW` | National laws (luat, bo_luat) |
| `1` | `DECREE` | Decrees, Government resolutions |
| `2` | `CIRCULAR` | Ministry circulars, ministry decisions |
| `3` | `DIRECTOR_DECISION` | Director-level decisions, regulations |
| `4` | `DEPARTMENT_REGULATION` | Department-level procedures, plans |
| `5` | `DOCUMENT` | Working documents, guidance |
| `6` | `REPORT` | Reports, minutes, official dispatches |
| `7` | `FORM` | Forms, templates |

#### `rank_label`
- **Type:** String — human-readable label matching `rank_level`

---

### 3.10 Financial Fields

Only populated for documents containing budget information:

- `budget_total` (Number): Total budget amount
- `budget_before_vat` (Number): Budget before VAT
- `vat_amount` (Number): VAT portion
- `currency` (String): Currency code, default `"VND"`
- `budget_source` (String): Budget source description

---

### 3.11 Content Statistics

Auto-generated. All from FR-03.1 processing:

| Field | Type | Description |
|---|---|---|
| `pages` | Integer | Number of pages |
| `words` | Integer | Word count |
| `passages` | Integer | Number of text passages/chunks |
| `chunk_count` | Integer | Same as `passages` |
| `total_tokens` | Integer | Total tokens across all passages |
| `avg_tokens_per_passage` | Float | Average passage size |
| `chunk_size` | Integer | Target chunk size (512 tokens) |
| `language_detected` | String | Language code (usually `"vi"`) |

---

### 3.12 Quality Metrics

#### `quality_score`
- **Type:** Float (0–1)
- **Purpose:** Overall extraction quality
- **Example:** `1.0`, `0.85`

#### `metadata_completeness`
- **Type:** Float (0–100)
- **Purpose:** Percentage of metadata fields populated
- **Example:** `76.2`, `95.0`
- **Note:** This value is 0–100 in `document.json`. When stored in `chroma_metadata`, it is divided by 100 (so 76.2 → 0.762).

#### `extraction_method`
- **Type:** String
- **Current value:** `"hybrid_v3"` (regex + optional LLM)

---

### 3.13 Storage / Provenance

| Field | Description |
|---|---|
| `source_file` | Original filename uploaded |
| `file_format` | File type (`"pdf"`, `"docx"`, `"md"`, etc.) |
| `file_size_bytes` | File size in bytes |
| `created_at` | ISO 8601 timestamp when document was processed |
| `updated_at` | ISO 8601 timestamp of last update |
| `generated_by` | Always `"System"` |
| `version` | Schema version `"3.0"` |

**No `author_email` in storage.** Uploader identity is at root level via `processed_by` / `processed_by_email`.

---

### 3.14 Governance Fields

#### `rank_level` / `rank_label`
(See §3.9)

#### `parent_id` / `root_id`
(See §3.8)

#### `implements`
- **Type:** String or null
- **Purpose:** Document number or standard this document implements
- **Example:** `"654/QĐ-CTCT"`, `"ISO 9001:2015"`

#### Governance context (from `raw_metadata_json.sources.NLP.governance`):
- `governing_laws`: Array of laws/standards this document follows
- `execution_scope`: Scope of application
- `is_derived`: Boolean
- `superseded_by`: Document that replaces this one
- `dependency_type`: `"DIRECT"`, `"PROCEDURAL"`, `"REFERENCE"`

**Note:** These governance fields are stored in `raw_metadata_json.sources.NLP.governance`. For Graph RAG consumers, read `references_json` and `parent_id` from root-level fields — do NOT rely on nested `raw_metadata_json.sources.*` for retrieval.

---

### 3.15 Graph Context Fields

From `raw_metadata_json.sources.NLP.graph_context`:
- `referenced_by`: Array — documents that reference this one
- `implements`: String — what this implements
- `related_projects`: Array — project names mentioned
- `related_people`: Array — people mentioned
- `related_technologies`: Array — technologies mentioned
- `aviation_products`: Array — aviation products mentioned
- `tag_keywords`: Array — top concepts for graph labeling

---

## 4. passages.jsonl — Passages and ChromaDB V14 Metadata

### 4.1 Passage Fields (Non-Metadata)

Each line in `passages.jsonl` is a JSON object:

```json
{
  "id": "e4891c09-9872-4b78-b028-3780febbd680",
  "doc_id": "d7b01224-8b61-4a71-a440-8c1c8d21e088",
  "content": "QUỐC HỘI\n\n**LUẬT TRÍ TUỆ NHÂN TẠO**...",
  "position": 1,
  "chunk_index": 0,
  "tokens": 256,
  "heading": "",
  "meta": {
    "dept": "RND",
    "type": "luat",
    "access": "public",
    "is_prohibition": false,
    "entities": { "email": [], "actions": [...], "departments": [...] }
  },
  "chroma_metadata": { ... }
}
```

### 4.2 ChromaDB V14 — 42 Metadata Fields

The `chroma_metadata` dict is ready for direct ingestion into ChromaDB. It contains 42 flat integer/float/string fields.

**Do NOT embed the passage `content` text as a ChromaDB metadata field — it is already the document text for embedding. The `chunk_content` field inside `chroma_metadata` is the same text, available as a metadata field for BM25 retrieval.**

#### Document-Level Fields (same value for all passages of a document — 26 fields)

| Field | Type | Description |
|---|---|---|
| `access_level` | int | 0=public, 1=internal, 2=restricted |
| `is_public` | int | 1 if access_level==0, else 0 |
| `department_owner` | str | Internal department code (e.g. "RND") |
| `doc_type` | str | Document type code (e.g. "luat", "quyet_dinh") |
| `doc_type_group` | str | Classification group (e.g. "LEGAL_NA") |
| `is_legal_document` | int | 1 if doc_type is a public legal document |
| `is_internal_policy` | int | 1 if internal + policy/procedure type |
| `is_aviation_tech` | int | 1 if organization is aviation-related |
| `hierarchy_level` | int | Document rank (0=highest) |
| `hierarchy_confidence` | float | Rank confidence (0.0 default) |
| `year` | int | Issue year (0 if unknown) |
| `month` | int | Issue month (0 if unknown) |
| `issue_date_ts` | int | Unix timestamp (0 if unknown) |
| `document_id` | str | UUID of parent document |
| `collection_label` | str | Business label (e.g. "LAW_PUBLIC") |
| `document_number` | str | Official document number |
| `title` | str | Document title |
| `has_parent` | int | 1 if parent_id non-empty |
| `parent_id` | str | Parent document number or "" |
| `root_id` | str | Root document number or "" |
| `signer` | str | Signer display name or "" |
| `organization` | str | Issuing organization |
| `keywords_text` | str | Space-separated keywords (for BM25 on metadata) |
| `reference_count` | int | Number of referenced documents |
| `metadata_completeness` | float | Completeness score 0.0–1.0 |
| `completeness_bucket` | int | floor(completeness × 10) — for range filtering |

#### Passage-Level Fields (unique per passage — 16 fields)

| Field | Type | Description |
|---|---|---|
| `chunk_quality_score` | float | Passage quality score (0.5 default) |
| `quality_bucket` | int | floor(chunk_quality_score × 10) |
| `chunk_index` | int | 0-based position in document |
| `is_title_chunk` | int | 1 if chunk_index == 0 (first passage) |
| `chunk_total` | int | Total number of passages in document |
| `chunk_position_pct` | float | chunk_index / (chunk_total - 1) × 100 |
| `is_article_header` | int | 1 if chunk_index == 0 or starts with Điều/Chương/Mục/Phần |
| `token_count` | int | Token count of this passage |
| `chunk_content` | str | Full passage text (copy of `content`) |
| `chunk_size_tokens` | int | Same as token_count |
| `is_continuation_from_prev` | int | 1 if this chunk continues an article started in the previous chunk |
| `is_continued_on_next` | int | 1 if the current article continues into the next chunk |
| `article_num_in_chunk` | int | Article number (Điều) this chunk belongs to; 0 if none detected |
| `chapter_num_in_chunk` | str | Chapter number this chunk belongs to (e.g. "I", "II"); "" if none |
| `article_number_str` | str | Human-readable citation string: "Điều 5" or "Khoản 2 Điều 5" |
| `chunk_keywords_text` | str | Top keywords from this chunk only (for BM25 chunk-level precision) |

#### ChromaDB Pre-Filter Query Examples

```python
# Only public legal documents from 2025+
where = {
    "$and": [
        {"access_level": {"$eq": 0}},
        {"is_legal_document": {"$eq": 1}},
        {"year": {"$gte": 2025}}
    ]
}

# Internal regulations from RND department
where = {
    "$and": [
        {"department_owner": {"$eq": "RND"}},
        {"collection_label": {"$eq": "INTERNAL_REGULATION"}}
    ]
}

# Documents with known parent (for hierarchy navigation)
where = {"has_parent": {"$eq": 1}}
```

---

## 5. PostgreSQL JSONB Canonical Structure

When storing document metadata in PostgreSQL, the recommended schema uses **5 nested JSONB sections**. Map fields from the flat `document.json` as follows.

FR-03.1 computes this structure internally (logged as `v14_jsonb` during processing). Use it as the canonical JSONB column value in your documents table.

```json
{
  "identification": {
    "document_number": "<document_number>",
    "issue_date": "<issue_date>",
    "document_type": "<document_type>",
    "subject": "<subject>"
  },
  "authority": {
    "signer": "<signer_display>",
    "organization": "<organization>",
    "department": "<department_owner>"
  },
  "domain": {
    "keywords": ["<keywords_json array>"],
    "tags": ["<tags_json array>"],
    "category": "<doc_type_group>"
  },
  "classification": {
    "access_level": "<access_level>",
    "collection_label": "<collection_label>"
  },
  "references": {
    "doc_numbers": ["<references_json array>"]
  }
}
```

### 5.1 Recommended PostgreSQL Table Schema

```sql
CREATE TABLE documents_v14 (
    document_id         UUID PRIMARY KEY,
    version             TEXT DEFAULT '3.0',
    title               TEXT,
    document_type       TEXT,
    doc_type_group      TEXT,
    access_level        TEXT,
    access_level_int    SMALLINT,
    collection_label    TEXT,
    department_owner    TEXT,
    organization        TEXT,
    document_number     TEXT,
    issue_date          TEXT,
    author_name         TEXT,
    processed_by        TEXT,
    processed_by_email  TEXT,
    rank_level          SMALLINT,
    rank_label          TEXT,
    parent_id           TEXT,
    root_id             TEXT,
    references_json     JSONB DEFAULT '[]',
    keywords_json       JSONB DEFAULT '[]',
    tags_json           JSONB DEFAULT '[]',
    searchable_text     TEXT,
    metadata_completeness FLOAT,
    quality_score       FLOAT,
    passages            SMALLINT,
    total_tokens        INTEGER,
    created_at          TIMESTAMPTZ,
    updated_at          TIMESTAMPTZ,
    -- Nested JSONB for Graph RAG queries
    v14_jsonb           JSONB,
    -- Internal source data (debug only — do NOT query for retrieval)
    raw_metadata_json   JSONB
);

-- BM25 full-text search index
CREATE INDEX idx_documents_v14_fts ON documents_v14
    USING GIN (to_tsvector('simple', searchable_text));

-- Collection routing index
CREATE INDEX idx_documents_v14_collection ON documents_v14 (collection_label);

-- Access control index
CREATE INDEX idx_documents_v14_access ON documents_v14 (access_level_int);

-- Document number lookup
CREATE INDEX idx_documents_v14_docnum ON documents_v14 (document_number);
```

---

## 6. Graph RAG Integration

### 6.1 What is Graph RAG?

**Graph RAG** (Retrieval-Augmented Generation with Knowledge Graph) combines:
- **Vector Search**: Semantic similarity via embeddings in ChromaDB
- **BM25 Search**: Keyword search via PostgreSQL `tsvector` on `searchable_text`
- **Knowledge Graph**: Explicit relationships between documents
- **LLM Generation**: Answer questions using both context types

### 6.2 Key Fields for Graph RAG

**Hard Links** (Unchanging IDs — 100% accuracy required):
1. `document_number` — unique document identifier
2. `task_code` — project linking (all docs with same code are linked)
3. `references_json` — parent documents referenced by this document
4. `parent_id` — direct parent document number
5. Governing laws (from `raw_metadata_json.sources.NLP.governance.governing_laws`)

**Semantic Links** (Content-based — 80% recommended):
1. `keywords_json` — keyword matching (>40% overlap = related)
2. `related_technologies` (from NLP graph context) — tech clustering
3. `related_projects` (from NLP graph context) — project ecosystem
4. `collection_label` — documents in same label are candidate-related

**Inferred Links** (Computed — background jobs):
1. `department_owner` + `issue_date` — chronological (report after decision in same dept)
2. `custom_fields.location` + `custom_fields.partner_organizations` — contextual

---

## 7. Relationship Detection Strategies

### 7.1 Strategy 1: Hard Linking (Most Accurate)

#### 7.1.1 Task Code Linking

Documents with same `task_code` belong to the same project.

```sql
INSERT INTO graph_edges (source_doc_id, target_doc_id, edge_type, confidence)
SELECT
  a.document_id,
  b.document_id,
  'SAME_PROJECT',
  1.0
FROM documents_v14 a
JOIN documents_v14 b
  ON a.v14_jsonb->'identification'->>'task_code' = b.v14_jsonb->'identification'->>'task_code'
WHERE a.document_id != b.document_id
  AND a.v14_jsonb->'identification'->>'task_code' IS NOT NULL;
```

#### 7.1.2 Governing Law Linking

If Document B lists Document A's `document_number` in its governing laws, B implements A.

```sql
INSERT INTO graph_edges (source_doc_id, target_doc_id, edge_type, confidence)
SELECT
  b.document_id,
  a.document_id,
  'IMPLEMENTS',
  1.0
FROM documents_v14 a
JOIN documents_v14 b
  ON b.raw_metadata_json->'sources'->'NLP'->'governance'->'governing_laws'
     @> to_jsonb(a.document_number)
WHERE a.document_id != b.document_id;
```

#### 7.1.3 References (Based-On) Linking

Documents in `references_json` are parents of this document.

```sql
INSERT INTO graph_edges (source_doc_id, target_doc_id, edge_type, confidence)
SELECT
  child.document_id,
  parent.document_id,
  CASE
    WHEN parent.document_number = child.parent_id THEN 'PRIMARY_PARENT'
    ELSE 'REFERENCES'
  END,
  1.0
FROM documents_v14 child
CROSS JOIN LATERAL jsonb_array_elements_text(child.references_json) AS ref(doc_num)
JOIN documents_v14 parent ON parent.document_number = ref.doc_num;
```

---

### 7.2 Strategy 2: Semantic Linking (Keyword-Based)

#### 7.2.1 Technology Clustering

```python
def calculate_tech_similarity(doc_a_techs, doc_b_techs):
    set_a = set(doc_a_techs)
    set_b = set(doc_b_techs)
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)  # Jaccard similarity

# Threshold: 0.3 minimum (30% overlap)
```

#### 7.2.2 Keyword Similarity Scoring

```python
def find_semantic_relationships(new_doc, existing_docs, threshold=0.4):
    suggestions = []
    new_keywords = set(new_doc['keywords_json'])

    for existing_doc in existing_docs:
        existing_keywords = set(existing_doc['keywords_json'])
        union = new_keywords | existing_keywords
        if not union:
            continue
        overlap = len(new_keywords & existing_keywords) / len(union)
        if overlap >= threshold:
            suggestions.append({
                'source_doc_id': new_doc['document_id'],
                'target_doc_id': existing_doc['document_id'],
                'edge_type': 'SEMANTIC_SIMILARITY',
                'confidence': overlap,
                'shared_keywords': list(new_keywords & existing_keywords),
                'status': 'PENDING_VERIFICATION'
            })
    return suggestions
```

---

### 7.3 Strategy 3: Inferred Relationships (Chronological)

**Principle:** Report after Decision in same department = likely implementation.

```sql
INSERT INTO graph_validation_log (source_doc_id, target_doc_id, edge_type, confidence, reason)
SELECT
  report.document_id,
  decision.document_id,
  'CHRONOLOGICAL_FOLLOW',
  0.7,
  'Report created after decision in same department'
FROM documents_v14 report
JOIN documents_v14 decision
  ON report.department_owner = decision.department_owner
WHERE report.rank_level = 6    -- Report
  AND decision.rank_level = 3  -- Decision
  AND report.issue_date > decision.issue_date
  AND NOT EXISTS (
    SELECT 1 FROM graph_edges
    WHERE source_doc_id = report.document_id
      AND target_doc_id = decision.document_id
  );
```

---

## 8. Best Practices

### 8.1 Critical Field Accuracy (Graph RAG)

**These fields MUST be accurate:**

1. **`document_number`**
   - ✅ `"134/2025/QH"`, `"01/2025/TTGV-NCPT"`
   - ❌ `"Law on AI"` (description instead of number)

2. **`task_code`**
   - ✅ `"ĐTCT.2024.05"` (exact project code)
   - ❌ `"FF-ICE"`, `"GPS Clock"`, `null` when a code exists

3. **`references_json`**
   - ✅ `["654/QĐ-CTCT", "324/QĐ-CTCT"]` (exact document numbers)
   - ❌ `["Decision about GPS"]` (descriptions)

4. **`parent_id`**
   - ✅ `"654/QĐ-CTCT"` (document number)
   - ❌ `"FF-ICE"` (technology name)

5. **`collection_label`**
   - ✅ One of the 5 valid values: `LAW_PUBLIC`, `GENERAL_PUBLIC`, `INTERNAL_REGULATION`, `INTERNAL_TECH`, `OTHERS`
   - ❌ `"kb_rnd_internal"` (old format — no longer valid)
   - ❌ `"qwen3_v14_law"` (physical ChromaDB collection name — set by chatbotR5, not FR-03.1)

### 8.2 Metadata Completeness Targets

| Field Group | Target |
|---|---|
| Core identity (`document_id`, `document_type`, `title`) | 100% |
| Authority (`organization`, `department_owner`) | 100% |
| Keywords (`keywords_json` with ≥ 5 keywords) | 95% |
| References (`references_json`) | 90% for legal docs |
| Hierarchy (`rank_level`, `parent_id`) | 90% |
| `metadata_completeness` score | ≥ 80 (0–100 scale) |

### 8.3 Keyword Quality

**Good keywords:** Specific terms, technology names, domain terms
- `"GPS"`, `"ISO 9001:2015"`, `"trí tuệ nhân tạo"`, `"SWIM"`, `"FF-ICE"`

**Bad keywords (auto-filtered by system):**
- Markdown: `"|"`, `"---"`, `"#"`, `"##"`
- Vietnamese stopwords: `"tên"`, `"Người"`, `"vụ"`, `"và"`, `"của"`
- Generic: `"Công ty"`, `"quy định"`

### 8.4 Collection Label Assignment

**Auto-suggestion rules (in priority order):**

1. `access_level` = `"restricted"` / `"confidential"` / `"secret"` → `INTERNAL_TECH`
2. `document_type` in (`luat`, `nghi_dinh`, `thong_tu`, ...) + `access_level` = `"public"` → `LAW_PUBLIC`
3. `document_type` in (`luat`, `nghi_dinh`, `thong_tu`, ...) → `INTERNAL_REGULATION`
4. `department_owner` in tech departments (IT, RND, TECH) → `INTERNAL_TECH`
5. `access_level` = `"public"` → `GENERAL_PUBLIC`
6. Default → `OTHERS`

**Never use `kb_*` format** (old format, deprecated).

### 8.5 Chunking Quality

- All passages ≥ 50 tokens (system auto-merges short passages)
- Target size: 512 tokens (optimised for Qwen3-Embedding-0.6B)
- Quality score ≥ 0.8

---

## 9. Examples

### 9.1 R&D Project Document (Flat document.json)

```json
{
  "document_id": "db2fd6e7-8e7d-439f-8247-442ffc40229e",
  "version": "3.0",
  "title": "Thoả thuận giao việc Chế tạo sản phẩm mẫu",
  "document_type": "bao_cao",
  "doc_type_group": "INTERNAL_ADMIN",
  "access_level": "internal",
  "access_level_int": 1,
  "collection_label": "INTERNAL_REGULATION",
  "department_owner": "RND",
  "organization": "Công ty TNHH Kỹ thuật Quản lý bay",
  "author_name": "Nguyễn Hoàng Giang",
  "author_email": "",
  "processed_by": "Ngô quý tuấn",
  "processed_by_email": "tuannq@attech.com",
  "document_number": "01/2025/TTGV-NCPT",
  "issue_date": "2025-10-06T00:00:00Z",
  "subject": "Thực hiện Chế tạo sản phẩm mẫu thuộc Nhiệm vụ KH&CN",
  "task_code": "ĐTCT.2024.05",
  "rank_level": 6,
  "rank_label": "REPORT",
  "parent_id": "654/QĐ-CTCT",
  "root_id": "654/QĐ-CTCT",
  "references_json": ["654/QĐ-CTCT", "324/QĐ-CTCT", "751/QĐ-CTCT"],
  "keywords_json": ["đồng hồ", "thời gian", "GPS", "chính xác", "CNS"],
  "tags_json": ["nghiên cứu phát triển", "chế tạo sản phẩm"],
  "searchable_text": "Thoả thuận giao việc Chế tạo sản phẩm mẫu RND đồng hồ GPS thời gian...",
  "metadata_completeness": 92.0,
  "quality_score": 1.0,
  "passages": 6,
  "total_tokens": 1530
}
```

**Graph RAG Links:**
1. Primary parent: 654/QĐ-CTCT (from `parent_id`)
2. Referenced: 324/QĐ-CTCT, 751/QĐ-CTCT (from `references_json`)
3. Project group: All docs with `task_code = ĐTCT.2024.05`
4. Semantic: GPS/time technology cluster

---

### 9.2 Public Legal Document (Flat document.json)

```json
{
  "document_id": "d7b01224-8b61-4a71-a440-8c1c8d21e088",
  "version": "3.0",
  "title": "Luật Trí tuệ nhân tạo",
  "document_type": "luat",
  "doc_type_group": "LEGAL_NA",
  "access_level": "public",
  "access_level_int": 0,
  "collection_label": "LAW_PUBLIC",
  "department_owner": "RND",
  "organization": "Ban Hành Luật Trí Tuệ Nhân Tạo",
  "author_name": "Ban Hành Luật Trí Tuệ Nhân Tạo",
  "processed_by": "Ngô quý tuấn",
  "processed_by_email": "tuannq@attech.com",
  "document_number": "134/2025/QH",
  "issue_date": null,
  "rank_level": 0,
  "rank_label": "LAW",
  "references_json": [],
  "keywords_json": ["trí tuệ nhân tạo", "hệ thống AI", "nghiên cứu phát triển"],
  "searchable_text": "Luật Trí tuệ nhân tạo 134/2025/QH RND hệ thống...",
  "metadata_completeness": 76.2,
  "passages": 50
}
```

**Corresponding chroma_metadata for first passage:**

```json
{
  "access_level": 0,
  "is_public": 1,
  "department_owner": "RND",
  "doc_type": "luat",
  "doc_type_group": "LEGAL_NA",
  "is_legal_document": 1,
  "is_internal_policy": 0,
  "is_aviation_tech": 0,
  "hierarchy_level": 0,
  "hierarchy_confidence": 0.0,
  "year": 0,
  "month": 0,
  "issue_date_ts": 0,
  "document_id": "d7b01224-8b61-4a71-a440-8c1c8d21e088",
  "collection_label": "LAW_PUBLIC",
  "document_number": "134/2025/QH",
  "title": "Luật Trí tuệ nhân tạo",
  "has_parent": 0,
  "parent_id": "",
  "root_id": "",
  "signer": "",
  "organization": "Ban Hành Luật Trí Tuệ Nhân Tạo",
  "keywords_text": "trí tuệ nhân tạo hệ thống AI nghiên cứu phát triển",
  "reference_count": 0,
  "metadata_completeness": 0.762,
  "completeness_bucket": 7,
  "chunk_quality_score": 0.5,
  "quality_bucket": 5,
  "chunk_index": 0,
  "is_title_chunk": 1,
  "chunk_total": 50,
  "chunk_position_pct": 0.0,
  "is_article_header": 0,
  "token_count": 256,
  "chunk_size_tokens": 256,
  "chunk_content": "QUỐC HỘI\n\n**LUẬT TRÍ TUỆ NHÂN TẠO**..."
}
```

---

## 10. Validation & Quality Assurance

### 10.1 Pre-Ingest Validation Checklist

**Before storing to database:**

- [ ] `document_id` is valid UUID
- [ ] `version` is `"3.0"`
- [ ] `document_type` is from allowed enum
- [ ] `doc_type_group` is from: `LEGAL_NA`, `LEGAL_GOV`, `LEGAL_MIN`, `INTERNAL_POLICY`, `INTERNAL_ADMIN`, `GENERAL`
- [ ] `access_level_int` is 0, 1, or 2
- [ ] `collection_label` is one of: `LAW_PUBLIC`, `GENERAL_PUBLIC`, `INTERNAL_REGULATION`, `INTERNAL_TECH`, `OTHERS`
- [ ] `document_number` is present (if document has one)
- [ ] `references_json` contains valid document numbers (not descriptions)
- [ ] `parent_id` is a document number or null (NOT a technology name)
- [ ] `keywords_json` has ≥ 3 keywords with no markdown noise
- [ ] `rank_level` is 0–7
- [ ] `passages` count > 0
- [ ] `metadata_completeness` ≥ 0 and ≤ 100

**For chroma_metadata validation:**

- [ ] `access_level` is 0, 1, or 2 (integer)
- [ ] `collection_label` is one of 5 valid values
- [ ] `chunk_content` is not empty
- [ ] `chunk_total` > 0 and `chunk_index` < `chunk_total`
- [ ] `metadata_completeness` is 0.0–1.0 (divided by 100)

### 10.2 Graph RAG Validation SQL

```sql
-- Documents with missing parent despite having references
SELECT
  document_id,
  document_number,
  parent_id,
  references_json
FROM documents_v14
WHERE jsonb_array_length(references_json) > 0
  AND parent_id IS NULL;

-- Documents with invalid parent_id (not resolvable to a known doc)
SELECT
  document_id,
  document_number,
  parent_id
FROM documents_v14
WHERE parent_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM documents_v14 p WHERE p.document_number = parent_id
  );

-- Orphaned lower-rank documents (should have a parent)
SELECT document_id, document_number, rank_level
FROM documents_v14
WHERE rank_level >= 5
  AND parent_id IS NULL
  AND jsonb_array_length(references_json) = 0;

-- Documents with old collection format (migration check)
SELECT document_id, document_number, collection_label
FROM documents_v14
WHERE collection_label NOT IN ('LAW_PUBLIC', 'GENERAL_PUBLIC', 'INTERNAL_REGULATION', 'INTERNAL_TECH', 'OTHERS')
   OR collection_label IS NULL;
```

---

## 11. Common Issues & Solutions

### 11.1 Parent ID Errors

**Problem:** `parent_id` contains technology name or description

```json
{ "parent_id": "FF-ICE" }  // WRONG
```

**Solution:** Use document number from `references_json`

```json
{
  "references_json": ["654/QĐ-CTCT"],
  "parent_id": "654/QĐ-CTCT"   // CORRECT
}
```

### 11.2 Missing Task Code

**Problem:** Project documents without `task_code`

```json
{ "subject": "GPS Clock project report", "task_code": null }  // WRONG
```

**Solution:** Extract code from subject or description

```json
{ "task_code": "ĐTCT.2024.05" }  // CORRECT
```

### 11.3 Wrong Collection Label Format

**Problem:** Old `kb_*` format or physical collection name used

```json
{ "collection_label": "kb_rnd_internal" }   // WRONG — old format
{ "collection_label": "qwen3_v14_law" }     // WRONG — physical name (chatbotR5 only)
```

**Solution:** Use one of the 5 business labels

```json
{ "collection_label": "INTERNAL_REGULATION" }   // CORRECT
{ "collection_label": "LAW_PUBLIC" }             // CORRECT
```

### 11.4 access_level_int Not Integer

**Problem:** `access_level_int` stored as string

```json
{ "access_level_int": "0" }   // WRONG
```

**Solution:** Always store as integer

```json
{ "access_level_int": 0 }   // CORRECT
```

### 11.5 metadata_completeness Scale Mismatch

**Problem:** `metadata_completeness` stored as 0–100 in ChromaDB (should be 0.0–1.0)

**Solution:** In `document.json` it is 0–100. In `chroma_metadata` it is pre-divided to 0.0–1.0. Do not divide again.

```python
# In chroma_metadata (already correct, do NOT divide)
meta["metadata_completeness"]  # e.g., 0.762 — ready for ChromaDB

# In document.json (human-readable scale)
doc["metadata_completeness"]   # e.g., 76.2
```

### 11.6 Author Name Confusion

**Problem:** `author_name` contains uploader name (from old v8.x documents)

**Solution:** Re-process document with v9.0, or manually set `author_name` to the signer/organization from the document text. `processed_by` should hold the uploader's name.

### 11.7 "CRITICAL: Tài liệu rỗng (không có nội dung)"

Nếu tài liệu rất ngắn (ví dụ: các biểu mẫu trống, template có < 50 tokens), Chunker có thể không tạo được passage nào nếu không có cơ chế dự phòng.

- **Khắc phục (v9.1.5+):** Hệ thống đã bổ sung logic fallback trong `FixedChunker` để luôn trả về ít nhất 1 passage cho mọi văn bản có nội dung thực tế, ngay cả khi nó dưới ngưỡng `min_chunk_size`.
- **Hành động người dùng:** Nếu vẫn gặp lỗi này, hãy kiểm tra xem file tải lên có thực sự chứa văn bản có thể trích xuất được không (không phải là file ảnh quét OCR hỏng hoặc file hoàn toàn trắng).

---

## 12. Developer Integration Guide

### 12.1 Saving document.json to PostgreSQL

```python
import json
import psycopg2

def save_document_metadata(doc: dict, conn):
    """
    Save flat document.json to PostgreSQL documents_v14 table.
    """
    # Build v14_jsonb from flat fields
    v14_jsonb = {
        "identification": {
            "document_number": doc.get("document_number", ""),
            "issue_date": doc.get("issue_date", ""),
            "document_type": doc.get("document_type", ""),
            "subject": doc.get("subject", ""),
        },
        "authority": {
            "signer": doc.get("signer_display", ""),
            "organization": doc.get("organization", ""),
            "department": doc.get("department_owner", ""),
        },
        "domain": {
            "keywords": doc.get("keywords_json", []),
            "tags": doc.get("tags_json", []),
            "category": doc.get("doc_type_group", "GENERAL"),
        },
        "classification": {
            "access_level": doc.get("access_level", "internal"),
            "collection_label": doc.get("collection_label", "OTHERS"),
        },
        "references": {
            "doc_numbers": doc.get("references_json", []),
        }
    }

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents_v14 (
            document_id, version, title, document_type, doc_type_group,
            access_level, access_level_int, collection_label,
            department_owner, organization, document_number, issue_date,
            author_name, processed_by, processed_by_email,
            rank_level, rank_label, parent_id, root_id,
            references_json, keywords_json, tags_json,
            searchable_text, metadata_completeness, quality_score,
            passages, total_tokens, created_at, updated_at,
            v14_jsonb, raw_metadata_json
        ) VALUES (
            %(document_id)s, %(version)s, %(title)s, %(document_type)s, %(doc_type_group)s,
            %(access_level)s, %(access_level_int)s, %(collection_label)s,
            %(department_owner)s, %(organization)s, %(document_number)s, %(issue_date)s,
            %(author_name)s, %(processed_by)s, %(processed_by_email)s,
            %(rank_level)s, %(rank_label)s, %(parent_id)s, %(root_id)s,
            %(references_json)s::jsonb, %(keywords_json)s::jsonb, %(tags_json)s::jsonb,
            %(searchable_text)s, %(metadata_completeness)s, %(quality_score)s,
            %(passages)s, %(total_tokens)s, %(created_at)s, %(updated_at)s,
            %(v14_jsonb)s::jsonb, %(raw_metadata_json)s::jsonb
        )
        ON CONFLICT (document_id) DO UPDATE SET
            updated_at = EXCLUDED.updated_at,
            collection_label = EXCLUDED.collection_label,
            metadata_completeness = EXCLUDED.metadata_completeness
    """, {
        **doc,
        "references_json": json.dumps(doc.get("references_json", [])),
        "keywords_json": json.dumps(doc.get("keywords_json", [])),
        "tags_json": json.dumps(doc.get("tags_json", [])),
        "raw_metadata_json": json.dumps(doc.get("raw_metadata_json", {})),
        "v14_jsonb": json.dumps(v14_jsonb),
    })
    conn.commit()
```

### 12.2 Ingesting passages.jsonl into ChromaDB

```python
import json
import chromadb

def ingest_passages(passages_jsonl_text: str, collection_name: str, embed_fn):
    """
    Ingest passages from passages.jsonl content into ChromaDB.

    collection_name: physical collection name (determined by chatbotR5 from collection_label)
    embed_fn: function that returns embedding vector for a text
    """
    client = chromadb.Client()
    collection = client.get_or_create_collection(collection_name)

    ids, documents, embeddings, metadatas = [], [], [], []

    for line in passages_jsonl_text.strip().split('\n'):
        passage = json.loads(line)
        chroma_meta = passage.get("chroma_metadata", {})

        # Validate required fields
        content = passage["content"]
        if not content.strip():
            continue

        ids.append(passage["id"])
        documents.append(content)
        embeddings.append(embed_fn(content))
        metadatas.append(chroma_meta)

    # Batch upsert
    if ids:
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
    return len(ids)
```

### 12.3 Building Graph Edges

```python
def build_graph_edges(document_id: str, conn):
    """Create graph edges from document metadata."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT document_id, document_number, references_json, parent_id, "
        "task_code, raw_metadata_json FROM documents_v14 WHERE document_id = %s",
        (document_id,)
    )
    doc = cursor.fetchone()
    if not doc:
        return

    doc_id, doc_num, refs, parent, task_code, raw_meta = doc

    # Hard Link 1: references_json → parent docs
    for ref_num in (refs or []):
        cursor.execute(
            "SELECT document_id FROM documents_v14 WHERE document_number = %s",
            (ref_num,)
        )
        row = cursor.fetchone()
        if row:
            edge_type = 'PRIMARY_PARENT' if ref_num == parent else 'REFERENCES'
            cursor.execute(
                "INSERT INTO graph_edges (source_doc_id, target_doc_id, edge_type, confidence) "
                "VALUES (%s, %s, %s, 1.0) ON CONFLICT DO NOTHING",
                (doc_id, row[0], edge_type)
            )

    # Hard Link 2: task_code → same project
    if task_code:
        cursor.execute(
            "SELECT document_id FROM documents_v14 WHERE task_code = %s AND document_id != %s",
            (task_code, doc_id)
        )
        for row in cursor.fetchall():
            cursor.execute(
                "INSERT INTO graph_edges (source_doc_id, target_doc_id, edge_type, confidence) "
                "VALUES (%s, %s, 'SAME_PROJECT', 1.0) ON CONFLICT DO NOTHING",
                (doc_id, row[0])
            )

    conn.commit()
```

---

## 13. Summary

### 13.1 Critical Fields for Graph RAG

**Must be accurate (100% required):**
1. `document_number` — unique identifier
2. `task_code` / `project_code` — project grouping
3. `references_json` — parent document references
4. `parent_id` — direct parent
5. `collection_label` — routing to correct ChromaDB collection

**Important for semantic linking (80% recommended):**
1. `keywords_json` — content keywords
2. `related_technologies` (from NLP graph context)
3. `related_projects` (from NLP graph context)
4. `department_owner` — department-level analysis

### 13.2 Quality Standards

| Metric | Target |
|---|---|
| `metadata_completeness` | ≥ 80 (0–100 scale) |
| Keyword quality | 0% noise |
| Passages ≥ 50 tokens | 100% |
| `collection_label` valid | 100% |
| `access_level_int` as integer | 100% |

### 13.3 FR-03.1 v9.1.5 System Guarantees

- ✅ 100% clean keywords (no markdown/noise)
- ✅ All passages ≥ 50 tokens
- ✅ `access_level_int` as integer (0/1/2)
- ✅ `chroma_metadata` with 42 V14 fields on every passage
- ✅ `collection_label` from fixed 5-value enum
- ✅ `author_name` from document content (not uploader config)
- ✅ `processed_by` separate from `author_name`
- ✅ `metadata_completeness` pre-scaled to 0.0–1.0 in `chroma_metadata`

---

## 14. Support & References

**Documentation:**
- `handover_fr03.1_20feb.md` — System architecture overview
- `UPGRADE_PLAN_CHROMADB_COMPAT_02Mar2026.md` — ChromaDB V14 upgrade plan
- `CLAUDE.md` — Developer instructions

**Contact:** tuannq@attech.com

**System:** FR-03.1 v9.1.5 — *This manual is current as of March 3, 2026*
