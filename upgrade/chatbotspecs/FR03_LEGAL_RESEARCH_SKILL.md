# FR03.3 Legal Information Retrieval Skill

**Purpose**: Guide LLM in efficiently finding legal information, tracing legal foundations, and analyzing document relationships in Vietnamese legal document database.

**System**: FR03.3 - Vietnamese Legal Document Search & RAG System
**Version**: R5.3 (Graph RAG + Document API)
**Last Updated**: 29 January 2026

---

## When to Use This Skill

Trigger this skill when user asks:
- "Tìm căn cứ pháp lý của [document]" / "Find legal basis of [document]"
- "Văn bản này dựa trên luật nào?" / "What laws does this cite?"
- "Các văn bản liên quan đến [topic]" / "Related documents about [topic]"
- "Quy định về [legal matter]" / "Regulations about [legal matter]"
- "Luật nào quy định về [topic]" / "Which law regulates [topic]"
- "Tìm các quyết định thực hiện [law]" / "Find decisions implementing [law]"
- "Truy xuất nguồn gốc của [regulation]" / "Trace origin of [regulation]"

**Keywords**: "căn cứ pháp lý", "legal basis", "tham chiếu", "citation", "quy định", "regulation", "dựa trên", "based on", "liên quan", "related"

---

## Core Concepts of Vietnamese Legal System

### 1. Legal Document Hierarchy

```
Vietnamese Legal System Hierarchy:
┌─────────────────────────────────────┐
│  Hiến pháp (Constitution)           │ ← Highest authority
├─────────────────────────────────────┤
│  Luật (Law) - Quốc hội              │ ← Primary legislation
├─────────────────────────────────────┤
│  Pháp lệnh (Ordinance)              │ ← When QH not in session
├─────────────────────────────────────┤
│  Nghị quyết (Resolution) - QH       │ ← Policy decisions
├─────────────────────────────────────┤
│  Nghị định (Decree) - Chính phủ     │ ← Government regulations
├─────────────────────────────────────┤
│  Quyết định (Decision) - Thủ tướng  │ ← PM directives
├─────────────────────────────────────┤
│  Thông tư (Circular) - Bộ           │ ← Ministry guidelines
├─────────────────────────────────────┤
│  Quyết định (Decision) - Cơ quan    │ ← Agency decisions
└─────────────────────────────────────┘
```

**Key Principle**: Lower documents must cite and comply with higher documents!

### 2. Legal Reference Patterns

Vietnamese legal documents typically reference:

```python
REFERENCE_PATTERNS = {
    # Direct citations (Căn cứ trực tiếp)
    "Căn cứ": "Based on",
    "Theo": "According to",
    "Thực hiện": "Implementing",
    "Thi hành": "Executing",
    
    # Related references (Liên quan)
    "Sửa đổi": "Amending",
    "Bổ sung": "Supplementing",
    "Thay thế": "Replacing",
    "Bãi bỏ": "Repealing",
    
    # Specific citations (Trích dẫn cụ thể)
    "Khoản": "Clause",
    "Điều": "Article",
    "Chương": "Chapter",
    "Mục": "Section",
}
```

### 3. Document Number Format

```
Vietnamese Legal Document Numbers:
┌────────────────────────────────────────────┐
│ [Number]/[Type]-[Issuing Authority]       │
└────────────────────────────────────────────┘

Examples:
- 50/2023/QH15          → Law 50/2023 by National Assembly term 15
- 635/QĐ-HĐQLQ          → Decision 635 by Science Council
- 120/2024/NĐ-CP        → Decree 120/2024 by Government
- 15/2024/TT-BTC        → Circular 15/2024 by Ministry of Finance
```

---

## Search Strategies by Query Type

### Strategy 1: Finding Legal Basis (Tìm căn cứ pháp lý)

**User Query Pattern**: 
- "Tìm căn cứ pháp lý của Quyết định 635"
- "What is the legal foundation for this decree?"
- "Văn bản này dựa trên luật nào?"

**Step-by-Step Approach**:

```python
def find_legal_basis(document_identifier):
    """
    Find legal foundation/basis of a document
    
    Returns: Hierarchy of parent documents
    """
    
    # Step 1: Find the target document
    # Use semantic search or exact match
    results = semantic_search(document_identifier, top_k=3)
    doc_id = results[0]['document_id']
    
    # Step 2: Extract legal references from document
    # This shows what laws/regulations it cites
    references = get_legal_references(doc_id)
    
    # Step 3: Categorize references by type
    legal_basis = categorize_references(references)
    # - Primary basis: Laws (Luật)
    # - Implementation: Parent decrees/decisions
    # - Related: Other relevant documents
    
    # Step 4: For each parent, optionally get its basis
    for parent_ref in legal_basis['primary']:
        parent_doc_id = find_document(parent_ref['number'])
        parent_references = get_legal_references(parent_doc_id)
        # Build hierarchy tree
    
    return legal_basis
```

**API Calls Sequence**:

```bash
# Step 1: Find document by number/title
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quyết định 635/QĐ-HĐQLQ",
    "top_k": 3
  }'

# Step 2: Get document references
DOC_ID="extracted-from-step1"
curl http://localhost:8000/api/v1/documents/$DOC_ID/references

# Step 3: For each parent law, get its overview
curl http://localhost:8000/api/v1/documents/[parent-law-id]/overview

# Result: Complete hierarchy chain
```

**Example Output**:

```
📊 Legal Basis of "Quyết định 635/QĐ-HĐQLQ"

🔝 Primary Legal Basis (Căn cứ chính):
├─ Luật Khoa học và Công nghệ số 50/2023/QH15
│  └─ (National Assembly Law - Highest authority)
│
├─ Luật Tổ chức Chính phủ số 54/2020/QH14
│  └─ (Government Organization Law)
│
└─ Nghị định 13/2023/NĐ-CP
   └─ (Implementation decree for Law 50/2023)

📋 Implementation References (Thực hiện):
├─ Nghị quyết 117/2023/QH15
└─ Quyết định 234/QĐ-TTg

🔗 Related Documents (Liên quan):
└─ Thông tư 05/2023/TT-BKHCN
```

---

### Strategy 2: Finding Regulations About Topic (Tìm quy định về chủ đề)

**User Query Pattern**:
- "Quy định về khoa học công nghệ"
- "Regulations about scientific research"
- "Luật nào quy định về startup?"

**Step-by-Step Approach**:

```python
def find_regulations_about(topic):
    """
    Find all regulations about a specific topic
    
    Returns: Documents organized by authority level
    """
    
    # Step 1: Broad semantic search
    all_results = semantic_search(
        query=topic,
        top_k=20  # Get more results
    )
    
    # Step 2: Filter by document type
    by_type = {
        'Luật': [],          # Laws (highest authority)
        'Nghị định': [],     # Decrees
        'Quyết định': [],    # Decisions
        'Thông tư': [],      # Circulars
    }
    
    for result in all_results:
        doc_type = extract_document_type(result['title'])
        by_type[doc_type].append(result)
    
    # Step 3: Sort by relevance and date
    for doc_type in by_type:
        by_type[doc_type].sort(
            key=lambda x: (x['score'], x['issued_date']),
            reverse=True
        )
    
    # Step 4: Get overview for top documents
    top_docs = []
    for doc_type in ['Luật', 'Nghị định', 'Quyết định']:
        for doc in by_type[doc_type][:3]:  # Top 3 each
            overview = get_overview(doc['document_id'])
            top_docs.append(overview)
    
    return top_docs
```

**API Calls**:

```bash
# Step 1: Search for topic
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "khoa học công nghệ startup đổi mới sáng tạo",
    "top_k": 20
  }'

# Step 2: For each result, get metadata to filter
for doc_id in results:
  curl http://localhost:8000/api/v1/documents/$doc_id | jq '.document_type'

# Step 3: Get overview of relevant documents
curl http://localhost:8000/api/v1/documents/$doc_id/overview
```

**Example Output**:

```
📚 Regulations about "Khoa học Công nghệ"

🏛️ LUẬT (Laws - Primary Legislation):
1. ⭐ Luật Khoa học và Công nghệ số 50/2023/QH15
   - Issued: 2023-06-19
   - Relevance: 0.89
   - Overview: Quy định về hoạt động khoa học và công nghệ...

2. Luật Chuyển giao Công nghệ số 07/2017/QH14
   - Issued: 2017-06-19
   - Relevance: 0.82
   - Overview: Quy định về việc chuyển giao công nghệ...

📜 NGHỊ ĐỊNH (Decrees - Government):
1. Nghị định 13/2023/NĐ-CP
   - Implementing: Luật 50/2023/QH15
   - Issued: 2023-04-15
   - Overview: Quy định chi tiết thi hành Luật KHCN...

2. Nghị định 95/2024/NĐ-CP
   - About: Hỗ trợ doanh nghiệp KHCN
   - Issued: 2024-09-01

📋 QUYẾT ĐỊNH (Decisions):
1. Quyết định 635/QĐ-HĐQLQ
   - About: Thành lập Hội đồng quản lý quỹ
   - Issued: 2024-12-31
```

---

### Strategy 3: Finding Related Documents (Tìm văn bản liên quan)

**User Query Pattern**:
- "Các văn bản liên quan đến Luật 50/2023"
- "Related documents to this law"
- "What implements this decree?"

**Step-by-Step Approach**:

```python
def find_related_documents(document_id):
    """
    Find documents related to target document
    
    Returns: 
    - Parent documents (what it cites)
    - Child documents (what cites it)
    - Sibling documents (same topic, same level)
    """
    
    # Step 1: Get target document info
    overview = get_overview(document_id)
    doc_number = overview['document_number']
    doc_type = overview['document_type']
    
    # Step 2: Get parent documents (what it cites)
    parents = get_legal_references(document_id)
    
    # Step 3: Find child documents (what cites it)
    # Search for documents mentioning this number
    children = semantic_search(
        query=f"căn cứ {doc_number}",
        top_k=20
    )
    
    # Step 4: Find siblings (same topic, similar level)
    topic_keywords = extract_key_topics(overview['content'])
    siblings = semantic_search(
        query=" ".join(topic_keywords),
        filters={"document_type": doc_type},
        top_k=10
    )
    
    return {
        'parents': parents,
        'children': children,
        'siblings': siblings
    }
```

**API Calls**:

```bash
# Target document
DOC_ID="7081963e-31b9-48fe-8f4d-088129377096"

# Step 1: Get document info
curl http://localhost:8000/api/v1/documents/$DOC_ID/overview

# Step 2: Get what it cites (parents)
curl http://localhost:8000/api/v1/documents/$DOC_ID/references

# Step 3: Find what cites it (children)
DOC_NUMBER="635/QĐ-HĐQLQ"
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -d "{\"query\": \"căn cứ $DOC_NUMBER thực hiện\", \"top_k\": 20}"

# Step 4: Find similar topic documents (siblings)
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -d '{"query": "quỹ phát triển khoa học công nghệ", "top_k\": 10}'
```

**Example Output**:

```
🔗 Documents Related to "Quyết định 635/QĐ-HĐQLQ"

⬆️ PARENT DOCUMENTS (Căn cứ - What it cites):
├─ Luật Khoa học và Công nghệ số 50/2023/QH15
├─ Nghị định 13/2023/NĐ-CP
└─ Nghị quyết 117/2023/QH15

⬇️ CHILD DOCUMENTS (Implementing documents):
├─ Thông tư 08/2025/TT-BKHCN (Implementation guidelines)
├─ Quyết định 142/QĐ-BKHCN (Ministry decision)
└─ [None found - This is a recent document]

↔️ SIBLING DOCUMENTS (Same level, same topic):
├─ Quyết định 234/QĐ-TTg (Similar fund management)
├─ Quyết định 567/QĐ-HĐQLQ (Related council decision)
└─ Quyết định 189/QĐ-BKHCN (Ministry level)
```

---

### Strategy 4: Tracing Document Evolution (Theo dõi sự phát triển)

**User Query Pattern**:
- "Lịch sử sửa đổi của Luật KHCN"
- "Evolution of this regulation"
- "Văn bản này đã được sửa đổi chưa?"

**Step-by-Step Approach**:

```python
def trace_document_evolution(document_id):
    """
    Trace how a document has evolved over time
    
    Returns: Timeline of amendments, replacements
    """
    
    # Step 1: Get document metadata
    doc = get_document_metadata(document_id)
    doc_number = doc['document_number']
    
    # Step 2: Find amendments
    amendments = semantic_search(
        query=f"sửa đổi bổ sung {doc_number}",
        top_k=20
    )
    
    # Step 3: Find replacements
    replacements = semantic_search(
        query=f"thay thế {doc_number}",
        top_k=10
    )
    
    # Step 4: Find what it replaces/amends
    overview = get_overview(document_id)
    content = overview['overview']['first_200_words']
    
    replaced_docs = extract_replaced_references(content)
    # Look for phrases like "Thay thế Quyết định 123..."
    
    # Step 5: Build timeline
    timeline = build_timeline([
        doc,
        *amendments,
        *replacements,
        *replaced_docs
    ])
    
    return timeline
```

**Search Keywords by Evolution Type**:

```python
EVOLUTION_KEYWORDS = {
    'amendments': [
        'sửa đổi',      # Amending
        'bổ sung',      # Supplementing
        'điều chỉnh',   # Adjusting
    ],
    'replacements': [
        'thay thế',     # Replacing
        'bãi bỏ',       # Repealing
        'hủy bỏ',       # Canceling
    ],
    'extensions': [
        'gia hạn',      # Extending
        'kéo dài',      # Prolonging
    ],
    'suspensions': [
        'đình chỉ',     # Suspending
        'tạm ngưng',    # Pausing
    ]
}
```

---

## Vietnamese Legal Search Patterns

### Common Vietnamese Legal Phrases

```python
LEGAL_SEARCH_PHRASES = {
    # Finding regulations
    'quy định về': 'regulations about',
    'điều khoản': 'provisions',
    'theo quy định': 'according to regulations',
    
    # Legal basis
    'căn cứ': 'based on',
    'dựa trên': 'based on',
    'theo': 'according to',
    'thực hiện': 'implementing',
    
    # Document relationships
    'tham chiếu': 'reference',
    'trích dẫn': 'citation',
    'viện dẫn': 'citing',
    
    # Amendments
    'sửa đổi': 'amending',
    'bổ sung': 'supplementing',
    'thay thế': 'replacing',
    
    # Document structure
    'điều': 'article',
    'khoản': 'clause',
    'điểm': 'point',
    'chương': 'chapter',
}
```

### Optimizing Vietnamese Search Queries

```python
def optimize_vietnamese_query(user_query):
    """
    Transform user query for better search results
    """
    
    # Step 1: Remove stop words
    stop_words = ['của', 'và', 'các', 'về', 'trong', 'này', 'đó']
    words = user_query.split()
    words = [w for w in words if w not in stop_words]
    
    # Step 2: Add legal context if missing
    if not any(legal_term in user_query for legal_term in 
               ['luật', 'nghị định', 'quyết định', 'thông tư']):
        # User asking about topic without document type
        # Search should include various document types
        words.extend(['quy định', 'hướng dẫn'])
    
    # Step 3: Expand acronyms
    acronyms = {
        'KHCN': 'khoa học công nghệ',
        'CNTT': 'công nghệ thông tin',
        'ĐĐSĐ': 'đổi mới sáng tạo',
    }
    for acronym, expansion in acronyms.items():
        if acronym in words:
            words.append(expansion)
    
    # Step 4: Handle diacritics (FR03.3 handles this internally)
    # No need to remove accents - system handles both
    
    return ' '.join(words)

# Examples:
optimize_vietnamese_query("Quy định của luật về KHCN")
# → "Quy định luật khoa học công nghệ"

optimize_vietnamese_query("startup đổi mới")
# → "startup đổi mới quy định hướng dẫn"
```

---

## Query Classification & Routing

### Auto-detect Query Intent

```python
def classify_legal_query(user_query):
    """
    Classify user's intent to choose best search strategy
    """
    
    query_lower = user_query.lower()
    
    # Pattern 1: Finding legal basis
    if any(phrase in query_lower for phrase in 
           ['căn cứ', 'dựa trên', 'legal basis', 'foundation']):
        return 'find_legal_basis'
    
    # Pattern 2: Finding related documents
    if any(phrase in query_lower for phrase in
           ['liên quan', 'related', 'tham chiếu', 'citation']):
        return 'find_related'
    
    # Pattern 3: Topic search
    if any(phrase in query_lower for phrase in
           ['quy định về', 'regulations about', 'luật nào']):
        return 'find_by_topic'
    
    # Pattern 4: Specific document lookup
    if re.search(r'\d+/\d{4}/', query_lower):  # Has document number
        return 'find_specific_document'
    
    # Pattern 5: Evolution/amendments
    if any(phrase in query_lower for phrase in
           ['sửa đổi', 'thay thế', 'amend', 'replace', 'evolution']):
        return 'trace_evolution'
    
    # Default: General topic search
    return 'general_search'

# Usage:
intent = classify_legal_query("Tìm căn cứ pháp lý của Quyết định 635")
# → 'find_legal_basis'

strategy = get_strategy(intent)
results = strategy.execute(user_query)
```

---

## Complete Example: Finding Legal Basis

Let's walk through a complete example of finding legal basis:

**User Query**: "Tìm căn cứ pháp lý của Quyết định 635/QĐ-HĐQLQ về việc thành lập Hội đồng quản lý Quỹ"

### Step 1: Find the Document

```bash
# Search for the document
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quyết định 635/QĐ-HĐQLQ thành lập Hội đồng quản lý Quỹ",
    "top_k": 3
  }'
```

**Response**:
```json
{
  "results": [
    {
      "document_id": "7081963e-31b9-48fe-8f4d-088129377096",
      "title": "Quyết định số 635/QĐ-HĐQLQ về việc thành lập Hội đồng...",
      "score": 0.92
    }
  ]
}
```

### Step 2: Extract Legal References

```bash
DOC_ID="7081963e-31b9-48fe-8f4d-088129377096"

curl http://localhost:8000/api/v1/documents/$DOC_ID/references
```

**Response**:
```json
{
  "success": true,
  "document_id": "7081963e-31b9-48fe-8f4d-088129377096",
  "references": [
    {
      "type": "Luật",
      "number": "50/2023/QH15",
      "title": "Luật Khoa học và Công nghệ",
      "context": "Căn cứ Luật Khoa học và Công nghệ số 50/2023/QH15 ngày 19 tháng 6 năm 2023"
    },
    {
      "type": "Luật",
      "number": "54/2020/QH14",
      "title": "Luật Tổ chức Chính phủ",
      "context": "Căn cứ Luật Tổ chức Chính phủ số 54/2020/QH14"
    },
    {
      "type": "Nghị định",
      "number": "13/2023/NĐ-CP",
      "title": "Nghị định quy định chi tiết thi hành Luật KHCN",
      "context": "Căn cứ Nghị định 13/2023/NĐ-CP"
    }
  ],
  "total_references": 7
}
```

### Step 3: Get Overview of Parent Documents

```bash
# For each parent reference, search and get overview
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -d '{"query": "Luật Khoa học và Công nghệ 50/2023/QH15", "top_k": 1}'

# Get the document_id from response
PARENT_ID="extracted-id"

curl http://localhost:8000/api/v1/documents/$PARENT_ID/overview
```

### Step 4: Present Hierarchical Result

**Final Output to User**:

```markdown
📊 Căn cứ Pháp lý của "Quyết định 635/QĐ-HĐQLQ"

🔝 CĂN CỨ CHÍNH (Primary Legal Basis):

1️⃣ **Luật Khoa học và Công nghệ số 50/2023/QH15**
   - Loại: Luật (Law - Highest authority)
   - Ngày ban hành: 19/06/2023
   - Nội dung: Quy định về hoạt động khoa học và công nghệ; quyền và nghĩa vụ của tổ chức, cá nhân...
   - Trích dẫn: "Căn cứ Luật Khoa học và Công nghệ số 50/2023/QH15 ngày 19 tháng 6 năm 2023"
   - 🔗 [Xem chi tiết](link)

2️⃣ **Luật Tổ chức Chính phủ số 54/2020/QH14**
   - Loại: Luật (Law)
   - Ngày ban hành: 19/06/2020
   - Nội dung: Quy định về tổ chức và hoạt động của Chính phủ
   - Trích dẫn: "Căn cứ Luật Tổ chức Chính phủ số 54/2020/QH14"
   - 🔗 [Xem chi tiết](link)

📜 CĂN CỨ THỰC HIỆN (Implementation Basis):

3️⃣ **Nghị định 13/2023/NĐ-CP**
   - Loại: Nghị định (Decree)
   - Ngày ban hành: 15/04/2023
   - Nội dung: Quy định chi tiết thi hành một số điều của Luật Khoa học và Công nghệ
   - Thực hiện: Luật 50/2023/QH15
   - 🔗 [Xem chi tiết](link)

🔗 CÁC VĂN BẢN LIÊN QUAN (Related Documents):

4️⃣ Nghị quyết 117/2023/QH15
5️⃣ Quyết định 234/QĐ-TTg
6️⃣ Thông tư 05/2023/TT-BKHCN

📈 CẤU TRÚC PHÁP LÝ (Legal Structure):

```
Hiến pháp (Constitution)
    ↓
Luật KHCN 50/2023/QH15 ←─────┐
    ↓                          │
Luật Tổ chức CP 54/2020/QH14 ←┤
    ↓                          │  Căn cứ
Nghị định 13/2023/NĐ-CP ←─────┤  (Based on)
    ↓                          │
Quyết định 635/QĐ-HĐQLQ ←─────┘
    ↓
Thông tư hướng dẫn (nếu có)
```

💡 **Kết luận**: 
Quyết định 635/QĐ-HĐQLQ có căn cứ pháp lý vững chắc, dựa trên:
- 2 Luật của Quốc hội (cấp cao nhất)
- 1 Nghị định của Chính phủ (hướng dẫn thực hiện Luật)
- Các nghị quyết và quyết định liên quan

✅ Văn bản có giá trị pháp lý đầy đủ và hợp lệ.
```

---

## Advanced Techniques

### Technique 1: Multi-hop Reference Tracing

For complex queries like "What is the ultimate legal basis?" - trace back multiple levels:

```python
def trace_to_ultimate_basis(document_id, max_depth=5):
    """
    Trace legal references back to Constitution/Primary Laws
    """
    visited = set()
    current_level = [document_id]
    hierarchy = []
    
    for depth in range(max_depth):
        next_level = []
        
        for doc_id in current_level:
            if doc_id in visited:
                continue
                
            visited.add(doc_id)
            
            # Get references
            refs = get_legal_references(doc_id)
            hierarchy.append({
                'level': depth,
                'document': get_overview(doc_id),
                'references': refs
            })
            
            # Find parent document IDs
            for ref in refs:
                parent_id = find_document_by_number(ref['number'])
                if parent_id:
                    next_level.append(parent_id)
        
        current_level = next_level
        
        # Stop if we've reached Laws (Luật) level
        if all(is_primary_law(doc) for doc in current_level):
            break
    
    return hierarchy

def is_primary_law(doc_id):
    """Check if document is a primary law (Luật)"""
    overview = get_overview(doc_id)
    return overview['document_type'] == 'Luật'
```

### Technique 2: Cross-reference Analysis

Find documents that cite the same sources:

```python
def find_documents_with_common_basis(doc_id1, doc_id2):
    """
    Find common legal foundations between two documents
    """
    refs1 = set(ref['number'] for ref in get_legal_references(doc_id1))
    refs2 = set(ref['number'] for ref in get_legal_references(doc_id2))
    
    common = refs1 & refs2
    only_in_1 = refs1 - refs2
    only_in_2 = refs2 - refs1
    
    return {
        'common_basis': common,
        'unique_to_doc1': only_in_1,
        'unique_to_doc2': only_in_2
    }
```

### Technique 3: Citation Network Analysis

Build a network of document relationships:

```python
def build_citation_network(starting_documents):
    """
    Build a graph of document citations
    """
    network = {
        'nodes': [],  # Documents
        'edges': []   # Citations
    }
    
    queue = starting_documents.copy()
    visited = set()
    
    while queue:
        doc_id = queue.pop(0)
        
        if doc_id in visited:
            continue
        visited.add(doc_id)
        
        # Add node
        overview = get_overview(doc_id)
        network['nodes'].append({
            'id': doc_id,
            'title': overview['title'],
            'type': overview['document_type']
        })
        
        # Add edges (citations)
        refs = get_legal_references(doc_id)
        for ref in refs:
            parent_id = find_document_by_number(ref['number'])
            if parent_id:
                network['edges'].append({
                    'from': doc_id,
                    'to': parent_id,
                    'type': ref['type']
                })
                queue.append(parent_id)
    
    return network

# Visualization suggestion:
# Use this network with GraphRAG or visualization tools
```

---

## Common Query Patterns & Solutions

### Query Pattern 1: "What law regulates X?"

```python
# User asks: "Luật nào quy định về startup?"

def handle_what_law_regulates(topic):
    # Step 1: Search broadly
    results = semantic_search(
        query=f"{topic} luật quy định",
        top_k=20
    )
    
    # Step 2: Filter for Laws only
    laws = [r for r in results if r['document_type'] == 'Luật']
    
    # Step 3: Rank by relevance and date
    laws.sort(key=lambda x: (x['score'], x['issued_date']), reverse=True)
    
    # Step 4: Get overview of top law
    top_law = laws[0]
    overview = get_overview(top_law['document_id'])
    
    return {
        'primary_law': top_law,
        'overview': overview,
        'related_regulations': results[:5]  # Top 5 overall
    }
```

### Query Pattern 2: "Is this regulation still valid?"

```python
# User asks: "Nghị định này còn hiệu lực không?"

def check_regulation_validity(document_id):
    # Step 1: Get document info
    doc = get_overview(document_id)
    doc_number = doc['document_number']
    
    # Step 2: Search for amendments/replacements
    amendments = semantic_search(
        query=f"sửa đổi bổ sung {doc_number}",
        top_k=10
    )
    
    replacements = semantic_search(
        query=f"thay thế bãi bỏ {doc_number}",
        top_k=10
    )
    
    # Step 3: Check dates
    latest_amendment = max(amendments, key=lambda x: x['issued_date'])
    
    if replacements:
        return {
            'status': 'replaced',
            'replaced_by': replacements[0],
            'replacement_date': replacements[0]['issued_date']
        }
    elif amendments:
        return {
            'status': 'amended',
            'latest_amendment': latest_amendment,
            'current_version': 'See amended version'
        }
    else:
        return {
            'status': 'valid',
            'issued_date': doc['issued_date'],
            'no_amendments': True
        }
```

### Query Pattern 3: "Show me the implementation chain"

```python
# User asks: "Các văn bản hướng dẫn thực hiện Luật KHCN"

def show_implementation_chain(primary_law_id):
    # Step 1: Get law info
    law = get_overview(primary_law_id)
    law_number = law['document_number']
    
    # Step 2: Find implementing decrees
    decrees = semantic_search(
        query=f"thực hiện {law_number} nghị định",
        filters={'document_type': 'Nghị định'},
        top_k=10
    )
    
    # Step 3: For each decree, find circulars
    implementation_tree = {
        'law': law,
        'decrees': []
    }
    
    for decree in decrees:
        decree_number = decree['document_number']
        circulars = semantic_search(
            query=f"hướng dẫn {decree_number} thông tư",
            filters={'document_type': 'Thông tư'},
            top_k=5
        )
        
        implementation_tree['decrees'].append({
            'decree': decree,
            'circulars': circulars
        })
    
    return implementation_tree
```

---

## Performance Optimization for Legal Queries

### Optimization 1: Cache Common Legal References

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache legal references (they don't change often)
@lru_cache(maxsize=500)
def get_legal_references_cached(document_id):
    return get_legal_references(document_id)

# Cache document overviews
@lru_cache(maxsize=1000)
def get_overview_cached(document_id):
    return get_overview(document_id)
```

### Optimization 2: Batch Processing

```python
async def get_multiple_references(document_ids):
    """Get references for multiple documents in parallel"""
    import asyncio
    
    async def fetch_refs(doc_id):
        # Assuming async API client
        return await get_legal_references_async(doc_id)
    
    tasks = [fetch_refs(doc_id) for doc_id in document_ids]
    return await asyncio.gather(*tasks)
```

### Optimization 3: Smart Search Limiting

```python
def smart_search(query, query_type):
    """
    Adjust top_k based on query type
    """
    
    top_k_by_type = {
        'find_specific_document': 3,   # Need exact match
        'find_legal_basis': 10,         # Need thorough check
        'find_by_topic': 20,            # Need broad results
        'general_search': 5             # Quick results
    }
    
    return semantic_search(
        query=query,
        top_k=top_k_by_type.get(query_type, 5)
    )
```

---

## Error Handling & Edge Cases

### Edge Case 1: Document Number Variations

Vietnamese document numbers can be written differently:

```python
def normalize_document_number(doc_number):
    """
    Normalize variations of document numbers
    
    Examples:
    - "635/QĐ-HĐQLQ" → "635/QĐ-HĐQLQ"
    - "Quyết định 635" → "635/QĐ-*"
    - "QĐ 635/2024" → "635/QĐ-*"
    """
    import re
    
    # Extract number
    number_match = re.search(r'\d+', doc_number)
    if not number_match:
        return doc_number
    
    number = number_match.group()
    
    # Extract type
    type_patterns = {
        'QĐ': ['quyết định', 'qđ', 'qd'],
        'NĐ': ['nghị định', 'nđ', 'nd'],
        'TT': ['thông tư', 'tt'],
        'Luật': ['luật', 'law'],
    }
    
    doc_lower = doc_number.lower()
    for code, patterns in type_patterns.items():
        if any(p in doc_lower for p in patterns):
            return f"{number}/{code}-"
    
    return doc_number
```

### Edge Case 2: No References Found

```python
def handle_no_references(document_id):
    """
    Handle case when document has no references
    """
    overview = get_overview(document_id)
    
    # Check document type
    if overview['document_type'] == 'Luật':
        return {
            'message': 'This is a primary law - it typically only references the Constitution',
            'suggestion': 'Search for documents that implement this law instead'
        }
    
    # Check if document is very recent
    issued_date = overview['issued_date']
    if (datetime.now() - issued_date).days < 90:
        return {
            'message': 'This is a recent document - references may not be fully indexed yet',
            'suggestion': 'Check the document content manually for references'
        }
    
    # Check if references might be in content but not extracted
    content_sample = get_content_sample(document_id)
    if 'căn cứ' in content_sample.lower():
        return {
            'message': 'Document appears to have references, but they were not extracted',
            'suggestion': 'Use full content search to find references manually',
            'search_query': f'căn cứ trong {document_id}'
        }
    
    return {
        'message': 'No legal references found in this document',
        'note': 'This may be a standalone decision or internal document'
    }
```

### Edge Case 3: Circular References

```python
def detect_circular_references(starting_doc_id, max_depth=10):
    """
    Detect if there are circular reference chains
    """
    visited = []
    current_doc = starting_doc_id
    
    for depth in range(max_depth):
        if current_doc in visited:
            return {
                'circular': True,
                'chain': visited + [current_doc],
                'loop_point': visited.index(current_doc)
            }
        
        visited.append(current_doc)
        
        # Get parent references
        refs = get_legal_references(current_doc)
        if not refs:
            break
        
        # Follow first reference
        parent_id = find_document_by_number(refs[0]['number'])
        if not parent_id:
            break
        
        current_doc = parent_id
    
    return {
        'circular': False,
        'chain': visited
    }
```

---

## Integration with GraphRAG (If Available)

If FR03.3 has GraphRAG enabled, use it for complex relationship queries:

```python
def query_with_graphrag(question):
    """
    Use GraphRAG for complex legal relationship queries
    """
    
    # GraphRAG excels at:
    # - "Why does document A cite document B?"
    # - "What is the relationship between X and Y?"
    # - "Show me the legal reasoning chain"
    
    if is_complex_relationship_query(question):
        # Use GraphRAG endpoint
        response = requests.post(
            'http://localhost:8000/api/v1/graph/query',
            json={'query': question}
        )
        return response.json()
    
    # For simple lookups, use regular search
    else:
        return semantic_search(question)

def is_complex_relationship_query(question):
    """Detect if query needs GraphRAG"""
    indicators = [
        'why', 'tại sao',
        'relationship', 'mối quan hệ',
        'reasoning', 'lý do',
        'how does', 'làm thế nào',
        'connection', 'liên kết'
    ]
    return any(ind in question.lower() for ind in indicators)
```

---

## Complete Workflow Example

**User Query**: "Tôi muốn hiểu rõ cơ sở pháp lý và các văn bản liên quan đến việc thành lập quỹ phát triển khoa học công nghệ"

**Translation**: "I want to understand the legal basis and related documents about establishing science and technology development funds"

### Complete Solution:

```python
def comprehensive_legal_research(topic_query):
    """
    Comprehensive legal research workflow
    """
    results = {}
    
    # Step 1: Find primary regulations about topic
    print("🔍 Step 1: Finding primary regulations...")
    primary_docs = semantic_search(
        query=topic_query,
        filters={'document_type': 'Luật'},
        top_k=5
    )
    results['primary_laws'] = primary_docs
    
    # Step 2: For each primary law, find implementing documents
    print("📜 Step 2: Finding implementing documents...")
    results['implementing_docs'] = []
    
    for law in primary_docs[:2]:  # Top 2 laws
        law_number = law['document_number']
        
        # Find decrees
        decrees = semantic_search(
            query=f"thực hiện {law_number} {topic_query}",
            filters={'document_type': 'Nghị định'},
            top_k=5
        )
        
        # Find decisions
        decisions = semantic_search(
            query=f"căn cứ {law_number} {topic_query}",
            filters={'document_type': 'Quyết định'},
            top_k=10
        )
        
        results['implementing_docs'].append({
            'law': law,
            'decrees': decrees,
            'decisions': decisions
        })
    
    # Step 3: Extract all legal references
    print("🔗 Step 3: Extracting legal references...")
    results['reference_network'] = {}
    
    all_docs = primary_docs + \
                [d for impl in results['implementing_docs'] 
                 for d in impl['decrees'] + impl['decisions']]
    
    for doc in all_docs[:10]:  # Limit to top 10 to avoid overload
        refs = get_legal_references(doc['document_id'])
        results['reference_network'][doc['document_id']] = refs
    
    # Step 4: Build hierarchy
    print("📊 Step 4: Building legal hierarchy...")
    results['hierarchy'] = build_legal_hierarchy(results)
    
    # Step 5: Generate summary
    print("📝 Step 5: Generating summary...")
    results['summary'] = generate_legal_summary(results)
    
    return results

def generate_legal_summary(results):
    """Generate human-readable summary"""
    summary = []
    
    # Primary laws
    summary.append("🏛️ LUẬT CHÍNH (Primary Laws):")
    for i, law in enumerate(results['primary_laws'][:3], 1):
        summary.append(f"{i}. {law['title']}")
        summary.append(f"   - Issued: {law['issued_date']}")
    
    # Implementing documents count
    total_decrees = sum(len(impl['decrees']) 
                       for impl in results['implementing_docs'])
    total_decisions = sum(len(impl['decisions']) 
                         for impl in results['implementing_docs'])
    
    summary.append(f"\n📜 IMPLEMENTING DOCUMENTS:")
    summary.append(f"- {total_decrees} Decrees (Nghị định)")
    summary.append(f"- {total_decisions} Decisions (Quyết định)")
    
    # Reference network
    summary.append(f"\n🔗 REFERENCE NETWORK:")
    summary.append(f"- Analyzed {len(results['reference_network'])} documents")
    total_refs = sum(len(refs) for refs in results['reference_network'].values())
    summary.append(f"- Found {total_refs} legal references")
    
    return "\n".join(summary)

# Execute comprehensive research
if __name__ == "__main__":
    query = "thành lập quỹ phát triển khoa học công nghệ"
    results = comprehensive_legal_research(query)
    
    print("\n" + "="*60)
    print("COMPREHENSIVE LEGAL RESEARCH RESULTS")
    print("="*60)
    print(results['summary'])
    print("="*60)
```

**Expected Output**:

```
============================================================
COMPREHENSIVE LEGAL RESEARCH RESULTS
============================================================
🏛️ LUẬT CHÍNH (Primary Laws):
1. Luật Khoa học và Công nghệ số 50/2023/QH15
   - Issued: 2023-06-19
2. Luật Ngân sách Nhà nước số 15/2015/QH13
   - Issued: 2015-06-25
3. Luật Đầu tư số 61/2020/QH14
   - Issued: 2020-06-17

📜 IMPLEMENTING DOCUMENTS:
- 8 Decrees (Nghị định)
- 23 Decisions (Quyết định)

🔗 REFERENCE NETWORK:
- Analyzed 10 documents
- Found 47 legal references

📊 LEGAL HIERARCHY:
[Detailed hierarchy tree showing relationships]

💡 KEY FINDINGS:
- Primary legal basis: Law 50/2023/QH15 on Science and Technology
- Main implementing decree: Decree 13/2023/NĐ-CP
- Recent decision: Decision 635/QĐ-HĐQLQ (2024-12-31)
- Total relevant documents: 31

✅ Research complete - ready for detailed analysis
============================================================
```

---

## Quick Reference Card

### Query Type → Strategy Mapping

| User Query Type | Strategy | API Calls | Time |
|----------------|----------|-----------|------|
| "Căn cứ pháp lý" | find_legal_basis | 2-3 calls | ~500ms |
| "Quy định về X" | find_by_topic | 1-2 calls | ~300ms |
| "Văn bản liên quan" | find_related | 3-4 calls | ~800ms |
| "Lịch sử sửa đổi" | trace_evolution | 4-5 calls | ~1000ms |
| "Văn bản cụ thể" | find_specific | 1 call | ~200ms |

### Vietnamese Legal Terms Quick Reference

```
Luật           = Law (National Assembly)
Nghị định      = Decree (Government)
Quyết định     = Decision (Various authorities)
Thông tư       = Circular (Ministries)
Nghị quyết     = Resolution
Căn cứ         = Based on / Legal basis
Thực hiện      = Implementing
Sửa đổi        = Amending
Bổ sung        = Supplementing
Thay thế       = Replacing
Bãi bỏ         = Repealing
```

---

## Troubleshooting

### Issue: "Cannot find legal references"

**Debug**:
```bash
# Check if document has references in metadata
curl http://localhost:8000/api/v1/documents/$DOC_ID/references

# If empty, check content manually
curl http://localhost:8000/api/v1/documents/$DOC_ID/overview | jq '.overview.first_200_words'

# Search for "căn cứ" in content
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -d "{\"query\": \"căn cứ\", \"document_id\": \"$DOC_ID\"}"
```

### Issue: "Too many results for topic search"

**Solution**: Add filters and refine query

```python
# Instead of:
results = semantic_search("khoa học", top_k=50)  # Too broad!

# Do this:
results = semantic_search(
    query="quỹ phát triển khoa học công nghệ",  # More specific
    filters={
        'document_type': 'Quyết định',
        'issued_date_from': '2023-01-01'
    },
    top_k=10  # Reasonable limit
)
```

### Issue: "Search returns wrong document type"

**Solution**: Use explicit document type filtering

```python
# Find only Laws about science
laws_only = semantic_search(
    query="khoa học công nghệ",
    filters={'document_type': 'Luật'},
    top_k=5
)
```

---

## Summary

### Key Takeaways

1. **Understand hierarchy** - Vietnamese legal system has clear hierarchy
2. **Start with document type** - Laws → Decrees → Decisions → Circulars
3. **Use references API** - Extract legal foundations directly
4. **Follow citation chains** - Trace relationships up and down
5. **Optimize queries** - Use Vietnamese legal terms correctly
6. **Cache results** - Legal references don't change often
7. **Present clearly** - Users want hierarchical, visual results

### Strategy Priority

```
1. find_legal_basis        ⭐⭐⭐⭐⭐ (Most requested)
2. find_by_topic          ⭐⭐⭐⭐⭐ (Common search)
3. find_related           ⭐⭐⭐⭐   (Research)
4. find_specific_document ⭐⭐⭐⭐   (Direct lookup)
5. trace_evolution        ⭐⭐⭐     (Advanced)
```

---

## Version Information

- **Skill Version**: 1.0
- **FR03.3 Version**: R5.3 (Graph RAG + Document API)
- **Last Updated**: 29 January 2026
- **Focus**: Legal information retrieval and citation analysis
- **Language**: Vietnamese legal documents

---

## Additional Resources

- **API Skill**: `FR03_API_SKILL.md` (How to use APIs)
- **Main Docs**: `/mnt/project/CLAUDE.md`
- **GraphRAG**: `/mnt/project/GRAPH_RAG_SUMMARY.md`
- **Citations**: `/mnt/project/CITATION_INTEGRATION_SUMMARY_20Dec.md`

---

**End of FR03.3 Legal Information Retrieval Skill**

*Remember: Legal basis → References → Hierarchy → Clear presentation!*
