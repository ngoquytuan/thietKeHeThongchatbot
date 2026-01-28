# Vietnamese Graph RAG System Development Skill

## Overview
This skill enables Claude to assist with developing, testing, and upgrading a Graph RAG (Retrieval-Augmented Generation) system specifically designed for Vietnamese legal and corporate documents. The system (FR-03.1 v7) transforms Vietnamese bureaucratic documents into structured metadata packages enabling sophisticated graph-based relationships and contextual reasoning.

## Project Context

### System Architecture
- **Purpose**: Transform Vietnamese legal, administrative, HR, IT, and quality management documents into structured metadata packages
- **Classification**: 7-tier hierarchical system (Level 0: National Laws → Level 6: Individual Reports)
- **Storage**: PostgreSQL with JSONB for metadata, ChromaDB for vector embeddings, BM25 for hybrid indexing
- **Output Format**: passages.jsonl and document.json with 50+ metadata fields across 9 sections
- **Current Maturity**: 92-95% metadata completeness, 40% relationship extraction accuracy (target for improvement)

### Technology Stack
```python
# Core Technologies
- PostgreSQL with JSONB: Structured metadata storage
- ChromaDB: Vector embeddings storage
- BM25: Hybrid keyword-based indexing
- underthesea: Vietnamese NLP library
- Streamlit: UI interface for manual curation
- Python 3.8+: Core development language
```

### Vietnamese Document Types (5 Patterns)
1. **LEGAL_RND**: Legal and regulatory documents (nghị định, quyết định, thông tư)
2. **HR_POLICY**: HR policies and procedures
3. **IT_MANUAL**: IT manuals and technical documentation
4. **GEN_REPORT**: General reports (quarterly, annual, project reports)
5. **GENERAL**: Other administrative documents

## Core Components

### 1. MetadataEnricher Class
Handles Vietnamese-specific document processing with three extraction layers:
- **Regex patterns**: Structured field extraction
- **Keyword-based classification**: 77+ IT keywords, domain-specific vocabularies
- **Fuzzy matching**: Handles Vietnamese text variations

### 2. Metadata Structure (9 Main Sections)
```json
{
  "basic_info": "Document ID, title, type, classification level",
  "temporal": "Creation date, effective date, expiration",
  "governance": "Parent documents, related regulations",
  "personnel": "Authors, approvers, responsible parties",
  "organizational": "Department, organizational unit",
  "content_structure": "Sections, articles, clauses",
  "technical": "Technologies, systems mentioned",
  "projects": "Related projects, tasks",
  "relationships": "Supersedes, implements, references"
}
```

### 3. Current Challenges
- **Relationship Extraction**: Only 40% accuracy due to implicit relationships in Vietnamese bureaucratic culture
- **Missing Explicit Metadata**: Internal documents often lack formal document numbers, task codes, parent references
- **Cultural Context**: Relationships are culturally understood rather than textually stated

## Development Guidelines

### Vietnamese NLP Processing
When working with Vietnamese text:
```python
# Always use underthesea for Vietnamese tokenization
from underthesea import word_tokenize, pos_tag

# Vietnamese-specific patterns
VIET_PATTERNS = {
    'legal_doc_number': r'Số\s*[:：]\s*(\d+/[\w-]+)',
    'decision_number': r'Quyết định số\s*(\d+/QĐ-[\w-]+)',
    'regulation_number': r'Nghị định số\s*(\d+/NĐ-CP)',
    'date_format': r'ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})'
}

# Fuzzy matching for Vietnamese variations
from fuzzywuzzy import fuzz
threshold = 80  # Minimum similarity score
```

### Metadata Extraction Best Practices
1. **Pattern-Specific Extraction**: Use different extraction logic for each document type
2. **Confidence Scoring**: Always provide confidence indicators for auto-extracted fields
3. **Fallback Logic**: Implement multiple extraction strategies with fallbacks
4. **Validation**: Cross-validate extracted metadata against known patterns

```python
class MetadataEnricher:
    def extract_metadata(self, document):
        # Layer 1: Regex patterns
        basic_fields = self._extract_with_regex(document)
        
        # Layer 2: Keyword classification
        doc_type = self._classify_document(document)
        
        # Layer 3: Fuzzy matching
        relationships = self._extract_relationships_fuzzy(document)
        
        # Combine with confidence scores
        return self._merge_with_confidence(basic_fields, doc_type, relationships)
```

### Hybrid Workflow Design
The system uses a hybrid automated-manual approach:

```python
# Step 1: Automated extraction
auto_metadata = extractor.extract_metadata(document)

# Step 2: Confidence filtering
uncertain_fields = [f for f in auto_metadata if f.confidence < 0.7]

# Step 3: Manual review interface (Streamlit)
if uncertain_fields:
    confirmed_metadata = streamlit_ui.review_and_confirm(
        auto_metadata, 
        uncertain_fields,
        ml_suggestions=suggest_relationships(document)
    )
else:
    confirmed_metadata = auto_metadata

# Step 4: Save to PostgreSQL + ChromaDB
save_metadata(confirmed_metadata)
```

### Database Schema Patterns
```python
# PostgreSQL JSONB structure
metadata_schema = {
    "document_id": "UUID",
    "metadata": {
        "basic_info": {...},
        "governance": {
            "parent_documents": [],  # List of parent doc IDs
            "child_documents": [],   # List of child doc IDs
            "related_docs": [],      # Cross-references
            "supersedes": [],        # Documents this replaces
            "implemented_by": []     # Implementation documents
        },
        "extraction_confidence": {
            "parent_documents": 0.85,
            "document_type": 0.95,
            "effective_date": 0.90
        }
    },
    "vector_id": "ChromaDB reference",
    "bm25_index": "Search index reference"
}
```

## Testing Strategy

### Unit Testing
```python
import pytest

def test_document_type_detection():
    """Test detection of 5 Vietnamese document patterns"""
    samples = load_test_documents()
    for doc in samples:
        result = enricher.detect_document_type(doc)
        assert result.type in ['LEGAL_RND', 'HR_POLICY', 'IT_MANUAL', 'GEN_REPORT', 'GENERAL']
        assert result.confidence >= 0.0 and result.confidence <= 1.0

def test_metadata_completeness():
    """Ensure 92-95% completeness for basic fields"""
    metadata = enricher.extract_metadata(test_doc)
    required_fields = ['document_id', 'title', 'type', 'creation_date']
    completeness = sum(field in metadata for field in required_fields) / len(required_fields)
    assert completeness >= 0.92

def test_vietnamese_pattern_extraction():
    """Test extraction of Vietnamese-specific patterns"""
    text = "Quyết định số 123/QĐ-ABC ngày 15 tháng 10 năm 2024"
    result = enricher.extract_decision_number(text)
    assert result == "123/QĐ-ABC"
```

### Integration Testing
```python
def test_end_to_end_pipeline():
    """Test full pipeline: upload → extract → store → retrieve"""
    # 1. Upload document
    doc_id = upload_document("test_legal_doc.pdf")
    
    # 2. Extract metadata
    metadata = enricher.extract_metadata(doc_id)
    
    # 3. Store in PostgreSQL + ChromaDB
    store_metadata(doc_id, metadata)
    
    # 4. Verify retrieval
    retrieved = retrieve_metadata(doc_id)
    assert retrieved['basic_info']['title'] == metadata['basic_info']['title']
    
    # 5. Test graph traversal
    children = get_child_documents(doc_id)
    assert len(children) >= 0
```

### Relationship Extraction Testing
```python
def test_relationship_accuracy():
    """Target: Improve from 40% to 70%+ accuracy"""
    test_pairs = load_known_document_pairs()
    
    correct = 0
    for parent, child in test_pairs:
        predicted = enricher.extract_parent_document(child)
        if predicted == parent:
            correct += 1
    
    accuracy = correct / len(test_pairs)
    print(f"Relationship accuracy: {accuracy:.1%}")
    assert accuracy >= 0.40  # Current baseline
```

## Upgrade Priorities

### 1. Relationship Extraction Enhancement (Priority: HIGH)
**Current**: 40% accuracy
**Target**: 70%+ accuracy

Strategies:
- ML-based relationship suggestion using document embeddings similarity
- Historical pattern learning from manually confirmed relationships
- Cross-document context analysis
- Organizational hierarchy inference

```python
class RelationshipSuggester:
    def suggest_parent_documents(self, child_doc):
        """Use multiple signals to suggest parent documents"""
        # Signal 1: Vector similarity
        similar_docs = chromadb.similarity_search(child_doc.embedding, top_k=10)
        
        # Signal 2: Temporal logic (parent created before child)
        temporal_candidates = [d for d in similar_docs if d.date < child_doc.date]
        
        # Signal 3: Organizational hierarchy
        dept_docs = [d for d in temporal_candidates if d.department == child_doc.department]
        
        # Signal 4: Document type hierarchy
        valid_parents = [d for d in dept_docs if d.level < child_doc.level]
        
        # Rank by confidence
        return self._rank_suggestions(valid_parents, child_doc)
```

### 2. Metadata Editor UI (Priority: HIGH)
Streamlit-based interface for manual curation:

```python
import streamlit as st

def metadata_editor_ui(document, auto_metadata):
    st.title("Metadata Review & Confirmation")
    
    # Show document preview
    st.subheader("Document Content")
    st.text_area("Preview", document.content[:500], height=200)
    
    # Auto-extracted metadata with confidence
    st.subheader("Auto-Extracted Metadata")
    for field, value in auto_metadata.items():
        confidence = value.get('confidence', 1.0)
        color = "green" if confidence > 0.8 else "orange" if confidence > 0.5 else "red"
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.text_input(field, value.get('value', ''))
        with col2:
            st.markdown(f":{color}[{confidence:.0%}]")
        with col3:
            if confidence < 0.8:
                st.button("Edit", key=f"edit_{field}")
    
    # Relationship suggestions
    st.subheader("Suggested Parent Documents")
    suggestions = suggest_parent_documents(document)
    selected = st.multiselect(
        "Confirm parent documents",
        options=[s['title'] for s in suggestions],
        help="Select all relevant parent documents"
    )
    
    # Save button
    if st.button("Save Metadata"):
        save_confirmed_metadata(document.id, auto_metadata, selected)
        st.success("Metadata saved successfully!")
```

### 3. Manual Chunking Interface (Priority: MEDIUM)
Allow domain experts to define semantic boundaries:

```python
def manual_chunking_ui(document):
    """UI for selecting chunk boundaries"""
    st.subheader("Manual Chunking")
    
    # Show full text with line numbers
    lines = document.content.split('\n')
    for i, line in enumerate(lines):
        st.text(f"{i+1:4d} | {line}")
    
    # Let user select boundaries
    st.subheader("Define Chunk Boundaries")
    chunk_boundaries = st.multiselect(
        "Select line numbers for chunk starts",
        options=list(range(1, len(lines)+1))
    )
    
    # Preview chunks
    if chunk_boundaries:
        chunks = create_chunks(lines, chunk_boundaries)
        for i, chunk in enumerate(chunks):
            with st.expander(f"Chunk {i+1}"):
                st.text(chunk)
```

### 4. Performance Optimization (Priority: MEDIUM)
- Batch processing for multiple documents
- Caching for frequently accessed metadata
- Async processing for large documents
- Index optimization for graph traversal

```python
import asyncio
from functools import lru_cache

class OptimizedEnricher:
    @lru_cache(maxsize=100)
    def get_cached_metadata(self, doc_id):
        """Cache frequently accessed metadata"""
        return self._load_from_db(doc_id)
    
    async def batch_enrich(self, document_ids):
        """Process multiple documents concurrently"""
        tasks = [self.enrich_async(doc_id) for doc_id in document_ids]
        return await asyncio.gather(*tasks)
    
    def create_graph_indices(self):
        """Optimize graph traversal queries"""
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_parent_docs 
            ON documents USING GIN ((metadata->'governance'->'parent_documents'))
        """)
```

## Code Review Checklist

When reviewing or writing code for this project:

- [ ] **Vietnamese Text Handling**: Uses underthesea for tokenization
- [ ] **Pattern Matching**: Vietnamese-specific regex patterns are correct
- [ ] **Confidence Scoring**: All auto-extracted fields have confidence scores
- [ ] **Error Handling**: Graceful fallbacks for missing or malformed data
- [ ] **Database Schema**: Maintains JSONB structure compatibility
- [ ] **Vector Storage**: Proper ChromaDB integration with embeddings
- [ ] **Test Coverage**: Unit tests for all extraction functions
- [ ] **Documentation**: Inline comments for Vietnamese-specific logic
- [ ] **Performance**: Efficient queries for graph traversal
- [ ] **UI/UX**: Streamlit interface is intuitive for non-technical users

## Common Issues & Solutions

### Issue 1: Low Relationship Extraction Accuracy
**Symptom**: Parent-child relationships not detected
**Root Cause**: Vietnamese documents don't explicitly state relationships
**Solution**: Hybrid approach with ML suggestions + manual confirmation

### Issue 2: Vietnamese Encoding Problems
**Symptom**: Special characters display incorrectly
**Solution**: 
```python
# Always use UTF-8 encoding
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# PostgreSQL connection
conn = psycopg2.connect(
    host="localhost",
    database="rag_db",
    client_encoding='UTF8'
)
```

### Issue 3: Slow Graph Traversal
**Symptom**: Queries take >5 seconds for document hierarchies
**Solution**: Create GIN indices on JSONB fields
```sql
CREATE INDEX idx_governance ON documents 
USING GIN ((metadata->'governance'));
```

### Issue 4: Inconsistent Fuzzy Matching
**Symptom**: Same terms matched differently across documents
**Solution**: Normalize Vietnamese text before matching
```python
def normalize_vietnamese(text):
    """Normalize Vietnamese text for consistent matching"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Lowercase
    text = text.lower()
    # Remove Vietnamese tone marks if needed
    # text = unidecode(text)  # Optional: for tone-insensitive matching
    return text
```

## Development Workflow

### 1. Adding New Document Type
```python
# Step 1: Define pattern in MetadataEnricher
PATTERNS['NEW_TYPE'] = {
    'keywords': ['keyword1', 'keyword2'],
    'regex': r'pattern',
    'required_fields': ['field1', 'field2']
}

# Step 2: Implement extraction logic
def extract_new_type(self, document):
    # Extraction logic here
    pass

# Step 3: Add test cases
def test_new_type_extraction():
    # Test cases here
    pass

# Step 4: Update UI to handle new type
def render_new_type_fields(metadata):
    # UI rendering logic
    pass
```

### 2. Improving Relationship Detection
```python
# Step 1: Analyze failure cases
failed_pairs = get_failed_relationship_extractions()

# Step 2: Identify patterns
patterns = analyze_failure_patterns(failed_pairs)

# Step 3: Implement new detection strategy
def enhanced_relationship_detection(doc):
    # Use multiple signals
    signals = [
        signal_semantic_similarity(doc),
        signal_temporal_logic(doc),
        signal_organizational_hierarchy(doc),
        signal_content_reference(doc)
    ]
    return combine_signals(signals)

# Step 4: Validate improvement
new_accuracy = validate_on_test_set()
```

### 3. Adding New Metadata Field
```python
# Step 1: Update schema
METADATA_SCHEMA['new_section']['new_field'] = {
    'type': 'string',
    'required': False,
    'confidence_tracked': True
}

# Step 2: Add extraction logic
def extract_new_field(self, document):
    value = self._pattern_match(document, PATTERN_NEW_FIELD)
    confidence = self._calculate_confidence(value)
    return {'value': value, 'confidence': confidence}

# Step 3: Update database migration
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS new_field JSONB;

# Step 4: Update UI
st.text_input("New Field", metadata.get('new_field', ''))
```

## Performance Benchmarks

Current system performance (target metrics):
- Metadata extraction: <2 seconds per document
- Graph traversal (depth 3): <1 second
- Full-text search: <500ms
- Relationship suggestion: <3 seconds
- Batch processing: >100 documents/minute

## Vietnamese-Specific Considerations

### Language Patterns
Vietnamese legal documents follow specific patterns:
```python
VIETNAMESE_PATTERNS = {
    'formal_title': 'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM',
    'independence': 'Độc lập - Tự do - Hạnh phúc',
    'date_preamble': 'Căn cứ',
    'articles': 'Điều \d+',
    'clauses': 'Khoản \d+',
    'points': 'Điểm [a-z]',
    'decision': 'QUYẾT ĐỊNH',
    'regulation': 'NGHỊ ĐỊNH',
    'circular': 'THÔNG TƯ'
}
```

### Document Hierarchy
Understanding Vietnamese document authority levels:
```python
HIERARCHY_LEVELS = {
    0: ['Luật', 'Hiến pháp'],  # National laws
    1: ['Nghị định', 'Nghị quyết'],  # Government decrees
    2: ['Quyết định', 'Thông tư'],  # Ministerial decisions
    3: ['Chỉ thị', 'Hướng dẫn'],  # Directives
    4: ['Quy định nội bộ', 'Quy trình'],  # Internal regulations
    5: ['Báo cáo', 'Biên bản'],  # Reports
    6: ['Công văn', 'Giấy mời']  # Individual documents
}
```

## Integration Points

### PostgreSQL Integration
```python
import psycopg2
from psycopg2.extras import Json

def save_metadata(doc_id, metadata):
    with psycopg2.connect(DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO documents (id, metadata)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE 
                SET metadata = EXCLUDED.metadata
            """, (doc_id, Json(metadata)))
```

### ChromaDB Integration
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("legal_documents")

def add_to_chromadb(doc_id, text, metadata):
    collection.add(
        documents=[text],
        metadatas=[metadata],
        ids=[doc_id]
    )

def search_similar(query, top_k=5):
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return results
```

### BM25 Integration
```python
from rank_bm25 import BM25Okapi

def create_bm25_index(documents):
    tokenized_docs = [doc.split() for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)
    return bm25

def bm25_search(bm25_index, query, documents, top_k=5):
    tokenized_query = query.split()
    scores = bm25_index.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [documents[i] for i in top_indices]
```

## Success Criteria

The system is considered successful when:
1. ✅ Metadata completeness ≥95% for basic fields
2. 🔄 Relationship extraction accuracy ≥70% (currently 40%)
3. ✅ Vietnamese NLP processing handles all 5 document types
4. 🔄 Manual curation UI is intuitive for non-technical users
5. ✅ Graph traversal supports complex legal reasoning queries
6. ✅ System processes >100 documents/minute in batch mode
7. 🔄 Integration tests cover all critical workflows

## Quick Reference

### Essential Commands
```bash
# Run tests
pytest tests/ -v --cov=src

# Start Streamlit UI
streamlit run app.py

# Batch process documents
python scripts/batch_enrich.py --input /path/to/docs --output /path/to/output

# Database migrations
psql -U postgres -d rag_db -f migrations/001_add_indices.sql
```

### Key Files
- `metadata_extractor_v3.py`: Core extraction logic
- `vietnamese_cleaner.py`: Vietnamese text preprocessing
- `validator.py`: Metadata validation
- `app.py`: Streamlit UI main file
- `processor.py`: Document processing pipeline
- `config.json`: System configuration
- `labels_config.json`: Document type definitions

## Notes for Claude Code

When assisting with this project:
1. **Always consider Vietnamese text specifics**: encoding, tone marks, special patterns
2. **Prioritize relationship extraction improvements**: This is the current bottleneck
3. **Maintain backward compatibility**: Don't break existing PostgreSQL/ChromaDB schemas
4. **Test with real Vietnamese documents**: Don't rely only on synthetic examples
5. **Focus on hybrid workflows**: Balance automation with manual curation
6. **Document Vietnamese patterns**: Inline comments for cultural/linguistic context
7. **Optimize for graph traversal**: Efficient queries are critical for legal reasoning
8. **Consider domain expertise**: Legal documents require specialized knowledge

## End of Skill File
