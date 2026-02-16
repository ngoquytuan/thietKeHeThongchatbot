# HAYSTACK PATTERNS ÁP DỤNG CHO ATTECH RAG
## Tổng hợp những kỹ thuật hay nhất để nâng cấp hệ thống

**Ngày:** 16/02/2026  
**Mục tiêu:** Cherry-pick các pattern tốt nhất từ Haystack framework để cải thiện ATTECH RAG mà KHÔNG cần migrate framework  
**Nguyên tắc:** Học ý tưởng, implement theo cách của mình trên FastAPI + PostgreSQL + ChromaDB stack hiện tại

---

## 1. RECIPROCAL RANK FUSION (RRF) — Thay thế Weighted Score

### Vấn đề hiện tại
Hệ thống đang dùng weighted combination đơn giản: `score = 0.7 * semantic + 0.3 * keyword`. Cách này có nhược điểm lớn: semantic score (cosine similarity 0-1) và keyword score (BM25 score, range không cố định) có scale khác nhau, normalize không chính xác dẫn đến bias.

### Haystack làm gì
Haystack cung cấp `DocumentJoiner` với 3 chiến lược merge, trong đó RRF được đánh giá hiệu quả nhất cho hybrid retrieval. RRF không cần normalize score — chỉ dùng ranking position, giải quyết triệt để vấn đề score scale khác nhau.

### Cách implement

```python
# src/core/search/rrf_ranker.py

from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class RankedResult:
    document_id: str
    chunk_id: str
    content: str
    metadata: dict
    rrf_score: float = 0.0
    sources: List[str] = None  # Từ engine nào

class ReciprocalRankFusion:
    """
    RRF: score(d) = Σ 1/(k + rank_i(d))
    k = smoothing constant (thường = 60)
    rank_i = thứ hạng của document d trong retriever thứ i
    """
    
    def __init__(self, k: int = 60):
        self.k = k
    
    def fuse(
        self,
        result_lists: Dict[str, List[dict]],  # {"semantic": [...], "bm25": [...], "substring": [...]}
        top_k: int = 10
    ) -> List[RankedResult]:
        """
        Merge kết quả từ nhiều search engines bằng RRF.
        
        Ưu điểm so với weighted combination:
        - Không cần normalize scores (chỉ dùng rank position)
        - Tự động ưu tiên documents xuất hiện ở nhiều engines
        - Robust với outlier scores
        """
        doc_scores: Dict[str, float] = {}
        doc_data: Dict[str, dict] = {}
        doc_sources: Dict[str, List[str]] = {}
        
        for engine_name, results in result_lists.items():
            for rank, result in enumerate(results, start=1):
                doc_key = f"{result['document_id']}_{result['chunk_id']}"
                
                # RRF formula
                rrf_contribution = 1.0 / (self.k + rank)
                doc_scores[doc_key] = doc_scores.get(doc_key, 0.0) + rrf_contribution
                
                # Track sources
                if doc_key not in doc_sources:
                    doc_sources[doc_key] = []
                doc_sources[doc_key].append(engine_name)
                
                # Keep best metadata
                if doc_key not in doc_data:
                    doc_data[doc_key] = result
        
        # Sort by RRF score descending
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_key, score in sorted_docs[:top_k]:
            data = doc_data[doc_key]
            results.append(RankedResult(
                document_id=data['document_id'],
                chunk_id=data['chunk_id'],
                content=data['content'],
                metadata=data.get('metadata', {}),
                rrf_score=score,
                sources=doc_sources[doc_key]
            ))
        
        return results
```

### Integration vào search orchestrator

```python
# Thay đổi trong search_orchestrator.py

async def hybrid_search(self, query: str, top_k: int = 10) -> List[RankedResult]:
    # Chạy song song nhiều engines
    semantic_task = self.semantic_engine.search(query, top_k=20)
    bm25_task = self.bm25_engine.search(query, top_k=20)
    substring_task = self.substring_engine.search(query, top_k=20)
    
    semantic_results, bm25_results, substring_results = await asyncio.gather(
        semantic_task, bm25_task, substring_task
    )
    
    # RRF fusion thay vì weighted combination
    rrf = ReciprocalRankFusion(k=60)
    fused = rrf.fuse({
        "semantic": semantic_results,
        "bm25": bm25_results,
        "substring": substring_results
    }, top_k=top_k)
    
    return fused
```

### Ước tính impact
- **Accuracy:** +5-10% so với weighted combination (vì giải quyết score normalization issue)
- **Effort:** 1-2 ngày code + test
- **Risk:** Thấp — có thể A/B test song song với cách cũ

---

## 2. CROSS-ENCODER RERANKER — Pattern chuẩn từ Haystack

### Haystack làm gì
Haystack dùng `TransformersSimilarityRanker` đặt SAU retrieval, TRƯỚC generation. Pattern: retrieve nhiều (top-20~50) rồi rerank xuống ít (top-5~10). Điểm đặc biệt: Haystack mới thêm support cho Qwen3 Reranker qua `query_suffix` và `document_suffix` parameters.

### Cách implement cho ATTECH

```python
# src/core/search/cross_encoder_reranker.py

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import List, Tuple

class CrossEncoderReranker:
    """
    Cross-encoder reranker — pattern từ Haystack TransformersSimilarityRanker.
    
    Khác bi-encoder (encode query và doc riêng):
    - Cross-encoder encode (query, doc) CÙNG NHAU
    - Chậm hơn nhưng chính xác hơn rất nhiều
    - Phù hợp cho reranking top-K nhỏ (10-50 docs)
    """
    
    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",  # Option 1: BGE
        # model_name: str = "Qwen/Qwen3-Reranker",     # Option 2: Qwen3
        device: str = None,
        batch_size: int = 16,
        max_length: int = 512
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.batch_size = batch_size
        self.max_length = max_length
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        # Qwen3 Reranker cần suffix (pattern từ Haystack 2.22+)
        self.query_suffix = ""
        self.document_suffix = ""
        if "qwen" in model_name.lower():
            self.query_suffix = "Instruct: Given a query, retrieve passages that are relevant.\nQuery: "
            self.document_suffix = ""
    
    @torch.no_grad()
    def rerank(
        self,
        query: str,
        documents: List[dict],
        top_k: int = 5
    ) -> List[dict]:
        """
        Rerank documents bằng cross-encoder.
        
        Pipeline: Retrieval (top-20~50) → Rerank (top-5~10) → Generation
        """
        if not documents:
            return []
        
        # Prepare pairs
        query_text = f"{self.query_suffix}{query}"
        pairs = [
            (query_text, f"{self.document_suffix}{doc['content']}")
            for doc in documents
        ]
        
        # Batch scoring
        all_scores = []
        for i in range(0, len(pairs), self.batch_size):
            batch = pairs[i:i + self.batch_size]
            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt"
            ).to(self.device)
            
            outputs = self.model(**inputs)
            scores = outputs.logits.squeeze(-1).cpu().tolist()
            
            if isinstance(scores, float):
                scores = [scores]
            all_scores.extend(scores)
        
        # Attach scores and sort
        for doc, score in zip(documents, all_scores):
            doc['rerank_score'] = score
        
        reranked = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
        return reranked[:top_k]
```

### Tích hợp vào pipeline

```python
# Pipeline hoàn chỉnh theo Haystack pattern:
# 
# Query → [RRF Fusion (Semantic + BM25 + Substring)] → top-20
#       → [CrossEncoder Rerank] → top-5
#       → [DiversityFilter] → top-5 (loại near-duplicate)  
#       → [LostInTheMiddle Reorder] → top-5 (tối ưu vị trí)
#       → [Generation (GPT-4)]

async def full_rag_pipeline(self, query: str) -> dict:
    # Step 1: Multi-engine retrieval + RRF fusion
    candidates = await self.hybrid_search(query, top_k=20)
    
    # Step 2: Cross-encoder reranking  
    reranked = self.reranker.rerank(
        query=query,
        documents=[r.__dict__ for r in candidates],
        top_k=10
    )
    
    # Step 3: Diversity filtering (xem Section 3)
    diverse = self.diversity_filter(reranked, top_k=5)
    
    # Step 4: Lost-in-the-middle reordering (xem Section 4)
    reordered = self.lost_in_middle_reorder(diverse)
    
    # Step 5: Generation
    response = await self.generate(query, reordered)
    
    return response
```

### Ước tính impact
- **Accuracy:** +15-30% (đây là P0 blocker, ước tính từ 75% → 85-90%)
- **Latency:** +200-500ms (chấp nhận được, vẫn dưới 60s target)
- **Effort:** 1 tuần (đã có trong roadmap)

---

## 3. DIVERSITY RANKER — Giảm redundancy trong kết quả

### Vấn đề hiện tại
Khi search văn bản pháp luật, nhiều chunks từ cùng một văn bản hoặc các văn bản sửa đổi/bổ sung thường có nội dung gần giống nhau. Kết quả retrieval chứa nhiều near-duplicates, lãng phí context window của LLM.

### Haystack làm gì
DiversityRanker dùng Maximal Marginal Relevance (MMR) — chọn documents vừa relevant với query, vừa diverse so với những documents đã chọn. Haystack report tăng 20-30% pairwise cosine distance (diversity) trong context đưa cho LLM.

### Cách implement

```python
# src/core/search/diversity_ranker.py

import numpy as np
from typing import List

class DiversityRanker:
    """
    MMR-based diversity ranking — pattern từ Haystack DiversityRanker.
    
    MMR = λ * Sim(doc, query) - (1-λ) * max(Sim(doc, selected_docs))
    
    Cân bằng giữa relevance và diversity.
    """
    
    def __init__(
        self,
        lambda_param: float = 0.7,  # 1.0 = pure relevance, 0.0 = pure diversity
        similarity_threshold: float = 0.92  # Near-duplicate threshold
    ):
        self.lambda_param = lambda_param
        self.similarity_threshold = similarity_threshold
    
    def rank(
        self,
        documents: List[dict],
        query_embedding: np.ndarray = None,
        top_k: int = 5
    ) -> List[dict]:
        """
        Chọn documents đa dạng nhất mà vẫn relevant.
        
        Đặc biệt hữu ích cho Vietnamese legal docs:
        - Nhiều Nghị định sửa đổi/bổ sung cùng chủ đề
        - Nhiều chunks từ cùng văn bản
        - Các văn bản liên quan có nội dung overlap
        """
        if len(documents) <= top_k:
            return documents
        
        # Dùng embedding nếu có, hoặc dùng rerank_score
        selected = [documents[0]]  # Best scoring document
        remaining = documents[1:]
        
        while len(selected) < top_k and remaining:
            best_mmr = -float('inf')
            best_idx = 0
            
            for i, candidate in enumerate(remaining):
                # Relevance score (từ reranker hoặc RRF)
                relevance = candidate.get('rerank_score', candidate.get('rrf_score', 0))
                
                # Max similarity với đã chọn (dùng content overlap đơn giản)
                max_sim = max(
                    self._content_similarity(candidate['content'], s['content'])
                    for s in selected
                )
                
                # MMR formula
                mmr = self.lambda_param * relevance - (1 - self.lambda_param) * max_sim
                
                if mmr > best_mmr:
                    best_mmr = mmr
                    best_idx = i
            
            selected.append(remaining.pop(best_idx))
        
        return selected
    
    def _content_similarity(self, text1: str, text2: str) -> float:
        """
        Tính similarity nhanh bằng token overlap (Jaccard).
        Với Vietnamese: dùng word-level tokens.
        """
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        
        return len(intersection) / len(union)
```

### Khi nào dùng
- **LUÔN dùng** khi hybrid search trả > 5 results
- **ĐẶC BIỆT quan trọng** khi search chủ đề rộng như "quy định về thuế" (nhiều văn bản liên quan)
- Đặt SAU reranker, TRƯỚC generation

### Ước tính impact
- **Quality:** LLM nhận context đa dạng hơn → câu trả lời toàn diện hơn
- **Effort:** 1-2 ngày
- **Risk:** Rất thấp

---

## 4. LOST IN THE MIDDLE REORDERING — Tối ưu context placement

### Vấn đề
Nghiên cứu (Liu et al., 2023) chỉ ra LLMs "quên" nội dung ở giữa context window. Document relevant nhất ở vị trí 3/5 sẽ bị LLM bỏ qua nhiều hơn so với ở vị trí 1/5 hoặc 5/5.

### Haystack làm gì
LostInTheMiddleRanker sắp xếp lại documents theo pattern: relevant nhất ở đầu và cuối, kém relevant nhất ở giữa. Đây là optimization "free" — không thay đổi nội dung, chỉ thay đổi thứ tự.

### Cách implement

```python
# src/core/search/context_reorderer.py

from typing import List

class LostInTheMiddleReorderer:
    """
    Reorder documents: best ở đầu + cuối, worst ở giữa.
    Pattern từ Haystack LostInTheMiddleRanker.
    
    Input (sorted by relevance):  [1st, 2nd, 3rd, 4th, 5th]
    Output (optimized for LLM):   [1st, 3rd, 5th, 4th, 2nd]
    
    Giải thích: 1st và 2nd quan trọng nhất nên đặt ở đầu và cuối.
    """
    
    @staticmethod
    def reorder(documents: List[dict]) -> List[dict]:
        """
        Interleave documents: odd positions từ đầu, even positions từ cuối.
        """
        if len(documents) <= 2:
            return documents
        
        reordered = []
        left = 0
        right = len(documents) - 1
        turn_left = True
        
        while left <= right:
            if turn_left:
                reordered.append(documents[left])
                left += 1
            else:
                reordered.append(documents[right])
                right -= 1
            turn_left = not turn_left
        
        return reordered
```

### Ước tính impact
- **Quality:** +5-10% answer accuracy trên long context queries
- **Effort:** 30 phút code
- **Risk:** Zero — hoàn toàn không ảnh hưởng logic khác

---

## 5. SEMANTIC CHUNKING — Thay thế Fixed-Size Chunking

### Vấn đề hiện tại
Hệ thống đang chunk theo fixed-size (words/sentences). Điều này cắt ngang ngữ cảnh pháp lý — một Điều luật có thể bị chia thành 2-3 chunks không hoàn chỉnh.

### Haystack làm gì
Haystack 2.22 ra mắt `EmbeddingBasedDocumentSplitter` — chunk dựa trên semantic similarity. Khi cosine distance giữa 2 nhóm câu vượt ngưỡng (percentile), nó tạo split point. Kết quả: mỗi chunk chứa nội dung coherent về ngữ nghĩa.

### Cách implement cho Vietnamese Legal Docs

```python
# src/core/chunking/semantic_chunker.py

import numpy as np
from typing import List, Tuple

class SemanticChunker:
    """
    Semantic chunking — inspired by Haystack EmbeddingBasedDocumentSplitter.
    
    Thay vì cắt theo số từ cố định, cắt tại điểm "chuyển chủ đề"
    dựa trên embedding distance giữa các nhóm câu.
    
    Đặc biệt phù hợp cho Vietnamese legal documents vì:
    - Mỗi Điều/Khoản là một đơn vị ngữ nghĩa
    - Các mục con (a, b, c) thuộc cùng ngữ cảnh
    - Fixed-size chunking phá vỡ cấu trúc này
    """
    
    def __init__(
        self,
        embedding_model,  # Qwen3-Embedding-0.6B instance
        sentences_per_group: int = 3,
        percentile_threshold: float = 0.90,  # Split khi distance > 90th percentile
        min_chunk_length: int = 100,   # chars - merge chunks quá ngắn
        max_chunk_length: int = 1500   # chars - split chunks quá dài
    ):
        self.embedding_model = embedding_model
        self.sentences_per_group = sentences_per_group
        self.percentile_threshold = percentile_threshold
        self.min_chunk_length = min_chunk_length
        self.max_chunk_length = max_chunk_length
    
    async def chunk(self, text: str) -> List[str]:
        """
        1. Split text thành sentences
        2. Group N sentences liên tiếp
        3. Embed mỗi group
        4. Tính cosine distance giữa groups liền kề
        5. Split tại điểm distance > percentile threshold
        6. Merge chunks quá ngắn, split chunks quá dài
        """
        # Step 1: Split thành sentences (Vietnamese-aware)
        sentences = self._split_sentences_vietnamese(text)
        
        if len(sentences) <= self.sentences_per_group:
            return [text]
        
        # Step 2: Group sentences
        groups = []
        for i in range(len(sentences) - self.sentences_per_group + 1):
            group_text = " ".join(sentences[i:i + self.sentences_per_group])
            groups.append(group_text)
        
        # Step 3: Embed groups
        embeddings = await self.embedding_model.embed_batch(groups)
        
        # Step 4: Cosine distances giữa groups liền kề
        distances = []
        for i in range(len(embeddings) - 1):
            dist = 1 - np.dot(embeddings[i], embeddings[i + 1]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i + 1])
            )
            distances.append(dist)
        
        # Step 5: Tìm split points
        threshold = np.percentile(distances, self.percentile_threshold * 100)
        split_indices = [i + self.sentences_per_group 
                        for i, d in enumerate(distances) if d > threshold]
        
        # Step 6: Tạo chunks
        chunks = []
        prev_idx = 0
        for idx in split_indices:
            chunk_text = " ".join(sentences[prev_idx:idx])
            chunks.append(chunk_text)
            prev_idx = idx
        
        # Last chunk
        if prev_idx < len(sentences):
            chunks.append(" ".join(sentences[prev_idx:]))
        
        # Step 7: Merge/split theo min/max length
        chunks = self._enforce_length_constraints(chunks)
        
        return chunks
    
    def _split_sentences_vietnamese(self, text: str) -> List[str]:
        """
        Vietnamese sentence splitting — ĐẶC BIỆT cho legal docs.
        
        QUAN TRỌNG: Không split tại dấu chấm trong legal codes!
        "Nghị định số 01/2024/NĐ-CP ngày 01.01.2024" phải giữ nguyên.
        """
        import re
        
        # Protect legal codes và dates trước khi split
        protected = {}
        counter = 0
        
        # Pattern cho legal codes: XX/YYYY/XX-XX
        for match in re.finditer(r'\d+/\d{4}/[A-ZĐ\-]+', text):
            key = f"__PROTECTED_{counter}__"
            protected[key] = match.group()
            text = text.replace(match.group(), key, 1)
            counter += 1
        
        # Pattern cho dates: dd.mm.yyyy hoặc dd/mm/yyyy
        for match in re.finditer(r'\d{1,2}[./]\d{1,2}[./]\d{4}', text):
            key = f"__PROTECTED_{counter}__"
            protected[key] = match.group()
            text = text.replace(match.group(), key, 1)
            counter += 1
        
        # Split sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Restore protected patterns
        restored = []
        for sent in sentences:
            for key, value in protected.items():
                sent = sent.replace(key, value)
            if sent.strip():
                restored.append(sent.strip())
        
        return restored
    
    def _enforce_length_constraints(self, chunks: List[str]) -> List[str]:
        """Merge chunks ngắn, split chunks dài."""
        result = []
        buffer = ""
        
        for chunk in chunks:
            buffer = f"{buffer} {chunk}".strip() if buffer else chunk
            
            if len(buffer) >= self.min_chunk_length:
                if len(buffer) > self.max_chunk_length:
                    # Split chunk dài tại sentence boundary
                    parts = self._split_long_chunk(buffer)
                    result.extend(parts)
                else:
                    result.append(buffer)
                buffer = ""
        
        if buffer:
            if result:
                result[-1] = f"{result[-1]} {buffer}"
            else:
                result.append(buffer)
        
        return result
    
    def _split_long_chunk(self, text: str) -> List[str]:
        """Split chunk quá dài tại sentence boundary gần mid-point nhất."""
        sentences = self._split_sentences_vietnamese(text)
        mid = len(sentences) // 2
        return [
            " ".join(sentences[:mid]),
            " ".join(sentences[mid:])
        ]
```

### Kết hợp với Legal Structure Chunking

```python
class HybridLegalChunker:
    """
    Ưu tiên cấu trúc pháp lý (Điều/Khoản/Điểm), 
    fallback sang semantic chunking cho phần text tự do.
    
    Hierarchy: 
    1. Nếu detect được Điều/Khoản → chunk theo structure
    2. Nếu không → dùng semantic chunking
    """
    
    def __init__(self, semantic_chunker: SemanticChunker):
        self.semantic_chunker = semantic_chunker
        self.legal_pattern = re.compile(
            r'(Điều\s+\d+|Khoản\s+\d+|Mục\s+[IVXLC]+|Chương\s+[IVXLC]+)'
        )
    
    async def chunk(self, text: str, doc_type: str = "legal") -> List[dict]:
        if doc_type == "legal" and self.legal_pattern.search(text):
            # Structure-based chunking
            return self._chunk_by_legal_structure(text)
        else:
            # Semantic chunking (fallback)
            chunks = await self.semantic_chunker.chunk(text)
            return [{"content": c, "chunk_type": "semantic"} for c in chunks]
```

### Ước tính impact
- **Quality:** Chunks coherent hơn → retrieval chính xác hơn (+10-15%)
- **Effort:** 1 tuần (cần test kỹ với Vietnamese legal docs)
- **Risk:** Trung bình — cần re-embed toàn bộ nếu thay đổi chunking strategy

---

## 6. QUERY EXPANSION — Multi-Query Parallel Retrieval

### Haystack làm gì
Haystack 2.22 release `QueryExpander` — tạo nhiều biến thể semantic của query, chạy retrieval song song trên tất cả biến thể, rồi merge kết quả. Boost retrieval recall đáng kể.

### So với implementation hiện tại
ATTECH đã có Query Expansion (session 4 Jan 2026), nhưng đang chạy sequential. Pattern của Haystack chạy parallel + merge bằng RRF.

### Cách cải thiện

```python
# src/core/search/parallel_query_expander.py

class ParallelQueryExpander:
    """
    Pattern từ Haystack QueryExpander — chạy parallel retrieval
    trên nhiều query variations.
    """
    
    async def expand_and_search(
        self,
        original_query: str,
        search_func,  # async search function
        n_expansions: int = 3,
        top_k_per_query: int = 10,
        final_top_k: int = 10
    ) -> List[dict]:
        # Step 1: Generate expansions
        expansions = await self._generate_expansions(original_query, n_expansions)
        
        all_queries = [original_query] + expansions
        
        # Step 2: Parallel retrieval
        tasks = [search_func(q, top_k=top_k_per_query) for q in all_queries]
        all_results = await asyncio.gather(*tasks)
        
        # Step 3: RRF merge tất cả kết quả
        result_dict = {
            f"query_{i}": results 
            for i, results in enumerate(all_results)
        }
        
        rrf = ReciprocalRankFusion(k=60)
        merged = rrf.fuse(result_dict, top_k=final_top_k)
        
        return merged
    
    async def _generate_expansions(
        self, 
        query: str, 
        n: int
    ) -> List[str]:
        """
        Tạo query variations cho Vietnamese legal context.
        
        Ví dụ: "quy định về thuế thu nhập cá nhân"
        → "luật thuế TNCN"
        → "nghĩa vụ nộp thuế cá nhân"  
        → "thuế suất thu nhập người lao động"
        """
        # Dùng LLM nhẹ (Qwen 0.6B hoặc free model từ OpenRouter) 
        # để generate expansions
        prompt = f"""Tạo {n} cách diễn đạt khác của câu hỏi sau, 
        giữ nguyên ý nghĩa nhưng dùng từ ngữ khác.
        Đặc biệt bao gồm: tên viết tắt, thuật ngữ pháp lý tương đương.
        
        Câu hỏi gốc: {query}
        
        Các biến thể:"""
        
        response = await self.llm.generate(prompt)
        return self._parse_expansions(response, n)
```

### Ước tính impact
- **Recall:** +15-25% (tìm được documents mà single query bỏ lỡ)
- **Latency:** +500ms-1s (parallel nên không x3 thời gian)
- **Effort:** 2-3 ngày (đã có base từ Jan 2026)

---

## 7. EVALUATION-IN-PIPELINE — Đo quality liên tục

### Haystack làm gì
Thay vì chạy evaluation riêng biệt (batch offline), Haystack cho phép gắn evaluation nodes NGAY TRONG pipeline. Mỗi query production đều có thể được đo faithfulness, relevancy tự động.

### Cách implement

```python
# src/core/evaluation/inline_evaluator.py

class InlineRAGEvaluator:
    """
    Evaluation-in-pipeline pattern từ Haystack.
    
    Chạy lightweight evaluation trên mỗi query production,
    log metrics cho monitoring mà KHÔNG ảnh hưởng latency nhiều.
    """
    
    def __init__(self, sample_rate: float = 0.1):
        """sample_rate: % queries được evaluate (0.1 = 10%)"""
        self.sample_rate = sample_rate
    
    async def evaluate_and_log(
        self,
        query: str,
        retrieved_docs: List[dict],
        generated_answer: str,
        skip_if_slow: bool = True
    ) -> dict:
        """
        Chạy sau generation, async, không block response.
        """
        import random
        if random.random() > self.sample_rate:
            return {}  # Skip evaluation cho query này
        
        metrics = {}
        
        # 1. Context Relevancy (nhanh, không cần LLM)
        metrics['context_relevancy'] = self._context_relevancy(
            query, retrieved_docs
        )
        
        # 2. Answer Groundedness (nhanh, token overlap)
        metrics['groundedness'] = self._groundedness(
            generated_answer, retrieved_docs
        )
        
        # 3. Source Diversity 
        metrics['source_diversity'] = self._source_diversity(retrieved_docs)
        
        # 4. Citation Accuracy (check nếu legal codes trong answer match docs)
        metrics['citation_accuracy'] = self._citation_accuracy(
            generated_answer, retrieved_docs
        )
        
        # Log to PostgreSQL analytics table
        await self._log_metrics(query, metrics)
        
        # Alert nếu metrics dưới threshold
        if metrics['groundedness'] < 0.5:
            await self._alert_low_quality(query, metrics)
        
        return metrics
    
    def _groundedness(self, answer: str, docs: List[dict]) -> float:
        """
        Kiểm tra % tokens trong answer có xuất hiện trong retrieved docs.
        Lightweight proxy cho faithfulness.
        """
        answer_tokens = set(answer.lower().split())
        doc_tokens = set()
        for doc in docs:
            doc_tokens.update(doc['content'].lower().split())
        
        if not answer_tokens:
            return 0.0
        
        grounded = answer_tokens & doc_tokens
        return len(grounded) / len(answer_tokens)
    
    def _context_relevancy(self, query: str, docs: List[dict]) -> float:
        """Average relevance score của retrieved docs."""
        if not docs:
            return 0.0
        scores = [
            doc.get('rerank_score', doc.get('rrf_score', 0))
            for doc in docs
        ]
        return sum(scores) / len(scores)
    
    def _source_diversity(self, docs: List[dict]) -> float:
        """Tỷ lệ unique documents trong kết quả."""
        if not docs:
            return 0.0
        unique_docs = set(doc.get('document_id', '') for doc in docs)
        return len(unique_docs) / len(docs)
    
    def _citation_accuracy(self, answer: str, docs: List[dict]) -> float:
        """
        Kiểm tra legal codes trong answer có match với docs hay không.
        ĐẶC BIỆT QUAN TRỌNG cho Vietnamese legal RAG.
        """
        import re
        # Extract legal codes từ answer
        answer_codes = set(re.findall(r'\d+/\d{4}/[A-ZĐ\-]+', answer))
        
        if not answer_codes:
            return 1.0  # Không có code → không có lỗi
        
        # Extract legal codes từ docs
        doc_codes = set()
        for doc in docs:
            doc_codes.update(re.findall(
                r'\d+/\d{4}/[A-ZĐ\-]+', doc['content']
            ))
        
        # Codes trong answer phải có trong docs (anti-hallucination)
        if not answer_codes:
            return 1.0
        
        correct = answer_codes & doc_codes
        return len(correct) / len(answer_codes)
```

### Dashboard integration

```python
# Prometheus metrics
from prometheus_client import Histogram, Counter

rag_groundedness = Histogram(
    'rag_groundedness_score', 
    'Distribution of answer groundedness scores'
)
rag_citation_accuracy = Counter(
    'rag_citation_errors_total',
    'Total number of citation accuracy failures'
)

# Trong evaluate_and_log:
rag_groundedness.observe(metrics['groundedness'])
if metrics['citation_accuracy'] < 1.0:
    rag_citation_errors.inc()
```

### Ước tính impact
- **Observability:** Từ "mù" → real-time quality monitoring
- **Effort:** 3-5 ngày
- **Risk:** Thấp — async, không block main pipeline

---

## 8. PIPELINE BREAKPOINTS — Debug Mode cho RAG

### Haystack làm gì
Cho phép đặt breakpoint giữa pipeline components, inspect data flow giữa chừng, thử thay đổi input cho component tiếp theo mà không chạy lại toàn bộ pipeline.

### Cách implement

```python
# src/core/pipeline/debug_pipeline.py

class DebugPipeline:
    """
    Pipeline với breakpoint support — inspired by Haystack.
    
    Cho phép:
    1. Dừng sau bất kỳ step nào để inspect data
    2. Thử prompt khác mà không re-run retrieval
    3. So sánh output của 2 reranker models
    """
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.breakpoints: Dict[str, bool] = {}
        self.step_outputs: Dict[str, any] = {}
    
    def set_breakpoint(self, step_name: str):
        """Đặt breakpoint tại step."""
        self.breakpoints[step_name] = True
    
    async def run(self, query: str, resume_from: str = None, 
                  override_input: dict = None) -> dict:
        """
        Chạy pipeline với breakpoint support.
        
        Ví dụ debug flow:
        1. run("thuế TNCN") → dừng sau retrieval
        2. Inspect retrieved docs
        3. run("thuế TNCN", resume_from="reranker", override_input={...})
           → Chỉ chạy từ reranker trở đi, skip retrieval
        """
        steps = [
            ("query_expansion", self._expand_query),
            ("retrieval", self._retrieve),
            ("rrf_fusion", self._fuse),
            ("reranker", self._rerank),
            ("diversity", self._diversity_filter),
            ("reorder", self._lost_in_middle),
            ("generation", self._generate),
            ("evaluation", self._evaluate)
        ]
        
        # Resume from specific step
        start_idx = 0
        if resume_from:
            for i, (name, _) in enumerate(steps):
                if name == resume_from:
                    start_idx = i
                    break
        
        current_data = override_input or {"query": query}
        
        for i, (step_name, step_func) in enumerate(steps):
            if i < start_idx:
                continue
            
            # Execute step
            current_data = await step_func(current_data)
            self.step_outputs[step_name] = current_data
            
            # Log nếu debug mode
            if self.debug_mode:
                self._log_step(step_name, current_data)
            
            # Check breakpoint
            if step_name in self.breakpoints:
                return {
                    "status": "breakpoint",
                    "step": step_name,
                    "data": current_data,
                    "remaining_steps": [s[0] for s in steps[i+1:]]
                }
        
        return current_data
    
    def _log_step(self, step_name: str, data: dict):
        """Log step output cho debugging."""
        import json
        import logging
        logger = logging.getLogger("rag.debug")
        
        summary = {
            "step": step_name,
            "num_docs": len(data.get('documents', [])),
            "top_scores": [
                d.get('rerank_score', d.get('rrf_score', 'N/A'))
                for d in data.get('documents', [])[:3]
            ]
        }
        logger.debug(f"Pipeline step: {json.dumps(summary, ensure_ascii=False)}")
```

### API endpoint cho debug

```python
# Thêm vào FastAPI
@router.post("/api/v1/search/debug")
async def debug_search(
    query: str,
    breakpoint_at: str = None,
    resume_from: str = None,
    override_input: dict = None
):
    """
    Debug endpoint — chỉ admin access.
    Cho phép step-by-step debugging của RAG pipeline.
    """
    pipeline = DebugPipeline(debug_mode=True)
    if breakpoint_at:
        pipeline.set_breakpoint(breakpoint_at)
    
    result = await pipeline.run(
        query, 
        resume_from=resume_from,
        override_input=override_input
    )
    return result
```

### Ước tính impact
- **Debug speed:** Từ "chạy lại toàn bộ" → chỉ chạy lại phần cần test
- **Effort:** 2-3 ngày
- **Đặc biệt hữu ích:** Khi so sánh BGE vs Qwen3 reranker, thử prompts khác nhau

---

## 9. HIERARCHICAL DOCUMENT SPLITTER + AUTO-MERGING RETRIEVAL

### Haystack làm gì
Tạo hierarchical chunks với parent-child relationships. Khi retrieve được child chunk, tự động merge lại parent chunk để LLM có ngữ cảnh rộng hơn. Đã được promote từ experimental vào core.

### Áp dụng cho Vietnamese Legal Docs

```
Document (Nghị định 01/2024/NĐ-CP)
├── Chapter I (Chương I - Quy định chung)         ← Level 1 (parent)
│   ├── Article 1 (Điều 1 - Phạm vi điều chỉnh)  ← Level 2 (child)
│   │   ├── Clause 1 (Khoản 1)                    ← Level 3 (grandchild)
│   │   └── Clause 2 (Khoản 2)                    ← Level 3
│   └── Article 2 (Điều 2 - Đối tượng áp dụng)   ← Level 2
└── Chapter II (Chương II - Quy định cụ thể)      ← Level 1
```

### Cách implement

```python
# src/core/chunking/hierarchical_chunker.py

class HierarchicalChunk:
    """Chunk với parent-child relationship."""
    chunk_id: str
    content: str
    level: int          # 0=doc, 1=chapter, 2=article, 3=clause
    parent_id: str      # ID của parent chunk
    children_ids: List[str]
    metadata: dict

class AutoMergingRetriever:
    """
    Khi retrieve được Khoản 2 của Điều 5,
    tự động lấy thêm toàn bộ Điều 5 làm context.
    
    Lý do: LLM cần biết Khoản 1, 3 để hiểu đúng Khoản 2.
    """
    
    async def retrieve_with_context(
        self,
        query: str,
        base_results: List[dict],
        expand_to_level: int = 2,  # Mở rộng đến level Article (Điều)
        max_context_tokens: int = 2000
    ) -> List[dict]:
        expanded = []
        seen_parents = set()
        
        for result in base_results:
            current_level = result.get('metadata', {}).get('level', 3)
            parent_id = result.get('metadata', {}).get('parent_id')
            
            if current_level > expand_to_level and parent_id:
                # Lấy parent chunk (Điều chứa Khoản)
                if parent_id not in seen_parents:
                    parent = await self._fetch_parent(parent_id)
                    if parent:
                        parent['_is_expanded_context'] = True
                        expanded.append(parent)
                        seen_parents.add(parent_id)
            else:
                expanded.append(result)
        
        return expanded
```

### Ước tính impact
- **Context quality:** LLM nhận đủ ngữ cảnh pháp lý → trả lời chính xác hơn
- **Effort:** 1-2 tuần (cần restructure chunking + re-index)
- **Risk:** Cao — ảnh hưởng data pipeline, cần test kỹ

---

## 10. TỔNG HỢP PIPELINE HOÀN CHỈNH

### Pipeline hiện tại (ATTECH)

```
Query → Query Intent Detection → Multi-Engine Search (5 engines)
      → Weighted Score Combination → Deduplication → Generation
```

### Pipeline nâng cấp (sau khi áp dụng Haystack patterns)

```
Query 
  → [Query Expansion] (parallel, 3 variations)
  → [Multi-Engine Retrieval] (Semantic + BM25 + Substring, parallel)
  → [RRF Fusion] (thay weighted combination)              ← MỚI
  → [Cross-Encoder Reranker] (BGE-v2-m3 hoặc Qwen3)      ← MỚI (P0)
  → [Diversity Ranker] (MMR, loại near-duplicate)          ← MỚI
  → [Auto-Merge Context] (lấy parent chunks)              ← MỚI
  → [Lost-in-Middle Reorder] (tối ưu vị trí context)      ← MỚI
  → [Generation] (GPT-4 / cost-optimized LLM)
  → [Inline Evaluation] (async, 10% queries)               ← MỚI
```

### Ước tính tổng impact

| Pattern | Accuracy Impact | Effort | Priority |
|---------|----------------|--------|----------|
| Cross-Encoder Reranker | +15-30% | 1 tuần | P0 - CRITICAL |
| RRF Fusion | +5-10% | 1-2 ngày | P1 - HIGH |
| Diversity Ranker | +5% quality | 1-2 ngày | P1 - HIGH |
| Lost-in-Middle Reorder | +5% | 30 phút | P1 - Quick Win |
| Inline Evaluation | Observability | 3-5 ngày | P1 - HIGH |
| Parallel Query Expansion | +15-25% recall | 2-3 ngày | P2 - MEDIUM |
| Semantic Chunking | +10-15% | 1 tuần | P2 - MEDIUM |
| Pipeline Breakpoints | Debug speed | 2-3 ngày | P2 - MEDIUM |
| Hierarchical Auto-Merge | Context quality | 1-2 tuần | P3 - Future |

### Thứ tự triển khai đề xuất

**Tuần 1:** Cross-Encoder Reranker + Lost-in-Middle Reorder (biggest impact, quick win)

**Tuần 2:** RRF Fusion + Diversity Ranker (thay thế weighted combination)

**Tuần 3:** Inline Evaluation + Pipeline Breakpoints (observability)

**Tuần 4+:** Parallel Query Expansion, Semantic Chunking, Hierarchical Auto-Merge

---

## KẾT LUẬN

Haystack không phải là thứ cần migrate sang — mà là kho tàng patterns đã được validate bởi cộng đồng lớn (Apple, Meta, NVIDIA đều dùng). ATTECH RAG đã có foundation tốt hơn Haystack ở nhiều điểm (5 search engines vs 2, Vietnamese-first architecture, Graph RAG, citation verification). Việc cần làm là cherry-pick những pattern hay nhất và implement theo cách phù hợp với stack hiện tại.

**Mục tiêu:** Từ ~75% accuracy hiện tại → 85-90% sau khi áp dụng Reranker + RRF + Diversity, hướng tới >90% với full pipeline upgrade.
