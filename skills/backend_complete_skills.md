# Vietnamese RAG System - Backend Skills

## Table of Contents
1. [API Development (FR04.4)](#api-development-fr044)
2. [Authentication & Security (FR06)](#authentication--security-fr06)
3. [Monitoring & Analytics (FR07-08)](#monitoring--analytics-fr07-08)
4. [Testing Strategies](#testing-strategies)
5. [Deployment & Docker](#deployment--docker)

---

# API Development (FR04.4)

## FastAPI Architecture

```python
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Vietnamese RAG Knowledge Assistant API",
    description="API for Vietnamese document retrieval and Q&A",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(5, ge=1, le=20)
    filters: Optional[Dict] = None
    stream: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Thủ tục cấp giấy phép xây dựng?",
                "top_k": 5,
                "filters": {"document_type": "LEGAL_RND"},
                "stream": False
            }
        }

class Source(BaseModel):
    citation_number: int
    source_id: str
    title: Optional[str]
    document_id: Optional[str]
    relevance_score: float

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Source]
    metadata: Dict
    timestamp: str

# Dependency injection
def get_rag_pipeline():
    """Dependency to get RAG pipeline instance"""
    # Initialize once and reuse
    from rag_pipeline import RAGPipeline
    return RAGPipeline()

# API Endpoints
@app.post("/api/v1/query", response_model=QueryResponse)
async def query_knowledge_base(
    request: QueryRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Query the knowledge base
    """
    try:
        result = await pipeline.query(
            user_query=request.query,
            top_k=request.top_k,
            filters=request.filters,
            stream=False
        )
        
        # Format sources
        sources = [
            Source(
                citation_number=cite['number'],
                source_id=cite['source_id'],
                title=cite['metadata'].get('title'),
                document_id=cite['metadata'].get('document_id'),
                relevance_score=cite.get('score', 0.0)
            )
            for cite in result['citations']
        ]
        
        return QueryResponse(
            query=request.query,
            answer=result['response'],
            sources=sources,
            metadata=result['metadata'],
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )

@app.post("/api/v1/query/stream")
async def query_stream(
    request: QueryRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Query with streaming response
    """
    if not request.stream:
        raise HTTPException(
            status_code=400,
            detail="Stream parameter must be True"
        )
    
    async def generate():
        result = await pipeline.query(
            user_query=request.query,
            top_k=request.top_k,
            filters=request.filters,
            stream=True
        )
        
        # Stream response chunks
        for chunk in result['response']:
            yield f"data: {chunk}\n\n"
        
        # Send citations at the end
        import json
        citations_data = json.dumps(result['citations'])
        yield f"data: [CITATIONS]{citations_data}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@app.get("/api/v1/documents/{document_id}")
async def get_document(document_id: str):
    """
    Retrieve specific document
    """
    # Fetch from database
    doc = fetch_document_by_id(document_id)
    
    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found"
        )
    
    return doc

@app.get("/api/v1/documents")
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    document_type: Optional[str] = None
):
    """
    List documents with pagination
    """
    filters = {}
    if document_type:
        filters['document_type'] = document_type
    
    docs = fetch_documents(skip=skip, limit=limit, filters=filters)
    total = count_documents(filters)
    
    return {
        "documents": docs,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@app.post("/api/v1/feedback")
async def submit_feedback(
    query_id: str,
    rating: int = Field(..., ge=1, le=5),
    comment: Optional[str] = None
):
    """
    Submit user feedback
    """
    feedback = {
        "query_id": query_id,
        "rating": rating,
        "comment": comment,
        "timestamp": datetime.utcnow()
    }
    
    save_feedback(feedback)
    
    return {"status": "success", "message": "Feedback recorded"}

@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/query")
@limiter.limit("10/minute")  # 10 requests per minute
async def rate_limited_query(request: Request, ...):
    # Implementation
    pass
```

## API Versioning

```python
from fastapi import APIRouter

# V1 Router
v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

@v1_router.post("/query")
async def query_v1(...):
    # V1 implementation
    pass

# V2 Router (with improvements)
v2_router = APIRouter(prefix="/api/v2", tags=["v2"])

@v2_router.post("/query")
async def query_v2(...):
    # V2 implementation with new features
    pass

# Register routers
app.include_router(v1_router)
app.include_router(v2_router)
```

## Error Handling

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class APIException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

# Usage
if not query:
    raise APIException(400, "Query cannot be empty")
```

---

# Authentication & Security (FR06)

## JWT Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# User model
class User(BaseModel):
    username: str
    email: str
    role: str  # "guest", "employee", "manager", "director"
    permissions: List[str]

# Token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    # Fetch user from database
    user = get_user_by_id(payload.get("user_id"))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return User(**user)

# Login endpoint
@app.post("/api/v1/auth/login")
async def login(username: str, password: str):
    """
    Authenticate user and return JWT token
    """
    user = authenticate_user(username, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(
        data={
            "user_id": user['id'],
            "username": user['username'],
            "role": user['role']
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# Protected endpoint
@app.post("/api/v1/query")
async def protected_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    # User is authenticated
    # Apply role-based filtering
    if current_user.role == "guest":
        request.filters = {"access_level": "public"}
    
    return await query_knowledge_base(request)
```

## Role-Based Access Control (RBAC)

```python
from enum import Enum
from functools import wraps

class Role(str, Enum):
    GUEST = "guest"
    EMPLOYEE = "employee"
    MANAGER = "manager"
    DIRECTOR = "director"

# Role hierarchy: Director > Manager > Employee > Guest
ROLE_HIERARCHY = {
    Role.DIRECTOR: 4,
    Role.MANAGER: 3,
    Role.EMPLOYEE: 2,
    Role.GUEST: 1
}

def require_role(minimum_role: Role):
    """
    Decorator to enforce role-based access
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User, **kwargs):
            user_role_level = ROLE_HIERARCHY.get(current_user.role, 0)
            required_level = ROLE_HIERARCHY.get(minimum_role, 0)
            
            if user_role_level < required_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage
@app.delete("/api/v1/documents/{document_id}")
@require_role(Role.MANAGER)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    # Only managers and directors can delete
    delete_document_by_id(document_id)
    return {"status": "deleted"}
```

## Document-Level Permissions

```python
def check_document_access(user: User, document: Dict) -> bool:
    """
    Check if user has access to document
    """
    doc_access_level = document.get('access_level', 'public')
    
    # Public documents: all roles
    if doc_access_level == 'public':
        return True
    
    # Internal documents: employee and above
    if doc_access_level == 'internal':
        return ROLE_HIERARCHY[user.role] >= ROLE_HIERARCHY[Role.EMPLOYEE]
    
    # Confidential: manager and above
    if doc_access_level == 'confidential':
        return ROLE_HIERARCHY[user.role] >= ROLE_HIERARCHY[Role.MANAGER]
    
    # Restricted: director only
    if doc_access_level == 'restricted':
        return user.role == Role.DIRECTOR
    
    return False

# Filter search results by access
def filter_by_access(
    documents: List[Dict], 
    user: User
) -> List[Dict]:
    """
    Filter documents based on user access rights
    """
    return [
        doc for doc in documents 
        if check_document_access(user, doc)
    ]
```

## API Key Management

```python
import secrets

class APIKey(BaseModel):
    key: str
    user_id: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

def generate_api_key() -> str:
    """Generate secure API key"""
    return f"sk_{secrets.token_urlsafe(32)}"

@app.post("/api/v1/auth/api-keys")
async def create_api_key(
    name: str,
    expires_in_days: int = 90,
    current_user: User = Depends(get_current_user)
):
    """
    Create API key for programmatic access
    """
    api_key = generate_api_key()
    
    # Store in database
    key_data = {
        "key": hash_api_key(api_key),  # Store hashed
        "user_id": current_user.id,
        "name": name,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=expires_in_days),
        "is_active": True
    }
    
    save_api_key(key_data)
    
    # Return plain key (only shown once)
    return {
        "api_key": api_key,
        "message": "Save this key securely. It won't be shown again."
    }
```

---

# Monitoring & Analytics (FR07-08)

## Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Define metrics
query_total = Counter(
    'rag_queries_total',
    'Total number of queries',
    ['status', 'user_role']
)

query_duration = Histogram(
    'rag_query_duration_seconds',
    'Query processing time',
    ['stage']
)

active_users = Gauge(
    'rag_active_users',
    'Number of active users'
)

retrieval_accuracy = Gauge(
    'rag_retrieval_accuracy',
    'Retrieval accuracy score'
)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    """
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

# Usage in code
@app.post("/api/v1/query")
async def query_with_metrics(...):
    with query_duration.labels(stage='total').time():
        try:
            # Retrieval
            with query_duration.labels(stage='retrieval').time():
                docs = retriever.retrieve(query)
            
            # Generation
            with query_duration.labels(stage='generation').time():
                response = generator.generate(query, context)
            
            query_total.labels(status='success', user_role=user.role).inc()
            
            return response
        
        except Exception as e:
            query_total.labels(status='error', user_role=user.role).inc()
            raise
```

## Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName
        }
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        if hasattr(record, 'query'):
            log_data['query'] = record.query
        
        return json.dumps(log_data)

# Setup logger
logger = logging.getLogger("rag_system")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
logger.info(
    "Query processed",
    extra={
        "user_id": user.id,
        "query": query_text,
        "num_results": len(results),
        "duration_ms": duration * 1000
    }
)
```

## Analytics Dashboard Data

```python
from datetime import datetime, timedelta

class AnalyticsService:
    """
    Service for generating analytics data
    """
    
    def get_usage_stats(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict:
        """
        Get usage statistics for time period
        """
        conn = get_db_connection()
        
        with conn.cursor() as cur:
            # Total queries
            cur.execute("""
                SELECT COUNT(*) as total_queries,
                       COUNT(DISTINCT user_id) as unique_users,
                       AVG(response_time_ms) as avg_response_time
                FROM query_logs
                WHERE timestamp BETWEEN %s AND %s
            """, (start_date, end_date))
            
            stats = cur.fetchone()
            
            # Queries by day
            cur.execute("""
                SELECT DATE(timestamp) as date,
                       COUNT(*) as count
                FROM query_logs
                WHERE timestamp BETWEEN %s AND %s
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (start_date, end_date))
            
            daily_queries = cur.fetchall()
            
            # Top queries
            cur.execute("""
                SELECT query_text, COUNT(*) as count
                FROM query_logs
                WHERE timestamp BETWEEN %s AND %s
                GROUP BY query_text
                ORDER BY count DESC
                LIMIT 10
            """, (start_date, end_date))
            
            top_queries = cur.fetchall()
        
        conn.close()
        
        return {
            "total_queries": stats[0],
            "unique_users": stats[1],
            "avg_response_time_ms": stats[2],
            "daily_queries": daily_queries,
            "top_queries": top_queries
        }
    
    def get_quality_metrics(self) -> Dict:
        """
        Get quality metrics from user feedback
        """
        conn = get_db_connection()
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT AVG(rating) as avg_rating,
                       COUNT(*) as total_feedback
                FROM user_feedback
                WHERE created_at > NOW() - INTERVAL '30 days'
            """)
            
            result = cur.fetchone()
        
        conn.close()
        
        return {
            "avg_rating": result[0],
            "total_feedback": result[1]
        }

# API endpoint
@app.get("/api/v1/analytics/usage")
async def get_usage_analytics(
    start_date: str,
    end_date: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get usage analytics (managers and above)
    """
    if ROLE_HIERARCHY[current_user.role] < ROLE_HIERARCHY[Role.MANAGER]:
        raise HTTPException(403, "Insufficient permissions")
    
    analytics = AnalyticsService()
    
    stats = analytics.get_usage_stats(
        start_date=datetime.fromisoformat(start_date),
        end_date=datetime.fromisoformat(end_date)
    )
    
    return stats
```

## Grafana Dashboard (JSON)

```json
{
  "dashboard": {
    "title": "RAG System Monitoring",
    "panels": [
      {
        "title": "Queries per Second",
        "targets": [
          {
            "expr": "rate(rag_queries_total[5m])"
          }
        ]
      },
      {
        "title": "Average Response Time",
        "targets": [
          {
            "expr": "avg(rag_query_duration_seconds{stage='total'})"
          }
        ]
      },
      {
        "title": "Active Users",
        "targets": [
          {
            "expr": "rag_active_users"
          }
        ]
      }
    ]
  }
}
```

---

# Testing Strategies

## Unit Testing

```python
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

def test_query_endpoint():
    """Test basic query endpoint"""
    response = client.post(
        "/api/v1/query",
        json={
            "query": "Thủ tục xin giấy phép?",
            "top_k": 5
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "answer" in data
    assert "sources" in data
    assert len(data["sources"]) <= 5

def test_authentication():
    """Test authentication requirement"""
    response = client.post(
        "/api/v1/query",
        json={"query": "test"}
    )
    
    assert response.status_code == 401

def test_rate_limiting():
    """Test rate limiting"""
    # Send 11 requests (limit is 10)
    for i in range(11):
        response = client.post("/api/v1/query", json={"query": f"test {i}"})
    
    assert response.status_code == 429  # Too Many Requests
```

## Integration Testing

```python
@pytest.mark.integration
def test_end_to_end_query():
    """Test complete query pipeline"""
    # 1. Authenticate
    auth_response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_user", "password": "test_pass"}
    )
    token = auth_response.json()["access_token"]
    
    # 2. Query
    query_response = client.post(
        "/api/v1/query",
        json={"query": "Nghị định số 123/NĐ-CP", "top_k": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert query_response.status_code == 200
    data = query_response.json()
    
    # 3. Verify sources
    assert len(data["sources"]) > 0
    
    # 4. Verify citation format
    for source in data["sources"]:
        assert "citation_number" in source
        assert "source_id" in source

@pytest.mark.integration
def test_document_access_control():
    """Test role-based document access"""
    # Guest user
    guest_token = get_token_for_role("guest")
    
    response = client.get(
        "/api/v1/documents/confidential_doc_123",
        headers={"Authorization": f"Bearer {guest_token}"}
    )
    
    assert response.status_code == 403
    
    # Manager user
    manager_token = get_token_for_role("manager")
    
    response = client.get(
        "/api/v1/documents/confidential_doc_123",
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    
    assert response.status_code == 200
```

## Load Testing

```python
# Using Locust
from locust import HttpUser, task, between

class RAGUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get token"""
        response = self.client.post(
            "/api/v1/auth/login",
            json={"username": "load_test", "password": "password"}
        )
        self.token = response.json()["access_token"]
    
    @task(3)
    def query_endpoint(self):
        """Simulate query requests (weight: 3)"""
        self.client.post(
            "/api/v1/query",
            json={"query": "Test query", "top_k": 5},
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def list_documents(self):
        """Simulate document listing (weight: 1)"""
        self.client.get(
            "/api/v1/documents?skip=0&limit=20",
            headers={"Authorization": f"Bearer {self.token}"}
        )

# Run: locust -f load_test.py --host=http://localhost:8000
```

---

# Deployment & Docker

## Dockerfile

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Docker Compose (Production)

```yaml
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: chatbotR4
      POSTGRES_USER: kb_admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kb_admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # ChromaDB
  chromadb:
    image: chromadb/chroma:latest
    environment:
      - CHROMA_SERVER_AUTH_CREDENTIALS_PROVIDER=chromadb.auth.token.TokenAuthCredentialsProvider
      - CHROMA_SERVER_AUTH_CREDENTIALS=${CHROMA_AUTH_TOKEN}
      - CHROMA_SERVER_AUTH_TOKEN_TRANSPORT_HEADER=X-Chroma-Token
    volumes:
      - chroma_data:/chroma/chroma
    ports:
      - "8001:8000"
    restart: unless-stopped

  # API Service
  api:
    build: .
    environment:
      - DATABASE_URL=postgresql://kb_admin:${POSTGRES_PASSWORD}@postgres:5432/chatbotR4
      - REDIS_URL=redis://redis:6379/0
      - CHROMA_URL=http://chromadb:8000
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      chromadb:
        condition: service_started
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G

  # Celery Worker
  worker:
    build: .
    command: celery -A tasks worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=postgresql://kb_admin:${POSTGRES_PASSWORD}@postgres:5432/chatbotR4
      - REDIS_URL=redis://redis:6379/0
      - CHROMA_URL=http://chromadb:8000
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    deploy:
      replicas: 2

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped

  # Grafana
  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    restart: unless-stopped

  # Nginx (Reverse Proxy)
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  chroma_data:
  prometheus_data:
  grafana_data:
```

## Nginx Configuration

```nginx
upstream api_backend {
    least_conn;
    server api:8000;
}

server {
    listen 80;
    server_name api.example.com;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /metrics {
        deny all;  # Only allow internal access
    }
}
```

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-api
  template:
    metadata:
      labels:
        app: rag-api
    spec:
      containers:
      - name: api
        image: rag-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: rag-api-service
spec:
  selector:
    app: rag-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Deployment Commands

```bash
# Build Docker image
docker build -t rag-api:latest .

# Run locally
docker-compose up -d

# View logs
docker-compose logs -f api

# Scale services
docker-compose up -d --scale api=3 --scale worker=2

# Backup database
docker exec postgres pg_dump -U kb_admin chatbotR4 > backup.sql

# Restore database
docker exec -i postgres psql -U kb_admin chatbotR4 < backup.sql

# Deploy to Kubernetes
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl describe pod rag-api-xxx

# View logs
kubectl logs -f rag-api-xxx

# Scale deployment
kubectl scale deployment rag-api --replicas=5
```

## CI/CD Pipeline (.gitlab-ci.yml)

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest tests/ -v --cov=src
  coverage: '/TOTAL.*\s+(\d+%)$/'

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main

deploy_staging:
  stage: deploy
  script:
    - kubectl set image deployment/rag-api api=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - kubectl rollout status deployment/rag-api
  environment:
    name: staging
  only:
    - main

deploy_production:
  stage: deploy
  script:
    - kubectl set image deployment/rag-api api=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - kubectl rollout status deployment/rag-api
  environment:
    name: production
  when: manual
  only:
    - main
```

## Quick Reference

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Run tests in Docker
docker-compose run --rm api pytest tests/

# Access PostgreSQL
docker exec -it postgres psql -U kb_admin -d chatbotR4

# Monitor logs (all services)
docker-compose logs -f

# Check service health
curl http://localhost:8000/api/v1/health

# View metrics
curl http://localhost:8000/metrics

# Access Grafana
open http://localhost:3000
```

## Success Criteria

- ✅ API response time < 200ms (95th percentile)
- ✅ Uptime > 99.9%
- ✅ Handles 100 concurrent requests
- ✅ Zero-downtime deployments
- ✅ Automated backups (daily)
- ✅ Comprehensive monitoring
- ✅ Security hardened (JWT, RBAC, HTTPS)
- ✅ Load balanced across 3+ instances

## End of Skill File
