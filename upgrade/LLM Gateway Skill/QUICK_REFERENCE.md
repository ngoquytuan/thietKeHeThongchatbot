# Enterprise LLM Gateway - Quick Reference

## 🚀 TL;DR - Sử dụng ngay

### 1. Cài đặt & Chạy (5 phút)

```bash
# Clone repo (hoặc tạo mới)
git clone your-repo && cd llm-gateway

# Start services
docker-compose up -d

# Gateway running at: http://localhost:8000
```

### 2. First Request

```python
from openai import OpenAI

# Kết nối Gateway (giống OpenAI)
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="vk-your-virtual-key"
)

# Gọi bất kỳ model nào
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Xin chào!"}]
)

print(response.choices[0].message.content)
```

### 3. Routing Configs

```python
# FALLBACK: OpenAI → Claude → Local
config = {
    "strategy": "fallback",
    "targets": [
        {"provider": "openai", "model": "gpt-4o-mini"},
        {"provider": "anthropic", "model": "claude-3-sonnet"},
        {"provider": "ollama", "model": "llama3:8b"}
    ]
}

# LOAD BALANCE: 70% OpenAI, 30% Claude
config = {
    "strategy": "loadbalance",
    "weights": [
        {"provider": "openai", "model": "gpt-4o-mini", "weight": 0.7},
        {"provider": "anthropic", "model": "claude-3-sonnet", "weight": 0.3}
    ]
}

# Gửi config qua header
import json
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    extra_headers={
        "x-portkey-config": json.dumps(config)
    }
)
```

---

## 📚 Config Examples

### Example 1: Chi phí tối ưu với Fallback

**Mục tiêu**: Dùng model rẻ trước, chỉ dùng model đắt khi cần

```json
{
  "strategy": "fallback",
  "targets": [
    {
      "provider": "openai",
      "model": "gpt-4o-mini",
      "on_errors": ["timeout", "rate_limit"]
    },
    {
      "provider": "anthropic",
      "model": "claude-3-sonnet",
      "on_errors": ["timeout"]
    },
    {
      "provider": "ollama",
      "model": "llama3:8b",
      "on_errors": ["*"]
    }
  ],
  "retry": {
    "attempts": 3,
    "on_status_codes": [429, 500, 502, 503],
    "exponential_backoff": true
  },
  "cache": {
    "mode": "semantic",
    "ttl": 3600
  }
}
```

**Chi phí**:
- GPT-4o-mini: $0.15/1M input, $0.60/1M output
- Claude-3-Sonnet: $3/1M input, $15/1M output
- Llama3 (local): $0

**Tiết kiệm**: 50-70% nếu GPT-4o-mini handle được 80% requests

### Example 2: Load Balance để A/B Testing

**Mục tiêu**: Test model mới với 10% traffic

```json
{
  "strategy": "loadbalance",
  "weights": [
    {
      "provider": "openai",
      "model": "gpt-4o-mini",
      "weight": 0.9
    },
    {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "weight": 0.1
    }
  ]
}
```

**Use case**: Gradual rollout model mới

### Example 3: Semantic Cache cho Q&A

**Mục tiêu**: Giảm 30% chi phí cho hệ thống FAQ/Support

```json
{
  "strategy": "single",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "cache": {
    "mode": "semantic",
    "ttl": 86400
  }
}
```

**Ví dụ cache hits**:
```
Query 1: "Quy trình mua sắm tài sản là gì?"
→ LLM call ($0.0005)

Query 2: "Tôi muốn biết về quy định mua sắm"  
→ Cache hit (similarity 96%) - FREE, 20x faster

Query 3: "Làm sao để mua thiết bị văn phòng?"
→ Cache hit (similarity 92%) - FREE
```

### Example 4: Guardrails cho PII Protection

```python
# Python SDK
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="vk-xxx"
)

config = {
    "guardrails": {
        "input": [
            {
                "type": "pii_detection",
                "action": "redact"  # "deny" | "redact" | "flag"
            }
        ],
        "output": [
            {
                "type": "pii_detection",
                "action": "deny"
            },
            {
                "type": "content_safety",
                "threshold": 0.8
            }
        ]
    }
}

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": "Nhân viên Nguyễn Văn A, CMND 123456789"
    }],
    extra_headers={"x-portkey-config": json.dumps(config)}
)

# Request đã được redact thành:
# "Nhân viên [NAME_REDACTED], CMND [CMND_REDACTED]"
```

### Example 5: Budget Limits

```python
# Thiết lập budget limit cho user
async def set_user_budget(user_id: str, limit_usd: float):
    await db.execute("""
        INSERT INTO user_budgets (user_id, monthly_limit_usd)
        VALUES ($1, $2)
        ON CONFLICT (user_id) 
        DO UPDATE SET monthly_limit_usd = $2
    """, user_id, limit_usd)

# Middleware sẽ tự động reject requests khi vượt budget
# Response: HTTP 429 - "Monthly budget limit $500 exceeded"
```

---

## 🔧 API Endpoints

### POST /v1/chat/completions

**OpenAI-compatible endpoint**

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer vk-your-virtual-key" \
  -H "x-portkey-config: {...}" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

**Response**:
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gpt-4o-mini",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Xin chào! Tôi có thể giúp gì cho bạn?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  },
  "metadata": {
    "cache_hit": false,
    "provider": "openai",
    "cost_usd": 0.0000075
  }
}
```

### GET /health

```bash
curl http://localhost:8000/health

# Response
{"status": "healthy", "version": "1.0.0"}
```

### GET /metrics

```bash
curl http://localhost:8000/metrics

# Prometheus format
# HELP llm_requests_total Total LLM requests
# TYPE llm_requests_total counter
llm_requests_total{provider="openai",model="gpt-4o-mini",status="success"} 1234
...
```

### POST /admin/virtual-keys

**Create virtual key**

```bash
curl -X POST http://localhost:8000/admin/virtual-keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  -d '{
    "name": "Production Key",
    "provider": "openai",
    "real_api_key": "sk-xxxxx",
    "rate_limit": 100,
    "budget_limit_usd": 500
  }'

# Response
{
  "virtual_key": "vk-abc123xyz",
  "name": "Production Key",
  "provider": "openai",
  "rate_limit": 100,
  "budget_limit_usd": 500,
  "created_at": "2025-01-15T10:00:00Z"
}
```

---

## 📊 Monitoring & Debugging

### Check Cache Hit Rate

```bash
# Redis CLI
redis-cli

# Count simple cache keys
KEYS "cache:simple:*" | wc -l

# Count semantic cache keys
KEYS "cache:embeddings:*" | wc -l

# Get cache stats
INFO stats
```

### View Logs

```bash
# Docker logs (JSON structured)
docker-compose logs -f gateway | jq .

# Filter by trace_id
docker-compose logs gateway | jq 'select(.trace_id == "abc-123")'

# Filter errors only
docker-compose logs gateway | jq 'select(.level == "error")'
```

### Prometheus Queries

```promql
# Request rate (per second)
rate(llm_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(llm_request_duration_seconds_bucket[5m]))

# Cost per hour
rate(llm_cost_total_usd[1h])

# Cache hit rate
(
  rate(cache_requests_total{result="hit"}[5m]) /
  rate(cache_requests_total[5m])
) * 100

# Error rate
(
  rate(llm_requests_total{status="error"}[5m]) /
  rate(llm_requests_total[5m])
) * 100
```

### Grafana Dashboard Import

```json
{
  "dashboard": {
    "title": "LLM Gateway Overview",
    "panels": [
      {
        "title": "Requests/sec",
        "targets": [{
          "expr": "rate(llm_requests_total[5m])"
        }]
      },
      {
        "title": "Latency P95",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(llm_request_duration_seconds_bucket[5m]))"
        }]
      },
      {
        "title": "Cost Today",
        "targets": [{
          "expr": "increase(llm_cost_total_usd[24h])"
        }]
      },
      {
        "title": "Cache Hit %",
        "targets": [{
          "expr": "cache_hit_rate * 100"
        }]
      }
    ]
  }
}
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Gateway không start

```bash
# Check logs
docker-compose logs gateway

# Common fixes
docker-compose down
docker-compose up -d --build

# Check ports
lsof -i :8000
```

### Issue 2: Cache không hoạt động

```bash
# 1. Check Redis connection
docker-compose exec redis redis-cli ping
# Kết quả: PONG

# 2. Check if caching is enabled in config
# config.cache.mode = "semantic" (or "simple")

# 3. Check embedding model
docker-compose exec gateway python3 -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model loaded OK')
"
```

### Issue 3: Fallback không trigger

```python
# Debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

# Check config
config = {
    "strategy": "fallback",
    "targets": [
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "on_errors": ["timeout", "rate_limit", "429"]  # ← ADD status code
        }
    ]
}
```

### Issue 4: Cost tracking sai

```sql
-- Check PostgreSQL data
SELECT 
    provider,
    model,
    SUM(cost) as total_cost,
    SUM(prompt_tokens + completion_tokens) as total_tokens
FROM llm_usage_log
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY provider, model;

-- Verify pricing
SELECT * FROM pricing_config WHERE provider = 'openai';
```

---

## 🎯 Performance Tuning

### 1. Optimize Connection Pool

```python
# src/gateway/main.py
async_client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=200,      # Increase from default 100
        max_keepalive_connections=50  # Keep alive for reuse
    ),
    timeout=httpx.Timeout(
        connect=5.0,
        read=60.0,
        write=5.0,
        pool=5.0
    )
)
```

### 2. Redis Pipelining

```python
# Batch operations
async with redis.pipeline() as pipe:
    pipe.get("key1")
    pipe.get("key2")
    pipe.get("key3")
    results = await pipe.execute()
```

### 3. Database Indexing

```sql
-- Add indexes for common queries
CREATE INDEX idx_usage_user_date ON llm_usage_log(user_id, timestamp DESC);
CREATE INDEX idx_usage_provider ON llm_usage_log(provider, model);
CREATE INDEX idx_virtual_keys_active ON virtual_keys(virtual_key) WHERE is_active = true;
```

### 4. Semantic Cache Optimization

```python
# Tune similarity threshold
semantic_cache = SemanticCache(
    redis_client,
    threshold=0.92,  # Lower = more hits, less accuracy
                      # Higher = fewer hits, better accuracy
    # Portkey uses 0.95 (balance of 20% hits, 99% accuracy)
)

# Use smaller embedding model for speed
# all-MiniLM-L6-v2: 384 dims, 50MB
# vs all-mpnet-base-v2: 768 dims, 420MB
```

---

## 🔒 Security Hardening

### 1. HTTPS/TLS Only

```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl

# nginx.conf
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://gateway:8000;
    }
}
```

### 2. Rate Limiting

```python
# src/gateway/middleware/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/v1/chat/completions")
@limiter.limit("100/minute")
async def chat_completions(...):
    ...
```

### 3. API Key Rotation

```bash
# Rotate virtual key's underlying real key
curl -X PUT http://localhost:8000/admin/virtual-keys/vk-abc123/rotate \
  -H "Authorization: Bearer admin-token" \
  -d '{"new_api_key": "sk-new-key-xxxxx"}'

# No client changes needed!
```

---

## 💡 Pro Tips

1. **Start with Fallback strategy** - Most reliable
2. **Enable semantic cache for Q&A workloads** - 20-60% cost reduction
3. **Use local LLM as final fallback** - Zero cost, 100% availability
4. **Monitor cache hit rate daily** - Target >15% for Q&A
5. **Set budget alerts at 80%** - Prevent surprise overruns
6. **Rotate virtual keys monthly** - Security best practice
7. **Use separate virtual keys per environment** - Dev/Staging/Prod
8. **Test fallback logic regularly** - Simulate provider outages

---

## 📈 ROI Calculator

```python
# Monthly costs
baseline_cost = 1000  # requests/day × 30 days × $0.0005 = $15,000/month

# With Gateway optimizations
cache_savings = baseline_cost * 0.30      # 30% cache hit rate
routing_savings = baseline_cost * 0.10    # 10% cheaper via routing
local_fallback = baseline_cost * 0.05     # 5% handled by local LLM

total_savings = cache_savings + routing_savings + local_fallback
# = $4,500 + $1,500 + $750 = $6,750/month

infrastructure_cost = 500  # Redis + PostgreSQL + Compute

net_savings = total_savings - infrastructure_cost
# = $6,750 - $500 = $6,250/month

roi = net_savings / infrastructure_cost
# = 12.5x ROI
```

---

**Last Updated**: 2025-01-15  
**Version**: 1.0.0  
**Skill File**: `/mnt/skills/user/enterprise-llm-gateway/SKILL.md`
