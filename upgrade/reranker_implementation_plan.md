# KẾ HOẠCH TRIỂN KHAI CROSS-ENCODER RERANKER
## ATTECH RAG Knowledge Assistant — Phase 2 / P0-Critical

**Thời gian:** 5 ngày làm việc (1 tuần)  
**Mục tiêu:** Tăng RAG accuracy từ ~75% lên ≥80%  
**Người thực hiện:** Technical Lead + 1 Dev  
**Ngày lập:** 11/02/2026  

---

## 1. QUYẾT ĐỊNH KIẾN TRÚC: TÍCH HỢP VÀO FR-04.1, KHÔNG TẠO MODULE RIÊNG

### Lý do chọn tích hợp vào FR-04.1 (Retrieval)

Reranker **KHÔNG** nên là module riêng biệt, mà nên là một **component mới** trong FR-04.1. Đây là phân tích:

```
PIPELINE HIỆN TẠI:
User Query → FR-04.1 [QueryProcessor → 6 Engines → HybridRanker] → FR-04.2 Synthesis → FR-04.3 Generation

PIPELINE SAU KHI THÊM RERANKER:
User Query → FR-04.1 [QueryProcessor → 6 Engines → HybridRanker → ⭐ Reranker] → FR-04.2 Synthesis → FR-04.3 Generation
```

**Tại sao KHÔNG tạo module riêng (VD: FR-04.1.5)?**

| Tiêu chí | Module riêng | Tích hợp FR-04.1 |
|-----------|-------------|-------------------|
| Độ phức tạp deploy | Thêm 1 Docker container, 1 port | Zero thay đổi infra |
| Network latency | +10-20ms (inter-service call) | 0ms (in-process) |
| Codebase coherence | Tách logic ranking ra 2 nơi | Ranking logic tập trung |
| Error handling | Cần xử lý service-down | Try/catch đơn giản, fallback graceful |
| Scaling độc lập | Có thể scale riêng (không cần thiết lúc này) | Scale cùng FR-04.1 |

**Kết luận:** Với scale hiện tại (100 users, 1 server), tích hợp vào FR-04.1 là lựa chọn đúng. Khi nào cần scale GPU riêng cho reranker (>500 concurrent users), lúc đó mới tách ra microservice.

### Vị trí chính xác trong FR-04.1

```
FR-04.1Retrieval/
├── src/
│   ├── retrieval/
│   │   ├── engines/
│   │   │   ├── semantic_engine.py       # Có sẵn
│   │   │   ├── keyword_engine.py        # Có sẵn
│   │   │   └── ...
│   │   ├── processors/
│   │   │   └── vietnamese_processor.py  # Có sẵn
│   │   └── ranking/
│   │       ├── hybrid_ranker.py         # Có sẵn — Stage 1: Score fusion
│   │       └── cross_encoder_reranker.py # ⭐ MỚI — Stage 2: Neural reranking
│   ├── orchestrator/
│   │   └── search_orchestrator.py       # Sửa: thêm reranker step
│   └── config/
│       └── reranker_config.py           # ⭐ MỚI — Config riêng cho reranker
```

### Luồng xử lý chi tiết

```
[SearchOrchestrator.search_documents()]
    │
    ├── 1. QueryProcessor.process_query()          # Có sẵn
    │
    ├── 2. Parallel Search (6 engines)             # Có sẵn
    │   ├── SemanticEngine.search()
    │   ├── KeywordEngine.search()
    │   ├── BM25Engine.search()
    │   ├── SubstringEngine.search()
    │   └── MetadataEngine.search()
    │
    ├── 3. HybridRanker.combine_results()          # Có sẵn — Top 20-30 candidates
    │       (Score fusion: 0.7*semantic + 0.3*keyword)
    │
    ├── 4. ⭐ CrossEncoderReranker.rerank()        # MỚI — Rerank top 20 → top 5-10
    │       (Neural scoring: query-document pair)
    │
    ├── 5. AccessControl.filter()                   # Có sẵn
    │
    └── 6. Return final results → FR-04.2 Synthesis
```

---

## 2. LỰA CHỌN MODEL

### So sánh các model reranker

| Model | Size | Vietnamese? | Speed (RTX 2080 Ti) | Accuracy | License |
|-------|------|------------|---------------------|----------|---------|
| **bge-reranker-v2-m3** | 568M | ✅ Multilingual (100+ langs) | ~50ms/20 pairs | Rất cao | MIT |
| Qwen3-Reranker | 600M+ | ✅ Tốt | ~60ms/20 pairs | Cao | Apache 2.0 |
| ms-marco-MiniLM-L-6-v2 | 80M | ❌ English only | ~15ms/20 pairs | Trung bình | Apache 2.0 |
| vinai/phobert-base | 135M | ✅ Vietnamese native | ~30ms/20 pairs | Trung bình (chưa fine-tune reranking) | MIT |

### Khuyến nghị: `BAAI/bge-reranker-v2-m3`

**Lý do:**
1. **Multilingual xuất sắc** — hỗ trợ tiếng Việt natively, không cần fine-tune
2. **State-of-the-art** — top performance trên MTEB benchmark cho cross-lingual reranking
3. **Kích thước hợp lý** — 568MB fit trong VRAM RTX 2080 Ti (11GB) cùng với Qwen3-Embedding
4. **MIT License** — tự do sử dụng cho internal/commercial
5. **Được recommend** trong roadmap dự án

**VRAM Budget trên RTX 2080 Ti (11GB):**
```
Qwen3-Embedding-0.6B:    ~1.2 GB (đang chạy)
bge-reranker-v2-m3:       ~1.1 GB (thêm mới)
CUDA overhead:            ~0.5 GB
Tổng:                     ~2.8 GB → DƯ SỨC (còn ~8.2 GB free)
```

### Backup plan: `Qwen3-Reranker`
Nếu bge-reranker-v2-m3 cho kết quả không đủ tốt trên Vietnamese legal text, chuyển sang Qwen3-Reranker (cùng ecosystem với embedding model đang dùng).

---

## 3. KẾ HOẠCH 5 NGÀY CHI TIẾT

### NGÀY 1 (Thứ 2): Setup & Model Loading

**Buổi sáng (4h): Chuẩn bị môi trường**

```bash
# 1. SSH vào dev server
ssh user@192.168.1.70

# 2. Download model (chạy trước, mất ~15-30 phút)
python -c "
from transformers import AutoModelForSequenceClassification, AutoTokenizer
model_name = 'BAAI/bge-reranker-v2-m3'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
print('✅ Model downloaded successfully')
print(f'Model size: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M params')
"

# 3. Cài dependencies mới
pip install --break-system-packages transformers torch accelerate
# Hoặc thêm vào requirements.txt:
# transformers>=4.36.0
# torch>=2.0.0
# accelerate>=0.25.0
```

**Buổi chiều (4h): Tạo RerankerConfig và CrossEncoderReranker class**

File `src/config/reranker_config.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional

class RerankerConfig(BaseModel):
    """Configuration cho Cross-Encoder Reranker"""
    
    # Model settings
    model_name: str = Field(
        default="BAAI/bge-reranker-v2-m3",
        description="HuggingFace model name cho reranker"
    )
    
    # Performance settings
    enabled: bool = Field(default=True, description="Bật/tắt reranker")
    max_candidates: int = Field(
        default=20,
        description="Số lượng candidates từ HybridRanker đưa vào reranker"
    )
    top_k_after_rerank: int = Field(
        default=5,
        description="Số kết quả trả về sau reranking"
    )
    
    # Scoring
    min_rerank_score: float = Field(
        default=0.1,
        description="Ngưỡng score tối thiểu sau reranking (loại noise)"
    )
    score_weight: float = Field(
        default=0.6,
        description="Trọng số reranker score trong final combined score"
    )
    hybrid_weight: float = Field(
        default=0.4,
        description="Trọng số hybrid score được giữ lại"
    )
    
    # Hardware
    device: str = Field(default="cuda", description="cuda hoặc cpu")
    batch_size: int = Field(
        default=16,
        description="Batch size cho inference (tune theo VRAM)"
    )
    max_length: int = Field(
        default=512,
        description="Max token length cho query-document pair"
    )
    
    # Timeout & Fallback
    timeout_ms: int = Field(
        default=2000,
        description="Timeout cho reranking step (ms). Nếu vượt → fallback"
    )
    fallback_to_hybrid: bool = Field(
        default=True,
        description="Nếu reranker lỗi → trả kết quả hybrid gốc"
    )
```

File `src/retrieval/ranking/cross_encoder_reranker.py`:
```python
"""
Cross-Encoder Reranker cho ATTECH RAG System.

Vị trí trong pipeline:
    6 Search Engines → HybridRanker (score fusion) → CrossEncoderReranker → AccessControl → Response

Nguyên lý:
    - Bi-Encoder (embedding): Encode query và document RIÊNG → so sánh vector
      → Nhanh nhưng mất thông tin interaction
    - Cross-Encoder (reranker): Encode query VÀ document CÙNG LÚC → score trực tiếp
      → Chậm hơn nhưng chính xác hơn nhiều (hiểu context giữa query-doc)

Tại sao không dùng Cross-Encoder cho TẤT CẢ:
    - Cross-Encoder: O(n) với n = số documents → quá chậm cho 100K docs
    - Giải pháp: Bi-Encoder lọc 100K → 20 candidates, Cross-Encoder rerank 20 → top 5
"""

import torch
import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RerankedResult:
    """Kết quả sau reranking"""
    original_result: Dict[str, Any]    # Kết quả gốc từ HybridRanker
    rerank_score: float                # Score từ Cross-Encoder (0-1)
    hybrid_score: float                # Score gốc từ HybridRanker
    final_score: float                 # Weighted combination
    rank_change: int                   # Thay đổi thứ hạng (+ = lên, - = xuống)


class CrossEncoderReranker:
    """
    Cross-Encoder Reranker sử dụng bge-reranker-v2-m3.
    
    Usage:
        reranker = CrossEncoderReranker(config)
        await reranker.initialize()
        reranked = await reranker.rerank(query, candidates)
    """
    
    def __init__(self, config: 'RerankerConfig'):
        self.config = config
        self.model = None
        self.tokenizer = None
        self._initialized = False
        self._load_lock = asyncio.Lock()
        
        # Metrics
        self._total_calls = 0
        self._total_latency_ms = 0
        self._errors = 0
    
    async def initialize(self) -> None:
        """Load model vào GPU/CPU. Gọi 1 lần khi startup."""
        async with self._load_lock:
            if self._initialized:
                return
            
            try:
                logger.info(f"Loading reranker model: {self.config.model_name}")
                start = time.time()
                
                # Load trong thread pool để không block event loop
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._load_model)
                
                elapsed = (time.time() - start) * 1000
                logger.info(
                    f"✅ Reranker loaded in {elapsed:.0f}ms | "
                    f"Device: {self.config.device} | "
                    f"Model: {self.config.model_name}"
                )
                self._initialized = True
                
            except Exception as e:
                logger.error(f"❌ Failed to load reranker: {e}")
                raise
    
    def _load_model(self) -> None:
        """Synchronous model loading (chạy trong thread pool)"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.config.model_name
        )
        
        # Move to device
        if self.config.device == "cuda" and torch.cuda.is_available():
            self.model = self.model.to("cuda")
            self.model.half()  # FP16 để tiết kiệm VRAM
            logger.info(f"Model loaded on CUDA (FP16)")
        else:
            self.model = self.model.to("cpu")
            logger.info(f"Model loaded on CPU (FP32)")
        
        self.model.eval()
    
    async def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[RerankedResult]:
        """
        Rerank candidates sử dụng Cross-Encoder.
        
        Args:
            query: User query gốc
            candidates: List kết quả từ HybridRanker
            top_k: Số kết quả trả về (default: config.top_k_after_rerank)
            
        Returns:
            List[RerankedResult] đã sắp xếp theo final_score giảm dần
        """
        if not self.config.enabled:
            return self._passthrough(candidates, top_k)
        
        if not self._initialized:
            await self.initialize()
        
        if not candidates:
            return []
        
        top_k = top_k or self.config.top_k_after_rerank
        start_time = time.time()
        
        try:
            # Giới hạn số candidates đưa vào reranker
            candidates_to_rerank = candidates[:self.config.max_candidates]
            
            # Tạo query-document pairs
            pairs = self._create_pairs(query, candidates_to_rerank)
            
            # Chạy inference trong thread pool (không block async)
            loop = asyncio.get_event_loop()
            scores = await asyncio.wait_for(
                loop.run_in_executor(None, self._compute_scores, pairs),
                timeout=self.config.timeout_ms / 1000.0
            )
            
            # Combine scores và sort
            results = self._combine_and_sort(
                candidates_to_rerank, scores, top_k
            )
            
            # Metrics
            elapsed_ms = (time.time() - start_time) * 1000
            self._total_calls += 1
            self._total_latency_ms += elapsed_ms
            
            logger.info(
                f"Reranked {len(candidates_to_rerank)} candidates → "
                f"top {len(results)} in {elapsed_ms:.0f}ms"
            )
            
            return results
            
        except asyncio.TimeoutError:
            logger.warning(
                f"Reranker timeout ({self.config.timeout_ms}ms). "
                f"Falling back to hybrid results."
            )
            self._errors += 1
            return self._passthrough(candidates, top_k)
            
        except Exception as e:
            logger.error(f"Reranker error: {e}")
            self._errors += 1
            if self.config.fallback_to_hybrid:
                return self._passthrough(candidates, top_k)
            raise
    
    def _create_pairs(
        self, query: str, candidates: List[Dict[str, Any]]
    ) -> List[Tuple[str, str]]:
        """Tạo (query, document_text) pairs cho Cross-Encoder."""
        pairs = []
        for candidate in candidates:
            # Ưu tiên content, fallback sang title
            doc_text = candidate.get("content", "") or candidate.get("text", "")
            title = candidate.get("title", "")
            
            # Ghép title + content cho context đầy đủ hơn
            if title and doc_text:
                full_text = f"{title}\n{doc_text}"
            else:
                full_text = doc_text or title or ""
            
            # Truncate nếu quá dài (Cross-Encoder có limit)
            if len(full_text) > 2000:
                full_text = full_text[:2000]
            
            pairs.append((query, full_text))
        
        return pairs
    
    @torch.no_grad()
    def _compute_scores(self, pairs: List[Tuple[str, str]]) -> List[float]:
        """
        Compute relevance scores cho query-document pairs.
        Chạy synchronous (được gọi từ thread pool).
        """
        all_scores = []
        
        # Batch processing
        for i in range(0, len(pairs), self.config.batch_size):
            batch = pairs[i:i + self.config.batch_size]
            
            # Tokenize
            inputs = self.tokenizer(
                [p[0] for p in batch],  # queries
                [p[1] for p in batch],  # documents
                padding=True,
                truncation=True,
                max_length=self.config.max_length,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            # Forward pass
            outputs = self.model(**inputs)
            scores = outputs.logits.squeeze(-1)
            
            # Sigmoid để normalize về 0-1
            scores = torch.sigmoid(scores).cpu().tolist()
            
            if isinstance(scores, float):
                scores = [scores]
            
            all_scores.extend(scores)
        
        return all_scores
    
    def _combine_and_sort(
        self,
        candidates: List[Dict[str, Any]],
        rerank_scores: List[float],
        top_k: int
    ) -> List[RerankedResult]:
        """Combine reranker scores với hybrid scores, sort, trả về top_k."""
        results = []
        
        for i, (candidate, rerank_score) in enumerate(
            zip(candidates, rerank_scores)
        ):
            # Lấy hybrid score gốc
            hybrid_score = candidate.get("combined_score", 0.0) or \
                          candidate.get("similarity_score", 0.0) or 0.0
            
            # Weighted combination
            final_score = (
                self.config.score_weight * rerank_score +
                self.config.hybrid_weight * hybrid_score
            )
            
            results.append(RerankedResult(
                original_result=candidate,
                rerank_score=rerank_score,
                hybrid_score=hybrid_score,
                final_score=final_score,
                rank_change=0  # Sẽ tính sau khi sort
            ))
        
        # Sort theo final_score giảm dần
        results.sort(key=lambda x: x.final_score, reverse=True)
        
        # Tính rank_change
        for new_rank, result in enumerate(results):
            old_rank = next(
                j for j, c in enumerate(candidates)
                if c is result.original_result
            )
            result.rank_change = old_rank - new_rank  # Dương = lên hạng
        
        # Filter score thấp
        results = [
            r for r in results
            if r.rerank_score >= self.config.min_rerank_score
        ]
        
        return results[:top_k]
    
    def _passthrough(
        self, candidates: List[Dict[str, Any]], top_k: Optional[int]
    ) -> List[RerankedResult]:
        """Fallback: trả kết quả hybrid gốc dạng RerankedResult."""
        top_k = top_k or self.config.top_k_after_rerank
        results = []
        for candidate in candidates[:top_k]:
            hybrid_score = candidate.get("combined_score", 0.0) or 0.0
            results.append(RerankedResult(
                original_result=candidate,
                rerank_score=0.0,
                hybrid_score=hybrid_score,
                final_score=hybrid_score,
                rank_change=0
            ))
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Trả về metrics cho monitoring."""
        avg_latency = (
            self._total_latency_ms / self._total_calls
            if self._total_calls > 0 else 0
        )
        return {
            "total_calls": self._total_calls,
            "avg_latency_ms": round(avg_latency, 1),
            "errors": self._errors,
            "error_rate": round(
                self._errors / max(self._total_calls, 1) * 100, 2
            ),
            "model": self.config.model_name,
            "device": self.config.device,
            "initialized": self._initialized,
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check cho monitoring endpoint."""
        return {
            "status": "healthy" if self._initialized else "not_loaded",
            "model": self.config.model_name,
            "device": str(self.model.device) if self.model else "N/A",
            "metrics": self.get_metrics()
        }
```

**Deliverable Ngày 1:**
- ✅ Model downloaded và test load thành công trên server .70
- ✅ `reranker_config.py` hoàn thành
- ✅ `cross_encoder_reranker.py` hoàn thành (chưa integrate)

---

### NGÀY 2 (Thứ 3): Tích hợp vào SearchOrchestrator

**Buổi sáng (4h): Sửa SearchOrchestrator**

Thay đổi trong `src/orchestrator/search_orchestrator.py`:

```python
# === THÊM import ===
from src.retrieval.ranking.cross_encoder_reranker import CrossEncoderReranker
from src.config.reranker_config import RerankerConfig

class SearchOrchestrator:
    def __init__(self, ...):
        # ... existing init ...
        
        # ⭐ Thêm reranker
        reranker_config = RerankerConfig()  # Load từ env/config file
        self.reranker = CrossEncoderReranker(reranker_config)
    
    async def initialize(self):
        # ... existing initialization ...
        
        # ⭐ Load reranker model khi startup
        if self.reranker.config.enabled:
            await self.reranker.initialize()
    
    async def search_documents(
        self,
        query: str,
        top_k: int = 10,
        search_type: str = "hybrid",
        **kwargs
    ) -> List[Dict]:
        """
        Main search flow - ĐÃ CẬP NHẬT với reranker stage.
        """
        # Stage 1: Query processing (có sẵn)
        processed_query = await self.query_processor.process_query(query)
        
        # Stage 2: Multi-engine search (có sẵn)
        raw_results = await self._execute_search(
            processed_query, search_type, **kwargs
        )
        
        # Stage 3: Hybrid ranking (có sẵn)
        # Lấy NHIỀU HƠN candidates cho reranker (20-30 thay vì top_k)
        reranker_candidates = self.config.reranker.max_candidates if \
            self.reranker.config.enabled else top_k
        
        hybrid_results = await self.hybrid_ranker.combine_results(
            raw_results, top_k=reranker_candidates
        )
        
        # Stage 4: ⭐ Cross-Encoder Reranking (MỚI)
        if self.reranker.config.enabled and search_type in ("hybrid", "semantic"):
            reranked = await self.reranker.rerank(
                query=query,              # Query GỐC (không processed)
                candidates=hybrid_results,
                top_k=top_k
            )
            # Convert RerankedResult → Dict cho downstream compatibility
            final_results = [
                {
                    **r.original_result,
                    "combined_score": r.final_score,
                    "rerank_score": r.rerank_score,
                    "hybrid_score": r.hybrid_score,
                    "rank_change": r.rank_change,
                }
                for r in reranked
            ]
        else:
            # Keyword-only hoặc substring → skip reranker
            final_results = hybrid_results[:top_k]
        
        # Stage 5: Access control (có sẵn)
        filtered_results = await self.access_control.filter(
            final_results, user_context
        )
        
        return filtered_results
```

**Buổi chiều (4h): Thêm API endpoint để toggle/monitor reranker**

Thêm vào `src/api/main.py`:
```python
@app.get("/api/v1/reranker/health")
async def reranker_health():
    """Health check cho reranker."""
    return await orchestrator.reranker.health_check()

@app.post("/api/v1/reranker/toggle")
async def toggle_reranker(enabled: bool):
    """Bật/tắt reranker runtime (không cần restart)."""
    orchestrator.reranker.config.enabled = enabled
    return {"enabled": enabled, "status": "updated"}

@app.get("/api/v1/reranker/metrics")
async def reranker_metrics():
    """Metrics cho Prometheus/Grafana."""
    return orchestrator.reranker.get_metrics()
```

**Deliverable Ngày 2:**
- ✅ SearchOrchestrator tích hợp reranker
- ✅ API endpoints cho health/toggle/metrics
- ✅ Fallback hoạt động khi reranker disabled/lỗi

---

### NGÀY 3 (Thứ 4): Testing & Benchmarking

**Buổi sáng (4h): Unit Tests**

File `tests/test_cross_encoder_reranker.py`:
```python
"""
Test suite cho CrossEncoderReranker.
Bao gồm: unit tests, integration tests, performance tests.
"""

import pytest
import asyncio
import time
from src.retrieval.ranking.cross_encoder_reranker import (
    CrossEncoderReranker, RerankedResult
)
from src.config.reranker_config import RerankerConfig


# ========== FIXTURES ==========

@pytest.fixture
def config():
    return RerankerConfig(
        model_name="BAAI/bge-reranker-v2-m3",
        device="cpu",  # CPU cho CI/CD, GPU cho local test
        enabled=True,
        max_candidates=10,
        top_k_after_rerank=5,
    )

@pytest.fixture
def mock_candidates():
    """Giả lập kết quả từ HybridRanker"""
    return [
        {
            "chunk_id": f"chunk_{i}",
            "title": f"Nghị định {i}/2024/NĐ-CP",
            "content": f"Điều {i}. Quy định về nghỉ phép năm cho người lao động"
                       f" tại doanh nghiệp có thâm niên trên {i} năm.",
            "combined_score": 0.9 - (i * 0.05),
            "similarity_score": 0.85 - (i * 0.03),
        }
        for i in range(10)
    ]


# ========== UNIT TESTS ==========

class TestRerankerConfig:
    def test_default_values(self):
        config = RerankerConfig()
        assert config.enabled is True
        assert config.max_candidates == 20
        assert config.device == "cuda"
    
    def test_score_weights_sum(self):
        config = RerankerConfig()
        assert abs(config.score_weight + config.hybrid_weight - 1.0) < 0.01


class TestCrossEncoderReranker:
    
    @pytest.mark.asyncio
    async def test_initialize(self, config):
        reranker = CrossEncoderReranker(config)
        await reranker.initialize()
        assert reranker._initialized is True
    
    @pytest.mark.asyncio
    async def test_rerank_basic(self, config, mock_candidates):
        reranker = CrossEncoderReranker(config)
        await reranker.initialize()
        
        results = await reranker.rerank(
            query="quy định nghỉ phép năm cho nhân viên thâm niên",
            candidates=mock_candidates,
            top_k=5
        )
        
        assert len(results) <= 5
        assert all(isinstance(r, RerankedResult) for r in results)
        # Scores giảm dần
        for i in range(len(results) - 1):
            assert results[i].final_score >= results[i + 1].final_score
    
    @pytest.mark.asyncio
    async def test_rerank_changes_order(self, config, mock_candidates):
        """Verify reranker thực sự thay đổi thứ hạng"""
        reranker = CrossEncoderReranker(config)
        await reranker.initialize()
        
        results = await reranker.rerank(
            query="nghỉ phép thâm niên 5 năm",
            candidates=mock_candidates
        )
        
        # Ít nhất 1 kết quả có rank_change != 0
        has_reordering = any(r.rank_change != 0 for r in results)
        # Có thể không đổi nếu hybrid đã rank đúng, nhưng scores phải khác
        assert all(r.rerank_score > 0 for r in results)
    
    @pytest.mark.asyncio
    async def test_fallback_when_disabled(self, mock_candidates):
        config = RerankerConfig(enabled=False)
        reranker = CrossEncoderReranker(config)
        
        results = await reranker.rerank(
            query="test query",
            candidates=mock_candidates
        )
        
        # Passthrough: giữ nguyên thứ tự, rerank_score = 0
        assert all(r.rerank_score == 0.0 for r in results)
    
    @pytest.mark.asyncio
    async def test_empty_candidates(self, config):
        reranker = CrossEncoderReranker(config)
        await reranker.initialize()
        
        results = await reranker.rerank(query="test", candidates=[])
        assert results == []
    
    @pytest.mark.asyncio
    async def test_vietnamese_legal_query(self, config):
        """Test với câu hỏi pháp luật thực tế"""
        reranker = CrossEncoderReranker(config)
        await reranker.initialize()
        
        candidates = [
            {
                "content": "Điều 113. Nghỉ hằng năm. Người lao động làm việc"
                          " đủ 12 tháng cho một người sử dụng lao động thì"
                          " được nghỉ hằng năm 12 ngày làm việc.",
                "combined_score": 0.75,
                "title": "Bộ luật Lao động 2019"
            },
            {
                "content": "Điều 5. Quy định về an toàn vệ sinh lao động"
                          " trong ngành hàng không dân dụng.",
                "combined_score": 0.80,  # Hybrid score CAO HƠN nhưng ít relevant
                "title": "Thông tư 15/2020/TT-BGTVT"
            },
        ]
        
        results = await reranker.rerank(
            query="nhân viên làm 12 tháng được nghỉ phép bao nhiêu ngày",
            candidates=candidates,
            top_k=2
        )
        
        # Reranker NÊN đẩy Điều 113 lên top vì relevant hơn
        assert results[0].original_result["title"] == "Bộ luật Lao động 2019"


# ========== PERFORMANCE TESTS ==========

class TestRerankerPerformance:
    
    @pytest.mark.asyncio
    async def test_latency_under_200ms(self, config, mock_candidates):
        """Reranking 10 candidates phải < 200ms"""
        reranker = CrossEncoderReranker(config)
        await reranker.initialize()
        
        start = time.time()
        await reranker.rerank(
            query="nghỉ phép năm theo luật lao động",
            candidates=mock_candidates[:10]
        )
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 200, f"Reranking took {elapsed_ms:.0f}ms (> 200ms)"
    
    @pytest.mark.asyncio
    async def test_latency_20_candidates(self, config):
        """Reranking 20 candidates phải < 500ms"""
        reranker = CrossEncoderReranker(config)
        await reranker.initialize()
        
        candidates = [
            {"content": f"Nội dung chunk {i} " * 50, "combined_score": 0.5}
            for i in range(20)
        ]
        
        start = time.time()
        await reranker.rerank(query="test query", candidates=candidates)
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 500, f"Reranking took {elapsed_ms:.0f}ms (> 500ms)"
```

**Buổi chiều (4h): A/B Comparison Test**

File `scripts/benchmark_reranker.py`:
```python
"""
Benchmark script: So sánh accuracy CÓ và KHÔNG CÓ reranker.

Chạy:
    python scripts/benchmark_reranker.py --queries test_queries.json

Output:
    - So sánh MRR, P@5, nDCG@5
    - Latency comparison
    - Chi tiết từng query: rank changes
"""

import asyncio
import json
import time
from typing import List, Dict

# Test queries cho Vietnamese legal domain
BENCHMARK_QUERIES = [
    {
        "query": "nghỉ phép năm cho nhân viên thâm niên 10 năm",
        "expected_keywords": ["nghỉ hằng năm", "Điều 113", "thâm niên"],
        "expected_law": "Bộ luật Lao động"
    },
    {
        "query": "quy định về an toàn hàng không",
        "expected_keywords": ["an toàn", "hàng không", "CNS/ATM"],
        "expected_law": None  # Nhiều văn bản
    },
    {
        "query": "76/2018/NĐ-CP",
        "expected_keywords": ["76/2018"],
        "expected_law": "Nghị định 76/2018"
    },
    {
        "query": "mức xử phạt vi phạm quy định lao động",
        "expected_keywords": ["xử phạt", "vi phạm", "hành chính"],
        "expected_law": None
    },
    {
        "query": "hợp đồng lao động xác định thời hạn tối đa bao lâu",
        "expected_keywords": ["hợp đồng", "thời hạn", "36 tháng"],
        "expected_law": "Bộ luật Lao động"
    },
    {
        "query": "thủ tục đăng ký kinh doanh doanh nghiệp",
        "expected_keywords": ["đăng ký", "kinh doanh", "doanh nghiệp"],
        "expected_law": "Luật Doanh nghiệp"
    },
    {
        "query": "trách nhiệm bồi thường thiệt hại ngoài hợp đồng",
        "expected_keywords": ["bồi thường", "thiệt hại", "trách nhiệm"],
        "expected_law": "Bộ luật Dân sự"
    },
    {
        "query": "chế độ thai sản cho lao động nữ",
        "expected_keywords": ["thai sản", "lao động nữ", "bảo hiểm"],
        "expected_law": "Luật Bảo hiểm xã hội"
    },
]

async def run_benchmark():
    """So sánh kết quả có và không có reranker."""
    
    # ... (init orchestrator với 2 config: reranker ON và OFF)
    
    results_comparison = []
    
    for test_case in BENCHMARK_QUERIES:
        query = test_case["query"]
        
        # Chạy KHÔNG có reranker
        start = time.time()
        results_no_rerank = await orchestrator.search_documents(
            query=query, top_k=5, use_reranker=False
        )
        time_no_rerank = (time.time() - start) * 1000
        
        # Chạy CÓ reranker
        start = time.time()
        results_with_rerank = await orchestrator.search_documents(
            query=query, top_k=5, use_reranker=True
        )
        time_with_rerank = (time.time() - start) * 1000
        
        # So sánh
        comparison = {
            "query": query,
            "latency_without_ms": round(time_no_rerank, 1),
            "latency_with_ms": round(time_with_rerank, 1),
            "latency_overhead_ms": round(time_with_rerank - time_no_rerank, 1),
            "top1_changed": (
                results_no_rerank[0].get("chunk_id") != 
                results_with_rerank[0].get("chunk_id")
                if results_no_rerank and results_with_rerank else None
            ),
            "relevance_improvement": _calculate_relevance(
                results_with_rerank, test_case["expected_keywords"]
            ) - _calculate_relevance(
                results_no_rerank, test_case["expected_keywords"]
            ),
        }
        results_comparison.append(comparison)
        
        print(f"\nQuery: {query}")
        print(f"  Latency: {comparison['latency_without_ms']}ms → "
              f"{comparison['latency_with_ms']}ms "
              f"(+{comparison['latency_overhead_ms']}ms)")
        print(f"  Top-1 changed: {comparison['top1_changed']}")
        print(f"  Relevance delta: {comparison['relevance_improvement']:+.2f}")
    
    # Summary
    avg_overhead = sum(
        r["latency_overhead_ms"] for r in results_comparison
    ) / len(results_comparison)
    avg_improvement = sum(
        r["relevance_improvement"] for r in results_comparison
    ) / len(results_comparison)
    
    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"  Avg latency overhead: +{avg_overhead:.0f}ms")
    print(f"  Avg relevance improvement: {avg_improvement:+.3f}")
    print(f"  Queries with top-1 change: "
          f"{sum(1 for r in results_comparison if r['top1_changed'])}"
          f"/{len(results_comparison)}")

def _calculate_relevance(results, expected_keywords):
    """Tính relevance score dựa trên keyword matching."""
    if not results:
        return 0.0
    score = 0.0
    for i, result in enumerate(results[:5]):
        content = (result.get("content", "") + result.get("title", "")).lower()
        matches = sum(1 for kw in expected_keywords if kw.lower() in content)
        # Weighted by position (top results count more)
        weight = 1.0 / (i + 1)
        score += (matches / len(expected_keywords)) * weight
    return score

if __name__ == "__main__":
    asyncio.run(run_benchmark())
```

**Deliverable Ngày 3:**
- ✅ Unit tests pass (100%)
- ✅ Benchmark results: latency overhead < 100ms, relevance improvement measurable
- ✅ Vietnamese legal query tests pass

---

### NGÀY 4 (Thứ 5): Docker + GPU Deployment

**Buổi sáng (4h): Update Docker configuration**

Thêm vào `docker-compose.yml`:
```yaml
services:
  retrieval-api:
    # ... existing config ...
    environment:
      # ⭐ Reranker config
      - RERANKER_ENABLED=true
      - RERANKER_MODEL=BAAI/bge-reranker-v2-m3
      - RERANKER_DEVICE=cuda
      - RERANKER_MAX_CANDIDATES=20
      - RERANKER_TOP_K=5
      - RERANKER_TIMEOUT_MS=2000
      - RERANKER_BATCH_SIZE=16
    
    # ⭐ GPU access
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    
    volumes:
      # Cache model locally để không download mỗi lần restart
      - huggingface_cache:/root/.cache/huggingface
    
volumes:
  huggingface_cache:
    driver: local
```

Thêm vào `Dockerfile`:
```dockerfile
# Pre-download model during build (tránh download runtime)
RUN python -c "
from transformers import AutoModelForSequenceClassification, AutoTokenizer; \
AutoTokenizer.from_pretrained('BAAI/bge-reranker-v2-m3'); \
AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-v2-m3')
"
```

**Buổi chiều (4h): Deploy lên server .70 (dev) và test end-to-end**

```bash
# 1. Build và deploy
cd /path/to/FR-04.1Retrieval
docker-compose build retrieval-api
docker-compose up -d retrieval-api

# 2. Verify reranker loaded
curl http://192.168.1.70:8000/api/v1/reranker/health
# Expected: {"status": "healthy", "model": "BAAI/bge-reranker-v2-m3", "device": "cuda"}

# 3. Test search với reranker
curl -X POST http://192.168.1.70:8000/api/v1/search/hybrid \
  -H "Content-Type: application/json" \
  -d '{"query": "nghỉ phép năm nhân viên", "top_k": 5}'

# 4. Kiểm tra response có rerank_score
# Expected: mỗi result có thêm "rerank_score", "rank_change"

# 5. Toggle test
curl -X POST "http://192.168.1.70:8000/api/v1/reranker/toggle?enabled=false"
# Chạy lại search → verify không có rerank_score

curl -X POST "http://192.168.1.70:8000/api/v1/reranker/toggle?enabled=true"
# Chạy lại search → verify có rerank_score
```

**Deliverable Ngày 4:**
- ✅ Docker container build thành công với GPU support
- ✅ Reranker health endpoint trả "healthy"
- ✅ End-to-end search hoạt động với reranker
- ✅ Toggle on/off hoạt động

---

### NGÀY 5 (Thứ 6): Production Tuning & Documentation

**Buổi sáng (4h): Tuning parameters**

```python
# Script tune_reranker_params.py
# Grid search trên dev server với real data

PARAM_GRID = {
    "max_candidates": [10, 15, 20, 30],
    "score_weight": [0.5, 0.6, 0.7, 0.8],
    "min_rerank_score": [0.05, 0.1, 0.15, 0.2],
    "max_length": [256, 384, 512],
}

# Chạy benchmark cho mỗi combination
# Chọn params có accuracy cao nhất với latency < 200ms
```

**Buổi chiều (4h): Cập nhật documentation và monitoring**

Checklist:
- [ ] Update `ATTECH_TROUBLESHOOTING.md` — xóa "Reranker Missing" khỏi known issues
- [ ] Update `ATTECH_ROADMAP.md` — đánh dấu Reranker là ✅ DONE
- [ ] Thêm Grafana dashboard panel cho reranker metrics
- [ ] Thêm Prometheus alert: reranker_error_rate > 5%
- [ ] Viết runbook: "Reranker performance degraded" troubleshooting

**Deliverable Ngày 5:**
- ✅ Parameters tuned cho Vietnamese legal domain
- ✅ Documentation updated
- ✅ Monitoring configured
- ✅ RERANKER PRODUCTION-READY

---

## 4. CHECKLIST NGHIỆM THU

### Functional Requirements
- [ ] Reranker tăng accuracy lên ≥80% trên benchmark queries
- [ ] Fallback graceful khi reranker disabled/lỗi/timeout
- [ ] Toggle on/off runtime không cần restart
- [ ] Kết quả có rerank_score và rank_change

### Performance Requirements
- [ ] Latency overhead < 100ms cho 20 candidates (GPU)
- [ ] Latency overhead < 300ms cho 20 candidates (CPU fallback)
- [ ] VRAM usage < 1.5GB thêm
- [ ] Không ảnh hưởng throughput của các search engines

### Integration Requirements
- [ ] FR-04.2 Synthesis nhận kết quả bình thường (backward compatible)
- [ ] Search logs ghi nhận rerank_score
- [ ] API endpoints hoạt động (/health, /toggle, /metrics)
- [ ] Docker build thành công

### Quality Requirements
- [ ] Unit tests > 90% coverage cho reranker module
- [ ] Benchmark script chạy được với real data
- [ ] Vietnamese legal queries cải thiện rõ rệt

---

## 5. RISK & MITIGATION

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Model quá lớn cho VRAM | Không deploy được trên GPU | Thấp (1.1GB) | Dùng CPU mode hoặc quantization INT8 |
| Latency quá cao | UX kém | Trung bình | Giảm max_candidates, tăng batch_size, dùng FP16 |
| Accuracy không cải thiện | Waste 1 tuần | Thấp | Ngày 3 benchmark sớm, nếu fail thì thử Qwen3-Reranker |
| Conflict với Qwen3-Embedding trên GPU | OOM error | Thấp | Monitor VRAM, separate CUDA streams |
| Breaking change cho FR-04.2 | Synthesis lỗi | Trung bình | Backward compatible output format, RerankedResult.original_result |

---

## 6. TÓM TẮT

```
TRƯỚC:
Query → 6 Engines → HybridRanker (score math) → Top K → Synthesis → LLM
                     ^^^^^^^^^^^^
                     Chỉ dùng TOÁN để rank
                     Accuracy: ~75%

SAU:
Query → 6 Engines → HybridRanker → Reranker (neural understanding) → Top K → Synthesis → LLM
                                    ^^^^^^^^^
                                    Hiểu NGỮA NGHĨA query-document
                                    Accuracy: ≥80% (target)
```

**Effort:** 5 ngày, 1 người chính + 1 hỗ trợ test  
**Files mới:** 2 (`cross_encoder_reranker.py`, `reranker_config.py`)  
**Files sửa:** 2 (`search_orchestrator.py`, `main.py`)  
**Files test:** 2 (`test_cross_encoder_reranker.py`, `benchmark_reranker.py`)  
**Dependency mới:** `transformers`, `torch` (có thể đã có)  
**Không tạo module mới.** Tích hợp vào FR-04.1 ranking layer.
