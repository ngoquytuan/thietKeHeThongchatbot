# Checklist Manual Mapping & Error Discovery

## 📋 Mục tiêu
Trong quá trình manual mapping, bạn sẽ:
1. ✅ Hoàn thành mapping 68 relationships
2. 🔍 Phát hiện lỗi ở 3 layers: Import → Metadata → Graph
3. 📝 Document root cause để fix đúng chỗ

---

## 🎯 CHECKLIST TỔNG QUAN

### Layer 1: Import Layer (từ file → database)
- [ ] Kiểm tra 42 documents đã import đúng chưa
- [ ] Phát hiện encoding issues (Đ vs D, Ă vs A)
- [ ] Phát hiện missing fields
- [ ] Phát hiện wrong data types

### Layer 2: Metadata Layer (sau khi import)
- [ ] Kiểm tra parent_id đúng format (UUID vs string)
- [ ] Kiểm tra governing_laws extraction
- [ ] Kiểm tra keywords extraction
- [ ] Kiểm tra department assignment

### Layer 3: Graph Layer (script tạo graph)
- [ ] Kiểm tra relationship detection logic
- [ ] Kiểm tra confidence scoring
- [ ] Kiểm tra link type classification

---

## 📊 FORM MANUAL MAPPING

### Document Inspection Form

Copy template này cho từng document:

```markdown
## Document: [Tên document]

### STEP 1: Basic Info Verification
- [ ] Document ID: _________________ (UUID format?)
- [ ] Document Number: _________________ (correct?)
- [ ] Title: _________________ (matches file?)
- [ ] Rank Level: _____ (0-6, correct?)
- [ ] Issue Date: _________________ (format: YYYY-MM-DD?)

**Errors Found:**
- [ ] Import error: _________________
- [ ] Metadata error: _________________
- [ ] Graph error: _________________

---

### STEP 2: Hierarchy Mapping
- [ ] Should have parent? YES / NO
- [ ] If YES, parent document: _________________
- [ ] Current parent_id in DB: _________________
- [ ] Format check: UUID? _____ String? _____ NULL? _____

**Errors Found:**
- [ ] Import: parent_id not set
- [ ] Import: parent_id is document_number (string) instead of UUID
- [ ] Metadata: wrong parent identified
- [ ] Graph: parent link not created

**Action Required:**
sql
-- Fix query (if needed):
UPDATE documents_metadata_v2 SET ...


---

### STEP 3: Governing Laws Mapping
Expected governing laws:
- [ ] Primary law: _________________
- [ ] Secondary laws: _________________

Actual in database:
sql
SELECT metadata->'governance'->'governing_laws' 
FROM documents_metadata_v2 
WHERE metadata->>'title' LIKE '%[Tên document]%';


Result: _________________

**Errors Found:**
- [ ] Import: governing_laws empty
- [ ] Import: governing_laws contains text snippets instead of law IDs
- [ ] Metadata: wrong law extracted
- [ ] Metadata: incomplete law list

---

### STEP 4: Task Code Mapping
- [ ] Should have task_code? YES / NO
- [ ] If YES, expected: _________________
- [ ] Actual in DB: _________________
- [ ] Encoding correct? (Đ not Ä)

**Errors Found:**
- [ ] Import: task_code missing
- [ ] Import: wrong encoding
- [ ] Metadata: extracted wrong task_code

---

### STEP 5: Keywords & Domain
Expected keywords: _________________

Actual in database:
sql
SELECT metadata->'domain'->'keywords' 
FROM documents_metadata_v2 
WHERE metadata->>'title' LIKE '%[Tên document]%';


Result: _________________

**Errors Found:**
- [ ] Import: keywords array empty
- [ ] Metadata: keywords not extracted from content
- [ ] Metadata: wrong keywords extracted

---

### STEP 6: Department
- [ ] Expected department: _________________
- [ ] Actual department: _________________
- [ ] Matches domain? YES / NO

**Errors Found:**
- [ ] Import: defaulted to "General"
- [ ] Metadata: department not extracted
```

---

## 🔍 DETAILED CHECKLIST BY DOCUMENT

### Rank 0: Laws (2 documents)

#### Document 1: LUAT_KHCN_2013

```markdown
### ✅ LUAT_KHCN_2013 Checklist

**STEP 1: Basic Verification**
- [ ] Document exists in database
- [ ] Rank level = 0
- [ ] Issue date = 2013-xx-xx
- [ ] Title contains "Khoa học và Công nghệ"

SQL to check:
```sql
SELECT 
    document_id,
    metadata->>'title' as title,
    metadata->'hierarchy'->>'rank_level' as rank,
    metadata->'identification'->>'issue_date' as issue_date
FROM documents_metadata_v2
WHERE metadata->'identification'->>'document_number' LIKE '%KHCN%'
   OR metadata->>'title' LIKE '%Khoa học%';
```

**Found Issues:**
- [ ] IMPORT ERROR: _________________
- [ ] METADATA ERROR: _________________
- [ ] GRAPH ERROR: _________________

**STEP 2: Hierarchy**
- [ ] parent_id should be NULL (it's a root law)
- [ ] Actual parent_id: _________________

**STEP 3: Should be referenced by**
Expected children (11 documents):
- [ ] 654/TT-BKH (Rank 1)
- [ ] QC-HDQLQ (Rank 2)
- [ ] 654/QĐ-CTCT (Rank 3)
- [ ] 888/QĐ-KTQLB (Rank 3)
- [ ] QT-DTCT (Rank 4)
- [ ] QT-NCPT (Rank 4)
- [ ] DA-DTCT-2024-05 (Rank 5)
- [ ] DA-GPS-2025 (Rank 5)
- [ ] BC-DTCT-Q1 (Rank 6)
- [ ] BC-GPS-TEST (Rank 6)

Verify they reference this law:
```sql
SELECT 
    metadata->>'title' as document,
    metadata->'governance'->'governing_laws' as laws
FROM documents_metadata_v2
WHERE metadata->'governance'->'governing_laws' @> '["LUAT_KHCN_2013"]'::jsonb;
-- Expected: 10 rows
```

**Found: _____ documents (expected 10)**

If < 10:
- [ ] IMPORT ERROR: governing_laws not populated
- [ ] METADATA ERROR: law reference not extracted
```

#### Document 2: LUAT_LD_2019

```markdown
### ✅ LUAT_LD_2019 Checklist

[Similar structure to above]

**Should be referenced by HR documents (10 documents):**
- [ ] 47/TT-BNV (Rank 1)
- [ ] QC-NHANSU (Rank 2)
- [ ] QD-NP-2025 (Rank 3)
- [ ] QT-NGHI-PHEP (Rank 4)
- [ ] QT-TUYEN-DUNG (Rank 4)
- [ ] DA-TRAINING-2025 (Rank 5)
- [ ] DA-PERF-REVIEW (Rank 5)
- [ ] BC-TRAINING-Q1 (Rank 6)
- [ ] BC-TUYEN-DUNG-2024 (Rank 6)
```

---

### Rank 1: Circulars (4 documents)

#### Document 3: 654/TT-BKH (KHCN Circular)

```markdown
### ✅ 654/TT-BKH Checklist

**STEP 1: Basic Info**
```sql
SELECT * FROM documents_metadata_v2
WHERE metadata->'identification'->>'document_number' LIKE '%654%TT%'
   OR metadata->'identification'->>'document_number' LIKE '%654/TT-BKH%';
```

**Found:**
- Document ID: _________________
- Title: _________________
- Rank: _____ (should be 1)

**STEP 2: Parent Relationship**
- [ ] parent_id should be: LUAT_KHCN_2013's document_id
- [ ] Actual parent_id: _________________

Check parent exists:
```sql
SELECT 
    d1.metadata->>'title' as child,
    d1.metadata->'hierarchy'->>'parent_id' as parent_id,
    d2.metadata->>'title' as parent_title
FROM documents_metadata_v2 d1
LEFT JOIN documents_metadata_v2 d2 ON d2.document_id::text = d1.metadata->'hierarchy'->>'parent_id'
WHERE d1.metadata->'identification'->>'document_number' LIKE '%654/TT-BKH%';
```

**Result:**
- [ ] ✅ Parent link valid
- [ ] ❌ Parent ID is NULL
- [ ] ❌ Parent ID is string (document_number) not UUID
- [ ] ❌ Parent ID points to wrong document

**Error Classification:**
If parent_id is NULL:
- [ ] IMPORT ERROR: parent_id not set during import

If parent_id is document_number:
- [ ] IMPORT ERROR: import script used document_number instead of resolving to UUID

If parent_id wrong:
- [ ] METADATA ERROR: wrong parent identified

**STEP 3: Children Check**
Should be referenced by:
- [ ] QC-HDQLQ (Rank 2)
- [ ] 654/QĐ-CTCT (Rank 3)
- [ ] QT-DTCT (Rank 4)
- [ ] DA-DTCT-2024-05 (Rank 5)
- [ ] BC-DTCT-Q1 (Rank 6)

**STEP 4: Governing Laws**
Should have:
- [ ] LUAT_KHCN_2013

```sql
SELECT metadata->'governance'->'governing_laws'
FROM documents_metadata_v2
WHERE metadata->'identification'->>'document_number' LIKE '%654/TT-BKH%';
```

**Result:** _________________

**Errors:**
- [ ] Empty array
- [ ] Contains text snippets ("Luật Và Công Ty")
- [ ] Missing expected law reference
```

---

### Rank 3: Decisions (6 documents)

#### Document X: 654/QĐ-CTCT (Decision with task_code)

```markdown
### ✅ 654/QĐ-CTCT Checklist

**CRITICAL: This is a key document with task_code**

**STEP 1: Identify Document**
```sql
SELECT 
    document_id,
    metadata->>'title' as title,
    metadata->'identification'->>'document_number' as doc_num,
    metadata->'identification'->>'task_code' as task_code
FROM documents_metadata_v2
WHERE metadata->'identification'->>'document_number' LIKE '%654%'
   OR metadata->'identification'->>'document_number' LIKE '%CTCT%'
   OR metadata->>'title' LIKE '%Đồng hồ%';
```

**Found:**
- Document ID: _________________
- Task Code: _________________ (should be "ĐTCT.2024.05")

**Encoding Check:**
- [ ] ✅ Correct: ĐTCT.2024.05
- [ ] ❌ Wrong: DTCT.2024.05 (missing dấu)
- [ ] ❌ Wrong: ÄTCT.2024.05 (wrong encoding)

**STEP 2: Parent Mapping**
Expected parent: QC-HDQLQ (Rank 2)

```sql
SELECT 
    d1.metadata->'hierarchy'->>'parent_id' as current_parent,
    d2.metadata->>'title' as parent_title
FROM documents_metadata_v2 d1
LEFT JOIN documents_metadata_v2 d2 ON d2.document_id::text = d1.metadata->'hierarchy'->>'parent_id'
WHERE d1.metadata->'identification'->>'document_number' LIKE '%654%CTCT%';
```

**Current parent:** _________________

**Errors:**
- [ ] parent_id is NULL
- [ ] parent_id is "QC-HDQLQ" (string, not UUID) ← IMPORT ERROR
- [ ] parent_id is "ĐTCT.2024.05" (task_code, not parent!) ← METADATA ERROR
- [ ] parent_id points to wrong document ← METADATA ERROR

**STEP 3: Task Code Group**
This document should be in group with:
- [ ] QT-DTCT (Rank 4)
- [ ] DA-DTCT-2024-05 (Rank 5)
- [ ] BC-DTCT-Q1 (Rank 6)

Verify all 4 have same task_code:
```sql
SELECT 
    metadata->>'title' as title,
    metadata->'hierarchy'->>'rank_level' as rank,
    metadata->'identification'->>'task_code' as task_code
FROM documents_metadata_v2
WHERE metadata->'identification'->>'task_code' LIKE '%DTCT%'
   OR metadata->'custom_fields'->>'project_code' LIKE '%DTCT%'
ORDER BY (metadata->'hierarchy'->>'rank_level')::int;
```

**Found: _____ documents (expected 4)**

**Errors:**
- [ ] < 4 documents: Some missing task_code
- [ ] Multiple encodings: ĐTCT vs DTCT vs ÄTCT
- [ ] task_code in wrong field (custom_fields instead of identification)

**STEP 4: Governing Laws**
Should have:
- [ ] LUAT_KHCN_2013 (root)
- [ ] 654/TT-BKH (Rank 1)
- [ ] QC-HDQLQ (Rank 2, parent)

```sql
SELECT metadata->'governance'->'governing_laws'
FROM documents_metadata_v2
WHERE metadata->'identification'->>'document_number' LIKE '%654%CTCT%';
```

**Result:** _________________

**Errors:**
- [ ] Empty or NULL
- [ ] Contains text snippets
- [ ] Missing laws
- [ ] Wrong laws
```

---

## 🎯 SYSTEMATIC ERROR DISCOVERY

### Error Discovery Matrix

Khi bạn tìm thấy lỗi, classify vào bảng này:

| Error Type | Layer | Example | Root Cause | Fix Location |
|------------|-------|---------|------------|--------------|
| parent_id is NULL | Import | QT_DTCT has NULL parent | Import script didn't populate | `import_script.py` line XX |
| parent_id is document_number | Import | parent_id = "654/QĐ-CTCT" | Import script didn't resolve to UUID | `import_script.py` line XX |
| parent_id wrong value | Metadata | Wrong parent identified | Metadata extractor logic wrong | `metadata_extractor.py` line XX |
| governing_laws text snippets | Metadata | "Luật Và Công Ty" | NER extracted sentence not law ID | `entity_extractor.py` line XX |
| task_code encoding | Import | "ÄTCT" vs "ĐTCT" | Character encoding issue | File encoding or import |
| task_code missing | Metadata | Expected but NULL | Regex pattern didn't match | `metadata_extractor.py` line XX |
| keywords empty | Metadata | Empty array | Keyword extraction failed | `metadata_extractor.py` line XX |
| department "General" | Import | Default value used | Didn't extract from metadata | `import_script.py` line XX |
| link not created | Graph | Valid metadata but no link | Graph builder logic issue | `graph_builder.py` line XX |

---

## 📝 ERROR TRACKING TEMPLATE

Tạo file `error_log.md` để track:

```markdown
# Error Discovery Log

## Error #1: parent_id as String Instead of UUID

**Discovered:** 2025-12-30 during 654/QĐ-CTCT mapping
**Affected:** 5 documents (QT_DTCT, DA_DTCT_2024_05, QD_DT_2025, QD_HC_001, 654_QD_CTCT)

**Layer:** Import

**Root Cause:**
Import script line 245:
```python
metadata['hierarchy']['parent_id'] = parent_doc_number  # Wrong!
# Should be:
metadata['hierarchy']['parent_id'] = resolve_to_uuid(parent_doc_number)
```

**Impact:**
- Cannot create parent-child links
- Graph traversal broken

**Fix Applied:**
```sql
UPDATE documents_metadata_v2 d1
SET metadata = jsonb_set(
    metadata,
    '{hierarchy,parent_id}',
    to_jsonb(d2.document_id::text)
)
FROM documents_metadata_v2 d2
WHERE d1.metadata->'hierarchy'->>'parent_id' = d2.metadata->'identification'->>'document_number';
```

**Prevention:**
- Add UUID validation in import script
- Add unit test for parent_id format

---

## Error #2: Governing Laws Text Extraction

**Discovered:** 2025-12-30 during governing_laws verification
**Affected:** 17 documents with wrong law references

**Layer:** Metadata

**Root Cause:**
entity_extractor.py line 156:
```python
# Wrong: extracts any sentence containing "Luật"
laws = re.findall(r'Luật\s+[^.]+', text)

# Should be: extract specific law identifiers
laws = re.findall(r'(LUAT_\w+|\d+/\d+/\w+-\w+)', text)
```

**Impact:**
- governing_laws contains text snippets instead of IDs
- Cannot query "find all docs implementing LAW_X"

**Fix Applied:**
1. Clear wrong data:
```sql
UPDATE documents_metadata_v2
SET metadata = jsonb_set(metadata, '{governance,governing_laws}', '[]'::jsonb)
WHERE metadata->'governance'->'governing_laws'::text LIKE '%Luật Và%';
```

2. Re-populate correctly (manual for now)

**Prevention:**
- Fix entity_extractor.py regex
- Add validation: governing_laws must match document_number pattern
- Add unit tests with sample Vietnamese legal documents

---

[Continue for each error discovered...]
```

---

## 🔍 SQL QUERIES FOR ERROR DISCOVERY

### Query 1: Find All NULL parent_id (Expected Count Analysis)

```sql
-- Documents with NULL parent_id by rank
SELECT 
    metadata->'hierarchy'->>'rank_level' as rank,
    COUNT(*) as count_null_parent
FROM documents_metadata_v2
WHERE metadata->'hierarchy'->>'parent_id' IS NULL
GROUP BY rank
ORDER BY rank::int;

-- Expected:
-- Rank 0: 2 (laws, OK)
-- Rank 1: 0-2 (circulars, some may be independent)
-- Rank 2+: 0 (all should have parents)
```

**Error Discovery:**
- If Rank 2+ has NULL → Import didn't set parent_id
- If count > expected → Wrong rank assignment

---

### Query 2: Find parent_id Format Issues

```sql
-- Parent IDs that don't match UUID format
SELECT 
    metadata->>'title' as title,
    metadata->'hierarchy'->>'parent_id' as parent_id,
    CASE 
        WHEN metadata->'hierarchy'->>'parent_id' ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN 'UUID'
        WHEN metadata->'hierarchy'->>'parent_id' IS NULL THEN 'NULL'
        ELSE 'STRING (ERROR)'
    END as format
FROM documents_metadata_v2
WHERE metadata->'hierarchy'->>'parent_id' IS NOT NULL
    AND NOT (metadata->'hierarchy'->>'parent_id' ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$');
```

**Error Discovery:**
- Any row returned → Import error (used string not UUID)

---

### Query 3: Find Orphaned Documents

```sql
-- Documents with parent_id that doesn't exist
SELECT 
    d1.metadata->>'title' as orphan_doc,
    d1.metadata->'hierarchy'->>'parent_id' as parent_id,
    d2.document_id as parent_exists
FROM documents_metadata_v2 d1
LEFT JOIN documents_metadata_v2 d2 ON d2.document_id::text = d1.metadata->'hierarchy'->>'parent_id'
WHERE d1.metadata->'hierarchy'->>'parent_id' IS NOT NULL
    AND d2.document_id IS NULL;
```

**Error Discovery:**
- Any row → Parent UUID doesn't exist (import error or metadata error)

---

### Query 4: Task Code Encoding Issues

```sql
-- Find all unique task codes (should be 2: ĐTCT.2024.05, GPS-2025)
SELECT 
    metadata->'identification'->>'task_code' as task_code,
    COUNT(*) as count
FROM documents_metadata_v2
WHERE metadata->'identification'->>'task_code' IS NOT NULL
GROUP BY task_code;

-- If you see: ĐTCT, DTCT, ÄTCT → Encoding error
```

---

### Query 5: Governing Laws Quality Check

```sql
-- Find documents with text snippets in governing_laws
SELECT 
    metadata->>'title' as title,
    metadata->'governance'->'governing_laws' as laws
FROM documents_metadata_v2
WHERE metadata->'governance'->'governing_laws'::text LIKE '%Luật Và%'
   OR metadata->'governance'->'governing_laws'::text LIKE '%Luật Thay%'
   OR metadata->'governance'->'governing_laws'::text LIKE '%Luật Này%';

-- Any row → Metadata extraction error
```

---

## 📊 PROGRESS TRACKING

### Manual Mapping Progress Tracker

```markdown
## Rank 0 (Laws): 2 documents
- [x] LUAT_KHCN_2013 ✅
  - Errors found: 0
- [x] LUAT_LD_2019 ✅
  - Errors found: 0

## Rank 1 (Circulars): 4 documents
- [ ] 654/TT-BKH
  - Errors found: parent_id NULL (Import)
- [ ] 47/TT-BNV
  - Errors found: 
- [ ] 200/TT-BTC
- [ ] 01/TT-BCA

## Rank 2 (Regulations): 4 documents
- [ ] QC-HDQLQ
- [ ] QC-NHANSU
- [ ] QC-TAICHINH
- [ ] QC-HANHCHINH

## Rank 3 (Decisions): 6 documents
- [ ] 654/QĐ-CTCT ⚠️
  - Errors found: parent_id is "ĐTCT.2024.05" not UUID (Import)
- [ ] 888/QĐ-KTQLB
- [ ] QD-NP-2025
- [ ] QD-DT-2025
- [ ] QD-HC-001
- [ ] QD-IT-SEC

[Continue...]

## Error Summary
- Import errors: 5
- Metadata errors: 3
- Graph errors: 0

## Completion: 12/42 documents (28.6%)
```

---

## 🎯 FINAL DELIVERABLES

Sau khi hoàn thành manual mapping, bạn sẽ có:

1. **error_log.md** - Danh sách tất cả lỗi phát hiện được
2. **fix_scripts/** - SQL scripts để fix từng loại lỗi
3. **prevention_rules.md** - Quy tắc để prevent lỗi này trong tương lai
4. **validation_report_after_fix.md** - Report sau khi fix xong

Bạn muốn bắt đầu từ đâu? Tôi gợi ý:
1. Start với 2 documents Rank 0 (dễ nhất)
2. Sau đó làm 4 documents Rank 1
3. Mỗi lần phát hiện lỗi → log vào error_log.md
4. Sau mỗi 10 documents → tổng kết pattern lỗi

Bạn có muốn tôi tạo sẵn file template để track không?
