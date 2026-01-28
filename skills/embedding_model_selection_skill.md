# Embedding Model Selection & Optimization Skill (FR01.1)

## Overview
This skill enables Claude to assist with selecting, evaluating, optimizing, and deploying embedding models for Vietnamese RAG systems. Focus on practical benchmarking, Vietnamese-specific performance tuning, and production deployment strategies.

## System Context

### Current Configuration
```python
# Production Model
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
EMBEDDING_DIM = 1024
MAX_SEQ_LENGTH = 512
BATCH_SIZE = 16

# Hardware
GPU: NVIDIA RTX 2080 Ti (11GB VRAM)
CUDA: 11.8
PyTorch: 2.7.1+cu118
```

### Evaluation Criteria
1. **Vietnamese Language Understanding** (40% weight)
2. **Retrieval Accuracy** (30% weight)
3. **Inference Speed** (15% weight)
4. **Memory Footprint** (10% weight)
5. **Cost Efficiency** (5% weight)

## Model Candidates for Vietnamese

### Tier 1: Production-Ready Models
```python
PRODUCTION_MODELS = {
    "qwen3-embedding-0.6b": {
        "model_id": "Qwen/Qwen3-Embedding-0.6B",
        "dimensions": 1024,
        "max_length": 512,
        "size_mb": 1200,
        "pros": [
            "Excellent Vietnamese support",
            "Fast inference",
            "Good multilingual capabilities"
        ],
        "cons": [
            "Larger model size"
        ],
        "use_case": "General purpose RAG"
    },
    
    "bge-m3": {
        "model_id": "BAAI/bge-m3",
        "dimensions": 1024,
        "max_length": 8192,
        "size_mb": 2300,
        "pros": [
            "Multi-vector retrieval",
            "Long context support",
            "Strong multilingual"
        ],
        "cons": [
            "Higher memory usage",
            "Slower inference"
        ],
        "use_case": "Long document retrieval"
    },
    
    "gte-multilingual": {
        "model_id": "Alibaba-NLP/gte-multilingual-base",
        "dimensions": 768,
        "max_length": 512,
        "size_mb": 1100,
        "pros": [
            "Good Vietnamese performance",
            "Balanced speed/accuracy",
            "Lower memory"
        ],
        "cons": [
            "Lower dimensions than Qwen3"
        ],
        "use_case": "Resource-constrained deployments"
    },
    
    "e5-mistral": {
        "model_id": "intfloat/e5-mistral-7b-instruct",
        "dimensions": 4096,
        "max_length": 32768,
        "size_mb": 14000,
        "pros": [
            "Very high quality embeddings",
            "Instruction-following",
            "Extremely long context"
        ],
        "cons": [
            "Very large model",
            "Slow inference",
            "Requires multiple GPUs or quantization"
        ],
        "use_case": "Research or cloud deployments"
    }
}
```

### Tier 2: Vietnamese-Specific Models
```python
VIETNAMESE_MODELS = {
    "vietnamese-sbert": {
        "model_id": "keepitreal/vietnamese-sbert",
        "dimensions": 768,
        "max_length": 256,
        "pros": [
            "Trained specifically on Vietnamese",
            "Good for short texts"
        ],
        "cons": [
            "Limited max length",
            "Older architecture"
        ]
    },
    
    "phobert-base": {
        "model_id": "vinai/phobert-base",
        "dimensions": 768,
        "max_length": 256,
        "pros": [
            "Vietnamese-focused",
            "Good for classification"
        ],
        "cons": [
            "Not optimized for retrieval",
            "Requires fine-tuning"
        ]
    }
}
```

## Evaluation Framework

### 1. Vietnamese Test Dataset
```python
import json
from typing import List, Dict

class VietnameseEvalDataset:
    """
    Evaluation dataset for Vietnamese embedding models
    """
    
    def __init__(self):
        self.queries = []
        self.documents = []
        self.relevance_labels = []
    
    def load_legal_qa_pairs(self) -> List[Dict]:
        """
        Load Vietnamese legal Q&A pairs for evaluation
        """
        # Example structure
        qa_pairs = [
            {
                "query": "Thủ tục cấp giấy phép xây dựng?",
                "positive_docs": ["doc_123", "doc_456"],
                "negative_docs": ["doc_789", "doc_012"],
                "difficulty": "easy"
            },
            {
                "query": "Quy định về thuế thu nhập cá nhân năm 2024",
                "positive_docs": ["doc_234"],
                "negative_docs": ["doc_345", "doc_567"],
                "difficulty": "medium"
            },
            {
                "query": "Điều kiện hưởng chế độ thai sản theo Luật Bảo hiểm xã hội",
                "positive_docs": ["doc_678", "doc_890"],
                "negative_docs": ["doc_901", "doc_123"],
                "difficulty": "hard"
            }
        ]
        
        return qa_pairs
    
    def create_synthetic_dataset(self, num_samples: int = 100):
        """
        Generate synthetic Vietnamese test data
        """
        from underthesea import word_tokenize
        import random
        
        # Legal domain keywords
        legal_terms = [
            "nghị định", "quyết định", "thông tư", "luật",
            "quy định", "thủ tục", "điều kiện", "hồ sơ"
        ]
        
        # Generate queries
        for i in range(num_samples):
            # Random legal query
            query = self._generate_legal_query(legal_terms)
            
            # Generate positive and negative documents
            pos_docs = self._generate_documents(query, relevant=True, count=3)
            neg_docs = self._generate_documents(query, relevant=False, count=7)
            
            self.queries.append(query)
            self.documents.extend(pos_docs + neg_docs)
            
            # Create relevance labels
            labels = [1] * len(pos_docs) + [0] * len(neg_docs)
            self.relevance_labels.append(labels)
        
        return self
    
    def _generate_legal_query(self, terms: List[str]) -> str:
        """Generate synthetic legal query"""
        # Implementation here
        pass
    
    def _generate_documents(
        self, 
        query: str, 
        relevant: bool, 
        count: int
    ) -> List[str]:
        """Generate synthetic documents"""
        # Implementation here
        pass
    
    def save_to_jsonl(self, filepath: str):
        """
        Save dataset in JSONL format
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, query in enumerate(self.queries):
                sample = {
                    "query_id": f"q_{i}",
                    "query": query,
                    "relevant_docs": [
                        doc for doc, label in zip(
                            self.documents[i*10:(i+1)*10],
                            self.relevance_labels[i]
                        ) if label == 1
                    ],
                    "non_relevant_docs": [
                        doc for doc, label in zip(
                            self.documents[i*10:(i+1)*10],
                            self.relevance_labels[i]
                        ) if label == 0
                    ]
                }
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
```

### 2. Benchmark Framework
```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time
from typing import Dict, List
import torch

class EmbeddingBenchmark:
    """
    Comprehensive benchmarking for embedding models
    """
    
    def __init__(self, device: str = "cuda"):
        self.device = device
        self.results = {}
    
    def benchmark_model(
        self, 
        model_id: str, 
        test_queries: List[str],
        test_documents: List[str],
        relevance_labels: List[List[int]]
    ) -> Dict:
        """
        Run complete benchmark on a model
        """
        print(f"\n{'='*60}")
        print(f"Benchmarking: {model_id}")
        print(f"{'='*60}")
        
        # Load model
        start_load = time.time()
        model = SentenceTransformer(model_id, device=self.device)
        load_time = time.time() - start_load
        
        # 1. Memory footprint
        memory_mb = self._measure_memory(model)
        
        # 2. Inference speed
        speed_metrics = self._measure_speed(model, test_queries)
        
        # 3. Retrieval accuracy
        accuracy_metrics = self._measure_accuracy(
            model, 
            test_queries, 
            test_documents, 
            relevance_labels
        )
        
        # 4. Vietnamese-specific tests
        viet_metrics = self._vietnamese_specific_tests(model)
        
        results = {
            "model_id": model_id,
            "load_time_seconds": load_time,
            "memory_mb": memory_mb,
            "speed": speed_metrics,
            "accuracy": accuracy_metrics,
            "vietnamese_performance": viet_metrics
        }
        
        self.results[model_id] = results
        
        # Clean up
        del model
        torch.cuda.empty_cache()
        
        return results
    
    def _measure_memory(self, model) -> float:
        """
        Measure model memory footprint
        """
        if self.device == "cuda":
            torch.cuda.reset_peak_memory_stats()
            
            # Dummy forward pass
            dummy_input = "Test sentence"
            _ = model.encode(dummy_input)
            
            memory_bytes = torch.cuda.max_memory_allocated()
            memory_mb = memory_bytes / (1024 ** 2)
            
            return round(memory_mb, 2)
        else:
            return 0.0
    
    def _measure_speed(
        self, 
        model, 
        queries: List[str], 
        batch_sizes: List[int] = [1, 8, 16, 32]
    ) -> Dict:
        """
        Measure inference speed at different batch sizes
        """
        speed_results = {}
        
        for batch_size in batch_sizes:
            # Select samples
            samples = queries[:batch_size * 10]  # 10 batches
            
            # Warmup
            _ = model.encode(samples[:batch_size])
            
            # Benchmark
            start = time.time()
            embeddings = model.encode(
                samples, 
                batch_size=batch_size,
                show_progress_bar=False
            )
            elapsed = time.time() - start
            
            # Calculate metrics
            throughput = len(samples) / elapsed  # sentences/second
            latency_ms = (elapsed / len(samples)) * 1000  # ms per sentence
            
            speed_results[f"batch_{batch_size}"] = {
                "throughput": round(throughput, 2),
                "latency_ms": round(latency_ms, 2)
            }
        
        return speed_results
    
    def _measure_accuracy(
        self,
        model,
        queries: List[str],
        documents: List[str],
        relevance_labels: List[List[int]]
    ) -> Dict:
        """
        Measure retrieval accuracy metrics
        """
        # Encode queries and documents
        query_embeddings = model.encode(queries, show_progress_bar=False)
        doc_embeddings = model.encode(documents, show_progress_bar=False)
        
        # Calculate similarities
        similarities = cosine_similarity(query_embeddings, doc_embeddings)
        
        # Calculate metrics
        mrr_scores = []
        ndcg_scores = []
        recall_at_k = {k: [] for k in [1, 3, 5, 10]}
        
        for i, query_sims in enumerate(similarities):
            labels = relevance_labels[i]
            
            # Get ranked indices
            ranked_indices = np.argsort(query_sims)[::-1]
            
            # MRR (Mean Reciprocal Rank)
            for rank, idx in enumerate(ranked_indices, 1):
                if labels[idx] == 1:
                    mrr_scores.append(1.0 / rank)
                    break
            else:
                mrr_scores.append(0.0)
            
            # NDCG (Normalized Discounted Cumulative Gain)
            dcg = self._calculate_dcg(query_sims, labels, k=10)
            idcg = self._calculate_idcg(labels, k=10)
            ndcg = dcg / idcg if idcg > 0 else 0.0
            ndcg_scores.append(ndcg)
            
            # Recall@K
            for k in recall_at_k.keys():
                top_k_indices = ranked_indices[:k]
                relevant_retrieved = sum(labels[idx] for idx in top_k_indices)
                total_relevant = sum(labels)
                recall = relevant_retrieved / total_relevant if total_relevant > 0 else 0.0
                recall_at_k[k].append(recall)
        
        return {
            "MRR": round(np.mean(mrr_scores), 4),
            "NDCG@10": round(np.mean(ndcg_scores), 4),
            "Recall@1": round(np.mean(recall_at_k[1]), 4),
            "Recall@3": round(np.mean(recall_at_k[3]), 4),
            "Recall@5": round(np.mean(recall_at_k[5]), 4),
            "Recall@10": round(np.mean(recall_at_k[10]), 4)
        }
    
    def _calculate_dcg(
        self, 
        scores: np.ndarray, 
        labels: List[int], 
        k: int
    ) -> float:
        """Calculate Discounted Cumulative Gain"""
        ranked_indices = np.argsort(scores)[::-1][:k]
        dcg = sum(
            labels[idx] / np.log2(rank + 2) 
            for rank, idx in enumerate(ranked_indices)
        )
        return dcg
    
    def _calculate_idcg(self, labels: List[int], k: int) -> float:
        """Calculate Ideal DCG"""
        sorted_labels = sorted(labels, reverse=True)[:k]
        idcg = sum(
            label / np.log2(rank + 2) 
            for rank, label in enumerate(sorted_labels)
        )
        return idcg
    
    def _vietnamese_specific_tests(self, model) -> Dict:
        """
        Test Vietnamese-specific capabilities
        """
        # Test 1: Tone mark sensitivity
        tone_pairs = [
            ("Hà Nội", "Ha Noi"),
            ("Việt Nam", "Viet Nam"),
            ("Quyết định", "Quyet dinh")
        ]
        
        tone_sensitivity = []
        for pair in tone_pairs:
            emb1 = model.encode(pair[0])
            emb2 = model.encode(pair[1])
            similarity = cosine_similarity([emb1], [emb2])[0][0]
            tone_sensitivity.append(similarity)
        
        # Test 2: Legal terminology understanding
        legal_queries = [
            "Nghị định số 123/NĐ-CP",
            "Quyết định số 456/QĐ-TTg",
            "Thông tư số 789/TT-BCA"
        ]
        
        legal_docs = [
            "Căn cứ Luật Tổ chức Chính phủ, Chính phủ ban hành Nghị định số 123/NĐ-CP",
            "Thủ tướng Chính phủ ký Quyết định số 456/QĐ-TTg về việc...",
            "Bộ Công an ban hành Thông tư số 789/TT-BCA hướng dẫn..."
        ]
        
        query_embs = model.encode(legal_queries)
        doc_embs = model.encode(legal_docs)
        
        legal_sims = cosine_similarity(query_embs, doc_embs)
        legal_accuracy = np.mean(np.diag(legal_sims))  # Diagonal should be highest
        
        # Test 3: Long Vietnamese text handling
        long_text = "Căn cứ " + " ".join(["Điều khoản"] * 100)
        short_text = "Căn cứ Điều khoản"
        
        try:
            _ = model.encode(long_text)
            long_text_support = True
        except:
            long_text_support = False
        
        return {
            "tone_mark_sensitivity": round(np.mean(tone_sensitivity), 4),
            "legal_terminology_accuracy": round(legal_accuracy, 4),
            "long_text_support": long_text_support
        }
    
    def compare_models(self) -> pd.DataFrame:
        """
        Generate comparison table
        """
        import pandas as pd
        
        comparison_data = []
        
        for model_id, results in self.results.items():
            row = {
                "Model": model_id.split('/')[-1],
                "Memory (MB)": results["memory_mb"],
                "Throughput (sent/s)": results["speed"]["batch_16"]["throughput"],
                "Latency (ms)": results["speed"]["batch_16"]["latency_ms"],
                "MRR": results["accuracy"]["MRR"],
                "NDCG@10": results["accuracy"]["NDCG@10"],
                "Recall@5": results["accuracy"]["Recall@5"],
                "Vietnamese Score": results["vietnamese_performance"]["legal_terminology_accuracy"]
            }
            comparison_data.append(row)
        
        df = pd.DataFrame(comparison_data)
        df = df.sort_values("MRR", ascending=False)
        
        return df
    
    def save_results(self, filepath: str):
        """
        Save benchmark results to JSON
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dumps(self.results, f, indent=2, ensure_ascii=False)
```

### 3. Running Benchmarks
```python
# Example usage
if __name__ == "__main__":
    # 1. Create test dataset
    dataset = VietnameseEvalDataset()
    dataset.create_synthetic_dataset(num_samples=100)
    
    # Or load real dataset
    # dataset.load_legal_qa_pairs()
    
    # 2. Initialize benchmark
    benchmark = EmbeddingBenchmark(device="cuda")
    
    # 3. Models to test
    models_to_test = [
        "Qwen/Qwen3-Embedding-0.6B",
        "BAAI/bge-m3",
        "Alibaba-NLP/gte-multilingual-base",
        "keepitreal/vietnamese-sbert"
    ]
    
    # 4. Run benchmarks
    for model_id in models_to_test:
        try:
            results = benchmark.benchmark_model(
                model_id,
                dataset.queries,
                dataset.documents,
                dataset.relevance_labels
            )
            print(f"\n✅ {model_id}: MRR={results['accuracy']['MRR']:.4f}")
        except Exception as e:
            print(f"\n❌ {model_id}: Error - {str(e)}")
    
    # 5. Compare results
    comparison_df = benchmark.compare_models()
    print("\n" + "="*80)
    print("COMPARISON TABLE")
    print("="*80)
    print(comparison_df.to_string(index=False))
    
    # 6. Save results
    benchmark.save_results("embedding_benchmark_results.json")
```

## Model Optimization Techniques

### 1. Quantization
```python
from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer

class QuantizedEmbeddingModel:
    """
    Quantized model for faster inference
    """
    
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # Load quantized ONNX model
        self.model = ORTModelForFeatureExtraction.from_pretrained(
            model_id,
            export=True,
            provider="CUDAExecutionProvider"
        )
    
    def encode(self, texts: List[str], batch_size: int = 32):
        """
        Encode texts using quantized model
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            
            outputs = self.model(**inputs)
            
            # Mean pooling
            batch_embeddings = self._mean_pooling(
                outputs.last_hidden_state,
                inputs['attention_mask']
            )
            
            embeddings.append(batch_embeddings)
        
        return torch.cat(embeddings, dim=0)
    
    def _mean_pooling(self, model_output, attention_mask):
        """Mean pooling"""
        token_embeddings = model_output
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(
            token_embeddings.size()
        ).float()
        
        return torch.sum(
            token_embeddings * input_mask_expanded, 1
        ) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
```

### 2. Dynamic Batching
```python
class DynamicBatchingEncoder:
    """
    Encoder with dynamic batching for optimal GPU utilization
    """
    
    def __init__(self, model, max_batch_size: int = 32):
        self.model = model
        self.max_batch_size = max_batch_size
    
    def encode_adaptive(self, texts: List[str]) -> np.ndarray:
        """
        Encode with adaptive batch sizing based on text length
        """
        # Sort by length for efficient batching
        indexed_texts = [(i, text) for i, text in enumerate(texts)]
        indexed_texts.sort(key=lambda x: len(x[1]))
        
        embeddings = [None] * len(texts)
        
        i = 0
        while i < len(indexed_texts):
            # Determine batch size based on text length
            current_length = len(indexed_texts[i][1])
            
            if current_length < 100:
                batch_size = self.max_batch_size
            elif current_length < 300:
                batch_size = self.max_batch_size // 2
            else:
                batch_size = self.max_batch_size // 4
            
            # Get batch
            batch_items = indexed_texts[i:i+batch_size]
            batch_texts = [item[1] for item in batch_items]
            batch_indices = [item[0] for item in batch_items]
            
            # Encode
            batch_embeddings = self.model.encode(batch_texts)
            
            # Place in original order
            for idx, emb in zip(batch_indices, batch_embeddings):
                embeddings[idx] = emb
            
            i += batch_size
        
        return np.array(embeddings)
```

### 3. Caching Strategy
```python
import hashlib
import pickle
from pathlib import Path

class EmbeddingCache:
    """
    Cache embeddings to avoid recomputation
    """
    
    def __init__(self, cache_dir: str = "/tmp/embedding_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_key(self, text: str, model_id: str) -> str:
        """
        Generate cache key from text and model
        """
        content = f"{model_id}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, text: str, model_id: str) -> np.ndarray:
        """
        Retrieve embedding from cache
        """
        key = self.get_cache_key(text, model_id)
        cache_file = self.cache_dir / f"{key}.pkl"
        
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        
        return None
    
    def set(self, text: str, model_id: str, embedding: np.ndarray):
        """
        Store embedding in cache
        """
        key = self.get_cache_key(text, model_id)
        cache_file = self.cache_dir / f"{key}.pkl"
        
        with open(cache_file, 'wb') as f:
            pickle.dump(embedding, f)
    
    def encode_with_cache(
        self, 
        texts: List[str], 
        model, 
        model_id: str
    ) -> np.ndarray:
        """
        Encode texts with caching
        """
        embeddings = []
        texts_to_encode = []
        cache_indices = []
        
        # Check cache
        for i, text in enumerate(texts):
            cached_emb = self.get(text, model_id)
            if cached_emb is not None:
                embeddings.append((i, cached_emb))
            else:
                texts_to_encode.append(text)
                cache_indices.append(i)
        
        # Encode uncached texts
        if texts_to_encode:
            new_embeddings = model.encode(texts_to_encode)
            
            # Cache new embeddings
            for text, emb in zip(texts_to_encode, new_embeddings):
                self.set(text, model_id, emb)
            
            # Add to results
            for idx, emb in zip(cache_indices, new_embeddings):
                embeddings.append((idx, emb))
        
        # Sort by original order
        embeddings.sort(key=lambda x: x[0])
        
        return np.array([emb for _, emb in embeddings])
```

## Production Deployment

### 1. Model Serving with FastAPI
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import torch
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Embedding Service")

# Global model instance
model = None

class EmbeddingRequest(BaseModel):
    texts: List[str]
    normalize: bool = True

class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    model_id: str
    dimensions: int

@app.on_event("startup")
async def load_model():
    """
    Load model on startup
    """
    global model
    
    MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"Loading model: {MODEL_ID} on {device}")
    model = SentenceTransformer(MODEL_ID, device=device)
    print("Model loaded successfully")

@app.post("/embed", response_model=EmbeddingResponse)
async def generate_embeddings(request: EmbeddingRequest):
    """
    Generate embeddings for input texts
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        embeddings = model.encode(
            request.texts,
            normalize_embeddings=request.normalize,
            show_progress_bar=False
        )
        
        return EmbeddingResponse(
            embeddings=embeddings.tolist(),
            model_id=model.get_sentence_embedding_dimension(),
            dimensions=model.get_sentence_embedding_dimension()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(model.device) if model else None
    }

@app.get("/model/info")
async def model_info():
    """
    Get model information
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_id": model.get_config_dict().get("sentence_bert_config", {}).get("model_name_or_path", "unknown"),
        "dimensions": model.get_sentence_embedding_dimension(),
        "max_seq_length": model.max_seq_length,
        "device": str(model.device)
    }
```

### 2. Docker Deployment
```dockerfile
# Dockerfile for embedding service
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run service
CMD ["uvicorn", "embedding_service:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  embedding-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_ID=Qwen/Qwen3-Embedding-0.6B
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - model_cache:/root/.cache/huggingface
    restart: unless-stopped

volumes:
  model_cache:
```

### 3. Load Balancing for High Throughput
```python
import asyncio
from typing import List
import aiohttp

class EmbeddingLoadBalancer:
    """
    Load balancer for multiple embedding service instances
    """
    
    def __init__(self, service_urls: List[str]):
        self.service_urls = service_urls
        self.current_index = 0
    
    def get_next_service(self) -> str:
        """
        Round-robin service selection
        """
        url = self.service_urls[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.service_urls)
        return url
    
    async def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts using load-balanced services
        """
        # Split texts across services
        chunk_size = len(texts) // len(self.service_urls) + 1
        chunks = [
            texts[i:i+chunk_size] 
            for i in range(0, len(texts), chunk_size)
        ]
        
        # Send requests in parallel
        tasks = []
        for chunk in chunks:
            service_url = self.get_next_service()
            task = self._send_request(service_url, chunk)
            tasks.append(task)
        
        # Gather results
        results = await asyncio.gather(*tasks)
        
        # Combine embeddings
        embeddings = np.vstack(results)
        
        return embeddings
    
    async def _send_request(
        self, 
        service_url: str, 
        texts: List[str]
    ) -> np.ndarray:
        """
        Send request to embedding service
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{service_url}/embed",
                json={"texts": texts, "normalize": True}
            ) as response:
                data = await response.json()
                return np.array(data["embeddings"])
```

## Fine-tuning for Vietnamese Legal Domain

### 1. Prepare Training Data
```python
from sentence_transformers import InputExample

def prepare_training_data(qa_pairs: List[Dict]) -> List[InputExample]:
    """
    Prepare training data for fine-tuning
    """
    examples = []
    
    for pair in qa_pairs:
        query = pair["query"]
        positive_doc = pair["positive_doc"]
        negative_doc = pair["negative_doc"]
        
        # Triplet: (anchor, positive, negative)
        examples.append(InputExample(
            texts=[query, positive_doc, negative_doc]
        ))
    
    return examples
```

### 2. Fine-tune Model
```python
from sentence_transformers import SentenceTransformer, losses
from torch.utils.data import DataLoader

def finetune_embedding_model(
    base_model_id: str,
    train_examples: List[InputExample],
    output_path: str,
    epochs: int = 3
):
    """
    Fine-tune embedding model on Vietnamese legal data
    """
    # Load base model
    model = SentenceTransformer(base_model_id)
    
    # Create dataloader
    train_dataloader = DataLoader(
        train_examples, 
        shuffle=True, 
        batch_size=16
    )
    
    # Define loss
    train_loss = losses.TripletLoss(model)
    
    # Train
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=epochs,
        warmup_steps=100,
        output_path=output_path
    )
    
    return model
```

## Monitoring & Evaluation

### 1. Continuous Evaluation
```python
class ContinuousEvaluator:
    """
    Continuously monitor embedding quality in production
    """
    
    def __init__(self, model):
        self.model = model
        self.metrics_history = []
    
    def evaluate_batch(
        self, 
        queries: List[str], 
        retrieved_docs: List[List[str]],
        relevance_labels: List[List[int]]
    ):
        """
        Evaluate a batch of production queries
        """
        # Calculate metrics
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "batch_size": len(queries),
            "avg_query_length": np.mean([len(q) for q in queries]),
            "mrr": self._calculate_batch_mrr(
                queries, 
                retrieved_docs, 
                relevance_labels
            )
        }
        
        self.metrics_history.append(metrics)
        
        # Alert if performance degrades
        if len(self.metrics_history) > 10:
            recent_mrr = np.mean([
                m["mrr"] for m in self.metrics_history[-10:]
            ])
            
            if recent_mrr < 0.6:  # Threshold
                self._send_alert(f"MRR dropped to {recent_mrr:.3f}")
        
        return metrics
    
    def _send_alert(self, message: str):
        """Send alert when performance degrades"""
        # Implementation: send to Slack, email, etc.
        print(f"⚠️ ALERT: {message}")
```

## Vietnamese-Specific Optimizations

### 1. Tone Mark Normalization Strategy
```python
def should_normalize_tones(query_type: str) -> bool:
    """
    Decide whether to normalize Vietnamese tone marks
    """
    # For legal document codes: keep tone marks
    if any(pattern in query_type for pattern in ['QĐ-', 'NĐ-', 'TT-']):
        return False
    
    # For semantic search: normalize to improve recall
    return True
```

### 2. Domain-Specific Preprocessing
```python
class VietnameseLegalPreprocessor:
    """
    Preprocessing optimized for Vietnamese legal documents
    """
    
    def preprocess_for_embedding(self, text: str) -> str:
        """
        Preprocess text before embedding
        """
        # Keep legal codes intact
        legal_codes = self._extract_legal_codes(text)
        
        # Replace with placeholders
        for i, code in enumerate(legal_codes):
            text = text.replace(code, f"__CODE{i}__")
        
        # Normal preprocessing
        text = self._clean_text(text)
        
        # Restore codes
        for i, code in enumerate(legal_codes):
            text = text.replace(f"__CODE{i}__", code)
        
        return text
    
    def _extract_legal_codes(self, text: str) -> List[str]:
        """Extract Vietnamese legal document codes"""
        import re
        patterns = [
            r'\d+/[A-Z]{2,}-[\w-]+',
            r'Số\s*\d+/[\w-]+'
        ]
        
        codes = []
        for pattern in patterns:
            codes.extend(re.findall(pattern, text))
        
        return list(set(codes))
```

## Quick Reference

### Model Selection Decision Tree
```
┌─────────────────────────────────────┐
│  Need long context (>512 tokens)?  │
└──────────────┬──────────────────────┘
               │
        ┌──────┴───────┐
        │YES           │NO
        ▼              ▼
   ┌─────────┐    ┌────────────┐
   │ bge-m3  │    │ Budget GPU?│
   └─────────┘    └──────┬─────┘
                         │
                   ┌─────┴──────┐
                   │YES         │NO
                   ▼            ▼
            ┌──────────┐   ┌─────────────┐
            │gte-multi │   │Qwen3-0.6B   │
            │-base     │   │(RECOMMENDED)│
            └──────────┘   └─────────────┘
```

### Performance Tuning Checklist
```
□ Enable FP16 inference: 2x speedup, minimal accuracy loss
□ Use batching: 4-8x throughput improvement
□ Enable caching: 10x speedup for repeated queries
□ Quantize model: 25% memory reduction
□ Use GPU: 50-100x faster than CPU
□ Optimize batch size: max GPU utilization
□ Enable ONNX runtime: 20-30% faster inference
```

### Commands
```bash
# Benchmark a model
python benchmark_embeddings.py \
  --model "Qwen/Qwen3-Embedding-0.6B" \
  --dataset "vietnamese_legal_qa.jsonl" \
  --device "cuda"

# Start embedding service
uvicorn embedding_service:app --host 0.0.0.0 --port 8000

# Test embedding service
curl -X POST "http://localhost:8000/embed" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Thủ tục xin giấy phép"], "normalize": true}'

# Fine-tune model
python finetune.py \
  --base_model "Qwen/Qwen3-Embedding-0.6B" \
  --train_data "legal_triplets.jsonl" \
  --output_dir "./finetuned_model" \
  --epochs 3
```

## Success Criteria

- ✅ MRR > 0.75 on Vietnamese legal Q&A
- ✅ Inference latency < 50ms per query (batch 16)
- ✅ Memory footprint < 2GB VRAM
- ✅ Handles Vietnamese tone marks correctly
- ✅ Throughput > 200 sentences/second
- ✅ Supports 100+ concurrent users
- ✅ 99.9% uptime in production

## End of Skill File
