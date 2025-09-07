Tôi sẽ giúp bạn tạo project structure hoàn chỉnh và setup database connections cho FR-02.2. Dựa trên thông tin handover từ FR-02.1, tôi sẽ tạo cấu trúc chuẩn cho FastAPI.

## 🏗️ **PROJECT STRUCTURE HOÀN CHỈNH**

```bash
# Tạo thư mục project chính
mkdir knowledge-assistant-api
cd knowledge-assistant-api

# Tạo cấu trúc thư mục
mkdir -p {
    app/{api/{endpoints,dependencies},core,models,schemas,crud,services,utils},
    tests/{unit,integration,performance},
    alembic/{versions},
    scripts/{deployment,testing,data},
    docs/{api,deployment},
    configs/{development,staging,production},
    logs,
    docker/{development,production},
    monitoring/{prometheus,grafana}
}

# Tạo các file cần thiết
touch {
    app/__init__.py,
    app/main.py,
    app/api/__init__.py,
    app/api/endpoints/__init__.py,
    app/core/__init__.py,
    app/models/__init__.py,
    app/schemas/__init__.py,
    app/crud/__init__.py,
    app/services/__init__.py,
    app/utils/__init__.py,
    tests/__init__.py,
    .env.example,
    .env.development,
    .gitignore,
    README.md,
    Dockerfile,
    docker-compose.yml,
    docker-compose.dev.yml,
    alembic.ini
}
```

### **Cấu trúc chi tiết:**

```
knowledge-assistant-api/
├── app/                              # Mã nguồn chính
│   ├── __init__.py
│   ├── main.py                       # FastAPI application entry point
│   ├── api/                          # API routes và endpoints
│   │   ├── __init__.py
│   │   ├── api_v1.py                # API router chính
│   │   ├── dependencies/             # API dependencies
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # Authentication dependencies
│   │   │   └── database.py          # Database session dependencies
│   │   └── endpoints/               # API endpoint handlers
│   │       ├── __init__.py
│   │       ├── auth.py              # Authentication endpoints
│   │       ├── documents.py         # Documents CRUD endpoints
│   │       ├── users.py             # Users management endpoints
│   │       ├── search.py            # Search endpoints
│   │       ├── access_control.py    # Access control endpoints
│   │       └── health.py            # Health check endpoints
│   ├── core/                        # Core configuration và utilities
│   │   ├── __init__.py
│   │   ├── config.py                # Application configuration
│   │   ├── security.py              # Security utilities
│   │   ├── logging.py               # Logging configuration
│   │   └── exceptions.py            # Custom exceptions
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py                  # Base model class
│   │   ├── document.py              # Document models
│   │   ├── user.py                  # User models
│   │   └── session.py               # Session models
│   ├── schemas/                     # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── document.py              # Document schemas
│   │   ├── user.py                  # User schemas
│   │   ├── search.py                # Search schemas
│   │   └── auth.py                  # Authentication schemas
│   ├── crud/                        # Database CRUD operations
│   │   ├── __init__.py
│   │   ├── base.py                  # Base CRUD class
│   │   ├── document.py              # Document CRUD operations
│   │   ├── user.py                  # User CRUD operations
│   │   └── session.py               # Session CRUD operations
│   ├── services/                    # Business logic services
│   │   ├── __init__.py
│   │   ├── document_service.py      # Document business logic
│   │   ├── search_service.py        # Search business logic
│   │   ├── embedding_service.py     # Embedding operations
│   │   ├── cache_service.py         # Redis cache service
│   │   └── auth_service.py          # Authentication service
│   └── utils/                       # Utility functions
│       ├── __init__.py
│       ├── vietnamese.py            # Vietnamese text processing
│       ├── embeddings.py            # Embedding utilities
│       └── validators.py            # Custom validators
├── tests/                           # Test files
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── performance/                 # Performance tests
├── alembic/                         # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── scripts/                         # Utility scripts
│   ├── deployment/
│   ├── testing/
│   └── data/
├── configs/                         # Environment configurations
├── docker/                          # Docker configurations
├── docs/                           # Documentation
├── monitoring/                      # Monitoring configs
└── logs/                           # Log files
```

## 🔧 **1. CORE CONFIGURATION SETUP**

### **app/core/config.py**
```python
"""
Core configuration cho FR-02.2 API Quản trị Thống nhất
Sử dụng thông tin database từ handover FR-02.1
"""
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, validator
import secrets
import os

class Settings(BaseSettings):
    """Application settings với thông tin từ FR-02.1 handover"""
    
    # ======================
    # API CONFIGURATION
    # ======================
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Knowledge Assistant API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FR-02.2 - API Quản trị Thống nhất"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # ======================
    # DATABASE CONFIGURATION (từ FR-02.1 handover)
    # ======================
    
    # PostgreSQL (Primary Database)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5433  # Port từ handover
    POSTGRES_USER: str = "kb_admin"  # Username từ handover
    POSTGRES_PASSWORD: str = "test_password_123"  # Password từ handover
    POSTGRES_DB: str = "knowledge_base_test"  # Database từ handover
    
    # PostgreSQL Connection URL
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # Async PostgreSQL URL
    @property 
    def ASYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # ======================
    # REDIS CONFIGURATION (từ FR-02.1 handover) 
    # ======================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6380  # Port từ handover
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None  # No password trong test env
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ======================
    # CHROMADB CONFIGURATION (từ FR-02.1 handover)
    # ======================
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001  # Port từ handover
    
    @property
    def CHROMA_URL(self) -> str:
        return f"http://{self.CHROMA_HOST}:{self.CHROMA_PORT}"
    
    # ======================
    # SECURITY CONFIGURATION
    # ======================
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # Frontend development
        "http://localhost:8080",  # Adminer từ handover
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # ======================
    # VIETNAMESE PROCESSING (theo quy tắc)
    # ======================
    DEFAULT_LANGUAGE: str = "vi"  # Vietnamese priority
    SUPPORTED_LANGUAGES: List[str] = ["vi", "en"]
    
    # Embedding settings
    EMBEDDING_MODEL: str = "Qwen/Qwen2.5-Embedding-0.6B"  # Theo quy tắc
    EMBEDDING_DIMENSION: int = 1536
    CHUNK_SIZE: int = 512  # Default theo quy tắc 
    CHUNK_OVERLAP: int = 50  # Default theo quy tắc
    
    # ======================
    # LOGGING & MONITORING
    # ======================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/api.log"
    
    # Performance settings
    MAX_CONNECTIONS_COUNT: int = 10
    MIN_CONNECTIONS_COUNT: int = 10
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # ======================
    # ENVIRONMENT DETECTION
    # ======================
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# ======================
# ENVIRONMENT-SPECIFIC SETTINGS
# ======================

class DevelopmentSettings(Settings):
    """Development environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
class StagingSettings(Settings):
    """Staging environment settings"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
class ProductionSettings(Settings):
    """Production environment settings"""
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    
    # Production database từ environment variables
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    
    # Production Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost") 
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

# ======================
# SETTINGS FACTORY
# ======================

def get_settings() -> Settings:
    """Factory function to get settings based on environment"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "staging":
        return StagingSettings()
    else:
        return DevelopmentSettings()

@lru_cache()
def get_cached_settings() -> Settings:
    """Cached settings instance"""
    return get_settings()

# Global settings instance
settings = get_cached_settings()
```

## 🗄️ **2. DATABASE CONNECTION SETUP**

### **app/core/database.py**
```python
"""
Database connection setup cho FR-02.2
Kết nối tới PostgreSQL, Redis, ChromaDB từ FR-02.1
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import redis.asyncio as redis
import chromadb
from chromadb.config import Settings as ChromaSettings
import asyncpg
import logging
from typing import Generator, AsyncGenerator
from .config import settings

# ======================
# LOGGING SETUP
# ======================
logger = logging.getLogger(__name__)

# ======================
# POSTGRESQL SETUP (từ FR-02.1 handover)
# ======================

# Sync engine for migrations
sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=settings.MAX_CONNECTIONS_COUNT,
    max_overflow=0,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Async engine for API operations
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=settings.MAX_CONNECTIONS_COUNT,
    max_overflow=0,
    echo=settings.DEBUG,
)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

# Base class cho ORM models
Base = declarative_base()

# Metadata cho reflection (sử dụng existing tables từ FR-02.1)
metadata = MetaData()

# ======================
# DATABASE DEPENDENCIES
# ======================

def get_db() -> Generator:
    """Dependency để get database session (sync)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency để get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# ======================
# REDIS SETUP (từ FR-02.1 handover)
# ======================

class RedisManager:
    """Redis connection manager"""
    
    def __init__(self):
        self.redis_client = None
    
    async def connect(self):
        """Kết nối tới Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Đóng kết nối Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
    
    async def get_client(self):
        """Get Redis client"""
        if not self.redis_client:
            await self.connect()
        return self.redis_client

# Global Redis manager instance
redis_manager = RedisManager()

async def get_redis():
    """Dependency để get Redis client"""
    return await redis_manager.get_client()

# ======================
# CHROMADB SETUP (từ FR-02.1 handover)
# ======================

class ChromaManager:
    """ChromaDB connection manager"""
    
    def __init__(self):
        self.client = None
        self.collections = {}
    
    def connect(self):
        """Kết nối tới ChromaDB"""
        try:
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=ChromaSettings(
                    chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
                    chroma_client_auth_credentials="your-token-here",  # Configure if needed
                )
            )
            
            # Test connection bằng cách list collections
            collections = self.client.list_collections()
            logger.info(f"✅ ChromaDB connection established. Collections: {[c.name for c in collections]}")
            
            # Load existing collections từ handover
            self._load_existing_collections()
            
        except Exception as e:
            logger.error(f"❌ ChromaDB connection failed: {e}")
            raise
    
    def _load_existing_collections(self):
        """Load các collections đã có từ FR-02.1"""
        try:
            # Collections từ handover document
            collection_names = ["knowledge_base_v1", "vietnamese_docs", "test_collection"]
            
            for name in collection_names:
                try:
                    collection = self.client.get_collection(name)
                    self.collections[name] = collection
                    logger.info(f"Loaded collection: {name}")
                except Exception as e:
                    logger.warning(f"Collection {name} not found: {e}")
                    
        except Exception as e:
            logger.error(f"Error loading collections: {e}")
    
    def get_collection(self, name: str):
        """Get collection by name"""
        if name not in self.collections:
            try:
                self.collections[name] = self.client.get_collection(name)
            except Exception as e:
                logger.error(f"Collection {name} not found: {e}")
                return None
        return self.collections[name]
    
    def disconnect(self):
        """Cleanup ChromaDB connection"""
        self.client = None
        self.collections = {}
        logger.info("ChromaDB connection closed")

# Global ChromaDB manager instance
chroma_manager = ChromaManager()

def get_chroma():
    """Dependency để get ChromaDB client"""
    if not chroma_manager.client:
        chroma_manager.connect()
    return chroma_manager.client

def get_chroma_collection(collection_name: str = "knowledge_base_v1"):
    """Dependency để get specific ChromaDB collection"""
    if not chroma_manager.client:
        chroma_manager.connect()
    return chroma_manager.get_collection(collection_name)

# ======================
# DATABASE HEALTH CHECKS
# ======================

async def check_postgres_health() -> bool:
    """Kiểm tra PostgreSQL connection"""
    try:
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        return False

async def check_redis_health() -> bool:
    """Kiểm tra Redis connection"""
    try:
        redis_client = await redis_manager.get_client()
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False

def check_chroma_health() -> bool:
    """Kiểm tra ChromaDB connection"""
    try:
        if not chroma_manager.client:
            chroma_manager.connect()
        chroma_manager.client.heartbeat()
        return True
    except Exception as e:
        logger.error(f"ChromaDB health check failed: {e}")
        return False

# ======================
# STARTUP/SHUTDOWN EVENTS
# ======================

async def connect_to_databases():
    """Kết nối tất cả databases khi startup"""
    logger.info("🔌 Connecting to databases...")
    
    # Test PostgreSQL
    if await check_postgres_health():
        logger.info("✅ PostgreSQL connected")
    else:
        raise Exception("❌ PostgreSQL connection failed")
    
    # Connect Redis
    await redis_manager.connect()
    
    # Connect ChromaDB
    chroma_manager.connect()
    
    logger.info("🎉 All database connections established!")

async def close_database_connections():
    """Đóng tất cả database connections khi shutdown"""
    logger.info("🔌 Closing database connections...")
    
    # Close async PostgreSQL engine
    await async_engine.dispose()
    
    # Close Redis
    await redis_manager.disconnect()
    
    # Close ChromaDB
    chroma_manager.disconnect()
    
    logger.info("👋 All database connections closed")
```

## 📝 **3. ENVIRONMENT CONFIGURATION**

### **.env.development**
```bash
# ======================
# FR-02.2 DEVELOPMENT ENVIRONMENT
# Based on FR-02.1 handover information
# ======================

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Knowledge Assistant API
VERSION=1.0.0
HOST=0.0.0.0
PORT=8000
DEBUG=true
ENVIRONMENT=development

# PostgreSQL (từ FR-02.1 handover)
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_USER=kb_admin
POSTGRES_PASSWORD=test_password_123
POSTGRES_DB=knowledge_base_test

# Redis (từ FR-02.1 handover)
REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_DB=0
REDIS_PASSWORD=

# ChromaDB (từ FR-02.1 handover)
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# CORS Origins
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Vietnamese Processing (theo quy tắc)
DEFAULT_LANGUAGE=vi
EMBEDDING_MODEL=Qwen/Qwen2.5-Embedding-0.6B
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=json
LOG_FILE=logs/api.log

# Performance
MAX_CONNECTIONS_COUNT=10
MIN_CONNECTIONS_COUNT=10
RATE_LIMIT_PER_MINUTE=100
```

### **.env.example**
```bash
# ======================
# ENVIRONMENT VARIABLES TEMPLATE
# Copy to .env.development, .env.staging, .env.production
# ======================

# Basic Configuration
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database Configuration (update with your values)
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_USER=kb_admin
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=knowledge_base_test

REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_DB=0
REDIS_PASSWORD=

CHROMA_HOST=localhost
CHROMA_PORT=8001

# Security (generate new secret key for production)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000

# Vietnamese Processing
DEFAULT_LANGUAGE=vi
EMBEDDING_MODEL=Qwen/Qwen2.5-Embedding-0.6B

# Logging
LOG_LEVEL=INFO
```

## 🧪 **4. DATABASE CONNECTION TEST**

### **scripts/test_connections.py**
```python
"""
Script để test tất cả database connections
Sử dụng thông tin từ FR-02.1 handover
"""
import asyncio
import sys
import os

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import (
    check_postgres_health,
    check_redis_health, 
    check_chroma_health,
    connect_to_databases,
    redis_manager,
    chroma_manager
)
from app.core.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_database_connections():
    """Test tất cả database connections từ FR-02.1"""
    
    logger.info("🧪 Testing database connections from FR-02.1...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    results = {}
    
    # Test PostgreSQL
    logger.info("📊 Testing PostgreSQL connection...")
    logger.info(f"Connection: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    results['postgresql'] = await check_postgres_health()
    
    if results['postgresql']:
        logger.info("✅ PostgreSQL: CONNECTED")
    else:
        logger.error("❌ PostgreSQL: FAILED")
    
    # Test Redis
    logger.info("🔴 Testing Redis connection...")
    logger.info(f"Connection: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    results['redis'] = await check_redis_health()
    
    if results['redis']:
        logger.info("✅ Redis: CONNECTED")
    else:
        logger.error("❌ Redis: FAILED")
    
    # Test ChromaDB
    logger.info("🟢 Testing ChromaDB connection...")
    logger.info(f"Connection: {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
    results['chromadb'] = check_chroma_health()
    
    if results['chromadb']:
        logger.info("✅ ChromaDB: CONNECTED")
        
        # List collections từ handover
        try:
            collections = chroma_manager.client.list_collections()
            logger.info(f"📋 Available collections: {[c.name for c in collections]}")
            
            # Test query collection if exists
            if collections:
                collection = collections[0]
                count = collection.count()
                logger.info(f"📊 Collection '{collection.name}' has {count} items")
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
    else:
        logger.error("❌ ChromaDB: FAILED")
    
    # Summary
    logger.info("=" * 50)
    logger.info("📋 CONNECTION TEST SUMMARY:")
    logger.info(f"PostgreSQL: {'✅ PASS' if results['postgresql'] else '❌ FAIL'}")
    logger.info(f"Redis: {'✅ PASS' if results['redis'] else '❌ FAIL'}")
    logger.info(f"ChromaDB: {'✅ PASS' if results['chromadb'] else '❌ FAIL'}")
    
    all_connected = all(results.values())
    if all_connected:
        logger.info("🎉 ALL DATABASES CONNECTED SUCCESSFULLY!")
        return True
    else:
        logger.error("💥 SOME DATABASES FAILED TO CONNECT")
        return False

async def test_existing_data():
    """Test data có sẵn từ FR-02.1"""
    logger.info("🔍 Testing existing data from FR-02.1...")
    
    try:
        # Test PostgreSQL data
        from sqlalchemy import create_engine, text
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Test documents_metadata_v2 table từ handover
            result = conn.execute(text("SELECT COUNT(*) FROM documents_metadata_v2"))
            doc_count = result.scalar()
            logger.info(f"📄 documents_metadata_v2: {doc_count} records")
            
            # Show sample documents
            if doc_count > 0:
                result = conn.execute(text("""
                    SELECT title, document_type, language_detected, status 
                    FROM documents_metadata_v2 
                    LIMIT 3
                """))
                docs = result.fetchall()
                logger.info("📋 Sample documents:")
                for doc in docs:
                    logger.info(f"  - {doc[0]} ({doc[1]}, {doc[2]}, {doc[3]})")
        
        # Test ChromaDB collections
        if chroma_manager.client:
            collections = chroma_manager.client.list_collections()
            for collection in collections:
                count = collection.count()
                logger.info(f"🗃️ Collection '{collection.name}': {count} items")
        
        logger.info("✅ Existing data test completed")
        
    except Exception as e:
        logger.error(f"❌ Error testing existing data: {e}")

if __name__ == "__main__":
    async def main():
        success = await test_database_connections()
        if success:
            await test_existing_data()
        
        # Cleanup
        await redis_manager.disconnect()
        chroma_manager.disconnect()
        
        return success
    
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
```

## 🚀 **5. QUICK START COMMANDS**

### **Setup Script: setup.sh**
```bash
#!/bin/bash
# ======================
# FR-02.2 QUICK SETUP SCRIPT
# ======================

set -e  # Exit on any error

echo "🚀 Setting up FR-02.2 API Quản trị Thống nhất..."

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3.10 --version 2>/dev/null || echo "Not found")
if [[ $python_version == *"3.10"* ]]; then
    echo "✅ Python 3.10 found: $python_version"
else
    echo "❌ Python 3.10.11 required for underthesea and pyvi"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3.10 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs configs/development scripts/testing

# Copy environment file
echo "🔧 Setting up environment..."
cp .env.example .env.development

# Test database connections
echo "🧪 Testing database connections..."
python scripts/test_connections.py

if [ $? -eq 0 ]; then
    echo "✅ All database connections successful!"
else
    echo "❌ Database connection failed. Please check FR-02.1 services are running:"
    echo "   docker-compose ps"
    exit 1
fi

# Generate secret key for development
echo "🔑 Generating secret key..."
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
sed -i "s/your-secret-key-here/$SECRET_KEY/g" .env.development

# Initialize Alembic
echo "🗄️ Initializing database migrations..."
alembic init alembic
alembic revision --autogenerate -m "Initial migration from FR-02.1 schema"

echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start development server: uvicorn app.main:app --reload"
echo "3. View API docs: http://localhost:8000/docs"
echo "4. Test health endpoint: curl http://localhost:8000/health"
```

### **Test Connection Script**
```bash
# Test kết nối với databases từ FR-02.1
chmod +x scripts/test_connections.py
python scripts/test_connections.py
```

## 🏗️ **6. FASTAPI APPLICATION ENTRY POINT**

### **app/main.py**
```python
"""
FastAPI Application cho FR-02.2 - API Quản trị Thống nhất
Entry point chính cho Knowledge Assistant API
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import time
import uvicorn
from contextlib import asynccontextmanager

# Import configurations và utilities
from app.core.config import settings
from app.core.database import (
    connect_to_databases, 
    close_database_connections,
    check_postgres_health,
    check_redis_health,
    check_chroma_health
)
from app.core.logging import setup_logging
from app.core.exceptions import (
    CustomException,
    custom_exception_handler,
    validation_exception_handler,
    http_exception_handler
)

# Import API routes
from app.api.api_v1 import api_router

# Setup logging
logger = setup_logging()

# ======================
# APPLICATION LIFECYCLE
# ======================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events"""
    # Startup
    logger.info("🚀 Starting FR-02.2 API Quản trị Thống nhất...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    try:
        # Connect to all databases từ FR-02.1
        await connect_to_databases()
        logger.info("✅ Application started successfully!")
        yield
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Shutting down application...")
        await close_database_connections()
        logger.info("👋 Application shutdown complete!")

# ======================
# FASTAPI APPLICATION
# ======================

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ======================
# MIDDLEWARE SETUP
# ======================

# CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Trusted Host Middleware (security)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", settings.HOST]
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# ======================
# EXCEPTION HANDLERS
# ======================

app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(422, validation_exception_handler)
app.add_exception_handler(500, http_exception_handler)

# ======================
# HEALTH CHECK ENDPOINTS
# ======================

@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "FR-02.2 API Quản trị Thống nhất",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check including database connections"""
    health_status = {
        "status": "healthy",
        "service": "FR-02.2 API Quản trị Thống nhất", 
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time(),
        "databases": {}
    }
    
    # Check PostgreSQL từ FR-02.1
    try:
        postgres_healthy = await check_postgres_health()
        health_status["databases"]["postgresql"] = {
            "status": "healthy" if postgres_healthy else "unhealthy",
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
            "database": settings.POSTGRES_DB
        }
    except Exception as e:
        health_status["databases"]["postgresql"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check Redis từ FR-02.1
    try:
        redis_healthy = await check_redis_health()
        health_status["databases"]["redis"] = {
            "status": "healthy" if redis_healthy else "unhealthy",
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT
        }
    except Exception as e:
        health_status["databases"]["redis"] = {
            "status": "error", 
            "error": str(e)
        }
    
    # Check ChromaDB từ FR-02.1
    try:
        chroma_healthy = check_chroma_health()
        health_status["databases"]["chromadb"] = {
            "status": "healthy" if chroma_healthy else "unhealthy",
            "host": settings.CHROMA_HOST,
            "port": settings.CHROMA_PORT
        }
    except Exception as e:
        health_status["databases"]["chromadb"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Overall health
    all_healthy = all(
        db.get("status") == "healthy" 
        for db in health_status["databases"].values()
    )
    
    if not all_healthy:
        health_status["status"] = "degraded"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return health_status

# ======================
# API ROUTES
# ======================

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# ======================
# ROOT ENDPOINT
# ======================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "FR-02.2 - API Quản trị Thống nhất",
        "description": "Knowledge Assistant Unified Management API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/health",
        "api_v1": settings.API_V1_STR,
        "endpoints": {
            "documents": f"{settings.API_V1_STR}/documents",
            "users": f"{settings.API_V1_STR}/users", 
            "search": f"{settings.API_V1_STR}/search",
            "access_control": f"{settings.API_V1_STR}/access-control",
            "auth": f"{settings.API_V1_STR}/auth"
        }
    }

# ======================
# CUSTOM OPENAPI SCHEMA
# ======================

def custom_openapi():
    """Custom OpenAPI schema với thông tin chi tiết"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=f"""
        ## FR-02.2 - API Quản trị Thống nhất
        
        **Knowledge Assistant Unified Management API**
        
        ### Overview
        RESTful API Gateway thống nhất cho hệ thống Trợ lý Tri thức Nội bộ.
        
        ### Features
        - **Documents Management**: CRUD operations cho tài liệu
        - **Users Management**: Quản lý người dùng và phân quyền  
        - **Search Engine**: Tìm kiếm hybrid (semantic + keyword)
        - **Access Control**: Hệ thống phân quyền theo cấp bậc
        
        ### Database Integration (từ FR-02.1)
        - **PostgreSQL**: Primary database cho metadata
        - **ChromaDB**: Vector database cho semantic search
        - **Redis**: Cache layer cho performance
        
        ### Authentication
        JWT-based authentication với role-based access control.
        
        ### Vietnamese Language Support
        Hỗ trợ xử lý tiếng Việt với `pyvi` và `underthesea`.
        
        ### Environment: {settings.ENVIRONMENT}
        """,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ======================
# DEVELOPMENT SERVER
# ======================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )
```

## 🔧 **7. CORE UTILITIES**

### **app/core/logging.py**
```python
"""
Logging configuration cho FR-02.2
"""
import logging
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings

def setup_logging():
    """Setup logging configuration"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    
    # File handler
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        str(log_file),
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
    )
    
    # Configure standard library logging to use loguru
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            
            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
    
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    return logger
```

### **app/core/exceptions.py**
```python
"""
Custom exceptions cho FR-02.2
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class CustomException(Exception):
    """Base custom exception"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DatabaseConnectionError(CustomException):
    """Database connection error"""
    def __init__(self, message: str = "Database connection failed"):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE)

class AuthenticationError(CustomException):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

class AuthorizationError(CustomException):
    """Authorization error"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)

class DocumentNotFoundError(CustomException):
    """Document not found error"""
    def __init__(self, document_id: str):
        super().__init__(f"Document {document_id} not found", status.HTTP_404_NOT_FOUND)

class ValidationError(CustomException):
    """Validation error"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)

# Exception handlers
async def custom_exception_handler(request: Request, exc: CustomException):
    """Handle custom exceptions"""
    logger.error(f"Custom exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "path": str(request.url)
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )
```

## 🐳 **8. DOCKER CONFIGURATION**

### **docker-compose.dev.yml**
```yaml
version: '3.8'

services:
  # FR-02.2 API Service
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: knowledge-assistant-api
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - POSTGRES_HOST=postgres
      - REDIS_HOST=redis
      - CHROMA_HOST=chromadb
    volumes:
      - .:/app
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
      - chromadb
    networks:
      - knowledge-assistant-network

  # Use existing PostgreSQL from FR-02.1 (reference)
  postgres:
    image: postgres:15
    container_name: chatbot-postgres-test
    external: true
    networks:
      - knowledge-assistant-network

  # Use existing Redis from FR-02.1 (reference)  
  redis:
    image: redis:7-alpine
    container_name: chatbot-redis-test
    external: true
    networks:
      - knowledge-assistant-network

  # Use existing ChromaDB from FR-02.1 (reference)
  chromadb:
    image: chromadb/chroma:latest
    container_name: chatbot-chroma-test
    external: true
    networks:
      - knowledge-assistant-network

networks:
  knowledge-assistant-network:
    external: true
    name: chatbot-enhanced-db_default
```

### **Dockerfile.dev**
```dockerfile
# Development Dockerfile cho FR-02.2
FROM python:3.10.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Development command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## 🧪 **9. TESTING SETUP**

### **tests/conftest.py**
```python
"""
Pytest configuration cho FR-02.2 testing
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.main import app
from app.core.config import settings
from app.core.database import get_async_db, Base
from app.api.dependencies.auth import get_current_user

# Test database URL (separate from main database)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Test engine
test_engine = create_async_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    echo=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        
        async with TestingSessionLocal() as session:
            yield session
            
        await connection.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Create a test client."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_async_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def mock_user():
    """Mock user for testing"""
    return {
        "user_id": "test-user-123",
        "username": "testuser",
        "email": "test@example.com",
        "access_level": "employee_only",
        "department": "IT",
        "is_active": True
    }

@pytest.fixture
def auth_headers(mock_user):
    """Authentication headers for testing"""
    # Mock JWT token (implement token generation)
    token = "mock-jwt-token"
    return {"Authorization": f"Bearer {token}"}
```

## ✅ **10. VERIFICATION COMMANDS**

### **Quick verification script**
```bash
#!/bin/bash
# verify_setup.sh - Kiểm tra setup FR-02.2

echo "🔍 Verifying FR-02.2 setup..."

# Check virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "❌ Virtual environment not activated"
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Check Python version
python_version=$(python --version)
if [[ $python_version == *"3.10"* ]]; then
    echo "✅ Python version correct: $python_version"
else
    echo "❌ Wrong Python version: $python_version"
    exit 1
fi

# Check dependencies
echo "📦 Checking key dependencies..."
python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)" || echo "❌ FastAPI not installed"
python -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)" || echo "❌ SQLAlchemy not installed"
python -c "import redis; print('✅ Redis:', redis.__version__)" || echo "❌ Redis not installed"
python -c "import chromadb; print('✅ ChromaDB:', chromadb.__version__)" || echo "❌ ChromaDB not installed"
python -c "import pyvi; print('✅ PyVi available')" || echo "❌ PyVi not installed"
python -c "import underthesea; print('✅ Underthesea available')" || echo "❌ Underthesea not installed"

# Test database connections
echo "🧪 Testing database connections..."
python scripts/test_connections.py

# Test API startup
echo "🚀 Testing API startup..."
timeout 10s uvicorn app.main:app --host 127.0.0.1 --port 8001 &
sleep 5

# Test health endpoint
curl -s http://127.0.0.1:8001/health | grep -q "healthy" && echo "✅ API health check passed" || echo "❌ API health check failed"

# Kill test server
pkill -f "uvicorn.*8001"

echo "🎉 Verification completed!"
```

**Để chạy verification:**
```bash
chmod +x verify_setup.sh
./verify_setup.sh
```

---

## 🎯 **TỔNG KẾT VÀ NEXT STEPS**

### ✅ **Những gì đã hoàn thành:**

1. **Project Structure hoàn chỉnh** với FastAPI architecture
2. **Database connections** tới cả 3 databases từ FR-02.1
3. **Configuration management** cho multiple environments  
4. **Core utilities** (logging, exceptions, security)
5. **Health check endpoints** để monitor system
6. **Testing framework** setup với pytest
7. **Docker configuration** cho development
8. **Verification scripts** để test setup

### 🔄 **Next Steps:**

**Bạn có thể tiếp tục với:**

1. **🔐 Authentication & Security** - Implement JWT, user management
2. **📄 Documents API** - CRUD operations cho documents từ FR-02.1 schema
3. **🔍 Search API** - Hybrid search với PostgreSQL + ChromaDB
4. **👥 Users API** - User management và permissions
5. **🛡️ Access Control API** - Role-based access control

**Bạn muốn tôi tiếp tục implement phần nào trước? Tôi khuyến nghị bắt đầu với Authentication system để có foundation cho các API endpoints khác.**