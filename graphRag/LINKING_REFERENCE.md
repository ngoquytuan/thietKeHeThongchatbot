# Linking Reference Map
**Complete relationship mapping for 40 test documents**

---

## 🌳 Full Hierarchy Trees

### Chain 1: KHCN (Science & Technology) - 11 Documents

```
LUAT_KHCN_2013 (Rank 0) ━━━━━━━━━━━━━━━┓
│                                        ┃
│                                        ▼
└─→ 654/TT-BKH (Rank 1)                 governing_laws
    │                                    
    └─→ QC-HDQLQ (Rank 2)               
        │
        ├─→ 654/QĐ-CTCT (Rank 3) ━━━━━━┳━━━ task_code: DTCT.2024.05
        │   │                           ┃
        │   └─→ QT-DTCT (Rank 4) ━━━━━━┫
        │       │                       ┃
        │       └─→ DA-DTCT-2024-05 ━━━┫
        │           │           (Rank 5)┃
        │           └─→ BC-DTCT-Q1 ━━━━┛
        │               (Rank 6)
        │
        └─→ 888/QĐ-KTQLB (Rank 3) ━━━━┳━━━ task_code: GPS-2025
            │                         ┃
            └─→ QT-NCPT (Rank 4) ━━━━┫
                │                     ┃
                └─→ DA-GPS-2025 ━━━━━┫
                    │         (Rank 5)┃
                    └─→ BC-GPS-TEST ━┛
                        (Rank 6)

Related Projects Links (Semantic):
  DA-DTCT-2024-05 ←→ DA-GPS-2025 (related_projects overlap)
  Both mention: "FF-ICE Lab"

Technology Overlap (Semantic):
  Keywords: GPS, Clock, Timing, GNSS, Navigation
```

**Hard Links in Chain 1:**
- 10 parent-child links
- 2 task_code groups (4 docs each)
- All reference LUAT_KHCN_2013 in governing_laws
**Total Hard Links:** 14

**Semantic Links:**
- 2 related_projects overlaps
- 8 documents share GPS/timing keywords
**Total Semantic Links:** 3

---

### Chain 2: HR (Human Resources) - 10 Documents

```
LUAT_LD_2019 (Rank 0) ━━━━━━━━━━━━━━━━┓
│                                       ┃
└─→ 47/TT-BNV (Rank 1)                 ┃
    │                                   ▼
    └─→ QC-NS-2024 (Rank 2)        governing_laws
        │
        ├─→ QD-NP-2025 (Rank 3)
        │   │
        │   └─→ QT-NP-2025 (Rank 4)
        │       │
        │       └─→ DA-TRAIN-2025 (Rank 5)
        │           │
        │           └─→ BC-TRAIN-Q1 (Rank 6)
        │
        └─→ (QC-NS also governs)
            └─→ QT-TD-2025 (Rank 4)
                │
                └─→ DA-PERF-2025 (Rank 5)
                    │
                    └─→ BC-TD-2024 (Rank 6)

Keyword Overlap (Semantic):
  Common: "nghỉ phép", "đào tạo", "tuyển dụng", "nhân sự"
  All HR documents share 60%+ keyword overlap
```

**Hard Links in Chain 2:**
- 8 parent-child links
- All reference LUAT_LD_2019 in governing_laws
**Total Hard Links:** 10

**Semantic Links:**
- 6 documents with keyword overlap > 60%
**Total Semantic Links:** 3

---

### Chain 3: Finance - 9 Documents

```
(No Rank 0 - inherits from national law)
│
200/TT-BTC (Rank 1)
│
└─→ QC-TC-2024 (Rank 2)
    │
    ├─→ QD-DT-2025 (Rank 3) ━━━━┳━━━ budget: 50B VND
    │   │                       ┃
    │   └─→ QT-TT-2025 (Rank 4)┃
    │       │                   ┃
    │       └─→ DA-BUDGET-Q1 ━━┫━━━ budget: 12B VND
    │           │       (Rank 5)┃
    │           └─→ BC-CHI-Q1 ━┛━━━ spent: 11.5B VND
    │               (Rank 6)
    │
    └─→ (QC-TC also governs)
        └─→ QT-QT-2025 (Rank 4)
            │
            └─→ DA-AUDIT-2025 (Rank 5)
                │
                └─→ BC-AUDIT (Rank 6)

Financial Data Overlap (Semantic):
  QD-DT → DA-BUDGET → BC-CHI (budget tracking chain)
  Keywords: "tài chính", "ngân sách", "quyết toán", "kiểm toán"
```

**Hard Links in Chain 3:**
- 8 parent-child links
- All reference 200/TT-BTC in governing_laws
**Total Hard Links:** 9

**Semantic Links:**
- Financial amount correlation
- Quarter-based temporal links
**Total Semantic Links:** 2

---

### Chain 4: Admin - 6 Documents

```
(No Rank 0)
│
01/TT-BCA (Rank 1)
│
└─→ QC-HC-2024 (Rank 2)
    │
    └─→ QD-HC-001 (Rank 3)
        │
        └─→ QT-VT-2025 (Rank 4)
            │
            └─→ DA-DOC-MGMT (Rank 5)
                │
                └─→ BC-VT-Q1 (Rank 6)

Keyword Overlap:
  "văn thư", "hành chính", "công văn", "quản lý"
```

**Hard Links in Chain 4:**
- 5 parent-child links
**Total Hard Links:** 5

**Semantic Links:**
- All share document management keywords
**Total Semantic Links:** 1

---

### Chain 5: IT - 4 Documents

```
(No Rank 0, No Rank 1, No Rank 2)
│
QD-IT-SEC (Rank 3)
│
└─→ QT-IT-SUP (Rank 4)
    │
    └─→ DA-CYBER (Rank 5)
        │
        └─→ BC-IT-Q4 (Rank 6)

Keyword Overlap:
  "IT", "security", "cyber", "bảo mật"
```

**Hard Links in Chain 5:**
- 3 parent-child links
**Total Hard Links:** 3

**Semantic Links:**
- IT security keyword cluster
**Total Semantic Links:** 1

---

## 📊 Summary Statistics

### Hard Links (Confidence 0.9-1.0)

| Type | Count | Documents Involved |
|------|-------|-------------------|
| Parent-Child | 34 | All 40 docs |
| Task Code Groups | 2 | 8 docs (DTCT, GPS) |
| Governing Laws | 11 | All KHCN docs |
| **TOTAL** | **47** | **40 docs** |

### Semantic Links (Confidence 0.6-0.89)

| Type | Count | Documents Involved |
|------|-------|-------------------|
| Related Projects | 2 | 4 docs |
| Keyword Overlap (>60%) | 6 | 15 docs |
| Technology Cluster | 3 | 8 docs |
| **TOTAL** | **11** | **27 docs** |

### Inferred Links (Confidence 0.4-0.7)

| Type | Count | Documents Involved |
|------|-------|-------------------|
| Chronological Sequence | 5 | 12 docs |
| Entity Co-occurrence | 2 | 6 docs |
| Content Similarity | 3 | 10 docs |
| **TOTAL** | **10** | **28 docs** |

### Grand Total

**Total Relationships:** 68 edges
**Total Documents:** 40
**Average Degree:** 3.4 edges/document

---

## 🔍 Task Code Groups (For Testing)

### Group 1: ĐTCT.2024.05

| Document | Rank | UUID Suffix |
|----------|------|-------------|
| 654/QĐ-CTCT | 3 | ...031 |
| QT-DTCT | 4 | ...041 |
| DA-DTCT-2024-05 | 5 | ...051 |
| BC-DTCT-Q1 | 6 | ...061 |

**Expected Hard Links:** 4 documents auto-linked

---

### Group 2: GPS-2025

| Document | Rank | UUID Suffix |
|----------|------|-------------|
| 888/QĐ-KTQLB | 3 | ...032 |
| QT-NCPT | 4 | ...042 |
| DA-GPS-2025 | 5 | ...052 |
| BC-GPS-TEST | 6 | ...062 |

**Expected Hard Links:** 4 documents auto-linked

---

## 🎯 Test Queries

### Query 1: Find All Ancestors of a Report

```sql
-- Get full path from BC-DTCT-Q1 to LUAT_KHCN_2013
WITH RECURSIVE ancestors AS (
    SELECT 
        document_id, 
        title,
        rank_level,
        parent_id,
        1 as depth
    FROM documents_metadata_v2
    WHERE document_id = '00000000-0000-0000-0000-000000000061'  -- BC-DTCT-Q1
    
    UNION ALL
    
    SELECT 
        d.document_id,
        d.title,
        d.rank_level,
        d.parent_id,
        a.depth + 1
    FROM documents_metadata_v2 d
    JOIN ancestors a ON d.document_id = a.parent_id
)
SELECT * FROM ancestors ORDER BY depth;
```

**Expected Result:** 7 rows (Rank 6 → 0)

---

### Query 2: Find All Documents in Same Project

```sql
-- Find all docs with task_code = 'DTCT.2024.05'
SELECT 
    document_id,
    title,
    rank_level,
    identification->>'task_code' as task_code
FROM documents_metadata_v2
WHERE 
    identification->>'task_code' = 'DTCT.2024.05'
    OR custom_fields->>'project_code' = 'DTCT.2024.05'
ORDER BY rank_level;
```

**Expected Result:** 4 documents

---

### Query 3: Find Semantically Related Documents

```sql
-- Find docs with keyword overlap > 60% with 654/QĐ-CTCT
WITH target_keywords AS (
    SELECT unnest(domain->'keywords') as keyword
    FROM documents_metadata_v2
    WHERE document_id = '00000000-0000-0000-0000-000000000031'
)
SELECT 
    d.document_id,
    d.title,
    COUNT(DISTINCT tk.keyword) as overlap_count
FROM documents_metadata_v2 d
CROSS JOIN LATERAL unnest(d.domain->'keywords') as doc_keyword
JOIN target_keywords tk ON doc_keyword = tk.keyword
WHERE d.document_id != '00000000-0000-0000-0000-000000000031'
GROUP BY d.document_id, d.title
HAVING COUNT(DISTINCT tk.keyword) >= 3
ORDER BY overlap_count DESC;
```

**Expected Result:** 6+ documents with GPS/KHCN overlap

---

## 📋 Checklist for Testing

### Phase 1: Data Import
- [ ] Import all 40 JSON files to PostgreSQL
- [ ] Verify metadata_completeness = 100% for all
- [ ] Check all parent_id references are valid
- [ ] Confirm all task_codes are populated correctly

### Phase 2: Hard Linking
- [ ] Detect 34 parent-child relationships
- [ ] Detect 2 task_code groups (8 docs)
- [ ] Detect 11 governing_laws implementations
- [ ] Total: 47+ hard links with confidence ≥ 0.9

### Phase 3: Semantic Linking
- [ ] Detect related_projects overlap (2 pairs)
- [ ] Detect keyword overlap clusters (6 pairs)
- [ ] Detect technology clusters (3 groups)
- [ ] Total: 11+ semantic links with confidence 0.6-0.89

### Phase 4: Inferred Linking
- [ ] Detect chronological sequences (5 chains)
- [ ] Detect entity co-occurrence (2 pairs)
- [ ] Detect content similarity (3 pairs)
- [ ] Total: 10+ inferred links with confidence 0.4-0.7

### Phase 5: Graph Queries
- [ ] Test hierarchy traversal (7-hop path)
- [ ] Test task_code clustering (4 docs per group)
- [ ] Test semantic search (keyword overlap)
- [ ] Test graph statistics (degree distribution)

---

**Last Updated:** December 28, 2025
**Status:** Ready for testing
**Contact:** ngoquytuan@gmail.com
