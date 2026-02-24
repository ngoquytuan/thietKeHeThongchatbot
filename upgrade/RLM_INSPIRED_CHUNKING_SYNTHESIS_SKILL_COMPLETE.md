# SKILL: RLM-Inspired Intelligent Chunking & Context Synthesis

**Version**: 1.0  
**Created**: 31 January 2026  
**Last Updated**: 31 January 2026  
**Author**: Claude (based on RLM research - Zhang et al. 2025)  
**Target**: ATTECH Vietnamese Legal Document RAG System

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [When to Use This Skill](#when-to-use-this-skill)
3. [Core Principles from RLM](#core-principles-from-rlm)
4. [Technique 1: Adaptive Chunking](#technique-1-adaptive-chunking)
5. [Technique 2: Hierarchical Context Management](#technique-2-hierarchical-context-management)
6. [Technique 3: Progressive Context Loading](#technique-3-progressive-context-loading)
7. [Technique 4: Intelligent Context Synthesis](#technique-4-intelligent-context-synthesis)
8. [Technique 5: Multi-hop Context Navigation](#technique-5-multi-hop-context-navigation)
9. [Implementation Patterns](#implementation-patterns)
10. [Anti-patterns to Avoid](#anti-patterns-to-avoid)
11. [Testing & Validation](#testing--validation)
12. [Vietnamese-Specific Considerations](#vietnamese-specific-considerations)

---

## OVERVIEW

### What is This Skill?

This skill provides **RLM-inspired techniques** for building intelligent document chunking and context synthesis systems, specifically optimized for Vietnamese legal documents. Rather than implementing full RLM (which requires complex sandboxing), we extract the **core principles and patterns** that made RLM successful.

### Key Insights from RLM Research

RLM achieved **110% accuracy improvement** over GPT-5 by:

1. **Treating context as explorable data** (not fixed chunks)
2. **Adaptive partitioning** based on document structure
3. **Progressive information loading** (peek → analyze → recurse)
4. **Multi-hop reasoning** through programmatic navigation
5. **Hierarchical synthesis** (bottom-up aggregation)

### What You'll Learn

- ✅ How to chunk documents **intelligently** based on structure (not fixed sizes)
- ✅ How to **progressively load context** like RLM does
- ✅ How to implement **multi-hop reasoning** without full recursion
- ✅ How to **synthesize context** from multiple sources efficiently
- ✅ Best practices for **Vietnamese legal documents**

---

## WHEN TO USE THIS SKILL

### ✅ Use This Skill When:

1. **Building chunking pipelines** for long documents (>10K tokens)
2. **Implementing RAG retrieval** with complex documents
3. **Synthesizing information** from multiple document sources
4. **Handling Vietnamese legal documents** with hierarchical structure
5. **Optimizing context window usage** for LLM calls
6. **Building multi-hop reasoning** systems

### ❌ Don't Use This Skill For:

1. Simple fixed-size chunking (use standard libraries)
2. Short documents (<2K tokens)
3. Real-time streaming applications (too much preprocessing)
4. Non-structured documents (blogs, social media, etc.)

### 🎯 Perfect For ATTECH Project:

- ✅ Vietnamese legal documents (highly structured)
- ✅ Long documents (Nghị định, Thông tư: 50-300 pages)
- ✅ Multi-hop queries (comparing laws, finding relationships)
- ✅ Graph RAG integration (document relationships)

---

## CORE PRINCIPLES FROM RLM

### Principle 1: Context is Explorable Data

**RLM Insight:**
> "Don't treat context as a monolithic block. Treat it as a data structure you can explore programmatically."

**Application:**
```python
# ❌ BAD: Traditional approach
def chunk_document(text: str, chunk_size: int = 512):
    """Fixed-size chunking - loses structure"""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks

# ✅ GOOD: RLM-inspired approach
class DocumentExplorer:
    """Treat document as explorable structure"""
    
    def __init__(self, text: str):
        self.text = text
        self.structure = self._analyze_structure()
        self.index = self._build_index()
    
    def _analyze_structure(self) -> Dict:
        """Understand document hierarchy"""
        return {
            'chapters': self._find_chapters(),
            'articles': self._find_articles(),
            'sections': self._find_sections(),
            'references': self._find_cross_references()
        }
    
    def peek(self, start: int, length: int) -> str:
        """Peek at specific region"""
        return self.text[start:start+length]
    
    def get_section(self, section_id: str) -> str:
        """Get specific logical section"""
        return self.index[section_id]
    
    def find_related(self, query: str) -> List[str]:
        """Find sections related to query"""
        # Use both semantic and structural search
        pass
```

### Principle 2: Adaptive Partitioning

**RLM Insight:**
> "Let document structure determine chunk boundaries, not arbitrary token counts."

**Application:**
```python
class AdaptiveChunker:
    """Chunk based on document structure"""
    
    LEGAL_DOC_PATTERNS = {
        'chapter': r'Chương\s+[IVX]+',
        'article': r'Điều\s+\d+',
        'section': r'Khoản\s+\d+',
        'point': r'[a-z]\)',
    }
    
    def chunk(self, document: str) -> List[Dict]:
        """
        Create semantic chunks respecting structure
        
        Returns chunks with metadata about their position in hierarchy
        """
        chunks = []
        
        # 1. Parse structure
        structure = self._parse_structure(document)
        
        # 2. Create chunks at appropriate levels
        for article in structure['articles']:
            # Each article = 1 chunk (or multiple if >2K tokens)
            chunk = self._create_article_chunk(article)
            
            # Attach hierarchical context
            chunk['metadata'] = {
                'chapter': article.parent_chapter,
                'article_number': article.number,
                'contains_sections': len(article.sections),
                'hierarchy_level': 'article'
            }
            chunks.append(chunk)
        
        return chunks
    
    def _create_article_chunk(self, article: Article) -> Dict:
        """
        Create chunk with context preservation
        """
        # Include parent context (chapter title)
        context_prefix = f"Chương {article.parent_chapter.number}: {article.parent_chapter.title}\n"
        
        # Main content
        main_content = f"Điều {article.number}. {article.title}\n{article.content}"
        
        # If article has many sections, split intelligently
        if len(article.content) > 2000:  # tokens
            return self._split_large_article(article)
        
        return {
            'text': context_prefix + main_content,
            'article': article
        }
```

### Principle 3: Progressive Information Loading

**RLM Insight:**
> "Don't load everything at once. Start with overview, then drill down as needed."

**Application:**
```python
class ProgressiveLoader:
    """
    Load context progressively like RLM does:
    1. Peek at structure
    2. Load relevant sections
    3. Expand if needed
    """
    
    def __init__(self, document_store):
        self.store = document_store
    
    async def load_context_for_query(
        self, 
        query: str,
        initial_budget: int = 4000  # tokens
    ) -> Dict:
        """
        Progressively load context
        
        Mimics RLM's peek → analyze → recurse pattern
        """
        context = {
            'overview': None,
            'relevant_sections': [],
            'deep_sections': [],
            'total_tokens': 0
        }
        
        # STEP 1: PEEK - Load document overview (table of contents)
        toc = await self._load_table_of_contents()
        context['overview'] = toc
        context['total_tokens'] += len(toc.split())
        
        # STEP 2: ANALYZE - Identify relevant chapters/articles
        relevant_ids = self._identify_relevant_sections(query, toc)
        
        # STEP 3: LOAD - Get those sections (with budget)
        budget_remaining = initial_budget - context['total_tokens']
        
        for section_id in relevant_ids:
            if budget_remaining <= 0:
                break
            
            section = await self._load_section(section_id)
            section_tokens = len(section.split())
            
            if section_tokens <= budget_remaining:
                context['relevant_sections'].append(section)
                context['total_tokens'] += section_tokens
                budget_remaining -= section_tokens
        
        # STEP 4: EXPAND if needed (for complex queries)
        if self._needs_deep_context(query):
            # Load additional context for cross-references
            expanded = await self._expand_context(
                context['relevant_sections'],
                budget_remaining
            )
            context['deep_sections'] = expanded
        
        return context
    
    def _needs_deep_context(self, query: str) -> bool:
        """
        Determine if query needs multi-hop reasoning
        """
        multi_hop_indicators = [
            'so sánh', 'khác biệt', 'liên quan',
            'tất cả', 'danh sách', 'tổng hợp'
        ]
        return any(indicator in query.lower() for indicator in multi_hop_indicators)
```

### Principle 4: Hierarchical Synthesis

**RLM Insight:**
> "Synthesize information bottom-up: section → article → chapter → document"

**Application:**
```python
class HierarchicalSynthesizer:
    """
    Synthesize context hierarchically like RLM
    """
    
    async def synthesize_multi_hop(
        self,
        query: str,
        documents: List[Document]
    ) -> Dict:
        """
        Multi-hop synthesis following RLM pattern:
        1. Extract from each document (parallel)
        2. Aggregate at article level
        3. Synthesize at document level
        4. Final cross-document synthesis
        """
        
        # LEVEL 1: Extract from individual sections
        section_extracts = await asyncio.gather(*[
            self._extract_from_section(query, section)
            for doc in documents
            for section in doc.sections
        ])
        
        # LEVEL 2: Aggregate by article
        article_summaries = {}
        for extract in section_extracts:
            article_id = extract['article_id']
            if article_id not in article_summaries:
                article_summaries[article_id] = []
            article_summaries[article_id].append(extract)
        
        # Synthesize each article
        article_results = await asyncio.gather(*[
            self._synthesize_article(query, extracts)
            for article_id, extracts in article_summaries.items()
        ])
        
        # LEVEL 3: Aggregate by document
        doc_summaries = {}
        for result in article_results:
            doc_id = result['document_id']
            if doc_id not in doc_summaries:
                doc_summaries[doc_id] = []
            doc_summaries[doc_id].append(result)
        
        # Synthesize each document
        doc_results = await asyncio.gather(*[
            self._synthesize_document(query, results)
            for doc_id, results in doc_summaries.items()
        ])
        
        # LEVEL 4: Final cross-document synthesis
        final_answer = await self._synthesize_final(
            query, 
            doc_results
        )
        
        return {
            'answer': final_answer,
            'supporting_evidence': doc_results,
            'synthesis_tree': self._build_synthesis_tree(
                section_extracts, 
                article_results, 
                doc_results
            )
        }
    
    async def _extract_from_section(
        self, 
        query: str, 
        section: Section
    ) -> Dict:
        """
        Extract relevant info from a single section
        Uses smaller LLM (like RLM uses GPT-5-mini)
        """
        prompt = f"""
        Trích xuất thông tin liên quan đến câu hỏi từ đoạn văn bản sau.
        
        Câu hỏi: {query}
        
        Văn bản:
        {section.text}
        
        Trả lời JSON:
        {{
            "relevant": true/false,
            "extracted_info": "...",
            "citation": {{"article": "...", "section": "..."}}
        }}
        """
        
        # Use cheap model for extraction
        response = await self.llm_mini.complete(prompt)
        return json.loads(response)
```

### Principle 5: Smart Context Windowing

**RLM Insight:**
> "Keep context window clean by only loading what's needed at each reasoning step."

**Application:**
```python
class SmartContextWindow:
    """
    Manage LLM context window intelligently
    """
    
    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens
        self.current_tokens = 0
        self.context_stack = []
    
    def add_context(
        self, 
        content: str, 
        priority: int = 5,
        metadata: Dict = None
    ):
        """
        Add content with priority
        Higher priority = less likely to be evicted
        """
        tokens = self._count_tokens(content)
        
        item = {
            'content': content,
            'tokens': tokens,
            'priority': priority,
            'metadata': metadata or {},
            'added_at': time.time()
        }
        
        # If adding this would exceed limit, evict low-priority items
        while self.current_tokens + tokens > self.max_tokens:
            self._evict_lowest_priority()
        
        self.context_stack.append(item)
        self.current_tokens += tokens
    
    def _evict_lowest_priority(self):
        """
        Evict item with lowest priority (and oldest if tie)
        """
        if not self.context_stack:
            raise ValueError("Cannot evict from empty context")
        
        # Sort by priority (ascending) and age (ascending)
        self.context_stack.sort(
            key=lambda x: (x['priority'], x['added_at'])
        )
        
        evicted = self.context_stack.pop(0)
        self.current_tokens -= evicted['tokens']
    
    def get_context_for_llm(self) -> str:
        """
        Return context formatted for LLM
        Highest priority items first
        """
        self.context_stack.sort(
            key=lambda x: x['priority'], 
            reverse=True
        )
        
        return "\n\n".join([
            item['content'] 
            for item in self.context_stack
        ])
    
    def get_usage_stats(self) -> Dict:
        """
        Get statistics about context usage
        """
        return {
            'total_tokens': self.current_tokens,
            'max_tokens': self.max_tokens,
            'utilization': self.current_tokens / self.max_tokens,
            'items_count': len(self.context_stack),
            'priority_distribution': self._get_priority_dist()
        }
```

---

## TECHNIQUE 1: ADAPTIVE CHUNKING

### Overview

Adaptive chunking respects document structure rather than blindly splitting at fixed token counts. For Vietnamese legal documents, this means chunking at natural boundaries (Điều, Khoản, etc.).

### Implementation

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
import re

@dataclass
class LegalDocumentChunk:
    """
    Semantic chunk for legal documents
    """
    chunk_id: str
    text: str
    
    # Hierarchy
    chapter_number: Optional[int] = None
    chapter_title: Optional[str] = None
    article_number: Optional[int] = None
    article_title: Optional[str] = None
    section_number: Optional[int] = None
    
    # Metadata
    document_id: str = ""
    law_id: str = ""
    hierarchy_level: str = ""  # 'chapter', 'article', 'section'
    
    # Context
    parent_context: str = ""  # Brief parent section info
    child_count: int = 0  # Number of child sections
    
    # Tokens
    token_count: int = 0
    
    # Relationships
    references: List[str] = None  # Other articles referenced
    
    def __post_init__(self):
        if self.references is None:
            self.references = []

class AdaptiveChunkerForVietnameseLaw:
    """
    Adaptive chunking specifically for Vietnamese legal documents
    
    Based on RLM principles:
    1. Respect document structure
    2. Preserve hierarchical context
    3. Keep semantic units together
    """
    
    # Vietnamese legal document patterns
    PATTERNS = {
        'chapter': re.compile(r'Chương\s+([IVX]+|[0-9]+)[\.\s:]+(.+?)(?=\n|$)', re.IGNORECASE),
        'article': re.compile(r'Điều\s+(\d+)[\.\s:]*(.+?)(?=\n|$)', re.IGNORECASE),
        'section': re.compile(r'Khoản\s+(\d+)[\.\s:]+(.+?)(?=\n|$)', re.IGNORECASE),
        'point': re.compile(r'^([a-z])\)(.+?)(?=\n|$)', re.IGNORECASE | re.MULTILINE),
        'clause': re.compile(r'^\d+\.(.+?)(?=\n|$)', re.MULTILINE),
    }
    
    # Chunking parameters
    MIN_CHUNK_SIZE = 200  # tokens
    MAX_CHUNK_SIZE = 1500  # tokens
    TARGET_CHUNK_SIZE = 800  # tokens
    
    def chunk_document(
        self, 
        document_text: str,
        document_id: str,
        law_id: str
    ) -> List[LegalDocumentChunk]:
        """
        Chunk document adaptively based on structure
        
        Strategy:
        1. Parse structure (chapters, articles, sections)
        2. Create chunks at article level (primary)
        3. Split large articles into section-level chunks
        4. Merge small articles if in same chapter
        """
        chunks = []
        
        # Parse document structure
        structure = self._parse_structure(document_text)
        
        # Iterate through chapters
        for chapter in structure['chapters']:
            chapter_context = f"Chương {chapter['number']}: {chapter['title']}"
            
            # Iterate through articles in this chapter
            for article in chapter['articles']:
                article_tokens = self._count_tokens(article['text'])
                
                # CASE 1: Article fits in one chunk
                if article_tokens <= self.MAX_CHUNK_SIZE:
                    chunk = self._create_article_chunk(
                        article, chapter, 
                        document_id, law_id
                    )
                    chunks.append(chunk)
                
                # CASE 2: Article too large - split by sections
                else:
                    section_chunks = self._split_large_article(
                        article, chapter,
                        document_id, law_id
                    )
                    chunks.extend(section_chunks)
        
        # Post-processing: merge very small adjacent chunks
        chunks = self._merge_small_chunks(chunks)
        
        # Add cross-references
        chunks = self._add_cross_references(chunks, document_text)
        
        return chunks
    
    def _parse_structure(self, text: str) -> Dict:
        """
        Parse document into hierarchical structure
        
        Returns:
            {
                'chapters': [
                    {
                        'number': 1,
                        'title': '...',
                        'text': '...',
                        'articles': [...]
                    }
                ]
            }
        """
        structure = {'chapters': []}
        
        # Split by chapters
        chapter_matches = list(self.PATTERNS['chapter'].finditer(text))
        
        for i, chapter_match in enumerate(chapter_matches):
            chapter_start = chapter_match.start()
            chapter_end = chapter_matches[i+1].start() if i+1 < len(chapter_matches) else len(text)
            
            chapter_text = text[chapter_start:chapter_end]
            chapter_number = chapter_match.group(1)
            chapter_title = chapter_match.group(2).strip()
            
            # Parse articles in this chapter
            articles = self._parse_articles(chapter_text)
            
            structure['chapters'].append({
                'number': chapter_number,
                'title': chapter_title,
                'text': chapter_text,
                'articles': articles
            })
        
        return structure
    
    def _parse_articles(self, chapter_text: str) -> List[Dict]:
        """
        Parse articles from chapter text
        """
        articles = []
        article_matches = list(self.PATTERNS['article'].finditer(chapter_text))
        
        for i, article_match in enumerate(article_matches):
            article_start = article_match.start()
            article_end = article_matches[i+1].start() if i+1 < len(article_matches) else len(chapter_text)
            
            article_text = chapter_text[article_start:article_end]
            article_number = int(article_match.group(1))
            article_title = article_match.group(2).strip()
            
            # Parse sections within article
            sections = self._parse_sections(article_text)
            
            articles.append({
                'number': article_number,
                'title': article_title,
                'text': article_text,
                'sections': sections
            })
        
        return articles
    
    def _parse_sections(self, article_text: str) -> List[Dict]:
        """
        Parse sections (khoản) from article text
        """
        sections = []
        section_matches = list(self.PATTERNS['section'].finditer(article_text))
        
        for i, section_match in enumerate(section_matches):
            section_start = section_match.start()
            section_end = section_matches[i+1].start() if i+1 < len(section_matches) else len(article_text)
            
            section_text = article_text[section_start:section_end]
            section_number = int(section_match.group(1))
            
            sections.append({
                'number': section_number,
                'text': section_text
            })
        
        return sections
    
    def _create_article_chunk(
        self,
        article: Dict,
        chapter: Dict,
        document_id: str,
        law_id: str
    ) -> LegalDocumentChunk:
        """
        Create a chunk for a single article
        """
        # Build context-aware text
        context_prefix = f"[Chương {chapter['number']}: {chapter['title']}]\n\n"
        article_text = f"Điều {article['number']}. {article['title']}\n{article['text']}"
        
        full_text = context_prefix + article_text
        
        return LegalDocumentChunk(
            chunk_id=f"{document_id}_article_{article['number']}",
            text=full_text,
            chapter_number=chapter['number'],
            chapter_title=chapter['title'],
            article_number=article['number'],
            article_title=article['title'],
            document_id=document_id,
            law_id=law_id,
            hierarchy_level='article',
            parent_context=context_prefix,
            child_count=len(article.get('sections', [])),
            token_count=self._count_tokens(full_text)
        )
    
    def _split_large_article(
        self,
        article: Dict,
        chapter: Dict,
        document_id: str,
        law_id: str
    ) -> List[LegalDocumentChunk]:
        """
        Split large article into section-level chunks
        """
        chunks = []
        
        # Create parent context
        parent_context = (
            f"[Chương {chapter['number']}: {chapter['title']}]\n"
            f"[Điều {article['number']}. {article['title']}]\n\n"
        )
        
        for section in article['sections']:
            section_text = parent_context + section['text']
            
            chunk = LegalDocumentChunk(
                chunk_id=f"{document_id}_article_{article['number']}_section_{section['number']}",
                text=section_text,
                chapter_number=chapter['number'],
                chapter_title=chapter['title'],
                article_number=article['number'],
                article_title=article['title'],
                section_number=section['number'],
                document_id=document_id,
                law_id=law_id,
                hierarchy_level='section',
                parent_context=parent_context,
                token_count=self._count_tokens(section_text)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _merge_small_chunks(
        self, 
        chunks: List[LegalDocumentChunk]
    ) -> List[LegalDocumentChunk]:
        """
        Merge very small adjacent chunks
        Only merge if same chapter and total < TARGET_CHUNK_SIZE
        """
        merged = []
        i = 0
        
        while i < len(chunks):
            current = chunks[i]
            
            # If current chunk is too small and has next chunk
            if (current.token_count < self.MIN_CHUNK_SIZE and 
                i + 1 < len(chunks)):
                
                next_chunk = chunks[i + 1]
                
                # Only merge if same chapter
                if current.chapter_number == next_chunk.chapter_number:
                    combined_tokens = current.token_count + next_chunk.token_count
                    
                    if combined_tokens <= self.TARGET_CHUNK_SIZE:
                        # Merge
                        merged_chunk = LegalDocumentChunk(
                            chunk_id=f"{current.chunk_id}_merged",
                            text=current.text + "\n\n" + next_chunk.text,
                            chapter_number=current.chapter_number,
                            chapter_title=current.chapter_title,
                            document_id=current.document_id,
                            law_id=current.law_id,
                            hierarchy_level='merged',
                            token_count=combined_tokens
                        )
                        merged.append(merged_chunk)
                        i += 2  # Skip next chunk
                        continue
            
            merged.append(current)
            i += 1
        
        return merged
    
    def _add_cross_references(
        self, 
        chunks: List[LegalDocumentChunk],
        full_text: str
    ) -> List[LegalDocumentChunk]:
        """
        Add cross-references to other articles mentioned
        """
        # Pattern for references like "theo quy định tại Điều 15"
        ref_pattern = re.compile(
            r'theo\s+(?:quy\s+định\s+)?(?:tại\s+)?Điều\s+(\d+)',
            re.IGNORECASE
        )
        
        for chunk in chunks:
            refs = ref_pattern.findall(chunk.text)
            chunk.references = [f"Điều {ref}" for ref in refs]
        
        return chunks
    
    def _count_tokens(self, text: str) -> int:
        """
        Estimate token count
        For Vietnamese: ~1 word = 1.5 tokens (approximation)
        """
        words = len(text.split())
        return int(words * 1.5)

# Usage example
chunker = AdaptiveChunkerForVietnameseLaw()

document_text = """
Chương I: QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh
Nghị định này quy định về quản lý, vận hành hệ thống hàng không dân dụng...

Khoản 1. Hệ thống hàng không bao gồm...
Khoản 2. Các quy định về an toàn bay...

Điều 2. Đối tượng áp dụng
Nghị định này áp dụng đối với...
"""

chunks = chunker.chunk_document(
    document_text=document_text,
    document_id="doc_001",
    law_id="92/2024/NĐ-CP"
)

for chunk in chunks:
    print(f"Chunk ID: {chunk.chunk_id}")
    print(f"Level: {chunk.hierarchy_level}")
    print(f"Tokens: {chunk.token_count}")
    print(f"References: {chunk.references}")
    print("---")
```

### Key Benefits

1. ✅ **Preserves semantic units** - Không bao giờ cắt giữa Điều/Khoản
2. ✅ **Maintains hierarchy** - Mỗi chunk biết mình thuộc Chương/Điều nào
3. ✅ **Context-aware** - Include parent context trong mỗi chunk
4. ✅ **Cross-references** - Track các điều khoản được reference
5. ✅ **Flexible sizing** - Adapt dựa trên content, không cố định

---

## TECHNIQUE 2: HIERARCHICAL CONTEXT MANAGEMENT

### Overview

Manage context in multiple levels like RLM does: document → chapter → article → section. This allows progressive loading based on query complexity.

### Implementation

```python
from enum import Enum
from typing import List, Dict, Optional
import asyncio

class ContextLevel(Enum):
    """
    Hierarchy levels for legal documents
    """
    DOCUMENT = 1  # Highest level - table of contents
    CHAPTER = 2   # Chapter level
    ARTICLE = 3   # Article level (most common)
    SECTION = 4   # Section/clause level (detailed)

class HierarchicalContextManager:
    """
    Manage context at multiple hierarchy levels
    Inspired by RLM's progressive loading
    """
    
    def __init__(
        self,
        document_store,
        embedding_model,
        max_tokens_per_level: Dict[ContextLevel, int] = None
    ):
        self.store = document_store
        self.embedding = embedding_model
        
        # Default token budgets per level
        self.max_tokens = max_tokens_per_level or {
            ContextLevel.DOCUMENT: 500,   # Just TOC
            ContextLevel.CHAPTER: 2000,   # Chapter summaries
            ContextLevel.ARTICLE: 4000,   # Full articles
            ContextLevel.SECTION: 8000    # Detailed sections
        }
    
    async def get_context_for_query(
        self,
        query: str,
        document_ids: List[str],
        initial_level: ContextLevel = ContextLevel.ARTICLE
    ) -> Dict:
        """
        Get context at appropriate level for query
        
        Flow:
        1. Determine query complexity
        2. Start at appropriate level
        3. Drill down if needed
        4. Expand laterally if multi-hop
        """
        # Analyze query
        analysis = self._analyze_query(query)
        
        context = {
            'level': initial_level,
            'query_analysis': analysis,
            'loaded_context': {},
            'total_tokens': 0
        }
        
        # STEP 1: Load at initial level
        if analysis['complexity'] == 'simple':
            # Simple lookup - article level is enough
            context['loaded_context'] = await self._load_level(
                ContextLevel.ARTICLE,
                document_ids,
                query
            )
        
        elif analysis['complexity'] == 'medium':
            # Medium - may need chapter context
            context['loaded_context'] = await self._load_level(
                ContextLevel.CHAPTER,
                document_ids,
                query
            )
            
            # If specific articles identified, load those too
            if analysis['specific_articles']:
                articles = await self._load_specific_articles(
                    analysis['specific_articles']
                )
                context['loaded_context']['articles'] = articles
        
        else:  # complex
            # Complex query - need full hierarchical context
            context['loaded_context'] = await self._load_hierarchical(
                document_ids,
                query,
                levels=[ContextLevel.DOCUMENT, ContextLevel.CHAPTER, ContextLevel.ARTICLE]
            )
        
        # STEP 2: Expand if multi-hop
        if analysis['is_multi_hop']:
            expanded = await self._expand_for_multi_hop(
                context['loaded_context'],
                query
            )
            context['loaded_context']['expanded'] = expanded
        
        return context
    
    def _analyze_query(self, query: str) -> Dict:
        """
        Analyze query to determine appropriate context level
        """
        query_lower = query.lower()
        
        # Detect specific article references
        article_pattern = re.compile(r'điều\s+(\d+)', re.IGNORECASE)
        specific_articles = article_pattern.findall(query)
        
        # Complexity indicators
        simple_indicators = ['điều', 'khoản', 'quy định', 'là gì']
        medium_indicators = ['giải thích', 'chi tiết', 'như thế nào']
        complex_indicators = ['so sánh', 'khác biệt', 'liên quan', 'tất cả', 'danh sách']
        
        # Multi-hop indicators
        multi_hop_indicators = ['và', 'cũng như', 'bao gồm cả', 'liên quan đến']
        
        # Determine complexity
        if any(ind in query_lower for ind in complex_indicators):
            complexity = 'complex'
        elif any(ind in query_lower for ind in medium_indicators):
            complexity = 'medium'
        else:
            complexity = 'simple'
        
        is_multi_hop = (
            any(ind in query_lower for ind in multi_hop_indicators) or
            len(specific_articles) > 1
        )
        
        return {
            'complexity': complexity,
            'specific_articles': specific_articles,
            'is_multi_hop': is_multi_hop,
            'estimated_answer_length': self._estimate_answer_length(query)
        }
    
    async def _load_level(
        self,
        level: ContextLevel,
        document_ids: List[str],
        query: str
    ) -> Dict:
        """
        Load context at specific hierarchy level
        """
        context = {}
        
        if level == ContextLevel.DOCUMENT:
            # Load table of contents
            for doc_id in document_ids:
                toc = await self.store.get_table_of_contents(doc_id)
                context[doc_id] = {
                    'type': 'toc',
                    'content': toc
                }
        
        elif level == ContextLevel.CHAPTER:
            # Load chapter summaries
            for doc_id in document_ids:
                chapters = await self.store.get_chapters(doc_id)
                # Use semantic search to find relevant chapters
                relevant_chapters = await self._semantic_search(
                    query, chapters, top_k=3
                )
                context[doc_id] = {
                    'type': 'chapters',
                    'content': relevant_chapters
                }
        
        elif level == ContextLevel.ARTICLE:
            # Load full articles
            for doc_id in document_ids:
                articles = await self.store.get_articles(doc_id)
                relevant_articles = await self._semantic_search(
                    query, articles, top_k=5
                )
                context[doc_id] = {
                    'type': 'articles',
                    'content': relevant_articles
                }
        
        elif level == ContextLevel.SECTION:
            # Load detailed sections
            for doc_id in document_ids:
                sections = await self.store.get_sections(doc_id)
                relevant_sections = await self._semantic_search(
                    query, sections, top_k=10
                )
                context[doc_id] = {
                    'type': 'sections',
                    'content': relevant_sections
                }
        
        return context
    
    async def _load_hierarchical(
        self,
        document_ids: List[str],
        query: str,
        levels: List[ContextLevel]
    ) -> Dict:
        """
        Load context at multiple levels simultaneously
        Build complete hierarchy
        """
        context = {
            'hierarchy': {}
        }
        
        for doc_id in document_ids:
            doc_hierarchy = {}
            
            # Load each level
            for level in levels:
                level_data = await self._load_level(
                    level, [doc_id], query
                )
                doc_hierarchy[level.name.lower()] = level_data[doc_id]
            
            context['hierarchy'][doc_id] = doc_hierarchy
        
        return context
    
    async def _expand_for_multi_hop(
        self,
        current_context: Dict,
        query: str
    ) -> Dict:
        """
        Expand context for multi-hop reasoning
        
        Steps:
        1. Identify cross-references in current context
        2. Load referenced articles
        3. Check graph relationships
        4. Load related documents
        """
        expanded = {
            'cross_referenced_articles': [],
            'graph_related_documents': [],
            'additional_context': []
        }
        
        # Extract all article references
        all_text = self._extract_all_text(current_context)
        ref_pattern = re.compile(r'Điều\s+(\d+)', re.IGNORECASE)
        referenced_articles = set(ref_pattern.findall(all_text))
        
        # Load referenced articles not already in context
        current_articles = self._extract_current_articles(current_context)
        missing_refs = referenced_articles - current_articles
        
        for article_num in missing_refs:
            article = await self.store.get_article_by_number(
                int(article_num)
            )
            if article:
                expanded['cross_referenced_articles'].append(article)
        
        # Check graph for related documents
        doc_ids = list(current_context.get('hierarchy', {}).keys())
        for doc_id in doc_ids:
            related = await self.store.get_related_documents(
                doc_id,
                relationship_types=['IMPLEMENTS', 'RELATES_TO', 'BASED_ON']
            )
            expanded['graph_related_documents'].extend(related)
        
        return expanded
    
    async def _semantic_search(
        self,
        query: str,
        items: List[Dict],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Semantic search within items
        """
        # Generate query embedding
        query_embedding = await self.embedding.embed(query)
        
        # Compute similarities
        scored_items = []
        for item in items:
            item_embedding = await self.embedding.embed(item['text'])
            similarity = self._cosine_similarity(
                query_embedding, 
                item_embedding
            )
            scored_items.append((similarity, item))
        
        # Sort and return top-k
        scored_items.sort(reverse=True, key=lambda x: x[0])
        return [item for _, item in scored_items[:top_k]]
    
    def _extract_all_text(self, context: Dict) -> str:
        """
        Extract all text from nested context structure
        """
        texts = []
        
        def recurse(obj):
            if isinstance(obj, dict):
                if 'text' in obj:
                    texts.append(obj['text'])
                elif 'content' in obj:
                    if isinstance(obj['content'], str):
                        texts.append(obj['content'])
                    else:
                        recurse(obj['content'])
                else:
                    for value in obj.values():
                        recurse(value)
            elif isinstance(obj, list):
                for item in obj:
                    recurse(item)
        
        recurse(context)
        return '\n\n'.join(texts)

# Usage example
manager = HierarchicalContextManager(
    document_store=document_store,
    embedding_model=embedding_model
)

# Simple query - just article level
context1 = await manager.get_context_for_query(
    query="Điều 15 quy định gì?",
    document_ids=["92/2024/NĐ-CP"],
    initial_level=ContextLevel.ARTICLE
)

# Complex query - need hierarchical context
context2 = await manager.get_context_for_query(
    query="So sánh quy định về an toàn bay giữa Nghị định 92 và các thông tư hướng dẫn",
    document_ids=["92/2024/NĐ-CP", "15/2024/TT-BGTVT"],
    initial_level=ContextLevel.CHAPTER
)
```

---

## TECHNIQUE 3: PROGRESSIVE CONTEXT LOADING

### Overview

Load context progressively as needed, rather than all at once. This is a core RLM pattern that reduces token waste and improves accuracy.

### Implementation

```python
class ProgressiveContextLoader:
    """
    Load context progressively following RLM pattern:
    PEEK → ANALYZE → LOAD → EXPAND
    """
    
    def __init__(
        self,
        document_store,
        token_budget: int = 8000
    ):
        self.store = document_store
        self.budget = token_budget
        self.loaded_tokens = 0
    
    async def load_for_query(
        self,
        query: str,
        document_ids: List[str]
    ) -> Dict:
        """
        Progressive loading pipeline
        """
        context = {
            'steps': [],
            'final_context': None,
            'tokens_used': 0
        }
        
        # STEP 1: PEEK - Quick overview
        peek_result = await self._peek_documents(document_ids)
        context['steps'].append({
            'name': 'peek',
            'tokens': peek_result['tokens'],
            'content': peek_result['toc']
        })
        self.loaded_tokens += peek_result['tokens']
        
        # STEP 2: ANALYZE - Identify relevant sections
        analyze_result = await self._analyze_relevance(
            query, 
            peek_result['toc']
        )
        context['steps'].append({
            'name': 'analyze',
            'relevant_sections': analyze_result['sections']
        })
        
        # STEP 3: LOAD - Get relevant sections
        remaining_budget = self.budget - self.loaded_tokens
        load_result = await self._load_sections(
            analyze_result['sections'],
            budget=remaining_budget
        )
        context['steps'].append({
            'name': 'load',
            'tokens': load_result['tokens'],
            'sections': load_result['sections']
        })
        self.loaded_tokens += load_result['tokens']
        
        # STEP 4: EXPAND (if budget allows and query is complex)
        if self._should_expand(query) and self.loaded_tokens < self.budget * 0.8:
            remaining_budget = self.budget - self.loaded_tokens
            expand_result = await self._expand_context(
                load_result['sections'],
                budget=remaining_budget
            )
            context['steps'].append({
                'name': 'expand',
                'tokens': expand_result['tokens'],
                'additional': expand_result['additional']
            })
            self.loaded_tokens += expand_result['tokens']
        
        # Build final context
        context['final_context'] = self._build_final_context(
            context['steps']
        )
        context['tokens_used'] = self.loaded_tokens
        
        return context
    
    async def _peek_documents(
        self, 
        document_ids: List[str]
    ) -> Dict:
        """
        PEEK: Get lightweight overview (table of contents)
        """
        toc_list = []
        total_tokens = 0
        
        for doc_id in document_ids:
            # Get cached TOC (very lightweight)
            toc = await self.store.get_toc(doc_id)
            toc_list.append({
                'document_id': doc_id,
                'toc': toc
            })
            total_tokens += self._count_tokens(toc)
        
        return {
            'toc': toc_list,
            'tokens': total_tokens
        }
    
    async def _analyze_relevance(
        self,
        query: str,
        toc_list: List[Dict]
    ) -> Dict:
        """
        ANALYZE: Use TOC to identify potentially relevant sections
        """
        relevant_sections = []
        
        for doc_toc in toc_list:
            doc_id = doc_toc['document_id']
            toc = doc_toc['toc']
            
            # Simple keyword matching on TOC
            # In production, could use lightweight embedding model
            keywords = self._extract_keywords(query)
            
            for chapter in toc['chapters']:
                # Check chapter title
                if any(kw in chapter['title'].lower() for kw in keywords):
                    for article in chapter['articles']:
                        relevant_sections.append({
                            'document_id': doc_id,
                            'chapter_number': chapter['number'],
                            'article_number': article['number'],
                            'relevance_score': 1.0  # Could be more sophisticated
                        })
        
        # Sort by relevance
        relevant_sections.sort(
            key=lambda x: x['relevance_score'],
            reverse=True
        )
        
        return {
            'sections': relevant_sections
        }
    
    async def _load_sections(
        self,
        section_refs: List[Dict],
        budget: int
    ) -> Dict:
        """
        LOAD: Actually fetch the relevant sections
        """
        sections = []
        tokens_used = 0
        
        for ref in section_refs:
            if tokens_used >= budget:
                break
            
            # Load full article text
            article = await self.store.get_article(
                document_id=ref['document_id'],
                article_number=ref['article_number']
            )
            
            article_tokens = self._count_tokens(article['text'])
            
            # Check budget
            if tokens_used + article_tokens <= budget:
                sections.append(article)
                tokens_used += article_tokens
            else:
                # Can't fit full article - try to get most relevant section
                section = await self._get_most_relevant_section(
                    article,
                    budget - tokens_used
                )
                if section:
                    sections.append(section)
                    tokens_used += self._count_tokens(section['text'])
                break
        
        return {
            'sections': sections,
            'tokens': tokens_used
        }
    
    async def _expand_context(
        self,
        loaded_sections: List[Dict],
        budget: int
    ) -> Dict:
        """
        EXPAND: Follow cross-references and add related context
        """
        additional = []
        tokens_used = 0
        
        # Extract all cross-references
        all_refs = set()
        for section in loaded_sections:
            refs = self._extract_cross_references(section['text'])
            all_refs.update(refs)
        
        # Load referenced articles (if not already loaded)
        loaded_articles = set([
            s['article_number'] for s in loaded_sections
        ])
        missing_refs = all_refs - loaded_articles
        
        for article_num in missing_refs:
            if tokens_used >= budget:
                break
            
            article = await self.store.get_article_by_number(
                article_num
            )
            
            if article:
                article_tokens = self._count_tokens(article['text'])
                if tokens_used + article_tokens <= budget:
                    additional.append(article)
                    tokens_used += article_tokens
        
        return {
            'additional': additional,
            'tokens': tokens_used
        }
    
    def _build_final_context(self, steps: List[Dict]) -> str:
        """
        Build final context string from all steps
        """
        parts = []
        
        # Add TOC for orientation
        peek_step = next(s for s in steps if s['name'] == 'peek')
        parts.append("=== DOCUMENT OVERVIEW ===")
        for doc_toc in peek_step['content']:
            parts.append(f"\nDocument: {doc_toc['document_id']}")
            # Summarized TOC
        
        # Add loaded sections
        load_step = next((s for s in steps if s['name'] == 'load'), None)
        if load_step:
            parts.append("\n\n=== RELEVANT SECTIONS ===")
            for section in load_step['sections']:
                parts.append(f"\n{section['text']}")
        
        # Add expanded context
        expand_step = next((s for s in steps if s['name'] == 'expand'), None)
        if expand_step:
            parts.append("\n\n=== RELATED REFERENCES ===")
            for item in expand_step['additional']:
                parts.append(f"\n{item['text']}")
        
        return '\n'.join(parts)
    
    def _should_expand(self, query: str) -> bool:
        """
        Determine if query needs expanded context
        """
        expansion_indicators = [
            'liên quan', 'so sánh', 'khác biệt',
            'tất cả', 'danh sách', 'bao gồm'
        ]
        return any(ind in query.lower() for ind in expansion_indicators)
```

---

Đây là phần 1 của skill file (1/3). File này đã cover:
- Overview và core principles
- Technique 1: Adaptive Chunking (đầy đủ implementation)
- Technique 2: Hierarchical Context Management (đầy đủ implementation) 
- Technique 3: Progressive Context Loading (đầy đủ implementation)

Tôi có tiếp tục với phần 2 (Techniques 4-5 + Implementation Patterns) và phần 3 (Anti-patterns + Testing + Vietnamese-specific considerations) không?# SKILL: RLM-Inspired Intelligent Chunking & Context Synthesis (PART 2/3)

## TECHNIQUE 4: INTELLIGENT CONTEXT SYNTHESIS

### Overview

Synthesize information from multiple sources in

 a structured, hierarchical way. This is how RLM builds answers bottom-up.

### Key Principles

1. **Bottom-up aggregation**: Section → Article → Chapter → Document
2. **Parallel processing**: Extract from multiple sources simultaneously
3. **Confidence scoring**: Track certainty of each piece of information
4. **Citation preservation**: Always maintain source links

### Implementation

```python
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import asyncio
from enum import Enum

class ConfidenceLevel(Enum):
    HIGH = 0.9
    MEDIUM = 0.6
    LOW = 0.3

@dataclass
class SynthesizedFact:
    """
    A single fact extracted from documents
    """
    text: str
    source_document: str
    source_article: str
    source_section: Optional[str] = None
    confidence: float = 1.0
    supporting_quotes: List[str] = None
    
    def __post_init__(self):
        if self.supporting_quotes is None:
            self.supporting_quotes = []

class IntelligentContextSynthesizer:
    """
    Synthesize context from multiple documents
    Following RLM's hierarchical synthesis pattern
    """
    
    def __init__(self, llm_mini, llm_main):
        self.llm_mini = llm_mini  # For extraction
        self.llm_main = llm_main  # For synthesis
    
    async def synthesize_answer(
        self,
        query: str,
        documents: List[Dict],
        synthesis_strategy: str = 'hierarchical'
    ) -> Dict:
        """
        Main synthesis method
        
        Args:
            query: User query
            documents: List of document dictionaries
            synthesis_strategy: 'hierarchical', 'flat', or 'adaptive'
        
        Returns:
            {
                'answer': str,
                'facts': List[SynthesizedFact],
                'synthesis_tree': Dict,
                'confidence': float
            }
        """
        if synthesis_strategy == 'hierarchical':
            return await self._hierarchical_synthesis(query, documents)
        elif synthesis_strategy == 'flat':
            return await self._flat_synthesis(query, documents)
        else:
            return await self._adaptive_synthesis(query, documents)
    
    async def _hierarchical_synthesis(
        self,
        query: str,
        documents: List[Dict]
    ) -> Dict:
        """
        RLM-style hierarchical synthesis
        
        Steps:
        1. Extract facts from each section (parallel, mini LLM)
        2. Aggregate facts by article
        3. Aggregate facts by document
        4. Synthesize final answer (main LLM)
        """
        # LEVEL 1: Extract from sections
        print("Level 1: Extracting from sections...")
        section_facts = await self._extract_from_sections(
            query, documents
        )
        
        # LEVEL 2: Aggregate by article
        print("Level 2: Aggregating by article...")
        article_facts = await self._aggregate_by_article(
            section_facts
        )
        
        # LEVEL 3: Aggregate by document
        print("Level 3: Aggregating by document...")
        document_facts = await self._aggregate_by_document(
            article_facts
        )
        
        # LEVEL 4: Final synthesis
        print("Level 4: Final synthesis...")
        final_answer = await self._synthesize_final(
            query, document_facts
        )
        
        return {
            'answer': final_answer['text'],
            'facts': section_facts + article_facts + document_facts,
            'synthesis_tree': self._build_tree(
                section_facts, article_facts, document_facts
            ),
            'confidence': final_answer['confidence']
        }
    
    async def _extract_from_sections(
        self,
        query: str,
        documents: List[Dict]
    ) -> List[SynthesizedFact]:
        """
        Extract facts from individual sections
        Use lightweight LLM (mini) for efficiency
        """
        extraction_tasks = []
        
        for doc in documents:
            for chapter in doc.get('chapters', []):
                for article in chapter.get('articles', []):
                    for section in article.get('sections', []):
                        # Create extraction task
                        task = self._extract_from_section(
                            query, section, article, chapter, doc
                        )
                        extraction_tasks.append(task)
        
        # Execute all extractions in parallel
        results = await asyncio.gather(*extraction_tasks)
        
        # Filter out empty results
        facts = [fact for fact in results if fact is not None]
        
        return facts
    
    async def _extract_from_section(
        self,
        query: str,
        section: Dict,
        article: Dict,
        chapter: Dict,
        document: Dict
    ) -> Optional[SynthesizedFact]:
        """
        Extract relevant information from a single section
        """
        prompt = f"""
        Trích xuất thông tin liên quan đến câu hỏi từ đoạn văn bản pháp luật.
        
        Câu hỏi: {query}
        
        Văn bản:
        Chương {chapter['number']}: {chapter['title']}
        Điều {article['number']}. {article['title']}
        Khoản {section['number']}: {section['text']}
        
        Hãy trả lời JSON:
        {{
            "relevant": true/false,
            "extracted_info": "thông tin trích xuất (nếu relevant)",
            "confidence": 0.0-1.0,
            "supporting_quote": "trích dẫn gốc"
        }}
        
        Chỉ trích xuất nếu thực sự liên quan. Nếu không liên quan, trả về relevant: false.
        """
        
        try:
            response = await self.llm_mini.complete(prompt)
            result = json.loads(response)
            
            if not result.get('relevant', False):
                return None
            
            return SynthesizedFact(
                text=result['extracted_info'],
                source_document=document['id'],
                source_article=f"Điều {article['number']}",
                source_section=f"Khoản {section['number']}",
                confidence=result.get('confidence', 0.5),
                supporting_quotes=[result.get('supporting_quote', '')]
            )
        
        except Exception as e:
            print(f"Error extracting from section: {e}")
            return None
    
    async def _aggregate_by_article(
        self,
        section_facts: List[SynthesizedFact]
    ) -> List[SynthesizedFact]:
        """
        Aggregate section-level facts into article-level facts
        """
        # Group facts by article
        article_groups = {}
        for fact in section_facts:
            key = (fact.source_document, fact.source_article)
            if key not in article_groups:
                article_groups[key] = []
            article_groups[key].append(fact)
        
        # Synthesize each article
        article_tasks = []
        for (doc_id, article_id), facts in article_groups.items():
            task = self._synthesize_article_facts(
                doc_id, article_id, facts
            )
            article_tasks.append(task)
        
        article_facts = await asyncio.gather(*article_tasks)
        return article_facts
    
    async def _synthesize_article_facts(
        self,
        document_id: str,
        article_id: str,
        facts: List[SynthesizedFact]
    ) -> SynthesizedFact:
        """
        Synthesize multiple section facts into single article fact
        """
        # Combine all section texts
        combined_text = "\n".join([f.text for f in facts])
        
        # Use mini LLM to synthesize
        prompt = f"""
        Tổng hợp các thông tin sau thành 1 đoạn văn ngắn gọn:
        
        {combined_text}
        
        Chỉ giữ lại thông tin quan trọng, loại bỏ trùng lặp.
        """
        
        synthesized_text = await self.llm_mini.complete(prompt)
        
        # Calculate aggregate confidence
        avg_confidence = sum(f.confidence for f in facts) / len(facts)
        
        return SynthesizedFact(
            text=synthesized_text,
            source_document=document_id,
            source_article=article_id,
            source_section=None,  # Article level
            confidence=avg_confidence,
            supporting_quotes=[
                quote 
                for fact in facts 
                for quote in fact.supporting_quotes
            ]
        )
    
    async def _aggregate_by_document(
        self,
        article_facts: List[SynthesizedFact]
    ) -> List[SynthesizedFact]:
        """
        Aggregate article-level facts into document-level facts
        """
        # Group by document
        doc_groups = {}
        for fact in article_facts:
            if fact.source_document not in doc_groups:
                doc_groups[fact.source_document] = []
            doc_groups[fact.source_document].append(fact)
        
        # Synthesize each document
        doc_tasks = []
        for doc_id, facts in doc_groups.items():
            task = self._synthesize_document_facts(doc_id, facts)
            doc_tasks.append(task)
        
        document_facts = await asyncio.gather(*doc_tasks)
        return document_facts
    
    async def _synthesize_document_facts(
        self,
        document_id: str,
        facts: List[SynthesizedFact]
    ) -> SynthesizedFact:
        """
        Synthesize article facts into document-level summary
        """
        # Combine article summaries
        combined = "\n\n".join([
            f"[{f.source_article}]: {f.text}"
            for f in facts
        ])
        
        prompt = f"""
        Tổng hợp các điều khoản sau từ văn bản {document_id}:
        
        {combined}
        
        Tạo 1 đoạn tóm tắt ngắn gọn (2-3 câu) về nội dung chính.
        """
        
        summary = await self.llm_mini.complete(prompt)
        
        return SynthesizedFact(
            text=summary,
            source_document=document_id,
            source_article="Tổng hợp",
            confidence=sum(f.confidence for f in facts) / len(facts)
        )
    
    async def _synthesize_final(
        self,
        query: str,
        document_facts: List[SynthesizedFact]
    ) -> Dict:
        """
        Final synthesis using main LLM
        Combine document-level summaries into final answer
        """
        # Build context from document facts
        context_parts = []
        for fact in document_facts:
            context_parts.append(
                f"[Từ {fact.source_document}]:\n{fact.text}"
            )
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""
        Dựa trên thông tin từ các văn bản pháp luật sau, hãy trả lời câu hỏi.
        
        Câu hỏi: {query}
        
        Thông tin từ các văn bản:
        {context}
        
        Yêu cầu:
        1. Trả lời trực tiếp câu hỏi
        2. Tổng hợp từ tất cả văn bản liên quan
        3. Nêu rõ nguồn trích dẫn (số điều, văn bản nào)
        4. Nếu có mâu thuẫn, chỉ ra và giải thích
        """
        
        answer = await self.llm_main.complete(prompt)
        
        # Calculate overall confidence
        avg_confidence = sum(f.confidence for f in document_facts) / len(document_facts)
        
        return {
            'text': answer,
            'confidence': avg_confidence
        }
    
    def _build_tree(
        self,
        section_facts: List[SynthesizedFact],
        article_facts: List[SynthesizedFact],
        document_facts: List[SynthesizedFact]
    ) -> Dict:
        """
        Build synthesis tree for transparency
        """
        tree = {
            'level_1_sections': len(section_facts),
            'level_2_articles': len(article_facts),
            'level_3_documents': len(document_facts),
            'total_sources': len(set(f.source_document for f in section_facts))
        }
        
        # Build hierarchical structure
        tree['hierarchy'] = {}
        for doc_fact in document_facts:
            doc_id = doc_fact.source_document
            tree['hierarchy'][doc_id] = {
                'summary': doc_fact.text,
                'articles': []
            }
            
            # Add article facts
            for art_fact in article_facts:
                if art_fact.source_document == doc_id:
                    tree['hierarchy'][doc_id]['articles'].append({
                        'article': art_fact.source_article,
                        'summary': art_fact.text,
                        'sections': []
                    })
                    
                    # Add section facts
                    for sec_fact in section_facts:
                        if (sec_fact.source_document == doc_id and
                            sec_fact.source_article == art_fact.source_article):
                            tree['hierarchy'][doc_id]['articles'][-1]['sections'].append({
                                'section': sec_fact.source_section,
                                'text': sec_fact.text
                            })
        
        return tree

# Usage example
synthesizer = IntelligentContextSynthesizer(
    llm_mini=openai_mini_client,
    llm_main=openai_main_client
)

# Complex multi-document query
result = await synthesizer.synthesize_answer(
    query="So sánh quy định về giấy phép bay giữa Nghị định 92/2024 và Thông tư 15/2024",
    documents=[doc1, doc2],
    synthesis_strategy='hierarchical'
)

print(result['answer'])
print(f"Confidence: {result['confidence']}")
print(f"Sources: {result['synthesis_tree']['total_sources']}")
```

### Advanced: Conflict Resolution

```python
class ConflictResolver:
    """
    Resolve conflicts when multiple documents give different information
    """
    
    async def resolve_conflicts(
        self,
        facts: List[SynthesizedFact],
        query: str
    ) -> Dict:
        """
        Identify and resolve conflicts between facts
        """
        # Group facts by semantic similarity
        fact_clusters = self._cluster_similar_facts(facts)
        
        conflicts = []
        for cluster in fact_clusters:
            if self._has_conflict(cluster):
                resolved = await self._resolve_cluster(cluster, query)
                conflicts.append(resolved)
        
        return {
            'conflicts_found': len(conflicts),
            'resolutions': conflicts
        }
    
    def _has_conflict(self, facts: List[SynthesizedFact]) -> bool:
        """
        Check if facts conflict with each other
        """
        # Simple heuristic: if facts have different key information
        # More sophisticated: use NLI model
        unique_texts = set(f.text for f in facts)
        return len(unique_texts) > 1
    
    async def _resolve_cluster(
        self,
        conflicting_facts: List[SynthesizedFact],
        query: str
    ) -> Dict:
        """
        Resolve a cluster of conflicting facts
        """
        # Present conflict to LLM for resolution
        conflict_text = "\n\n".join([
            f"Nguồn: {f.source_document}, {f.source_article}\n"
            f"Nội dung: {f.text}\n"
            f"Độ tin cậy: {f.confidence}"
            for f in conflicting_facts
        ])
        
        prompt = f"""
        Các quy định sau có vẻ mâu thuẫn với nhau. Hãy phân tích và giải thích:
        
        Câu hỏi gốc: {query}
        
        Các quy định:
        {conflict_text}
        
        Yêu cầu:
        1. Xác định điểm mâu thuẫn
        2. Giải thích tại sao mâu thuẫn (nếu có)
        3. Xác định quy định nào ưu tiên (dựa trên thứ bậc pháp luật)
        4. Đưa ra kết luận cuối cùng
        """
        
        resolution = await self.llm_main.complete(prompt)
        
        return {
            'conflict_description': conflict_text,
            'resolution': resolution,
            'winning_fact': self._select_winner(conflicting_facts)
        }
    
    def _select_winner(
        self, 
        facts: List[SynthesizedFact]
    ) -> SynthesizedFact:
        """
        Select most authoritative fact
        Priority: Nghị định > Thông tư > Quyết định
        """
        # Sort by document type priority
        doc_type_priority = {
            'NĐ-CP': 3,  # Nghị định
            'TT': 2,     # Thông tư
            'QĐ': 1      # Quyết định
        }
        
        def get_priority(fact):
            doc_type = fact.source_document.split('/')[1].split('-')[0]
            return doc_type_priority.get(doc_type, 0)
        
        facts_sorted = sorted(facts, key=get_priority, reverse=True)
        return facts_sorted[0]
```

---

## TECHNIQUE 5: MULTI-HOP CONTEXT NAVIGATION

### Overview

Navigate through document relationships to answer complex queries that require information from multiple interconnected sources.

### Implementation

```python
from typing import Set, List, Dict, Tuple
from collections import deque

class MultiHopNavigator:
    """
    Navigate document relationships for multi-hop queries
    Inspired by RLM's recursive navigation
    """
    
    def __init__(
        self,
        document_store,
        graph_store,
        max_hops: int = 3
    ):
        self.doc_store = document_store
        self.graph_store = graph_store
        self.max_hops = max_hops
    
    async def navigate_for_query(
        self,
        query: str,
        start_documents: List[str],
        navigation_strategy: str = 'bfs'
    ) -> Dict:
        """
        Navigate through documents to gather context
        
        Args:
            query: User query
            start_documents: Initial document IDs
            navigation_strategy: 'bfs' or 'dfs'
        
        Returns:
            {
                'visited_documents': List[str],
                'navigation_path': List[Dict],
                'gathered_context': Dict
            }
        """
        if navigation_strategy == 'bfs':
            return await self._bfs_navigate(query, start_documents)
        else:
            return await self._dfs_navigate(query, start_documents)
    
    async def _bfs_navigate(
        self,
        query: str,
        start_docs: List[str]
    ) -> Dict:
        """
        Breadth-First Search navigation
        Good for finding shortest path to relevant information
        """
        visited = set()
        queue = deque([(doc_id, 0) for doc_id in start_docs])  # (doc_id, depth)
        path = []
        context = {}
        
        while queue and len(visited) < 20:  # Limit total docs
            current_doc, depth = queue.popleft()
            
            if current_doc in visited or depth > self.max_hops:
                continue
            
            visited.add(current_doc)
            
            # Load document content
            doc_content = await self.doc_store.get_document(current_doc)
            
            # Check relevance to query
            relevance = await self._check_relevance(query, doc_content)
            
            if relevance['score'] > 0.3:  # Threshold
                context[current_doc] = {
                    'content': doc_content,
                    'relevance': relevance['score'],
                    'depth': depth
                }
                
                path.append({
                    'document': current_doc,
                    'depth': depth,
                    'relevance': relevance['score'],
                    'reason': relevance['reason']
                })
            
            # Get related documents
            if depth < self.max_hops:
                related = await self.graph_store.get_related(
                    current_doc,
                    relationship_types=['IMPLEMENTS', 'BASED_ON', 'RELATES_TO']
                )
                
                for rel_doc in related:
                    if rel_doc not in visited:
                        queue.append((rel_doc, depth + 1))
        
        return {
            'visited_documents': list(visited),
            'navigation_path': path,
            'gathered_context': context
        }
    
    async def _check_relevance(
        self,
        query: str,
        document: Dict
    ) -> Dict:
        """
        Check if document is relevant to query
        """
        # Simple keyword-based relevance (can be improved with embeddings)
        query_keywords = set(query.lower().split())
        doc_keywords = set(document['text'].lower().split())
        
        overlap = len(query_keywords & doc_keywords)
        score = overlap / len(query_keywords) if query_keywords else 0
        
        return {
            'score': min(score, 1.0),
            'reason': f"Matched {overlap}/{len(query_keywords)} keywords"
        }
    
    async def _dfs_navigate(
        self,
        query: str,
        start_docs: List[str]
    ) -> Dict:
        """
        Depth-First Search navigation
        Good for following specific chains of references
        """
        visited = set()
        path = []
        context = {}
        
        async def dfs_helper(doc_id: str, depth: int):
            if doc_id in visited or depth > self.max_hops:
                return
            
            visited.add(doc_id)
            
            # Load and check relevance
            doc_content = await self.doc_store.get_document(doc_id)
            relevance = await self._check_relevance(query, doc_content)
            
            if relevance['score'] > 0.3:
                context[doc_id] = {
                    'content': doc_content,
                    'relevance': relevance['score'],
                    'depth': depth
                }
                path.append({
                    'document': doc_id,
                    'depth': depth,
                    'relevance': relevance['score']
                })
                
                # Explore related documents
                related = await self.graph_store.get_related(
                    doc_id,
                    relationship_types=['IMPLEMENTS', 'BASED_ON']
                )
                
                for rel_doc in related:
                    await dfs_helper(rel_doc, depth + 1)
        
        # Start DFS from each starting document
        for doc_id in start_docs:
            await dfs_helper(doc_id, 0)
        
        return {
            'visited_documents': list(visited),
            'navigation_path': path,
            'gathered_context': context
        }

class SmartReferenceResolver:
    """
    Resolve cross-references intelligently
    """
    
    def __init__(self, document_store, graph_store):
        self.doc_store = document_store
        self.graph_store = graph_store
    
    async def resolve_references(
        self,
        text: str,
        current_document: str
    ) -> Dict:
        """
        Find and resolve all references in text
        
        Examples:
        - "theo quy định tại Điều 15" → load Điều 15
        - "Thông tư hướng dẫn" → find related Thông tư
        - "văn bản quy phạm pháp luật có liên quan" → search graph
        """
        references = {
            'explicit': [],  # "Điều 15"
            'implicit': [],  # "Thông tư hướng dẫn"
            'graph': []      # From knowledge graph
        }
        
        # EXPLICIT REFERENCES: "Điều X", "Khoản Y"
        explicit_refs = self._extract_explicit_references(text)
        for ref in explicit_refs:
            resolved = await self._resolve_explicit_reference(
                ref, current_document
            )
            if resolved:
                references['explicit'].append(resolved)
        
        # IMPLICIT REFERENCES: "văn bản hướng dẫn"
        implicit_refs = self._extract_implicit_references(text)
        for ref in implicit_refs:
            resolved = await self._resolve_implicit_reference(
                ref, current_document
            )
            references['implicit'].extend(resolved)
        
        # GRAPH REFERENCES: Use knowledge graph
        graph_refs = await self._resolve_from_graph(current_document)
        references['graph'] = graph_refs
        
        return references
    
    def _extract_explicit_references(self, text: str) -> List[str]:
        """
        Extract explicit article/section references
        """
        patterns = [
            r'Điều\s+(\d+)',
            r'Khoản\s+(\d+)',
            r'Điểm\s+([a-z])',
        ]
        
        refs = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            refs.extend(matches)
        
        return refs
    
    async def _resolve_explicit_reference(
        self,
        ref: str,
        current_doc: str
    ) -> Optional[Dict]:
        """
        Load content of explicitly referenced article
        """
        try:
            # Try to load from current document first
            article = await self.doc_store.get_article(
                document_id=current_doc,
                article_number=int(ref)
            )
            
            if article:
                return {
                    'type': 'explicit',
                    'reference': f"Điều {ref}",
                    'document': current_doc,
                    'content': article
                }
        except:
            pass
        
        return None
    
    def _extract_implicit_references(self, text: str) -> List[str]:
        """
        Extract implicit references like "văn bản hướng dẫn"
        """
        implicit_patterns = [
            'văn bản hướng dẫn',
            'thông tư hướng dẫn',
            'quyết định quy định',
            'nghị định liên quan'
        ]
        
        refs = []
        text_lower = text.lower()
        for pattern in implicit_patterns:
            if pattern in text_lower:
                refs.append(pattern)
        
        return refs
    
    async def _resolve_implicit_reference(
        self,
        ref: str,
        current_doc: str
    ) -> List[Dict]:
        """
        Search for documents matching implicit reference
        """
        # Use graph to find related documents
        if 'hướng dẫn' in ref:
            rel_type = 'IMPLEMENTS'
        elif 'liên quan' in ref:
            rel_type = 'RELATES_TO'
        else:
            rel_type = 'BASED_ON'
        
        related_docs = await self.graph_store.get_related(
            current_doc,
            relationship_types=[rel_type]
        )
        
        results = []
        for doc_id in related_docs:
            doc = await self.doc_store.get_document(doc_id)
            results.append({
                'type': 'implicit',
                'reference': ref,
                'document': doc_id,
                'content': doc,
                'relationship': rel_type
            })
        
        return results
```

---

## IMPLEMENTATION PATTERNS

### Pattern 1: Smart Query Pipeline

```python
class SmartQueryPipeline:
    """
    Complete query processing pipeline using all techniques
    """
    
    def __init__(self, config: Dict):
        self.chunker = AdaptiveChunkerForVietnameseLaw()
        self.context_manager = HierarchicalContextManager(...)
        self.loader = ProgressiveContextLoader(...)
        self.synthesizer = IntelligentContextSynthesizer(...)
        self.navigator = MultiHopNavigator(...)
    
    async def process_query(self, query: str, document_ids: List[str]) -> Dict:
        """
        End-to-end query processing
        """
        # STEP 1: Analyze query
        analysis = self._analyze_query(query)
        
        # STEP 2: Determine strategy
        if analysis['complexity'] == 'simple':
            return await self._simple_path(query, document_ids)
        elif analysis['is_multi_hop']:
            return await self._multi_hop_path(query, document_ids)
        else:
            return await self._standard_path(query, document_ids)
    
    async def _simple_path(self, query: str, doc_ids: List[str]) -> Dict:
        """
        Fast path for simple queries
        """
        # Direct semantic search + quick synthesis
        context = await self.context_manager.get_context_for_query(
            query, doc_ids, 
            initial_level=ContextLevel.ARTICLE
        )
        
        answer = await self.synthesizer.synthesize_answer(
            query, context, 
            synthesis_strategy='flat'
        )
        
        return answer
    
    async def _multi_hop_path(self, query: str, doc_ids: List[str]) -> Dict:
        """
        Multi-hop path using navigation
        """
        # Navigate through related documents
        nav_result = await self.navigator.navigate_for_query(
            query, doc_ids,
            navigation_strategy='bfs'
        )
        
        # Hierarchical synthesis
        answer = await self.synthesizer.synthesize_answer(
            query,
            nav_result['gathered_context'],
            synthesis_strategy='hierarchical'
        )
        
        return {
            **answer,
            'navigation_path': nav_result['navigation_path']
        }
```

### Pattern 2: Iterative Refinement

```python
class IterativeRefiner:
    """
    Iteratively refine answer by loading more context as needed
    """
    
    async def refine_answer(
        self,
        query: str,
        initial_answer: Dict,
        max_iterations: int = 3
    ) -> Dict:
        """
        Refine answer iteratively
        """
        current_answer = initial_answer
        iteration = 0
        
        while iteration < max_iterations:
            # Check if answer is sufficient
            is_sufficient = await self._check_sufficiency(
                query, current_answer
            )
            
            if is_sufficient:
                break
            
            # Identify gaps
            gaps = await self._identify_gaps(query, current_answer)
            
            # Load additional context to fill gaps
            additional_context = await self._load_for_gaps(gaps)
            
            # Re-synthesize with additional context
            current_answer = await self.synthesizer.synthesize_answer(
                query,
                {**current_answer['context'], **additional_context}
            )
            
            iteration += 1
        
        return current_answer
```

Phần 2 đã hoàn thành! Bây giờ tôi sẽ tạo phần 3 với Anti-patterns, Testing, và Vietnamese-specific considerations.

# SKILL: RLM-Inspired Intelligent Chunking & Context Synthesis (PART 3/3)

## ANTI-PATTERNS TO AVOID

### Anti-Pattern 1: Over-Chunking

**❌ BAD:**
```python
def bad_chunking(text: str):
    """
    Creating too many tiny chunks
    """
    chunks = []
    sentences = text.split('.')
    
    # Each sentence = 1 chunk (TOO GRANULAR)
    for sentence in sentences:
        chunks.append({
            'text': sentence,
            'tokens': len(sentence.split())
        })
    
    return chunks  # Returns 1000+ chunks for a 50-page document!
```

**✅ GOOD:**
```python
def good_chunking(text: str):
    """
    Create semantic chunks at appropriate level
    """
    chunker = AdaptiveChunkerForVietnameseLaw()
    
    # Chunk at article level (meaningful units)
    chunks = chunker.chunk_document(text, doc_id, law_id)
    
    # Typical result: 50-100 chunks for 50-page document
    return chunks
```

**Why it matters:**
- Too many chunks → embedding/search overhead
- Loses context → semantic meaning breaks
- Retrieval noise → LLM gets irrelevant tiny fragments

---

### Anti-Pattern 2: Ignoring Document Structure

**❌ BAD:**
```python
def bad_structure_ignore(text: str, chunk_size: int = 512):
    """
    Blindly splitting without considering structure
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size):
        chunk_text = ' '.join(words[i:i+chunk_size])
        chunks.append(chunk_text)
    
    # This can split in the middle of an Article or Section!
    return chunks
```

**✅ GOOD:**
```python
def good_structure_aware(document: str):
    """
    Respect document boundaries
    """
    # Parse structure first
    structure = parse_vietnamese_legal_doc(document)
    
    chunks = []
    for article in structure['articles']:
        # Never split an article unless it's too large
        if article.token_count < MAX_CHUNK_SIZE:
            chunks.append(article)
        else:
            # Split by sections within the article
            for section in article.sections:
                chunks.append(section)
    
    return chunks
```

---

### Anti-Pattern 3: Loading All Context at Once

**❌ BAD:**
```python
async def bad_context_loading(query: str, doc_ids: List[str]):
    """
    Loading everything upfront
    """
    all_docs = []
    
    # Load ALL documents in full
    for doc_id in doc_ids:
        full_doc = await load_full_document(doc_id)  # 100K+ tokens each!
        all_docs.append(full_doc)
    
    # Try to cram everything into LLM context (FAILS!)
    context = '\n\n'.join(all_docs)  # 1M+ tokens
    answer = await llm.complete(f"{query}\n\nContext:\n{context}")
    
    return answer
```

**✅ GOOD:**
```python
async def good_progressive_loading(query: str, doc_ids: List[str]):
    """
    Load progressively as RLM does
    """
    loader = ProgressiveContextLoader(token_budget=8000)
    
    # PEEK → ANALYZE → LOAD → EXPAND
    context = await loader.load_for_query(query, doc_ids)
    
    # Only loaded relevant parts (8K tokens)
    answer = await llm.complete(
        f"{query}\n\nContext:\n{context['final_context']}"
    )
    
    return answer
```

---

### Anti-Pattern 4: Flat Synthesis Without Hierarchy

**❌ BAD:**
```python
async def bad_flat_synthesis(query: str, chunks: List[str]):
    """
    Concatenate all chunks and ask LLM
    """
    # Just dump everything into one prompt
    all_text = '\n\n'.join([chunk['text'] for chunk in chunks])
    
    prompt = f"""
    Answer this question: {query}
    
    Here are all the documents:
    {all_text}
    """
    
    answer = await llm.complete(prompt)
    return answer
```

**✅ GOOD:**
```python
async def good_hierarchical_synthesis(query: str, documents: List[Dict]):
    """
    Synthesize hierarchically like RLM
    """
    synthesizer = IntelligentContextSynthesizer(llm_mini, llm_main)
    
    # Bottom-up: section → article → document → final
    result = await synthesizer.synthesize_answer(
        query, documents,
        synthesis_strategy='hierarchical'
    )
    
    return result
```

**Why hierarchical is better:**
- Reduces hallucination (facts aggregated step-by-step)
- Better citation (know which section → article → document)
- Handles conflicts (can compare at each level)
- Scales better (parallel processing at each level)

---

### Anti-Pattern 5: No Context Preservation in Chunks

**❌ BAD:**
```python
def bad_no_context(article: Dict):
    """
    Chunk loses its context
    """
    chunk = {
        'text': article['content'],  # Just raw content
        'article_number': article['number']
    }
    return chunk
```

**✅ GOOD:**
```python
def good_with_context(article: Dict, chapter: Dict):
    """
    Preserve hierarchical context
    """
    # Include parent context
    context_prefix = f"[Chương {chapter['number']}: {chapter['title']}]\n\n"
    
    chunk = {
        'text': context_prefix + f"Điều {article['number']}. {article['title']}\n{article['content']}",
        'metadata': {
            'chapter_number': chapter['number'],
            'chapter_title': chapter['title'],
            'article_number': article['number'],
            'article_title': article['title']
        }
    }
    return chunk
```

**Why context matters:**
- LLM understands where chunk fits in document
- Better semantic search (chapter context helps)
- Citation is complete (can cite "Chương 2, Điều 15")

---

### Anti-Pattern 6: Synchronous Processing

**❌ BAD:**
```python
def bad_synchronous(sections: List[Dict]):
    """
    Process sections one by one
    """
    results = []
    
    for section in sections:  # Sequential!
        result = extract_facts(section)  # Takes 2 seconds each
        results.append(result)
    
    # Total time: 2s × 100 sections = 200 seconds!
    return results
```

**✅ GOOD:**
```python
async def good_parallel(sections: List[Dict]):
    """
    Process sections in parallel
    """
    # Create all tasks
    tasks = [extract_facts_async(section) for section in sections]
    
    # Run in parallel
    results = await asyncio.gather(*tasks)
    
    # Total time: ~2 seconds (limited by slowest task)
    return results
```

---

## TESTING & VALIDATION

### Test Suite for Chunking

```python
import pytest
from typing import List

class TestAdaptiveChunking:
    """
    Comprehensive tests for adaptive chunking
    """
    
    @pytest.fixture
    def sample_document(self):
        """
        Sample Vietnamese legal document
        """
        return """
        Chương I: QUY ĐỊNH CHUNG
        
        Điều 1. Phạm vi điều chỉnh
        Nghị định này quy định về quản lý, vận hành hệ thống hàng không dân dụng...
        
        Khoản 1. Hệ thống hàng không bao gồm:
        a) Các cảng hàng không, sân bay;
        b) Các trung tâm kiểm soát không lưu;
        c) Hệ thống thông tin, dẫn đường hàng không.
        
        Khoản 2. Các quy định về an toàn bay được áp dụng thống nhất trên toàn quốc.
        
        Điều 2. Đối tượng áp dụng
        Nghị định này áp dụng đối với...
        """
    
    def test_chunks_preserve_structure(self, sample_document):
        """
        Test that chunks respect document structure
        """
        chunker = AdaptiveChunkerForVietnameseLaw()
        chunks = chunker.chunk_document(
            sample_document, 
            doc_id="test_001",
            law_id="92/2024/NĐ-CP"
        )
        
        # Verify each chunk is a complete semantic unit
        for chunk in chunks:
            # Should not split in middle of article
            assert 'Điều' in chunk.text or 'Khoản' in chunk.text
            
            # Should have hierarchy metadata
            assert chunk.chapter_number is not None
            assert chunk.article_number is not None
    
    def test_chunks_have_context(self, sample_document):
        """
        Test that chunks include parent context
        """
        chunker = AdaptiveChunkerForVietnameseLaw()
        chunks = chunker.chunk_document(sample_document, "test", "test")
        
        for chunk in chunks:
            # Should have chapter context
            assert 'Chương' in chunk.text
            
            # Should have parent_context field
            assert chunk.parent_context is not None
            assert len(chunk.parent_context) > 0
    
    def test_chunk_size_within_limits(self, sample_document):
        """
        Test that chunks are within size limits
        """
        chunker = AdaptiveChunkerForVietnameseLaw()
        chunks = chunker.chunk_document(sample_document, "test", "test")
        
        for chunk in chunks:
            # Should be within limits
            assert chunk.token_count >= chunker.MIN_CHUNK_SIZE
            assert chunk.token_count <= chunker.MAX_CHUNK_SIZE
    
    def test_no_information_loss(self, sample_document):
        """
        Test that all content is preserved in chunks
        """
        chunker = AdaptiveChunkerForVietnameseLaw()
        chunks = chunker.chunk_document(sample_document, "test", "test")
        
        # Concatenate all chunk texts
        all_chunk_text = '\n'.join([chunk.text for chunk in chunks])
        
        # All important content should be present
        assert 'Điều 1' in all_chunk_text
        assert 'Điều 2' in all_chunk_text
        assert 'Khoản 1' in all_chunk_text
        assert 'an toàn bay' in all_chunk_text
    
    def test_cross_references_detected(self, sample_document):
        """
        Test that cross-references are detected
        """
        # Add cross-reference to sample
        doc_with_ref = sample_document + """
        
        Điều 3. Quy định bổ sung
        Theo quy định tại Điều 1 và Điều 2 của Nghị định này...
        """
        
        chunker = AdaptiveChunkerForVietnameseLaw()
        chunks = chunker.chunk_document(doc_with_ref, "test", "test")
        
        # Find chunk containing Điều 3
        dieu_3_chunk = next(
            c for c in chunks if c.article_number == 3
        )
        
        # Should have detected references
        assert len(dieu_3_chunk.references) > 0
        assert 'Điều 1' in dieu_3_chunk.references or 'Điều 2' in dieu_3_chunk.references

### Test Suite for Context Synthesis

```python
class TestHierarchicalSynthesis:
    """
    Tests for hierarchical synthesis
    """
    
    @pytest.fixture
    def mock_llm(self):
        """
        Mock LLM for testing
        """
        class MockLLM:
            async def complete(self, prompt: str) -> str:
                if 'trích xuất' in prompt.lower():
                    return '{"relevant": true, "extracted_info": "Test info", "confidence": 0.8}'
                elif 'tổng hợp' in prompt.lower():
                    return 'Tổng hợp: Test summary'
                else:
                    return 'Final answer: Test answer'
        
        return MockLLM()
    
    @pytest.mark.asyncio
    async def test_hierarchical_synthesis_preserves_structure(self, mock_llm):
        """
        Test that synthesis maintains hierarchical structure
        """
        synthesizer = IntelligentContextSynthesizer(
            llm_mini=mock_llm,
            llm_main=mock_llm
        )
        
        sample_docs = [
            {
                'id': 'doc1',
                'chapters': [
                    {
                        'number': 1,
                        'title': 'Test Chapter',
                        'articles': [
                            {
                                'number': 1,
                                'title': 'Test Article',
                                'sections': [
                                    {
                                        'number': 1,
                                        'text': 'Test section content'
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        
        result = await synthesizer.synthesize_answer(
            query="Test query",
            documents=sample_docs,
            synthesis_strategy='hierarchical'
        )
        
        # Should have synthesis tree
        assert 'synthesis_tree' in result
        tree = result['synthesis_tree']
        
        # Tree should have all levels
        assert tree['level_1_sections'] > 0
        assert tree['level_2_articles'] > 0
        assert tree['level_3_documents'] > 0
    
    @pytest.mark.asyncio
    async def test_synthesis_confidence_tracking(self, mock_llm):
        """
        Test that confidence scores are tracked
        """
        synthesizer = IntelligentContextSynthesizer(
            llm_mini=mock_llm,
            llm_main=mock_llm
        )
        
        result = await synthesizer.synthesize_answer(
            query="Test",
            documents=[...],
            synthesis_strategy='hierarchical'
        )
        
        # Should have confidence score
        assert 'confidence' in result
        assert 0 <= result['confidence'] <= 1
```

### Integration Tests

```python
class TestEndToEndPipeline:
    """
    Integration tests for complete pipeline
    """
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_simple_query_pipeline(self):
        """
        Test simple query end-to-end
        """
        pipeline = SmartQueryPipeline(config={...})
        
        result = await pipeline.process_query(
            query="Điều 15 quy định gì?",
            document_ids=["92/2024/NĐ-CP"]
        )
        
        # Should return answer
        assert 'answer' in result
        assert len(result['answer']) > 0
        
        # Should have used simple path (fast)
        assert result.get('strategy') == 'simple'
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_multi_hop_query_pipeline(self):
        """
        Test multi-hop query end-to-end
        """
        pipeline = SmartQueryPipeline(config={...})
        
        result = await pipeline.process_query(
            query="So sánh quy định về an toàn bay giữa Nghị định 92 và Thông tư 15",
            document_ids=["92/2024/NĐ-CP", "15/2024/TT-BGTVT"]
        )
        
        # Should have navigation path
        assert 'navigation_path' in result
        assert len(result['navigation_path']) > 1
        
        # Should have used multi-hop strategy
        assert result.get('strategy') == 'multi_hop'
```

### Performance Benchmarks

```python
import time
import asyncio

class PerformanceBenchmarks:
    """
    Benchmark tests for performance validation
    """
    
    @pytest.mark.benchmark
    def test_chunking_performance(self, benchmark, large_document):
        """
        Benchmark chunking speed
        """
        chunker = AdaptiveChunkerForVietnameseLaw()
        
        def run_chunking():
            return chunker.chunk_document(
                large_document,
                "bench_001",
                "test"
            )
        
        result = benchmark(run_chunking)
        
        # Should complete in reasonable time
        assert benchmark.stats['mean'] < 5.0  # < 5 seconds
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_synthesis_latency(self, sample_documents):
        """
        Benchmark synthesis latency
        """
        synthesizer = IntelligentContextSynthesizer(llm_mini, llm_main)
        
        start = time.time()
        
        result = await synthesizer.synthesize_answer(
            query="Test query",
            documents=sample_documents,
            synthesis_strategy='hierarchical'
        )
        
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        # (10 docs, 3-level hierarchy, async processing)
        assert elapsed < 30.0  # < 30 seconds
```

---

## VIETNAMESE-SPECIFIC CONSIDERATIONS

### 1. Diacritics Handling

```python
import unicodedata

def normalize_vietnamese(text: str) -> str:
    """
    Normalize Vietnamese text for consistent processing
    """
    # Normalize to NFC form (composed characters)
    text = unicodedata.normalize('NFC', text)
    
    # Vietnamese-specific normalizations
    replacements = {
        'đ': 'đ',  # Ensure correct đ character
        'Đ': 'Đ',
        # Add more as needed
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

class VietnameseAwareChunker(AdaptiveChunkerForVietnameseLaw):
    """
    Chunker with Vietnamese-specific handling
    """
    
    def chunk_document(self, document_text: str, *args, **kwargs):
        # Normalize before processing
        normalized_text = normalize_vietnamese(document_text)
        
        # Continue with normal chunking
        return super().chunk_document(normalized_text, *args, **kwargs)
```

### 2. Legal Term Detection

```python
class VietnameseLegalTermDetector:
    """
    Detect and handle Vietnamese legal terminology
    """
    
    LEGAL_TERMS = {
        # Hierarchy
        'nghị định': 'decree',
        'thông tư': 'circular',
        'quyết định': 'decision',
        'chỉ thị': 'directive',
        
        # Structure
        'chương': 'chapter',
        'mục': 'section',
        'điều': 'article',
        'khoản': 'clause',
        'điểm': 'point',
        
        # References
        'theo quy định tại': 'as stipulated in',
        'căn cứ': 'based on',
        'thực hiện': 'implement',
        
        # Actions
        'ban hành': 'promulgate',
        'hướng dẫn': 'guide',
        'quy định': 'regulate',
    }
    
    def detect_terms(self, text: str) -> List[Dict]:
        """
        Detect legal terms in text
        """
        terms_found = []
        text_lower = text.lower()
        
        for viet_term, eng_term in self.LEGAL_TERMS.items():
            if viet_term in text_lower:
                # Find all occurrences
                start = 0
                while True:
                    pos = text_lower.find(viet_term, start)
                    if pos == -1:
                        break
                    
                    terms_found.append({
                        'term': viet_term,
                        'translation': eng_term,
                        'position': pos,
                        'context': text[max(0, pos-50):pos+50]
                    })
                    
                    start = pos + len(viet_term)
        
        return terms_found
    
    def enrich_chunk_with_legal_terms(
        self, 
        chunk: LegalDocumentChunk
    ) -> LegalDocumentChunk:
        """
        Add legal term metadata to chunk
        """
        terms = self.detect_terms(chunk.text)
        
        # Add to metadata
        chunk.metadata['legal_terms'] = terms
        chunk.metadata['term_count'] = len(terms)
        
        # Categorize chunk based on terms
        if any(t['term'] == 'quy định' for t in terms):
            chunk.metadata['chunk_type'] = 'regulatory'
        elif any(t['term'] == 'hướng dẫn' for t in terms):
            chunk.metadata['chunk_type'] = 'guidance'
        
        return chunk
```

### 3. Date and Number Formats

```python
import re
from datetime import datetime

class VietnameseDateParser:
    """
    Parse Vietnamese date formats in legal documents
    """
    
    MONTH_NAMES = {
        'một': 1, 'hai': 2, 'ba': 3, 'bốn': 4, 
        'năm': 5, 'sáu': 6, 'bảy': 7, 'tám': 8,
        'chín': 9, 'mười': 10, 'mười một': 11, 'mười hai': 12
    }
    
    def parse_date(self, text: str) -> Optional[datetime]:
        """
        Parse dates like "ngày 15 tháng 6 năm 2024"
        """
        # Pattern: ngày DD tháng MM năm YYYY
        pattern = r'ngày\s+(\d+)\s+tháng\s+(\d+)\s+năm\s+(\d+)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            day, month, year = match.groups()
            try:
                return datetime(int(year), int(month), int(day))
            except:
                pass
        
        return None
    
    def parse_document_number(self, text: str) -> Optional[str]:
        """
        Parse document numbers like "92/2024/NĐ-CP"
        """
        pattern = r'(\d+)/([\d-]+)/(NĐ-CP|TT|QĐ|CT)[- ]?(\w+)?'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(0)
        
        return None

class VietnameseNumberParser:
    """
    Parse Vietnamese number formats
    """
    
    def parse_article_number(self, text: str) -> Optional[int]:
        """
        Extract article number from "Điều 15" or "Điều mười lăm"
        """
        # Try digit format first
        pattern = r'Điều\s+(\d+)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return int(match.group(1))
        
        # Try word format
        number_words = {
            'một': 1, 'hai': 2, 'ba': 3, 'bốn': 4, 'năm': 5,
            'sáu': 6, 'bảy': 7, 'tám': 8, 'chín': 9, 'mười': 10,
            'mười một': 11, 'mười hai': 12, 'mười ba': 13,
            'mười bốn': 14, 'mười lăm': 15
        }
        
        for word, number in number_words.items():
            if f'điều {word}' in text.lower():
                return number
        
        return None
```

### 4. Stopwords for Vietnamese

```python
VIETNAMESE_LEGAL_STOPWORDS = [
    # Common Vietnamese stopwords
    'là', 'và', 'của', 'có', 'được', 'cho', 'để',
    'này', 'đó', 'các', 'những', 'một', 'từ', 'trong',
    
    # Legal document stopwords
    'quy định', 'theo', 'tại', 'về', 'của', 'bao gồm',
    'như sau', 'sau đây', 'điều khoản', 'văn bản',
    
    # Filler words
    'đã', 'sẽ', 'đang', 'cũng', 'rất', 'thì', 'nhưng'
]

def filter_vietnamese_stopwords(tokens: List[str]) -> List[str]:
    """
    Remove Vietnamese stopwords from tokens
    """
    return [
        token for token in tokens
        if token.lower() not in VIETNAMESE_LEGAL_STOPWORDS
    ]
```

---

## BEST PRACTICES SUMMARY

### DO's ✅

1. **Respect Document Structure**
   ```python
   # Always parse structure before chunking
   structure = parse_vietnamese_legal_doc(text)
   chunks = create_chunks_from_structure(structure)
   ```

2. **Preserve Context**
   ```python
   # Include parent context in every chunk
   chunk_text = f"[Chương {ch_num}]\nĐiều {art_num}...\n{content}"
   ```

3. **Progressive Loading**
   ```python
   # Start with TOC, then load relevant sections
   toc = await load_toc(doc_id)
   relevant = identify_relevant_from_toc(query, toc)
   content = await load_sections(relevant)
   ```

4. **Hierarchical Synthesis**
   ```python
   # Bottom-up aggregation
   section_facts → article_facts → doc_facts → final_answer
   ```

5. **Async Processing**
   ```python
   # Process sections in parallel
   results = await asyncio.gather(*[
       extract_from_section(s) for s in sections
   ])
   ```

6. **Vietnamese Normalization**
   ```python
   # Always normalize Vietnamese text
   text = unicodedata.normalize('NFC', text)
   ```

### DON'Ts ❌

1. **Don't Over-Chunk**
   ```python
   # ❌ BAD: 1 sentence = 1 chunk
   # ✅ GOOD: 1 article = 1 chunk (or multiple if >1500 tokens)
   ```

2. **Don't Ignore Cross-References**
   ```python
   # ❌ BAD: Chunk without tracking references
   # ✅ GOOD: Extract and store all "Điều X" references
   ```

3. **Don't Load Everything**
   ```python
   # ❌ BAD: Load all 100 documents at once
   # ✅ GOOD: Load progressively (PEEK → ANALYZE → LOAD)
   ```

4. **Don't Flatten Hierarchy**
   ```python
   # ❌ BAD: Concatenate all chunks → single LLM call
   # ✅ GOOD: Hierarchical synthesis with aggregation
   ```

5. **Don't Skip Normalization**
   ```python
   # ❌ BAD: Process raw Vietnamese text
   # ✅ GOOD: Normalize diacritics and encoding first
   ```

---

## QUICK REFERENCE GUIDE

### Chunking Checklist

- [ ] Parse document structure (Chương → Điều → Khoản)
- [ ] Create chunks at appropriate level (article by default)
- [ ] Include parent context in each chunk
- [ ] Track cross-references (Điều X, Khoản Y)
- [ ] Add hierarchical metadata
- [ ] Normalize Vietnamese text
- [ ] Validate chunk sizes (200-1500 tokens)

### Context Loading Checklist

- [ ] Analyze query complexity
- [ ] Start with overview (TOC)
- [ ] Identify relevant sections
- [ ] Load within token budget
- [ ] Expand if multi-hop query
- [ ] Track loaded tokens
- [ ] Cache frequently accessed content

### Synthesis Checklist

- [ ] Use hierarchical strategy for complex queries
- [ ] Process sections in parallel
- [ ] Aggregate bottom-up
- [ ] Track confidence scores
- [ ] Preserve citations
- [ ] Handle conflicts
- [ ] Build synthesis tree for transparency

### Vietnamese Processing Checklist

- [ ] Normalize Unicode (NFC)
- [ ] Detect legal terms
- [ ] Parse dates and numbers
- [ ] Handle diacritics correctly
- [ ] Use Vietnamese stopwords
- [ ] Preserve document structure keywords

---

## CODE EXAMPLES FOR COMMON SCENARIOS

### Scenario 1: Chunking a New Legal Document

```python
from adaptive_chunker import AdaptiveChunkerForVietnameseLaw

# Initialize chunker
chunker = AdaptiveChunkerForVietnameseLaw()

# Load document
with open('nghidinh_92_2024.txt', 'r', encoding='utf-8') as f:
    document_text = f.read()

# Chunk document
chunks = chunker.chunk_document(
    document_text=document_text,
    document_id='doc_92_2024',
    law_id='92/2024/NĐ-CP'
)

# Store chunks in database
for chunk in chunks:
    await db.store_chunk(chunk)
    
    # Also create embedding
    embedding = await embedding_model.embed(chunk.text)
    await vector_db.store(chunk.chunk_id, embedding, chunk)

print(f"Created {len(chunks)} chunks")
```

### Scenario 2: Processing a Query

```python
from smart_pipeline import SmartQueryPipeline

# Initialize pipeline
pipeline = SmartQueryPipeline(config={
    'max_tokens': 8000,
    'llm_mini': 'gpt-4o-mini',
    'llm_main': 'gpt-4o'
})

# User query
query = "So sánh quy định về giấy phép bay giữa Nghị định 92/2024 và Thông tư 15/2024"

# Process query
result = await pipeline.process_query(
    query=query,
    document_ids=['92/2024/NĐ-CP', '15/2024/TT-BGTVT']
)

# Return response
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
print(f"Sources: {len(result['synthesis_tree']['hierarchy'])} documents")
```

### Scenario 3: Multi-hop Navigation

```python
from multi_hop_navigator import MultiHopNavigator

# Initialize navigator
navigator = MultiHopNavigator(
    document_store=doc_store,
    graph_store=graph_store,
    max_hops=3
)

# Navigate from starting document
result = await navigator.navigate_for_query(
    query="Các văn bản hướng dẫn thi hành Nghị định 92",
    start_documents=['92/2024/NĐ-CP'],
    navigation_strategy='bfs'
)

# Print navigation path
for step in result['navigation_path']:
    print(f"Hop {step['depth']}: {step['document']} (relevance: {step['relevance']})")
```

---

## CONCLUSION

This skill provides RLM-inspired techniques that can significantly improve your Vietnamese legal document RAG system without requiring full RLM implementation. Key takeaways:

1. **Adaptive Chunking** → Respect document structure
2. **Hierarchical Context** → Load progressively, not all at once
3. **Smart Synthesis** → Bottom-up aggregation with parallel processing
4. **Multi-hop Navigation** → Follow relationships programmatically
5. **Vietnamese-Aware** → Handle diacritics, legal terms, and formats

### Next Steps

1. **Start Small**: Implement adaptive chunking first
2. **Measure Impact**: Compare with current fixed chunking
3. **Iterate**: Add progressive loading and hierarchical synthesis
4. **Optimize**: Profile and optimize bottlenecks
5. **Scale**: Add caching, async, and parallelization

### References

- RLM Paper: https://arxiv.org/abs/2512.24601v1
- RLM GitHub: https://github.com/alexzhang13/rlm
- ATTECH Project Docs: /mnt/project/

---

**End of Skill File**

**Version**: 1.0  
**Last Updated**: 31 January 2026  
**Author**: Claude AI Assistant (based on RLM research by Zhang et al. 2025)
