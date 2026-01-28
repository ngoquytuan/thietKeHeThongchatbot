# FR03.3 Vietnamese Legal Document API Skill

**Purpose**: Guide LLM in selecting the optimal API endpoint for Vietnamese legal document retrieval and debugging common issues in FR03.3 system.

**System**: FR03.3 - Production Vietnamese Legal Document Search & RAG System
**Version**: R5.3 (Graph RAG + Document API)
**Last Updated**: 28 January 2026

---

## When to Use This Skill

Trigger this skill when:
- User asks to retrieve Vietnamese legal documents
- User needs to search within specific documents
- User wants to extract legal references or citations
- User needs to navigate through document chunks
- Debugging document retrieval issues
- Optimizing API calls for performance
- Building frontends for legal document display

**Keywords**: "FR03.3", "legal document", "văn bản pháp luật", "quyết định", "nghị định", "luật", "retrieve document", "get chunk", "search within document"

---

## Core Concepts

### 1. Document Structure in FR03.3

```
Document (Văn bản)
├── Metadata (document_id, title, document_number, issued_date)
├── Content (Full text, 500KB-2MB)
├── Chunks (Segments with position 0, 1, 2...)
│   ├── Chunk 0 (First chunk)
│   ├── Chunk 1 (Second chunk)
│   └── Chunk N (Last chunk)
└── References (Legal citations: 7 refs avg)
```

### 2. Database Configuration

```python
# Production Database (Updated 28 Jan 2026)
POSTGRES_HOST = "100.92.240.51"
POSTGRES_PORT = 5432
DATABASE = "chatbotR4"
USER = "kb_admin"

# Base URL
BASE_URL = "http://localhost:8000"

# ⚠️ OLD examples may show 192.168.1.88:15432 - ignore them!
```

### 3. Response Size Characteristics

| Endpoint | Response Size | Use Case | Speed |
|----------|--------------|----------|-------|
| `/overview` | 8 KB | Quick preview | ⚡ Fast (80-150ms) |
| `/references` | 3 KB | Legal citations | ⚡ Fast (100-200ms) |
| `/chunks/position/{n}` | 2-5 KB | Sequential reading | ⚡ Fast (80-150ms) |
| `/{id}` (metadata) | 1 KB | Basic info only | ⚡ Very fast (50-100ms) |
| `/content` | 500KB-2MB | Full document | 🐢 Slow (1-3s) |

---

## API Endpoint Decision Tree

### Step 1: What does the user need?

```
User Query Analysis:
├── "Show me document X" / "Tóm tắt văn bản Y"
│   └─→ Use /overview (Phase 1 Smart Overview)
│
├── "What laws does this cite?" / "Tham chiếu luật nào?"
│   └─→ Use /references (Legal Reference Extraction)
│
├── "Read chunk by chunk" / "Đọc từng đoạn"
│   └─→ Use /chunks/position/{n} (Position-based access)
│
├── "Search within document X" / "Tìm trong văn bản X"
│   └─→ Use POST /search/semantic with document_id filter
│
├── "Get full text" / "Lấy toàn bộ nội dung"
│   └─→ Use /content (⚠️ Large response)
│
└── "Document metadata only" / "Chỉ cần thông tin cơ bản"
    └─→ Use /{id} (Metadata only)
```

### Step 2: Performance Consideration

```python
# Quick preview needed? → /overview (8KB vs 2MB)
if need_quick_preview:
    endpoint = f"/documents/{doc_id}/overview"
    
# Need legal references? → /references (Fast)
elif need_citations:
    endpoint = f"/documents/{doc_id}/references"
    
# Sequential reading? → /chunks/position/{n} (Easy)
elif reading_chunk_by_chunk:
    endpoint = f"/documents/{doc_id}/chunks/position/{position}"
    
# Full document required? → /content (Slow but complete)
elif need_full_text:
    endpoint = f"/documents/{doc_id}/content"  # ⚠️ Large!
```

---

## 9 Essential Endpoints - Complete Guide

### 1. Smart Document Overview ⭐ **RECOMMENDED**

```bash
GET /api/v1/documents/{document_id}/overview
```

**When to use**:
- User asks: "Show me document X" / "Tóm tắt văn bản Y"
- Need quick preview before reading full document
- Building document list/preview UI
- Initial document inspection

**Response**: 8KB (62-250x smaller than full content!)

**Example**:
```bash
curl http://localhost:8000/api/v1/documents/7081963e-31b9-48fe-8f4d-088129377096/overview
```

**Response Structure**:
```json
{
  "success": true,
  "document_id": "7081963e-31b9-48fe-8f4d-088129377096",
  "title": "Quyết định số 635/QĐ-HĐQLQ...",
  "overview": {
    "first_200_words": "Nội dung đầu văn bản...",
    "last_100_words": "...kết thúc văn bản",
    "total_words": 2543,
    "total_chunks": 15,
    "key_metadata": {
      "document_number": "635/QĐ-HĐQLQ",
      "issued_date": "2024-12-31"
    }
  }
}
```

---

### 2. Legal References Extraction 📚

```bash
GET /api/v1/documents/{document_id}/references
```

**When to use**:
- User asks: "What laws does this cite?" / "Tham chiếu luật nào?"
- Need to show related legal documents
- Building legal reference network
- Citation analysis

**Response**: ~3KB with 7 references average

**Example**:
```bash
curl http://localhost:8000/api/v1/documents/7081963e-31b9-48fe-8f4d-088129377096/references
```

**Response Structure**:
```json
{
  "success": true,
  "document_id": "7081963e-31b9-48fe-8f4d-088129377096",
  "references": [
    {
      "type": "Luật",
      "number": "50/2023/QH15",
      "title": "Luật Khoa học và Công nghệ",
      "context": "Căn cứ Luật Khoa học và Công nghệ số 50/2023/QH15..."
    }
  ],
  "total_references": 7
}
```

---

### 3. Chunk by Position ⭐ **EASIEST ACCESS** (NEW 28 Jan)

```bash
GET /api/v1/documents/{document_id}/chunks/position/{position}
```

**When to use**:
- Sequential reading: position 0, 1, 2, 3...
- User says: "Read first chunk" / "Đọc đoạn đầu tiên"
- Building slider/navigation UI
- Paginated reading without knowing UUIDs

**Why better than UUID**:
- ✅ ONE step (vs 3 steps with UUID)
- ✅ Easy to remember: 0, 1, 2...
- ✅ No JSON parsing needed
- ✅ Sequential navigation: just increment position

**Example**:
```bash
# First chunk
curl http://localhost:8000/api/v1/documents/7081963e-31b9-48fe-8f4d-088129377096/chunks/position/0

# Second chunk
curl http://localhost:8000/api/v1/documents/7081963e-31b9-48fe-8f4d-088129377096/chunks/position/1

# Sequential reading loop
for i in {0..10}; do
  curl "http://localhost:8000/api/v1/documents/xxx/chunks/position/$i"
done
```

**Response**: 2-5 KB per chunk

---

### 4. Chunk by UUID (When you have it)

```bash
GET /api/v1/documents/{document_id}/chunks/{chunk_id}
```

**When to use**:
- Already have chunk_id from search results
- Direct link to specific chunk
- Bookmark/share specific chunk

**Example**:
```bash
curl http://localhost:8000/api/v1/documents/7081963e-31b9-48fe-8f4d-088129377096/chunks/abc123ef-4567-89ab-cdef-0123456789ab
```

---

### 5. Paginated Chunks List

```bash
GET /api/v1/documents/{document_id}/chunks?page={page}&size={size}
```

**When to use**:
- Building table/list UI
- Need multiple chunks at once
- Pagination with page numbers

**Example**:
```bash
# First 10 chunks
curl "http://localhost:8000/api/v1/documents/xxx/chunks?page=1&size=10"

# Next 10 chunks
curl "http://localhost:8000/api/v1/documents/xxx/chunks?page=2&size=10"
```

---

### 6. Search Within Document 🔍

```bash
POST /api/v1/search/semantic
```

**When to use**:
- User asks: "Find X in document Y" / "Tìm X trong văn bản Y"
- Search within specific document
- Focused search in known document

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quy định về khoa học công nghệ",
    "document_id": "7081963e-31b9-48fe-8f4d-088129377096",
    "top_k": 5
  }'
```

**Response**: Ranked chunks matching query within document

---

### 7. Full Document Content ⚠️

```bash
GET /api/v1/documents/{document_id}/content
```

**When to use**:
- User explicitly asks for full text
- Need complete content for processing
- Export/download full document

**⚠️ Warning**: 500KB-2MB response, 1-3 seconds

**Example**:
```bash
curl http://localhost:8000/api/v1/documents/7081963e-31b9-48fe-8f4d-088129377096/content > document.txt
```

---

### 8. Document Metadata Only

```bash
GET /api/v1/documents/{document_id}
```

**When to use**:
- Only need title, number, date
- Building document list
- Quick metadata check

**Response**: ~1KB

**Example**:
```bash
curl http://localhost:8000/api/v1/documents/7081963e-31b9-48fe-8f4d-088129377096
```

---

### 9. Health Check

```bash
GET /api/v1/health
```

**When to use**:
- Verify server is running
- Check database connectivity
- System status

**Example**:
```bash
curl http://localhost:8000/api/v1/health
```

---

## Common Patterns & Best Practices

### Pattern 1: Progressive Loading (Best UX)

```python
# Step 1: Quick overview (8KB, fast)
overview = get_overview(doc_id)
display_to_user(overview)

# Step 2: If user wants more, load references (3KB, fast)
if user_clicks_references:
    refs = get_references(doc_id)
    display_references(refs)

# Step 3: If user wants to read, load chunks by position
if user_clicks_read:
    for position in range(total_chunks):
        chunk = get_chunk_by_position(doc_id, position)
        display_chunk(chunk)
        if user_stops_reading:
            break

# Step 4: Only load full content if absolutely needed
if user_clicks_download_full:
    content = get_full_content(doc_id)  # ⚠️ Large
    download_file(content)
```

### Pattern 2: Search Then Retrieve

```python
# Step 1: Semantic search to find relevant documents
results = semantic_search("quy định về khoa học")

# Step 2: For each result, show overview (not full content!)
for doc in results[:5]:
    overview = get_overview(doc.document_id)
    display_in_list(overview)

# Step 3: When user clicks one document, show details
selected_doc = user_selection()
refs = get_references(selected_doc.id)
chunks = get_chunks_paginated(selected_doc.id, page=1)
```

### Pattern 3: Chunk Navigation UI

```python
# Build a slider/navigator
def chunk_navigator(doc_id, total_chunks):
    position = 0
    
    while True:
        # Load current chunk by position (easy!)
        chunk = get_chunk_by_position(doc_id, position)
        display(chunk)
        
        # Navigation
        if user_clicks_next and position < total_chunks - 1:
            position += 1
        elif user_clicks_prev and position > 0:
            position -= 1
        elif user_clicks_exit:
            break
```

---

## Debugging Guide

### Issue 1: "Document not found" (404)

**Symptoms**:
```json
{"detail": "Document with ID xxx not found"}
```

**Debug steps**:
```bash
# 1. Verify document_id format (must be UUID)
echo "7081963e-31b9-48fe-8f4d-088129377096" | grep -E '^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$'

# 2. Check if document exists in database
psql -h 100.92.240.51 -p 5432 -U kb_admin -d chatbotR4 -c \
  "SELECT document_id, title FROM documents WHERE document_id = '7081963e-31b9-48fe-8f4d-088129377096';"

# 3. List available documents
curl http://localhost:8000/api/v1/search/semantic -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "", "top_k": 10}'
```

**Solution**:
- Use valid UUID from database
- Check if document was imported correctly

---

### Issue 2: "Connection refused" or timeout

**Symptoms**:
```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Debug steps**:
```bash
# 1. Check if server is running
curl http://localhost:8000/api/v1/health

# 2. Check FastAPI logs
tail -f logs/fr03_3.log

# 3. Verify database connection
python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect(
        host='100.92.240.51',
        port=5432,
        user='kb_admin',
        password='1234567890',
        database='chatbotR4'
    )
    result = await conn.fetchval('SELECT COUNT(*) FROM documents')
    print(f'Documents: {result}')
    await conn.close()
asyncio.run(test())
"

# 4. Restart server
cd /path/to/FR03_3
./kill_fr03.bat
./01_startHere_run_FR03.3.bat
```

---

### Issue 3: "Chunk position not found" (404)

**Symptoms**:
```json
{"detail": "Chunk at position 999 not found in document xxx"}
```

**Debug steps**:
```bash
# 1. Get document overview to see total_chunks
curl http://localhost:8000/api/v1/documents/xxx/overview | jq '.overview.total_chunks'

# 2. List first page of chunks
curl "http://localhost:8000/api/v1/documents/xxx/chunks?page=1&size=10"

# 3. Query database directly
psql -h 100.92.240.51 -p 5432 -U kb_admin -d chatbotR4 -c \
  "SELECT COUNT(*), MAX(chunk_position) FROM document_chunks_enhanced WHERE document_id = 'xxx';"
```

**Solution**:
- Use position < total_chunks
- Valid range: 0 to (total_chunks - 1)

---

### Issue 4: Slow response from `/content`

**Symptoms**:
```
Response time: 3-5 seconds for /content endpoint
```

**Solution**:
```python
# ❌ BAD: Loading full content unnecessarily
def show_document(doc_id):
    content = get_full_content(doc_id)  # 2MB, 3 seconds
    return content

# ✅ GOOD: Use overview first
def show_document(doc_id):
    overview = get_overview(doc_id)  # 8KB, 150ms
    return overview

# ✅ GOOD: Progressive loading
def show_document_progressive(doc_id):
    # Quick preview
    overview = get_overview(doc_id)
    display(overview)
    
    # Load chunks only if needed
    if user_wants_full_read:
        for pos in range(overview['total_chunks']):
            chunk = get_chunk_by_position(doc_id, pos)
            display(chunk)
```

---

### Issue 5: Empty references list

**Symptoms**:
```json
{
  "success": true,
  "references": [],
  "total_references": 0
}
```

**Debug steps**:
```bash
# 1. Check if document has reference_metadata
curl http://localhost:8000/api/v1/documents/xxx/overview | jq '.document.reference_metadata'

# 2. Check database
psql -h 100.92.240.51 -p 5432 -U kb_admin -d chatbotR4 -c \
  "SELECT reference_metadata FROM documents WHERE document_id = 'xxx';"

# 3. Check if document was processed for references
psql -h 100.92.240.51 -p 5432 -U kb_admin -d chatbotR4 -c \
  "SELECT COUNT(*) FROM documents WHERE reference_metadata IS NOT NULL;"
```

**Solution**:
- Some documents may not cite other laws
- Re-import document with reference extraction enabled
- Check reference extraction pipeline

---

## Vietnamese Language Considerations

### Text Processing with underthesea and pyvi

```python
from underthesea import word_tokenize
from pyvi import ViTokenizer

# Vietnamese word segmentation
text = "Luật Khoa học và Công nghệ"
tokens = word_tokenize(text)  # ['Luật', 'Khoa_học', 'và', 'Công_nghệ']

# Remove accents for search (handled by FR03.3)
# "Quyết định" → "Quyet dinh"
```

### Common Vietnamese Legal Terms

```python
LEGAL_DOCUMENT_TYPES = [
    "Luật",           # Law
    "Nghị định",      # Decree
    "Thông tư",       # Circular
    "Quyết định",     # Decision
    "Chỉ thị",        # Directive
    "Nghị quyết",     # Resolution
]

# Document number patterns
# Example: "635/QĐ-HĐQLQ"
# Format: number/type-organization
```

---

## Performance Optimization Tips

### 1. Cache Frequently Accessed Documents

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_overview_cached(doc_id: str):
    return get_overview(doc_id)

# Use cached version for repeated access
overview = get_overview_cached(doc_id)
```

### 2. Parallel Requests for Multiple Documents

```python
import asyncio
import aiohttp

async def get_multiple_overviews(doc_ids: list):
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_overview(session, doc_id) 
            for doc_id in doc_ids
        ]
        return await asyncio.gather(*tasks)

# 10x faster than sequential
overviews = await get_multiple_overviews(doc_ids)
```

### 3. Use Position-based Access for Sequential Reading

```python
# ❌ SLOW: Get all chunks then iterate
all_chunks = get_all_chunks(doc_id)  # Loads everything
for chunk in all_chunks:
    display(chunk)

# ✅ FAST: Load on demand by position
for position in range(total_chunks):
    chunk = get_chunk_by_position(doc_id, position)
    display(chunk)
    if user_stops:
        break  # Save bandwidth!
```

---

## Example Code: Complete Document Viewer

```python
import requests
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"

class DocumentViewer:
    """FR03.3 Vietnamese Legal Document Viewer"""
    
    def __init__(self, document_id: str):
        self.document_id = document_id
        self.base_url = BASE_URL
    
    def show_overview(self):
        """Step 1: Quick preview (8KB)"""
        url = f"{self.base_url}/documents/{self.document_id}/overview"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 {data['title']}")
            print(f"📊 Total words: {data['overview']['total_words']}")
            print(f"📚 Total chunks: {data['overview']['total_chunks']}")
            print(f"\n📖 Preview:")
            print(data['overview']['first_200_words'])
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            return None
    
    def show_references(self):
        """Step 2: Legal references (3KB)"""
        url = f"{self.base_url}/documents/{self.document_id}/references"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n🔗 Legal References ({data['total_references']}):")
            for ref in data['references']:
                print(f"  - {ref['type']} {ref['number']}: {ref['title']}")
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            return None
    
    def read_chunks(self, start: int = 0, end: Optional[int] = None):
        """Step 3: Read chunks by position"""
        # Get total chunks
        overview = self.show_overview()
        total_chunks = overview['overview']['total_chunks']
        
        if end is None:
            end = total_chunks
        
        print(f"\n📖 Reading chunks {start} to {end-1}:")
        for position in range(start, min(end, total_chunks)):
            url = f"{self.base_url}/documents/{self.document_id}/chunks/position/{position}"
            response = requests.get(url)
            
            if response.status_code == 200:
                chunk = response.json()['chunk']
                print(f"\n--- Chunk {position} ---")
                print(chunk['content'][:200] + "...")
            else:
                print(f"❌ Chunk {position} error: {response.status_code}")
                break
    
    def search_within(self, query: str, top_k: int = 5):
        """Step 4: Search within document"""
        url = f"{self.base_url}/search/semantic"
        payload = {
            "query": query,
            "document_id": self.document_id,
            "top_k": top_k
        }
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            results = response.json()
            print(f"\n🔍 Search results for '{query}':")
            for i, result in enumerate(results['results'], 1):
                print(f"{i}. Score: {result['score']:.3f}")
                print(f"   {result['content'][:150]}...")
            return results
        else:
            print(f"❌ Error: {response.status_code}")
            return None

# Usage example
if __name__ == "__main__":
    doc_id = "7081963e-31b9-48fe-8f4d-088129377096"
    viewer = DocumentViewer(doc_id)
    
    # Progressive loading
    viewer.show_overview()           # Quick preview
    viewer.show_references()         # Legal citations
    viewer.read_chunks(0, 3)        # First 3 chunks
    viewer.search_within("khoa học công nghệ")  # Search
```

---

## Testing & Verification

### Quick Test Suite

```bash
#!/bin/bash
# test_fr03_api.sh

DOC_ID="7081963e-31b9-48fe-8f4d-088129377096"
BASE_URL="http://localhost:8000/api/v1"

echo "🧪 Testing FR03.3 API Endpoints..."

# Test 1: Health check
echo "1. Health check..."
curl -s "$BASE_URL/health" | jq '.status'

# Test 2: Document overview
echo "2. Document overview..."
curl -s "$BASE_URL/documents/$DOC_ID/overview" | jq '.success'

# Test 3: References
echo "3. Legal references..."
curl -s "$BASE_URL/documents/$DOC_ID/references" | jq '.total_references'

# Test 4: Chunk by position
echo "4. First chunk (position 0)..."
curl -s "$BASE_URL/documents/$DOC_ID/chunks/position/0" | jq '.chunk.position'

# Test 5: Search within document
echo "5. Search within document..."
curl -s -X POST "$BASE_URL/search/semantic" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"khoa học\", \"document_id\": \"$DOC_ID\", \"top_k\": 3}" \
  | jq '.results | length'

echo "✅ All tests complete!"
```

### Python Test Suite

```python
# test_document_api.py (included in FR03.3)
python test_document_api.py

# Expected output:
# ✅ Test 1 (References): PASS
# ✅ Test 2 (Content): PASS  
# ✅ Test 3 (Overview - Phase 1): PASS
# ✅ Test 4 (Info): PASS
# ✅ Test 5 (Chunks Paginated - Phase 2): PASS
# ✅ Test 6 (Chunk by Position - Phase 2): PASS
# ✅ Test 7 (Chunk by UUID - Phase 2): PASS
# 🎉 All tests passed!
```

---

## Quick Reference Card

### Endpoint Selection Cheatsheet

| User Request | Endpoint | Response Size | Speed |
|-------------|----------|---------------|-------|
| "Show document" | `/overview` | 8 KB | ⚡ 80-150ms |
| "What laws cited?" | `/references` | 3 KB | ⚡ 100-200ms |
| "Read first chunk" | `/chunks/position/0` | 2-5 KB | ⚡ 80-150ms |
| "Search in doc" | `/search/semantic` | Varies | ⚡ 300-500ms |
| "Full text" | `/content` | 500KB-2MB | 🐢 1-3s |

### API URLs

```bash
# Base
http://localhost:8000/api/v1

# Document endpoints
/documents/{id}/overview          # ⭐ Best for preview
/documents/{id}/references        # Legal citations
/documents/{id}/content           # ⚠️ Large response
/documents/{id}                   # Metadata only
/documents/{id}/chunks/position/{n}  # ⭐ Easy access
/documents/{id}/chunks/{chunk_id} # UUID-based
/documents/{id}/chunks?page=X     # Paginated list

# Search
/search/semantic                  # POST with body

# System
/health                          # Server status
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Loading full content when overview is enough

```python
# BAD
content = get_content(doc_id)  # 2MB, 3 seconds
display(content[:500])  # Only showing 500 chars!

# GOOD
overview = get_overview(doc_id)  # 8KB, 150ms
display(overview['first_200_words'])
```

### ❌ Mistake 2: Using UUID when position is easier

```python
# BAD - 3 steps
chunks_list = get_chunks_list(doc_id)
first_chunk_uuid = chunks_list[0]['chunk_id']
chunk = get_chunk_by_uuid(doc_id, first_chunk_uuid)

# GOOD - 1 step
chunk = get_chunk_by_position(doc_id, 0)
```

### ❌ Mistake 3: Sequential API calls instead of parallel

```python
# BAD - Sequential (slow)
for doc_id in doc_ids:
    overview = get_overview(doc_id)  # 150ms each
    process(overview)
# Total: 150ms × 10 = 1.5 seconds

# GOOD - Parallel (fast)
import asyncio
overviews = await asyncio.gather(*[
    get_overview_async(doc_id) for doc_id in doc_ids
])
# Total: ~150ms for all 10!
```

### ❌ Mistake 4: Using wrong database host

```python
# ❌ OLD (from old examples)
POSTGRES_HOST = "192.168.1.88"
POSTGRES_PORT = 15432

# ✅ CURRENT (updated 28 Jan 2026)
POSTGRES_HOST = "100.92.240.51"
POSTGRES_PORT = 5432
```

### ❌ Mistake 5: Not handling Vietnamese text properly

```python
# ❌ BAD - Ignoring Vietnamese diacritics
query = "khoa hoc"  # Missing accents

# ✅ GOOD - Proper Vietnamese
query = "khoa học"  # With accents

# ✅ GOOD - FR03.3 handles accent removal internally
# You can pass either "khoa học" or "khoa hoc" - both work!
```

---

## Integration Examples

### Example 1: Chatbot Integration

```python
def chatbot_handle_document_query(user_message: str):
    """
    Handle user queries about legal documents in a chatbot
    """
    # Extract document ID from context or search
    if "show document" in user_message.lower():
        doc_id = extract_doc_id(user_message)
        
        # Quick preview
        overview = get_overview(doc_id)
        return format_overview_message(overview)
    
    elif "legal references" in user_message.lower():
        doc_id = extract_doc_id(user_message)
        
        # Get references
        refs = get_references(doc_id)
        return format_references_message(refs)
    
    elif "search for" in user_message.lower():
        doc_id = extract_doc_id(user_message)
        query = extract_search_query(user_message)
        
        # Search within document
        results = search_within_document(doc_id, query)
        return format_search_results(results)
```

### Example 2: Web UI Integration

```javascript
// React component for document viewer
import { useState, useEffect } from 'react';

function DocumentViewer({ documentId }) {
  const [overview, setOverview] = useState(null);
  const [currentChunk, setCurrentChunk] = useState(0);
  const [chunk, setChunk] = useState(null);
  
  // Load overview on mount
  useEffect(() => {
    fetch(`http://localhost:8000/api/v1/documents/${documentId}/overview`)
      .then(r => r.json())
      .then(data => setOverview(data));
  }, [documentId]);
  
  // Load chunk when position changes
  useEffect(() => {
    if (overview) {
      fetch(`http://localhost:8000/api/v1/documents/${documentId}/chunks/position/${currentChunk}`)
        .then(r => r.json())
        .then(data => setChunk(data.chunk));
    }
  }, [currentChunk, overview]);
  
  return (
    <div>
      {overview && (
        <>
          <h1>{overview.title}</h1>
          <p>Words: {overview.overview.total_words}</p>
          <p>Chunks: {overview.overview.total_chunks}</p>
        </>
      )}
      
      {chunk && (
        <>
          <div>{chunk.content}</div>
          <button 
            disabled={currentChunk === 0}
            onClick={() => setCurrentChunk(c => c - 1)}
          >
            Previous
          </button>
          <button 
            disabled={currentChunk >= overview.overview.total_chunks - 1}
            onClick={() => setCurrentChunk(c => c + 1)}
          >
            Next
          </button>
        </>
      )}
    </div>
  );
}
```

---

## Troubleshooting Flowchart

```
API Call Failed?
├─ Status 404 Not Found
│  ├─ Check document_id is valid UUID
│  ├─ Verify document exists in database
│  └─ Check chunk position < total_chunks
│
├─ Status 500 Internal Server Error
│  ├─ Check server logs: tail -f logs/fr03_3.log
│  ├─ Verify database connection: psql -h 100.92.240.51 -p 5432
│  └─ Restart server: ./kill_fr03.bat && ./01_startHere_run_FR03.3.bat
│
├─ Connection Refused
│  ├─ Check server is running: curl localhost:8000/health
│  ├─ Check port 8000 is not blocked
│  └─ Start server: ./01_startHere_run_FR03.3.bat
│
├─ Slow Response (>3s)
│  ├─ Using /content? → Switch to /overview
│  ├─ Sequential calls? → Use asyncio.gather()
│  └─ Check database performance: EXPLAIN ANALYZE query
│
└─ Empty Results
   ├─ Check document has content: get_overview()
   ├─ Verify reference_metadata exists
   └─ Check search query is not too specific
```

---

## Summary

### Key Takeaways

1. **Use `/overview` by default** - 62-250x smaller than full content
2. **Use position-based chunk access** - Much easier than UUIDs
3. **Avoid `/content` unless necessary** - It's slow and large
4. **Progressive loading** - Show overview first, details on demand
5. **Handle Vietnamese properly** - FR03.3 handles accent removal
6. **Use correct database** - 100.92.240.51:5432 (not old host)
7. **Cache frequently accessed documents** - Better performance
8. **Parallel requests** - Use asyncio for multiple documents

### Endpoint Priority

```
1. /overview           ⭐⭐⭐⭐⭐ (Use first!)
2. /references         ⭐⭐⭐⭐⭐ (Fast & useful)
3. /chunks/position/{n} ⭐⭐⭐⭐⭐ (Easier than UUID)
4. /search/semantic    ⭐⭐⭐⭐ (Powerful search)
5. /{id} (metadata)    ⭐⭐⭐ (Basic info only)
6. /chunks/{uuid}      ⭐⭐⭐ (When you have UUID)
7. /chunks?page=X      ⭐⭐ (Pagination)
8. /content            ⭐ (Last resort, slow)
```

---

## Version Information

- **Skill Version**: 1.0
- **FR03.3 Version**: R5.3 (Graph RAG + Document API)
- **Last Updated**: 28 January 2026
- **Document API Phase**: Phase 1 Complete ✅
- **New Features**: Position-based chunk access (28 Jan 2026)

---

## Additional Resources

- **Main Documentation**: `/mnt/project/CLAUDE.md`
- **API Guide**: `/mnt/project/docs/DOCUMENT_API_GUIDE.md`
- **Phase 1 Summary**: `/mnt/project/PHASE1_COMPLETE_SUMMARY.md`
- **Enhancement Guide**: `/mnt/project/ENHANCEMENT_CHUNK_BY_POSITION_28Jan.md`
- **Test File**: `/mnt/project/test_document_api.py`

---

**End of FR03.3 API Skill Guide**

*Remember: Start with `/overview`, use position-based chunks, avoid `/content` unless necessary!*
