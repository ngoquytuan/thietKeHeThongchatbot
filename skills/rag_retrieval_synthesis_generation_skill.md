# RAG Retrieval, Synthesis & Generation Skill (FR04)

## Overview
This skill covers the core RAG pipeline: Retrieval (FR04.1), Synthesis (FR04.2), and Generation (FR04.3) for Vietnamese document systems with hybrid search, context optimization, and LLM integration.

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     RAG PIPELINE                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐      │
│  │  RETRIEVAL  │──▶│  SYNTHESIS   │──▶│   GENERATION    │      │
│  │   (FR04.1)  │   │   (FR04.2)   │   │    (FR04.3)     │      │
│  └─────────────┘   └──────────────┘   └─────────────────┘      │
│        │                   │                     │               │
│        ▼                   ▼                     ▼               │
│  Vector Search      Context Merge         LLM Response          │
│  BM25 Search        Deduplication         Streaming             │
│  Hybrid Rank        Compression           Citations             │
│  Graph Traverse     Reranking             Quality Check         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## FR04.1 - RETRIEVAL

### 1. Hybrid Search Implementation

```python
from typing import List, Dict, Tuple
import numpy as np
from rank_bm25 import BM25Okapi
import chromadb

class HybridRetriever:
    """
    Hybrid retrieval combining vector search, BM25, and optional graph traversal
    """
    
    def __init__(
        self,
        chroma_client: chromadb.Client,
        collection_name: str,
        bm25_corpus: List[str] = None
    ):
        self.chroma_collection = chroma_client.get_collection(collection_name)
        
        # BM25 setup
        if bm25_corpus:
            tokenized_corpus = [doc.split() for doc in bm25_corpus]
            self.bm25 = BM25Okapi(tokenized_corpus)
            self.bm25_corpus = bm25_corpus
        else:
            self.bm25 = None
    
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        alpha: float = 0.5,  # weight for vector vs BM25
        use_graph: bool = False,
        filters: Dict = None
    ) -> List[Dict]:
        """
        Hybrid retrieval with multiple strategies
        
        Args:
            query: Search query
            top_k: Number of results to return
            alpha: Weight balance (0=pure BM25, 1=pure vector)
            use_graph: Include graph-based retrieval
            filters: Metadata filters (e.g., {"document_type": "LEGAL_RND"})
        
        Returns:
            List of retrieved documents with scores
        """
        results = []
        
        # 1. Vector Search
        vector_results = self._vector_search(query, top_k * 2, filters)
        
        # 2. BM25 Search
        if self.bm25:
            bm25_results = self._bm25_search(query, top_k * 2)
        else:
            bm25_results = []
        
        # 3. Hybrid Ranking
        hybrid_results = self._hybrid_rank(
            vector_results, 
            bm25_results, 
            alpha
        )
        
        # 4. Graph Enhancement (optional)
        if use_graph:
            hybrid_results = self._enhance_with_graph(hybrid_results, top_k)
        
        # 5. Select top_k
        final_results = hybrid_results[:top_k]
        
        return final_results
    
    def _vector_search(
        self, 
        query: str, 
        top_k: int,
        filters: Dict = None
    ) -> List[Dict]:
        """
        Vector similarity search using ChromaDB
        """
        # Query ChromaDB
        results = self.chroma_collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filters if filters else None
        )
        
        # Format results
        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'vector_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                'source': 'vector'
            })
        
        return formatted
    
    def _bm25_search(self, query: str, top_k: int) -> List[Dict]:
        """
        BM25 keyword-based search
        """
        # Tokenize query
        tokenized_query = query.split()
        
        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        # Format results
        results = []
        for idx in top_indices:
            results.append({
                'id': f"bm25_{idx}",
                'text': self.bm25_corpus[idx],
                'bm25_score': scores[idx],
                'source': 'bm25'
            })
        
        return results
    
    def _hybrid_rank(
        self,
        vector_results: List[Dict],
        bm25_results: List[Dict],
        alpha: float
    ) -> List[Dict]:
        """
        Combine and rank results from vector and BM25 search
        
        Using Reciprocal Rank Fusion (RRF)
        """
        # Create unified result dict
        unified_results = {}
        
        # Process vector results
        for rank, result in enumerate(vector_results, 1):
            doc_id = result['id']
            rrf_score = 1.0 / (60 + rank)  # RRF constant = 60
            
            if doc_id not in unified_results:
                unified_results[doc_id] = result.copy()
                unified_results[doc_id]['rrf_score'] = 0
                unified_results[doc_id]['rank_sources'] = []
            
            unified_results[doc_id]['rrf_score'] += alpha * rrf_score
            unified_results[doc_id]['rank_sources'].append(('vector', rank))
        
        # Process BM25 results
        for rank, result in enumerate(bm25_results, 1):
            doc_id = result['id']
            rrf_score = 1.0 / (60 + rank)
            
            if doc_id not in unified_results:
                unified_results[doc_id] = result.copy()
                unified_results[doc_id]['rrf_score'] = 0
                unified_results[doc_id]['rank_sources'] = []
            
            unified_results[doc_id]['rrf_score'] += (1 - alpha) * rrf_score
            unified_results[doc_id]['rank_sources'].append(('bm25', rank))
        
        # Sort by RRF score
        sorted_results = sorted(
            unified_results.values(),
            key=lambda x: x['rrf_score'],
            reverse=True
        )
        
        return sorted_results
    
    def _enhance_with_graph(
        self, 
        results: List[Dict], 
        expand_to: int
    ) -> List[Dict]:
        """
        Enhance results using graph relationships
        """
        enhanced = results.copy()
        seen_ids = {r['id'] for r in results}
        
        # For each result, find related documents
        for result in results[:5]:  # Only expand top 5
            related_ids = self._get_related_docs(result['id'])
            
            for related_id in related_ids:
                if related_id not in seen_ids:
                    # Fetch related document
                    related_doc = self._fetch_document(related_id)
                    if related_doc:
                        related_doc['rrf_score'] = result['rrf_score'] * 0.5  # Dampen score
                        related_doc['source'] = 'graph'
                        enhanced.append(related_doc)
                        seen_ids.add(related_id)
                        
                        if len(enhanced) >= expand_to:
                            break
            
            if len(enhanced) >= expand_to:
                break
        
        # Re-sort
        enhanced.sort(key=lambda x: x['rrf_score'], reverse=True)
        
        return enhanced
    
    def _get_related_docs(self, doc_id: str) -> List[str]:
        """Get related document IDs from graph"""
        # Query PostgreSQL for related documents
        import psycopg2
        
        conn = psycopg2.connect(
            host="192.168.1.88",
            port=15432,
            database="chatbotR4",
            user="kb_admin",
            password="1234567890"
        )
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT related_docs 
                FROM documents 
                WHERE document_id = %s
            """, (doc_id,))
            
            result = cur.fetchone()
            if result and result[0]:
                return result[0]  # Assuming JSONB array
        
        conn.close()
        return []
    
    def _fetch_document(self, doc_id: str) -> Dict:
        """Fetch document by ID"""
        results = self.chroma_collection.get(ids=[doc_id])
        
        if results['ids']:
            return {
                'id': results['ids'][0],
                'text': results['documents'][0],
                'metadata': results['metadatas'][0]
            }
        
        return None
```

### 2. Query Expansion for Vietnamese

```python
from underthesea import word_tokenize

class VietnameseQueryExpander:
    """
    Expand Vietnamese queries with synonyms and related terms
    """
    
    def __init__(self):
        # Legal domain vocabulary
        self.synonyms = {
            "quy định": ["quy chế", "quy tắc", "điều lệ"],
            "thủ tục": ["trình tự", "quy trình", "các bước"],
            "hồ sơ": ["giấy tờ", "tài liệu", "chứng từ"],
            "nghị định": ["NĐ", "nghị định của chính phủ"],
            "quyết định": ["QĐ", "quyết định hành chính"],
            "thông tư": ["TT", "thông tư hướng dẫn"]
        }
        
        # Common abbreviations
        self.abbreviations = {
            "NĐ": "nghị định",
            "QĐ": "quyết định",
            "TT": "thông tư",
            "CP": "chính phủ",
            "TTg": "thủ tướng chính phủ"
        }
    
    def expand_query(self, query: str, max_terms: int = 3) -> List[str]:
        """
        Expand query with synonyms and related terms
        
        Returns:
            List of expanded query variants
        """
        expanded_queries = [query]  # Original query
        
        # Tokenize
        tokens = word_tokenize(query.lower())
        
        # Find synonyms
        for token in tokens:
            if token in self.synonyms:
                # Create new queries with synonyms
                for synonym in self.synonyms[token][:max_terms]:
                    expanded_query = query.lower().replace(token, synonym)
                    if expanded_query not in expanded_queries:
                        expanded_queries.append(expanded_query)
        
        # Expand abbreviations
        for abbr, full in self.abbreviations.items():
            if abbr in query:
                expanded_query = query.replace(abbr, full)
                if expanded_query not in expanded_queries:
                    expanded_queries.append(expanded_query)
        
        return expanded_queries
    
    def expand_with_llm(self, query: str, llm_client) -> List[str]:
        """
        Use LLM to generate query variations
        """
        prompt = f"""Given this Vietnamese query: "{query}"
        
        Generate 3 alternative ways to phrase the same question in Vietnamese.
        Focus on legal and administrative contexts.
        
        Output format (one per line):
        1. [alternative 1]
        2. [alternative 2]
        3. [alternative 3]
        """
        
        response = llm_client.generate(prompt)
        
        # Parse response
        alternatives = []
        for line in response.split('\n'):
            if line.strip() and any(line.startswith(str(i)) for i in range(1, 4)):
                alt_query = line.split('.', 1)[1].strip()
                alternatives.append(alt_query)
        
        return [query] + alternatives
```

### 3. Reranking Module

```python
from sentence_transformers import CrossEncoder

class Reranker:
    """
    Rerank retrieved documents using cross-encoder
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)
    
    def rerank(
        self, 
        query: str, 
        documents: List[Dict], 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Rerank documents using cross-encoder
        """
        # Prepare query-document pairs
        pairs = [(query, doc['text']) for doc in documents]
        
        # Get cross-encoder scores
        scores = self.model.predict(pairs)
        
        # Add scores to documents
        for doc, score in zip(documents, scores):
            doc['rerank_score'] = float(score)
        
        # Sort by rerank score
        reranked = sorted(
            documents, 
            key=lambda x: x['rerank_score'], 
            reverse=True
        )
        
        return reranked[:top_k]
```

## FR04.2 - SYNTHESIS

### 1. Context Builder

```python
class ContextBuilder:
    """
    Build optimized context from retrieved documents
    """
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
    
    def build_context(
        self, 
        query: str,
        retrieved_docs: List[Dict],
        include_metadata: bool = True
    ) -> Dict:
        """
        Build context from retrieved documents
        
        Returns:
            Dict with context text, citations, and metadata
        """
        # 1. Deduplicate documents
        unique_docs = self._deduplicate(retrieved_docs)
        
        # 2. Extract relevant passages
        relevant_passages = self._extract_relevant(query, unique_docs)
        
        # 3. Compress if needed
        if self._count_tokens(relevant_passages) > self.max_tokens:
            relevant_passages = self._compress(relevant_passages, self.max_tokens)
        
        # 4. Format context
        context_text = self._format_context(relevant_passages, include_metadata)
        
        # 5. Build citations
        citations = self._build_citations(relevant_passages)
        
        return {
            "context": context_text,
            "citations": citations,
            "num_sources": len(unique_docs),
            "token_count": self._count_tokens([context_text])
        }
    
    def _deduplicate(self, documents: List[Dict]) -> List[Dict]:
        """
        Remove duplicate or highly similar documents
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        if len(documents) <= 1:
            return documents
        
        # Extract texts
        texts = [doc['text'] for doc in documents]
        
        # Calculate TF-IDF similarity
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarities = cosine_similarity(tfidf_matrix)
        
        # Keep documents below similarity threshold
        unique_docs = []
        used_indices = set()
        
        for i, doc in enumerate(documents):
            if i in used_indices:
                continue
            
            # Check similarity with already selected docs
            is_unique = True
            for j in range(i):
                if j in used_indices and similarities[i][j] > 0.85:  # 85% similarity threshold
                    is_unique = False
                    break
            
            if is_unique:
                unique_docs.append(doc)
                used_indices.add(i)
        
        return unique_docs
    
    def _extract_relevant(
        self, 
        query: str, 
        documents: List[Dict]
    ) -> List[Dict]:
        """
        Extract most relevant passages from each document
        """
        from underthesea import word_tokenize
        
        query_tokens = set(word_tokenize(query.lower()))
        
        relevant_passages = []
        
        for doc in documents:
            # Split into sentences
            sentences = doc['text'].split('.')
            
            # Score each sentence
            sentence_scores = []
            for sent in sentences:
                sent_tokens = set(word_tokenize(sent.lower()))
                
                # Calculate overlap
                overlap = len(query_tokens & sent_tokens)
                score = overlap / len(query_tokens) if query_tokens else 0
                
                sentence_scores.append((sent, score))
            
            # Select top sentences
            top_sentences = sorted(
                sentence_scores, 
                key=lambda x: x[1], 
                reverse=True
            )[:3]  # Top 3 sentences per document
            
            relevant_text = '. '.join([s[0] for s in top_sentences])
            
            relevant_passages.append({
                'text': relevant_text,
                'source_id': doc['id'],
                'metadata': doc.get('metadata', {})
            })
        
        return relevant_passages
    
    def _compress(
        self, 
        passages: List[Dict], 
        max_tokens: int
    ) -> List[Dict]:
        """
        Compress passages to fit token limit
        """
        # Simple truncation strategy
        # TODO: Implement smarter compression (extractive summarization)
        
        current_tokens = 0
        compressed = []
        
        for passage in passages:
            passage_tokens = self._count_tokens([passage['text']])
            
            if current_tokens + passage_tokens <= max_tokens:
                compressed.append(passage)
                current_tokens += passage_tokens
            else:
                # Truncate last passage
                remaining_tokens = max_tokens - current_tokens
                if remaining_tokens > 50:  # Only include if meaningful
                    truncated_text = self._truncate_to_tokens(
                        passage['text'], 
                        remaining_tokens
                    )
                    compressed.append({
                        **passage,
                        'text': truncated_text
                    })
                break
        
        return compressed
    
    def _count_tokens(self, texts: List[str]) -> int:
        """
        Estimate token count (rough approximation)
        """
        # Vietnamese: ~1 token per word
        total_words = sum(len(text.split()) for text in texts)
        return total_words
    
    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to max tokens"""
        words = text.split()
        return ' '.join(words[:max_tokens])
    
    def _format_context(
        self, 
        passages: List[Dict], 
        include_metadata: bool
    ) -> str:
        """
        Format context for LLM
        """
        formatted_passages = []
        
        for i, passage in enumerate(passages, 1):
            text = f"[Source {i}]\n{passage['text']}"
            
            if include_metadata and passage.get('metadata'):
                metadata = passage['metadata']
                if 'document_type' in metadata:
                    text += f"\nLoại văn bản: {metadata['document_type']}"
                if 'document_id' in metadata:
                    text += f"\nMã văn bản: {metadata['document_id']}"
            
            formatted_passages.append(text)
        
        return "\n\n".join(formatted_passages)
    
    def _build_citations(self, passages: List[Dict]) -> List[Dict]:
        """
        Build citation references
        """
        citations = []
        
        for i, passage in enumerate(passages, 1):
            citation = {
                'citation_number': i,
                'source_id': passage['source_id'],
                'metadata': passage.get('metadata', {})
            }
            citations.append(citation)
        
        return citations
```

## FR04.3 - GENERATION

### 1. LLM Integration

```python
from anthropic import Anthropic
import openai
from typing import Generator

class LLMGenerator:
    """
    LLM-based response generation with multiple provider support
    """
    
    def __init__(
        self, 
        provider: str = "anthropic",  # or "openai"
        model: str = None,
        api_key: str = None
    ):
        self.provider = provider
        
        if provider == "anthropic":
            self.client = Anthropic(api_key=api_key)
            self.model = model or "claude-sonnet-4-20250514"
        elif provider == "openai":
            openai.api_key = api_key
            self.model = model or "gpt-4o"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate(
        self,
        query: str,
        context: str,
        system_prompt: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """
        Generate response using LLM
        
        Args:
            query: User query
            context: Retrieved context
            system_prompt: System instructions
            temperature: Randomness (0-1)
            max_tokens: Max response length
            stream: Enable streaming
        
        Returns:
            Generated response (or generator if streaming)
        """
        # Build prompt
        if not system_prompt:
            system_prompt = self._default_system_prompt()
        
        user_message = f"""Based on the following context, answer the question in Vietnamese.

Context:
{context}

Question: {query}

Answer:"""
        
        # Generate
        if self.provider == "anthropic":
            return self._generate_anthropic(
                system_prompt, 
                user_message, 
                temperature, 
                max_tokens, 
                stream
            )
        elif self.provider == "openai":
            return self._generate_openai(
                system_prompt, 
                user_message, 
                temperature, 
                max_tokens, 
                stream
            )
    
    def _generate_anthropic(
        self, 
        system_prompt: str, 
        user_message: str,
        temperature: float,
        max_tokens: int,
        stream: bool
    ):
        """Generate using Claude API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": user_message
            }],
            stream=stream
        )
        
        if stream:
            return self._stream_anthropic(response)
        else:
            return response.content[0].text
    
    def _stream_anthropic(self, response) -> Generator[str, None, None]:
        """Stream Claude responses"""
        for event in response:
            if event.type == "content_block_delta":
                yield event.delta.text
    
    def _generate_openai(
        self, 
        system_prompt: str, 
        user_message: str,
        temperature: float,
        max_tokens: int,
        stream: bool
    ):
        """Generate using OpenAI API"""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        if stream:
            return self._stream_openai(response)
        else:
            return response.choices[0].message.content
    
    def _stream_openai(self, response) -> Generator[str, None, None]:
        """Stream OpenAI responses"""
        for chunk in response:
            if chunk.choices[0].delta.get("content"):
                yield chunk.choices[0].delta.content
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for Vietnamese RAG"""
        return """You are a helpful Vietnamese legal and administrative assistant.

Your task is to answer questions based ONLY on the provided context.

Guidelines:
- Answer in Vietnamese
- Be concise and accurate
- Cite sources using [Source X] notation
- If the context doesn't contain enough information, say "Tôi không tìm thấy đủ thông tin trong tài liệu để trả lời câu hỏi này."
- Preserve legal document codes and terminology exactly as they appear
- Format lists and bullet points clearly
"""
```

### 2. Citation Injection

```python
class CitationInjector:
    """
    Inject citations into generated responses
    """
    
    def inject_citations(
        self, 
        response: str, 
        citations: List[Dict]
    ) -> Dict:
        """
        Add citations to response
        
        Returns:
            Dict with response and formatted citations
        """
        # Find citation markers in response (e.g., [Source 1])
        import re
        
        citation_pattern = r'\[Source (\d+)\]'
        matches = re.findall(citation_pattern, response)
        
        # Build citation list
        used_citations = []
        for match in matches:
            citation_num = int(match)
            if citation_num <= len(citations):
                citation = citations[citation_num - 1]
                used_citations.append({
                    'number': citation_num,
                    'source_id': citation['source_id'],
                    'metadata': citation['metadata']
                })
        
        # Format citation list
        citation_text = self._format_citations(used_citations)
        
        return {
            'response': response,
            'citations': used_citations,
            'citation_text': citation_text
        }
    
    def _format_citations(self, citations: List[Dict]) -> str:
        """Format citations for display"""
        if not citations:
            return ""
        
        lines = ["\n\nNguồn tham khảo:"]
        
        for cite in citations:
            metadata = cite['metadata']
            line = f"[{cite['number']}] "
            
            if 'title' in metadata:
                line += metadata['title']
            
            if 'document_id' in metadata:
                line += f" (Mã: {metadata['document_id']})"
            
            lines.append(line)
        
        return "\n".join(lines)
```

### 3. Complete RAG Pipeline

```python
class RAGPipeline:
    """
    Complete RAG pipeline orchestrating retrieval, synthesis, and generation
    """
    
    def __init__(
        self,
        retriever: HybridRetriever,
        context_builder: ContextBuilder,
        generator: LLMGenerator,
        reranker: Reranker = None
    ):
        self.retriever = retriever
        self.context_builder = context_builder
        self.generator = generator
        self.reranker = reranker
    
    async def query(
        self,
        user_query: str,
        top_k: int = 5,
        use_reranking: bool = True,
        stream: bool = False,
        filters: Dict = None
    ) -> Dict:
        """
        Execute complete RAG query
        
        Returns:
            Dict with response, sources, and metadata
        """
        # Step 1: Retrieval
        retrieved_docs = self.retriever.retrieve(
            query=user_query,
            top_k=top_k * 2,  # Retrieve more for reranking
            filters=filters
        )
        
        # Step 2: Reranking (optional)
        if use_reranking and self.reranker:
            retrieved_docs = self.reranker.rerank(
                query=user_query,
                documents=retrieved_docs,
                top_k=top_k
            )
        else:
            retrieved_docs = retrieved_docs[:top_k]
        
        # Step 3: Synthesis
        context_data = self.context_builder.build_context(
            query=user_query,
            retrieved_docs=retrieved_docs
        )
        
        # Step 4: Generation
        response = self.generator.generate(
            query=user_query,
            context=context_data['context'],
            stream=stream
        )
        
        # Step 5: Citation Injection
        if not stream:
            injector = CitationInjector()
            final_output = injector.inject_citations(
                response,
                context_data['citations']
            )
        else:
            # For streaming, citations added at the end
            final_output = {
                'response': response,  # Generator
                'citations': context_data['citations']
            }
        
        # Add metadata
        final_output['metadata'] = {
            'num_retrieved': len(retrieved_docs),
            'num_sources': context_data['num_sources'],
            'token_count': context_data['token_count']
        }
        
        return final_output
```

## Vietnamese-Specific Optimizations

### Query Preprocessing
```python
def preprocess_vietnamese_query(query: str) -> str:
    """
    Preprocess Vietnamese query before retrieval
    """
    from underthesea import word_tokenize
    
    # Normalize whitespace
    query = ' '.join(query.split())
    
    # Expand common abbreviations
    abbreviations = {
        'NĐ': 'nghị định',
        'QĐ': 'quyết định',
        'TT': 'thông tư'
    }
    
    for abbr, full in abbreviations.items():
        if abbr in query:
            query = query + ' ' + query.replace(abbr, full)
    
    return query
```

## Performance Monitoring

```python
import time
from functools import wraps

def monitor_pipeline_stage(stage_name: str):
    """
    Decorator to monitor RAG pipeline stages
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            elapsed = time.time() - start
            
            print(f"⏱️  {stage_name}: {elapsed:.2f}s")
            
            return result
        return wrapper
    return decorator

# Usage
@monitor_pipeline_stage("Retrieval")
async def monitored_retrieve(query):
    return retriever.retrieve(query)
```

## Testing

```python
# Test retrieval
def test_retrieval():
    query = "Thủ tục cấp giấy phép xây dựng?"
    results = retriever.retrieve(query, top_k=5)
    
    assert len(results) == 5
    assert all('text' in r for r in results)
    assert all('score' in r or 'rrf_score' in r for r in results)

# Test context building
def test_context_building():
    docs = [...]  # Mock documents
    context = context_builder.build_context("test query", docs)
    
    assert 'context' in context
    assert 'citations' in context
    assert context['token_count'] <= 4000

# Test generation
def test_generation():
    response = generator.generate(
        query="Test query",
        context="Test context",
        stream=False
    )
    
    assert len(response) > 0
    assert isinstance(response, str)
```

## Quick Reference

### Retrieval Parameters
```python
# Conservative (precision-focused)
top_k=5, alpha=0.7, use_reranking=True

# Balanced
top_k=10, alpha=0.5, use_reranking=True

# Exploratory (recall-focused)
top_k=20, alpha=0.3, use_reranking=False, use_graph=True
```

### Commands
```bash
# Test retrieval
python test_retrieval.py --query "Nghị định 123/NĐ-CP" --top-k 10

# Benchmark pipeline
python benchmark_rag.py --queries test_queries.json --output results.csv

# Test streaming
python test_streaming.py --query "Quy định về BHXH"
```

## Success Criteria

- ✅ Retrieval precision@5 > 0.8
- ✅ Average retrieval time < 200ms
- ✅ Context token count < 4000
- ✅ Response generation time < 3s
- ✅ Citation accuracy > 95%
- ✅ Handles 100 concurrent requests

## End of Skill File
