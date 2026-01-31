# Enterprise LLM Gateway Implementation Skill

## WHEN TO USE THIS SKILL

Use this skill when working on **FR-04.3 Generation Engine** or any system that requires:

- Multi-provider LLM integration (OpenAI, Claude, Gemini, local models)
- Unified API interface for all LLM providers
- Advanced routing (fallback, retries, load balancing)
- Semantic caching for cost optimization
- Request logging & tracing
- Cost tracking & budget management
- Content guardrails (PII detection, safety checks)
- Virtual key management for security
- Production-grade reliability (99.9%+ uptime)

**Key indicators to use this skill:**
- User mentions "Gateway", "multi-provider", "fallback", "caching", "routing"
- Requirements include reliability, cost optimization, or security features
- Building production LLM infrastructure
- Need to support 100+ concurrent users

---

## ARCHITECTURAL OVERVIEW

### Core Design Principles (from Portkey Analysis)

```mermaid
graph TB
    subgraph "🎯 REQUEST FLOW"
        A[Client Request] --> B{Gateway Entry}
        B --> C[Config Parser]
        C --> D[Provider Router]
        D --> E{Cache Check}
        E -->|Hit| F[Return Cached]
        E -->|Miss| G[Provider Selection]
        G --> H[Guardrails Check]
        H --> I[LLM Provider]
        I --> J[Response Processing]
        J --> K[Cache Update]
        K --> L[Logging & Metrics]
        L --> M[Return Response]
    end
    
    subgraph "⚡ CORE MODULES"
        N[Unified API Layer]
        O[Provider Adapters]
        P[Routing Engine]
        Q[Caching Layer]
        R[Monitoring System]
    end
    
    style A fill:#4CAF50
    style F fill:#2196F3
    style I fill:#FF9800
    style M fill:#4CAF50
```

### Tech Stack Recommendation

```python
# Based on Portkey's production-proven stack
TECH_STACK = {
    "Language": "Python 3.11+ with type hints",
    "Framework": "FastAPI (async)",
    "HTTP Client": "httpx (async)",
    "Caching": {
        "Simple": "Redis 7.0+",
        "Semantic": "Redis + Vector DB (ChromaDB/Qdrant)"
    },
    "Database": "PostgreSQL 15+ (metrics, config)",
    "Monitoring": "Prometheus + Grafana",
    "Logging": "Structlog (JSON)",
    "Deployment": "Docker + Kubernetes"
}
```

---

## FEATURE 1: UNIFIED API INTERFACE

### 1.1 OpenAI-Compatible Base Layer

**Concept**: All providers translate to OpenAI's API format.

```python
# src/gateway/unified_api.py
from typing import Protocol, Union, AsyncIterator
from pydantic import BaseModel

class ChatMessage(BaseModel):
    """Universal message format"""
    role: str  # "system" | "user" | "assistant"
    content: str
    
class ChatRequest(BaseModel):
    """Universal request format (OpenAI-compatible)"""
    model: str
    messages: list[ChatMessage]
    temperature: float = 0.7
    max_tokens: int | None = None
    stream: bool = False
    
class ChatResponse(BaseModel):
    """Universal response format"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[dict]
    usage: dict
    
class LLMProvider(Protocol):
    """Interface that all providers must implement"""
    
    async def chat_completion(
        self, 
        request: ChatRequest
    ) -> ChatResponse | AsyncIterator[ChatResponse]:
        """Standard method for chat completions"""
        ...
    
    async def get_cost(self, usage: dict) -> float:
        """Calculate cost for this request"""
        ...
```

### 1.2 Provider Adapters

**Pattern**: Adapter pattern to translate provider-specific APIs.

```python
# src/gateway/providers/anthropic_adapter.py
from anthropic import AsyncAnthropic
import time

class AnthropicAdapter:
    """Translates Claude API to OpenAI format"""
    
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model_map = {
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-3-sonnet": "claude-3-5-sonnet-20241022"
        }
    
    async def chat_completion(
        self, 
        request: ChatRequest
    ) -> ChatResponse:
        """Convert OpenAI request → Claude request → OpenAI response"""
        
        # Extract system message
        system_msg = ""
        user_messages = []
        
        for msg in request.messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                user_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Call Claude API
        response = await self.client.messages.create(
            model=self.model_map.get(request.model, request.model),
            system=system_msg,
            messages=user_messages,
            max_tokens=request.max_tokens or 4096,
            temperature=request.temperature
        )
        
        # Translate to OpenAI format
        return ChatResponse(
            id=f"chatcmpl-{response.id}",
            created=int(time.time()),
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response.content[0].text
                },
                "finish_reason": response.stop_reason
            }],
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": (
                    response.usage.input_tokens + 
                    response.usage.output_tokens
                )
            }
        )
    
    async def get_cost(self, usage: dict) -> float:
        """Claude pricing (example)"""
        PRICING = {
            "claude-3-opus": {
                "input": 0.000015,   # $15 per 1M tokens
                "output": 0.000075   # $75 per 1M tokens
            },
            "claude-3-sonnet": {
                "input": 0.000003,   # $3 per 1M tokens
                "output": 0.000015   # $15 per 1M tokens
            }
        }
        
        model_pricing = PRICING.get("claude-3-sonnet")
        cost = (
            usage["prompt_tokens"] * model_pricing["input"] +
            usage["completion_tokens"] * model_pricing["output"]
        )
        return cost
```

**Key Insight from Portkey**: Universal API reduces client-side complexity. User writes code once, switches providers via config.

---

## FEATURE 2: INTELLIGENT PROVIDER ROUTING

### 2.1 Config-Based Routing

**Pattern**: Declarative routing configuration (Portkey's approach).

```python
# src/gateway/routing/config.py
from pydantic import BaseModel
from typing import Literal

class RetryConfig(BaseModel):
    """Retry configuration"""
    attempts: int = 3
    on_status_codes: list[int] = [429, 500, 502, 503]
    exponential_backoff: bool = True
    base_delay_ms: int = 1000
    max_delay_ms: int = 60000

class FallbackTarget(BaseModel):
    """Fallback provider configuration"""
    provider: str
    model: str
    on_errors: list[str] = ["timeout", "rate_limit", "500", "503"]

class LoadBalanceTarget(BaseModel):
    """Load balancing target"""
    provider: str
    model: str
    weight: float  # Must sum to 1.0 across all targets

class RoutingConfig(BaseModel):
    """Complete routing configuration"""
    strategy: Literal["single", "fallback", "loadbalance"]
    
    # Single provider
    provider: str | None = None
    model: str | None = None
    
    # Fallback chain
    targets: list[FallbackTarget] = []
    
    # Load balancing
    weights: list[LoadBalanceTarget] = []
    
    # Retry configuration
    retry: RetryConfig = RetryConfig()
    
    # Cache settings
    cache: dict = {
        "mode": "simple",  # "simple" | "semantic"
        "ttl": 3600        # seconds
    }

# Example configurations
FALLBACK_CONFIG = RoutingConfig(
    strategy="fallback",
    targets=[
        FallbackTarget(
            provider="openai",
            model="gpt-4o-mini",
            on_errors=["timeout", "rate_limit"]
        ),
        FallbackTarget(
            provider="anthropic",
            model="claude-3-sonnet",
            on_errors=["*"]  # Catch all
        ),
        FallbackTarget(
            provider="ollama",
            model="llama3:8b",
            on_errors=["*"]
        )
    ]
)

LOADBALANCE_CONFIG = RoutingConfig(
    strategy="loadbalance",
    weights=[
        LoadBalanceTarget(
            provider="openai",
            model="gpt-4o-mini",
            weight=0.7  # 70% traffic
        ),
        LoadBalanceTarget(
            provider="anthropic",
            model="claude-3-sonnet",
            weight=0.3  # 30% traffic
        )
    ]
)
```

### 2.2 Router Implementation

```python
# src/gateway/routing/router.py
import random
import asyncio
from typing import AsyncIterator
import httpx

class ProviderRouter:
    """Intelligent routing with fallback & load balancing"""
    
    def __init__(self, config: RoutingConfig, providers: dict):
        self.config = config
        self.providers = providers  # {provider_name: ProviderAdapter}
    
    async def route_request(
        self, 
        request: ChatRequest
    ) -> ChatResponse:
        """Main routing logic"""
        
        if self.config.strategy == "single":
            return await self._single_provider(request)
        
        elif self.config.strategy == "fallback":
            return await self._fallback_chain(request)
        
        elif self.config.strategy == "loadbalance":
            return await self._load_balance(request)
    
    async def _single_provider(
        self, 
        request: ChatRequest
    ) -> ChatResponse:
        """Single provider with retries"""
        provider = self.providers[self.config.provider]
        
        return await self._execute_with_retry(
            provider, 
            request
        )
    
    async def _fallback_chain(
        self, 
        request: ChatRequest
    ) -> ChatResponse:
        """Try providers in order until success"""
        
        last_error = None
        
        for i, target in enumerate(self.config.targets):
            try:
                provider = self.providers[target.provider]
                
                # Update model in request
                modified_request = request.model_copy(
                    update={"model": target.model}
                )
                
                response = await self._execute_with_retry(
                    provider,
                    modified_request
                )
                
                # Add fallback metadata
                response.metadata = {
                    "fallback_used": i > 0,
                    "fallback_index": i,
                    "provider": target.provider
                }
                
                return response
                
            except Exception as e:
                last_error = e
                
                # Check if error matches fallback condition
                if self._should_fallback(e, target.on_errors):
                    continue
                else:
                    raise
        
        # All providers failed
        raise Exception(
            f"All fallback providers failed. Last error: {last_error}"
        )
    
    async def _load_balance(
        self, 
        request: ChatRequest
    ) -> ChatResponse:
        """Weighted random selection"""
        
        # Select provider based on weights
        weights = [t.weight for t in self.config.weights]
        target = random.choices(
            self.config.weights, 
            weights=weights
        )[0]
        
        provider = self.providers[target.provider]
        
        modified_request = request.model_copy(
            update={"model": target.model}
        )
        
        response = await self._execute_with_retry(
            provider,
            modified_request
        )
        
        response.metadata = {
            "loadbalance_provider": target.provider,
            "loadbalance_weight": target.weight
        }
        
        return response
    
    async def _execute_with_retry(
        self,
        provider: LLMProvider,
        request: ChatRequest
    ) -> ChatResponse:
        """Execute with exponential backoff retry"""
        
        retry_config = self.config.retry
        last_error = None
        
        for attempt in range(retry_config.attempts):
            try:
                response = await provider.chat_completion(request)
                return response
                
            except httpx.HTTPStatusError as e:
                last_error = e
                
                # Check if should retry
                if e.response.status_code not in retry_config.on_status_codes:
                    raise
                
                # Calculate backoff delay
                if retry_config.exponential_backoff:
                    delay = min(
                        retry_config.base_delay_ms * (2 ** attempt),
                        retry_config.max_delay_ms
                    ) / 1000.0  # Convert to seconds
                else:
                    delay = retry_config.base_delay_ms / 1000.0
                
                await asyncio.sleep(delay)
        
        raise Exception(
            f"Max retries ({retry_config.attempts}) exceeded: {last_error}"
        )
    
    def _should_fallback(
        self, 
        error: Exception, 
        on_errors: list[str]
    ) -> bool:
        """Check if error matches fallback conditions"""
        
        if "*" in on_errors:
            return True
        
        error_str = str(error).lower()
        
        for condition in on_errors:
            if condition.lower() in error_str:
                return True
        
        return False
```

**Key Insights**:
- **Declarative config**: Easy to test, version control
- **Exponential backoff**: Prevents thundering herd
- **Weighted load balancing**: Gradual rollout of new models

---

## FEATURE 3: SEMANTIC CACHING

### 3.1 Architecture (Portkey-inspired)

**Two-tier caching**:
1. **Simple cache**: Exact match (Redis hash)
2. **Semantic cache**: Embedding similarity (Vector DB)

```python
# src/gateway/caching/semantic_cache.py
from sentence_transformers import SentenceTransformer
import redis
import numpy as np
from typing import Optional
import hashlib
import json

class SemanticCache:
    """
    Semantic caching using embeddings
    
    Based on Portkey's approach:
    - Cosine similarity > threshold → cache hit
    - Only cache requests < 8k tokens
    - Only cache messages array length <= 4
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        embedding_model: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.95,
        ttl: int = 3600
    ):
        self.redis = redis_client
        self.model = SentenceTransformer(embedding_model)
        self.threshold = similarity_threshold
        self.ttl = ttl
    
    def _get_cache_key(self, request: ChatRequest) -> str:
        """Generate cache key from request"""
        
        # Portkey approach: Only cache user messages
        # System message is ignored for semantic matching
        user_messages = [
            msg.content 
            for msg in request.messages 
            if msg.role != "system"
        ]
        
        cache_text = " ".join(user_messages)
        cache_embedding = self.model.encode(cache_text)
        
        # Store embedding in Redis for similarity search
        return cache_text, cache_embedding
    
    async def get(
        self, 
        request: ChatRequest
    ) -> Optional[ChatResponse]:
        """Check cache for semantically similar request"""
        
        # Validate request
        if not self._is_cacheable(request):
            return None
        
        cache_text, query_embedding = self._get_cache_key(request)
        
        # Search Redis for similar queries
        # Format: cache:embeddings:{hash} → embedding vector
        #         cache:responses:{hash} → response JSON
        
        # Scan all cached embeddings
        keys = self.redis.keys("cache:embeddings:*")
        
        best_match = None
        best_similarity = 0.0
        
        for key in keys:
            # Get cached embedding
            cached_emb_bytes = self.redis.get(key)
            cached_embedding = np.frombuffer(
                cached_emb_bytes, 
                dtype=np.float32
            )
            
            # Compute cosine similarity
            similarity = self._cosine_similarity(
                query_embedding, 
                cached_embedding
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = key
        
        # Check threshold
        if best_similarity >= self.threshold:
            # Cache hit!
            hash_key = best_match.decode().split(":")[-1]
            response_key = f"cache:responses:{hash_key}"
            
            cached_response = self.redis.get(response_key)
            
            if cached_response:
                response = ChatResponse.model_validate_json(
                    cached_response
                )
                
                # Add cache metadata
                response.metadata = {
                    "cache_hit": True,
                    "cache_type": "semantic",
                    "similarity_score": best_similarity
                }
                
                return response
        
        return None
    
    async def set(
        self,
        request: ChatRequest,
        response: ChatResponse
    ):
        """Store response in cache"""
        
        if not self._is_cacheable(request):
            return
        
        cache_text, embedding = self._get_cache_key(request)
        
        # Generate hash
        hash_key = hashlib.sha256(cache_text.encode()).hexdigest()[:16]
        
        # Store embedding
        embedding_key = f"cache:embeddings:{hash_key}"
        self.redis.setex(
            embedding_key,
            self.ttl,
            embedding.tobytes()
        )
        
        # Store response
        response_key = f"cache:responses:{hash_key}"
        self.redis.setex(
            response_key,
            self.ttl,
            response.model_dump_json()
        )
    
    def _is_cacheable(self, request: ChatRequest) -> bool:
        """Check if request meets caching criteria"""
        
        # Portkey constraints
        if len(request.messages) > 4:
            return False
        
        # Estimate token count (rough approximation)
        total_text = " ".join([m.content for m in request.messages])
        estimated_tokens = len(total_text.split()) * 1.3
        
        if estimated_tokens > 8191:
            return False
        
        return True
    
    def _cosine_similarity(
        self, 
        a: np.ndarray, 
        b: np.ndarray
    ) -> float:
        """Compute cosine similarity"""
        return float(
            np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        )
```

### 3.2 Simple Cache (Fast Path)

```python
# src/gateway/caching/simple_cache.py
import hashlib
import json

class SimpleCache:
    """Exact match caching (fast path)"""
    
    def __init__(self, redis_client: redis.Redis, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl
    
    def _get_cache_key(self, request: ChatRequest) -> str:
        """Generate deterministic key"""
        
        # Serialize entire request
        request_json = request.model_dump_json(sort_keys=True)
        
        # Hash it
        return hashlib.sha256(request_json.encode()).hexdigest()
    
    async def get(
        self, 
        request: ChatRequest
    ) -> Optional[ChatResponse]:
        """Get exact match from cache"""
        
        key = f"cache:simple:{self._get_cache_key(request)}"
        
        cached = self.redis.get(key)
        
        if cached:
            response = ChatResponse.model_validate_json(cached)
            response.metadata = {
                "cache_hit": True,
                "cache_type": "simple"
            }
            return response
        
        return None
    
    async def set(
        self,
        request: ChatRequest,
        response: ChatResponse
    ):
        """Store response"""
        
        key = f"cache:simple:{self._get_cache_key(request)}"
        
        self.redis.setex(
            key,
            self.ttl,
            response.model_dump_json()
        )
```

### 3.3 Unified Cache Layer

```python
# src/gateway/caching/cache_manager.py

class CacheManager:
    """
    Unified cache with fallback strategy
    
    Strategy:
    1. Try simple cache (O(1) lookup)
    2. Try semantic cache (O(n) similarity search)
    3. Return None (cache miss)
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        mode: str = "semantic"
    ):
        self.simple_cache = SimpleCache(redis_client)
        self.semantic_cache = SemanticCache(redis_client)
        self.mode = mode
    
    async def get(
        self, 
        request: ChatRequest
    ) -> Optional[ChatResponse]:
        """Try caches in order"""
        
        # Always try simple first (fastest)
        response = await self.simple_cache.get(request)
        if response:
            return response
        
        # Try semantic if enabled
        if self.mode == "semantic":
            response = await self.semantic_cache.get(request)
            if response:
                return response
        
        return None
    
    async def set(
        self,
        request: ChatRequest,
        response: ChatResponse
    ):
        """Store in both caches"""
        
        await self.simple_cache.set(request, response)
        
        if self.mode == "semantic":
            await self.semantic_cache.set(request, response)
```

**Key Insights**:
- **Layered approach**: Fast simple cache + slower semantic cache
- **Portkey's 95% threshold**: Balance between cache hits and accuracy
- **Embedding model**: Lightweight (all-MiniLM-L6-v2) for speed

---

## FEATURE 4: GUARDRAILS SYSTEM

### 4.1 Plugin Architecture

**Pattern**: Extensible guardrail plugins (Portkey approach).

```python
# src/gateway/guardrails/base.py
from abc import ABC, abstractmethod
from typing import Literal

class GuardrailResult(BaseModel):
    """Result from guardrail check"""
    passed: bool
    violation_type: str | None = None
    details: dict = {}
    action: Literal["allow", "deny", "flag"] = "allow"

class Guardrail(ABC):
    """Base class for all guardrails"""
    
    @abstractmethod
    async def check_input(
        self, 
        request: ChatRequest
    ) -> GuardrailResult:
        """Validate request before sending to LLM"""
        pass
    
    @abstractmethod
    async def check_output(
        self, 
        response: ChatResponse
    ) -> GuardrailResult:
        """Validate LLM response before returning"""
        pass
```

### 4.2 PII Detection Guardrail

```python
# src/gateway/guardrails/pii_detector.py
import re

class PIIDetector(Guardrail):
    """
    Detect and redact PII (Vietnamese context)
    
    Patterns:
    - CMND/CCCD: 9-12 digits
    - Phone: 0xxxxxxxxx
    - Email: xxx@xxx.xxx
    - Credit card: 16 digits
    """
    
    PATTERNS = {
        "cmnd": r"\b\d{9,12}\b",
        "phone": r"\b0\d{9,10}\b",
        "email": r"\b[\w.-]+@[\w.-]+\.\w+\b",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
    }
    
    def __init__(self, action: str = "deny"):
        self.action = action  # "allow", "deny", "redact"
    
    async def check_input(
        self, 
        request: ChatRequest
    ) -> GuardrailResult:
        """Scan input for PII"""
        
        violations = []
        
        for msg in request.messages:
            for pii_type, pattern in self.PATTERNS.items():
                matches = re.findall(pattern, msg.content)
                
                if matches:
                    violations.append({
                        "type": pii_type,
                        "count": len(matches),
                        "samples": matches[:2]  # Don't log actual PII
                    })
        
        if violations:
            if self.action == "deny":
                return GuardrailResult(
                    passed=False,
                    violation_type="pii_detected",
                    details={"violations": violations},
                    action="deny"
                )
            
            elif self.action == "redact":
                # Redact PII from messages
                for msg in request.messages:
                    for pii_type, pattern in self.PATTERNS.items():
                        msg.content = re.sub(
                            pattern, 
                            f"[{pii_type.upper()}_REDACTED]", 
                            msg.content
                        )
                
                return GuardrailResult(
                    passed=True,
                    violation_type="pii_detected",
                    details={
                        "violations": violations,
                        "action": "redacted"
                    },
                    action="flag"
                )
        
        return GuardrailResult(passed=True)
    
    async def check_output(
        self, 
        response: ChatResponse
    ) -> GuardrailResult:
        """Scan output for leaked PII"""
        
        output_text = response.choices[0]["message"]["content"]
        
        violations = []
        
        for pii_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, output_text)
            
            if matches:
                violations.append({
                    "type": pii_type,
                    "count": len(matches)
                })
        
        if violations:
            return GuardrailResult(
                passed=False,
                violation_type="pii_in_output",
                details={"violations": violations},
                action="deny"
            )
        
        return GuardrailResult(passed=True)
```

### 4.3 Content Safety Guardrail

```python
# src/gateway/guardrails/content_safety.py

class ContentSafetyGuardrail(Guardrail):
    """
    Block toxic/harmful content
    
    Uses keyword lists + ML classifier (optional)
    """
    
    BLOCKED_KEYWORDS = [
        # Violence
        "kill", "murder", "bomb", "terrorist",
        
        # Hate speech (Vietnamese)
        "ngu", "đồ ngu", "khốn nạn",
        
        # NSFW
        # ... (add as needed)
    ]
    
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold
    
    async def check_input(
        self, 
        request: ChatRequest
    ) -> GuardrailResult:
        """Check input for harmful content"""
        
        input_text = " ".join([
            m.content for m in request.messages
        ]).lower()
        
        # Keyword check
        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in input_text:
                return GuardrailResult(
                    passed=False,
                    violation_type="blocked_keyword",
                    details={"keyword": keyword},
                    action="deny"
                )
        
        # Optional: ML-based toxicity detection
        # toxicity_score = await self._ml_classify(input_text)
        # if toxicity_score > self.threshold:
        #     return GuardrailResult(passed=False, ...)
        
        return GuardrailResult(passed=True)
    
    async def check_output(
        self, 
        response: ChatResponse
    ) -> GuardrailResult:
        """Validate model output"""
        
        output_text = response.choices[0]["message"]["content"].lower()
        
        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in output_text:
                return GuardrailResult(
                    passed=False,
                    violation_type="unsafe_output",
                    details={"keyword": keyword},
                    action="deny"
                )
        
        return GuardrailResult(passed=True)
```

### 4.4 Guardrail Manager

```python
# src/gateway/guardrails/manager.py

class GuardrailManager:
    """Orchestrate multiple guardrails"""
    
    def __init__(self, guardrails: list[Guardrail]):
        self.guardrails = guardrails
    
    async def check_input(
        self, 
        request: ChatRequest
    ) -> GuardrailResult:
        """Run all input guardrails"""
        
        for guardrail in self.guardrails:
            result = await guardrail.check_input(request)
            
            if not result.passed:
                return result
        
        return GuardrailResult(passed=True)
    
    async def check_output(
        self, 
        response: ChatResponse
    ) -> GuardrailResult:
        """Run all output guardrails"""
        
        for guardrail in self.guardrails:
            result = await guardrail.check_output(response)
            
            if not result.passed:
                return result
        
        return GuardrailResult(passed=True)
```

**Key Insights**:
- **Plugin system**: Easy to add new guardrails
- **Input + Output checks**: Protect both directions
- **Flexible actions**: deny, redact, flag

---

## FEATURE 5: COST TRACKING & BUDGET LIMITS

### 5.1 Token-Based Cost Calculation

```python
# src/gateway/cost/tracker.py
from datetime import datetime, timedelta
import redis

class CostTracker:
    """
    Track costs with budget limits
    
    Portkey approach:
    - Real-time cost calculation
    - Per-user budget limits
    - Daily/monthly aggregation
    """
    
    def __init__(self, redis_client: redis.Redis, postgres_conn):
        self.redis = redis_client
        self.db = postgres_conn
        
        # Pricing database (from Portkey's model catalog)
        self.pricing = self._load_pricing()
    
    def _load_pricing(self) -> dict:
        """
        Load pricing from database
        
        Format matches Portkey's pricing DB:
        https://github.com/Portkey-AI/models
        """
        return {
            "openai": {
                "gpt-4o-mini": {
                    "input": 0.00000015,   # $0.15 per 1M tokens
                    "output": 0.0000006    # $0.60 per 1M tokens
                },
                "gpt-4o": {
                    "input": 0.0000025,
                    "output": 0.00001
                }
            },
            "anthropic": {
                "claude-3-sonnet": {
                    "input": 0.000003,
                    "output": 0.000015
                },
                "claude-3-opus": {
                    "input": 0.000015,
                    "output": 0.000075
                }
            },
            "ollama": {
                "*": {  # Local models
                    "input": 0.0,
                    "output": 0.0
                }
            }
        }
    
    async def calculate_cost(
        self,
        provider: str,
        model: str,
        usage: dict
    ) -> float:
        """Calculate cost for this request"""
        
        model_pricing = self.pricing.get(provider, {}).get(model)
        
        if not model_pricing:
            # Unknown model, return 0
            return 0.0
        
        cost = (
            usage["prompt_tokens"] * model_pricing["input"] +
            usage["completion_tokens"] * model_pricing["output"]
        )
        
        return cost
    
    async def record_usage(
        self,
        user_id: str,
        provider: str,
        model: str,
        usage: dict,
        cost: float
    ):
        """Record usage in database"""
        
        # Store in PostgreSQL
        query = """
        INSERT INTO llm_usage_log (
            user_id, provider, model, 
            prompt_tokens, completion_tokens, cost,
            timestamp
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        await self.db.execute(
            query,
            user_id, provider, model,
            usage["prompt_tokens"],
            usage["completion_tokens"],
            cost,
            datetime.utcnow()
        )
        
        # Update Redis counters (for real-time budget)
        await self._update_redis_counters(user_id, cost)
    
    async def _update_redis_counters(self, user_id: str, cost: float):
        """Update real-time cost counters"""
        
        today = datetime.utcnow().date()
        month = today.strftime("%Y-%m")
        
        # Daily cost
        daily_key = f"cost:daily:{user_id}:{today}"
        self.redis.incrbyfloat(daily_key, cost)
        self.redis.expire(daily_key, 86400 * 2)  # 2 days TTL
        
        # Monthly cost
        monthly_key = f"cost:monthly:{user_id}:{month}"
        self.redis.incrbyfloat(monthly_key, cost)
        self.redis.expire(monthly_key, 86400 * 60)  # 60 days TTL
    
    async def check_budget(
        self,
        user_id: str,
        budget_limit_usd: float
    ) -> bool:
        """Check if user is within budget"""
        
        # Get monthly spending
        month = datetime.utcnow().strftime("%Y-%m")
        monthly_key = f"cost:monthly:{user_id}:{month}"
        
        spent = float(self.redis.get(monthly_key) or 0.0)
        
        if spent >= budget_limit_usd:
            return False
        
        return True
    
    async def get_cost_report(
        self,
        user_id: str,
        days: int = 30
    ) -> dict:
        """Generate cost report"""
        
        query = """
        SELECT 
            DATE(timestamp) as date,
            provider,
            model,
            SUM(prompt_tokens) as total_input_tokens,
            SUM(completion_tokens) as total_output_tokens,
            SUM(cost) as total_cost
        FROM llm_usage_log
        WHERE user_id = $1
          AND timestamp >= $2
        GROUP BY DATE(timestamp), provider, model
        ORDER BY date DESC
        """
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = await self.db.fetch(query, user_id, start_date)
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_cost_usd": sum(r["total_cost"] for r in results),
            "breakdown": [dict(r) for r in results]
        }
```

### 5.2 Budget Middleware

```python
# src/gateway/middleware/budget_check.py

class BudgetCheckMiddleware:
    """Enforce budget limits before routing"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.tracker = cost_tracker
    
    async def __call__(
        self,
        request: ChatRequest,
        user_id: str,
        budget_limit: float
    ) -> ChatResponse:
        """Check budget before processing"""
        
        # Check if user is within budget
        within_budget = await self.tracker.check_budget(
            user_id, 
            budget_limit
        )
        
        if not within_budget:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "budget_exceeded",
                    "message": f"Monthly budget limit ${budget_limit} exceeded"
                }
            )
        
        # Continue with request
        # (actual routing happens downstream)
        return None
```

**Key Insights**:
- **Dual storage**: Redis (real-time) + PostgreSQL (analytics)
- **Granular tracking**: Per-user, per-model, per-day
- **Proactive limits**: Block requests before hitting budget

---

## FEATURE 6: LOGGING & OBSERVABILITY

### 6.1 Structured Logging

**Pattern**: JSON logging with trace IDs (Portkey approach).

```python
# src/gateway/logging/structured_logger.py
import structlog
import uuid
from contextvars import ContextVar

# Context variable for request tracing
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

class RequestLogger:
    """Structure logger for all requests"""
    
    def __init__(self):
        self.logger = structlog.get_logger()
    
    async def log_request(
        self,
        request: ChatRequest,
        user_id: str,
        trace_id: str
    ):
        """Log incoming request"""
        
        # Set trace ID in context
        trace_id_var.set(trace_id)
        
        self.logger.info(
            "llm_request_received",
            trace_id=trace_id,
            user_id=user_id,
            model=request.model,
            message_count=len(request.messages),
            temperature=request.temperature,
            stream=request.stream
        )
    
    async def log_provider_call(
        self,
        provider: str,
        model: str,
        attempt: int,
        latency_ms: float
    ):
        """Log provider API call"""
        
        self.logger.info(
            "provider_call",
            trace_id=trace_id_var.get(),
            provider=provider,
            model=model,
            attempt=attempt,
            latency_ms=latency_ms
        )
    
    async def log_response(
        self,
        response: ChatResponse,
        provider: str,
        cost_usd: float,
        cache_hit: bool
    ):
        """Log response"""
        
        self.logger.info(
            "llm_response_sent",
            trace_id=trace_id_var.get(),
            provider=provider,
            model=response.model,
            tokens_input=response.usage["prompt_tokens"],
            tokens_output=response.usage["completion_tokens"],
            cost_usd=cost_usd,
            cache_hit=cache_hit
        )
    
    async def log_error(
        self,
        error: Exception,
        provider: str,
        attempt: int
    ):
        """Log errors"""
        
        self.logger.error(
            "llm_error",
            trace_id=trace_id_var.get(),
            provider=provider,
            attempt=attempt,
            error_type=type(error).__name__,
            error_message=str(error)
        )
```

### 6.2 Prometheus Metrics

```python
# src/gateway/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
llm_requests_total = Counter(
    "llm_requests_total",
    "Total LLM requests",
    ["provider", "model", "status"]
)

llm_request_duration = Histogram(
    "llm_request_duration_seconds",
    "Request latency",
    ["provider", "model"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Cost metrics
llm_cost_total = Counter(
    "llm_cost_total_usd",
    "Total cost in USD",
    ["provider", "model"]
)

llm_tokens_total = Counter(
    "llm_tokens_total",
    "Total tokens processed",
    ["provider", "model", "type"]  # type = "input" | "output"
)

# Cache metrics
cache_requests_total = Counter(
    "cache_requests_total",
    "Total cache lookups",
    ["cache_type", "result"]  # result = "hit" | "miss"
)

cache_hit_rate = Gauge(
    "cache_hit_rate",
    "Current cache hit rate"
)

# Guardrail metrics
guardrail_violations = Counter(
    "guardrail_violations_total",
    "Total guardrail violations",
    ["type", "action"]  # action = "deny" | "flag"
)

def record_request_metrics(
    provider: str,
    model: str,
    duration: float,
    status: str,
    tokens: dict,
    cost: float,
    cache_hit: bool
):
    """Record all metrics for a request"""
    
    # Request counter
    llm_requests_total.labels(
        provider=provider,
        model=model,
        status=status
    ).inc()
    
    # Latency histogram
    llm_request_duration.labels(
        provider=provider,
        model=model
    ).observe(duration)
    
    # Cost counter
    llm_cost_total.labels(
        provider=provider,
        model=model
    ).inc(cost)
    
    # Token counters
    llm_tokens_total.labels(
        provider=provider,
        model=model,
        type="input"
    ).inc(tokens["prompt_tokens"])
    
    llm_tokens_total.labels(
        provider=provider,
        model=model,
        type="output"
    ).inc(tokens["completion_tokens"])
    
    # Cache metrics
    if cache_hit:
        cache_requests_total.labels(
            cache_type="semantic",
            result="hit"
        ).inc()
    else:
        cache_requests_total.labels(
            cache_type="semantic",
            result="miss"
        ).inc()
```

**Key Insights**:
- **Trace IDs**: Link all logs for a single request
- **Structured JSON**: Easy to parse, query in ELK
- **Standard metrics**: Prometheus/Grafana compatible

---

## FEATURE 7: VIRTUAL KEY MANAGEMENT

### 7.1 Virtual Key System

**Concept**: Abstract layer over real API keys.

```python
# src/gateway/auth/virtual_keys.py
import secrets
from datetime import datetime, timedelta

class VirtualKey(BaseModel):
    """Virtual API key"""
    virtual_key: str
    user_id: str
    name: str
    provider: str
    real_api_key: str  # Encrypted
    created_at: datetime
    expires_at: datetime | None = None
    rate_limit: int = 100  # requests per minute
    budget_limit_usd: float | None = None
    is_active: bool = True

class VirtualKeyManager:
    """Manage virtual keys"""
    
    def __init__(self, db_conn, encryption_key: bytes):
        self.db = db_conn
        self.cipher = Fernet(encryption_key)
    
    async def create_virtual_key(
        self,
        user_id: str,
        name: str,
        provider: str,
        real_api_key: str,
        **kwargs
    ) -> VirtualKey:
        """Create new virtual key"""
        
        # Generate virtual key
        virtual_key = f"vk-{secrets.token_urlsafe(32)}"
        
        # Encrypt real API key
        encrypted_key = self.cipher.encrypt(
            real_api_key.encode()
        ).decode()
        
        # Store in database
        query = """
        INSERT INTO virtual_keys (
            virtual_key, user_id, name, provider,
            encrypted_api_key, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6)
        """
        
        await self.db.execute(
            query,
            virtual_key, user_id, name, provider,
            encrypted_key, datetime.utcnow()
        )
        
        return VirtualKey(
            virtual_key=virtual_key,
            user_id=user_id,
            name=name,
            provider=provider,
            real_api_key=real_api_key,
            created_at=datetime.utcnow(),
            **kwargs
        )
    
    async def get_real_key(
        self, 
        virtual_key: str
    ) -> tuple[str, str]:
        """Decrypt and return real API key"""
        
        query = """
        SELECT provider, encrypted_api_key
        FROM virtual_keys
        WHERE virtual_key = $1 AND is_active = true
        """
        
        result = await self.db.fetchrow(query, virtual_key)
        
        if not result:
            raise ValueError("Invalid virtual key")
        
        # Decrypt
        real_key = self.cipher.decrypt(
            result["encrypted_api_key"].encode()
        ).decode()
        
        return result["provider"], real_key
    
    async def rotate_key(
        self,
        virtual_key: str,
        new_real_key: str
    ):
        """Rotate underlying API key"""
        
        encrypted_key = self.cipher.encrypt(
            new_real_key.encode()
        ).decode()
        
        query = """
        UPDATE virtual_keys
        SET encrypted_api_key = $1,
            updated_at = $2
        WHERE virtual_key = $3
        """
        
        await self.db.execute(
            query,
            encrypted_key,
            datetime.utcnow(),
            virtual_key
        )
    
    async def revoke_key(self, virtual_key: str):
        """Revoke virtual key"""
        
        query = """
        UPDATE virtual_keys
        SET is_active = false,
            revoked_at = $1
        WHERE virtual_key = $2
        """
        
        await self.db.execute(
            query,
            datetime.utcnow(),
            virtual_key
        )
```

**Key Insights**:
- **Separation of concerns**: Virtual keys != real API keys
- **Easy rotation**: Change real key without client changes
- **Granular control**: Per-key rate limits, budgets

---

## INTEGRATION EXAMPLE: COMPLETE GATEWAY

### Main Gateway Service

```python
# src/gateway/main.py
from fastapi import FastAPI, HTTPException, Header
import time
import uuid

app = FastAPI(title="Enterprise LLM Gateway")

# Initialize components
redis_client = redis.from_url("redis://localhost:6379")
db_pool = await asyncpg.create_pool("postgresql://...")

# Core modules
cache_manager = CacheManager(redis_client, mode="semantic")
cost_tracker = CostTracker(redis_client, db_pool)
request_logger = RequestLogger()

# Providers
providers = {
    "openai": OpenAIAdapter(api_key=os.getenv("OPENAI_API_KEY")),
    "anthropic": AnthropicAdapter(api_key=os.getenv("ANTHROPIC_API_KEY")),
    "ollama": OllamaAdapter(base_url="http://localhost:11434")
}

# Guardrails
guardrail_manager = GuardrailManager([
    PIIDetector(action="redact"),
    ContentSafetyGuardrail()
])

# Virtual keys
virtual_key_manager = VirtualKeyManager(
    db_pool, 
    encryption_key=os.getenv("ENCRYPTION_KEY").encode()
)

@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatRequest,
    authorization: str = Header(...),
    x_portkey_config: str = Header(None)
):
    """
    Main endpoint - OpenAI-compatible
    
    Headers:
    - Authorization: Bearer vk-xxxxx (virtual key)
    - x-portkey-config: JSON routing config (optional)
    """
    
    # Generate trace ID
    trace_id = str(uuid.uuid4())
    
    start_time = time.time()
    
    try:
        # 1. Authenticate
        virtual_key = authorization.replace("Bearer ", "")
        provider_name, real_key = await virtual_key_manager.get_real_key(
            virtual_key
        )
        
        # 2. Parse config
        if x_portkey_config:
            config = RoutingConfig.model_validate_json(x_portkey_config)
        else:
            # Default config
            config = RoutingConfig(
                strategy="single",
                provider=provider_name,
                model=request.model
            )
        
        # 3. Log request
        await request_logger.log_request(
            request, 
            virtual_key, 
            trace_id
        )
        
        # 4. Check guardrails (input)
        guardrail_result = await guardrail_manager.check_input(request)
        if not guardrail_result.passed:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "guardrail_violation",
                    "type": guardrail_result.violation_type,
                    "details": guardrail_result.details
                }
            )
        
        # 5. Check cache
        cached_response = await cache_manager.get(request)
        if cached_response:
            # Cache hit!
            return cached_response
        
        # 6. Route request
        router = ProviderRouter(config, providers)
        response = await router.route_request(request)
        
        # 7. Check guardrails (output)
        output_result = await guardrail_manager.check_output(response)
        if not output_result.passed:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "output_violation",
                    "type": output_result.violation_type
                }
            )
        
        # 8. Store in cache
        await cache_manager.set(request, response)
        
        # 9. Track cost
        cost = await cost_tracker.calculate_cost(
            provider_name,
            request.model,
            response.usage
        )
        
        await cost_tracker.record_usage(
            virtual_key,
            provider_name,
            request.model,
            response.usage,
            cost
        )
        
        # 10. Log response
        duration = time.time() - start_time
        
        await request_logger.log_response(
            response,
            provider_name,
            cost,
            cache_hit=False
        )
        
        # 11. Record metrics
        record_request_metrics(
            provider_name,
            request.model,
            duration,
            "success",
            response.usage,
            cost,
            cache_hit=False
        )
        
        return response
        
    except Exception as e:
        # Error handling
        await request_logger.log_error(e, provider_name, 0)
        
        record_request_metrics(
            provider_name,
            request.model,
            time.time() - start_time,
            "error",
            {"prompt_tokens": 0, "completion_tokens": 0},
            0.0,
            cache_hit=False
        )
        
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics"""
    from prometheus_client import generate_latest
    return Response(
        generate_latest(),
        media_type="text/plain"
    )
```

---

## DEPLOYMENT BEST PRACTICES

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY src/ ./src/

# Expose ports
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "src.gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: "3.8"

services:
  gateway:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/gateway
    depends_on:
      - redis
      - postgres
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=gateway
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  postgres_data:
```

### Environment Configuration

```bash
# .env
OPENAI_API_KEY=sk-xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx

REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost:5432/gateway

ENCRYPTION_KEY=xxxxx  # For virtual keys

# Optional
OLLAMA_URL=http://localhost:11434
GROQ_API_KEY=gsk_xxxxx
```

---

## TESTING STRATEGY

### Unit Tests

```python
# tests/test_semantic_cache.py
import pytest

@pytest.mark.asyncio
async def test_semantic_cache_hit():
    """Test semantic cache with similar queries"""
    
    cache = SemanticCache(redis_client)
    
    # Store original
    request1 = ChatRequest(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "What is the capital of France?"}
        ]
    )
    
    response1 = ChatResponse(
        id="test-1",
        created=123,
        model="gpt-4o-mini",
        choices=[{
            "message": {"content": "Paris"}
        }],
        usage={"prompt_tokens": 10, "completion_tokens": 5}
    )
    
    await cache.set(request1, response1)
    
    # Query with similar text
    request2 = ChatRequest(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "What's the capital city of France?"}
        ]
    )
    
    cached = await cache.get(request2)
    
    assert cached is not None
    assert cached.choices[0]["message"]["content"] == "Paris"
    assert cached.metadata["cache_hit"] == True
    assert cached.metadata["similarity_score"] > 0.95
```

### Integration Tests

```python
# tests/test_fallback.py
@pytest.mark.asyncio
async def test_fallback_on_error():
    """Test fallback to secondary provider"""
    
    # Mock primary provider to fail
    with patch.object(
        providers["openai"], 
        "chat_completion",
        side_effect=httpx.HTTPStatusError(
            "Rate limit", 
            request=None, 
            response=Mock(status_code=429)
        )
    ):
        config = RoutingConfig(
            strategy="fallback",
            targets=[
                FallbackTarget(provider="openai", model="gpt-4o-mini"),
                FallbackTarget(provider="anthropic", model="claude-3-sonnet")
            ]
        )
        
        router = ProviderRouter(config, providers)
        
        response = await router.route_request(request)
        
        # Should have used Claude
        assert response.metadata["fallback_used"] == True
        assert response.metadata["provider"] == "anthropic"
```

---

## PERFORMANCE OPTIMIZATION

### Key Metrics from Portkey

Based on Portkey's production experience:

```python
PERFORMANCE_TARGETS = {
    "p50_latency_ms": 500,     # 50th percentile
    "p95_latency_ms": 2000,    # 95th percentile
    "p99_latency_ms": 5000,    # 99th percentile
    
    "cache_hit_rate": 0.20,    # 20% (Q&A workloads)
    "cache_accuracy": 0.99,    # 99% correct responses
    
    "cost_reduction": 0.30,    # 30% via caching + routing
    
    "availability": 0.999      # 99.9% uptime
}
```

### Optimization Techniques

1. **Connection Pooling**
```python
# Use httpx.AsyncClient with connection pooling
async_client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20
    ),
    timeout=httpx.Timeout(60.0)
)
```

2. **Async Everywhere**
```python
# All I/O operations should be async
async def call_provider(request):
    async with httpx.AsyncClient() as client:
        response = await client.post(...)
    return response
```

3. **Redis Pipeline**
```python
# Batch Redis operations
async with redis.pipeline() as pipe:
    pipe.get("key1")
    pipe.get("key2")
    results = await pipe.execute()
```

---

## SECURITY CHECKLIST

- [ ] **API Keys**: Encrypted at rest, never logged
- [ ] **Virtual Keys**: Implement Fernet encryption
- [ ] **Rate Limiting**: Per-user, per-key limits
- [ ] **Input Validation**: Pydantic models, sanitization
- [ ] **PII Detection**: Scan inputs/outputs
- [ ] **HTTPS Only**: Force TLS in production
- [ ] **CORS**: Whitelist allowed origins
- [ ] **Audit Logs**: Log all access, changes
- [ ] **Budget Limits**: Enforce spending caps
- [ ] **Secrets Management**: Use environment vars, not hardcode

---

## MONITORING DASHBOARD (Grafana)

### Key Panels

```yaml
# Grafana dashboard config
dashboard:
  title: "LLM Gateway Monitoring"
  panels:
    - title: "Request Rate"
      metric: rate(llm_requests_total[5m])
      
    - title: "Latency (P95)"
      metric: histogram_quantile(0.95, llm_request_duration_seconds_bucket)
      
    - title: "Cost per Hour"
      metric: rate(llm_cost_total_usd[1h])
      
    - title: "Cache Hit Rate"
      metric: cache_hit_rate
      target: 0.20
      
    - title: "Error Rate"
      metric: rate(llm_requests_total{status="error"}[5m])
      alert_threshold: 0.01  # 1%
      
    - title: "Provider Distribution"
      metric: llm_requests_total
      groupby: provider
```

---

## TROUBLESHOOTING GUIDE

### Common Issues

**Issue**: Cache not working
```bash
# Check Redis connection
redis-cli ping

# Check cache keys
redis-cli keys "cache:*"

# Check embedding model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

**Issue**: High latency
```bash
# Check provider latency
curl -w "@curl-format.txt" https://api.openai.com/v1/...

# Check network
ping api.openai.com

# Check connection pool
# Increase max_connections in httpx.Limits
```

**Issue**: Fallback not triggering
```python
# Debug logs
import logging
logging.basicConfig(level=logging.DEBUG)

# Check error matching
print(config.targets[0].on_errors)
print(str(error))  # Should match
```

---

## MIGRATION FROM FR-04.3

### Step-by-Step Migration

```python
# Week 1: Add unified API layer
# - Create ChatRequest/ChatResponse models
# - Add OpenAI-compatible endpoint

# Week 2: Implement provider adapters
# - AnthropicAdapter
# - OllamaAdapter
# - Test with existing code

# Week 3: Add routing engine
# - ProviderRouter
# - Fallback logic
# - Retry with backoff

# Week 4: Semantic caching
# - SimpleCache (Redis)
# - SemanticCache (embeddings)
# - CacheManager integration

# Week 5: Guardrails
# - PIIDetector
# - ContentSafety
# - GuardrailManager

# Week 6: Cost tracking
# - Pricing database
# - CostTracker
# - Budget middleware

# Week 7: Virtual keys
# - VirtualKeyManager
# - Encryption setup
# - Migration tool

# Week 8: Observability
# - Structured logging
# - Prometheus metrics
# - Grafana dashboards

# Week 9: Testing
# - Unit tests (80%+ coverage)
# - Integration tests
# - Load testing

# Week 10: Deployment
# - Docker setup
# - Kubernetes manifests
# - Production rollout
```

---

## CONCLUSION

This skill provides a **production-grade LLM Gateway** implementation based on proven patterns from **Portkey AI Gateway**, which processes **billions of tokens daily** for **enterprise customers**.

### Key Takeaways

1. **Unified API**: OpenAI-compatible interface for all providers
2. **Smart Routing**: Fallback, retry, load balancing
3. **Semantic Caching**: 20-60% cost reduction
4. **Guardrails**: PII detection, content safety
5. **Cost Control**: Real-time tracking, budget limits
6. **Virtual Keys**: Security, rotation, revocation
7. **Observability**: Structured logs, metrics, tracing

### Next Steps

1. Read this skill thoroughly
2. Set up Docker development environment
3. Implement features incrementally (see migration plan)
4. Test with real workloads
5. Monitor metrics, optimize

**Remember**: Start simple, measure everything, optimize based on data.

---

## REFERENCES

- [Portkey Gateway GitHub](https://github.com/Portkey-AI/gateway)
- [Semantic Caching Blog](https://portkey.ai/blog/reducing-llm-costs-and-latency-semantic-cache/)
- [Portkey Model Pricing DB](https://github.com/Portkey-AI/models)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/deployment/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
