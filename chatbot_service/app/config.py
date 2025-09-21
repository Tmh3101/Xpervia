import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env ở thư mục gốc dự án
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

print(Path(__file__).resolve().parent.parent.parent / ".env")

# SUPABASE PostgreSQL
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "")
SUPABASE_DB_HOST = os.getenv("SUPABASE_DB_HOST", "")
SUPABASE_DB_PORT = os.getenv("SUPABASE_DB_PORT", 5432)  
SUPABASE_DB_NAME = os.getenv("SUPABASE_DB_NAME", "postgres")
SUPABASE_DB_USER = os.getenv("SUPABASE_DB_USER", "postgres")
DATABASE_URL_ASYNC = f"postgresql+asyncpg://{SUPABASE_DB_USER}:{SUPABASE_DB_PASSWORD}@{SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}/{SUPABASE_DB_NAME}"

# SUPABASE (cho API nếu cần)
SUPABASE_URL = os.getenv("SUPABASE_URL", None)
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", None)
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", None)

# REDIS (optional cache/queue)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Chunking & Indexing
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 256))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 32))

# HuggingFace models
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "Alibaba-NLP/gte-multilingual-base")
EMBED_DIM = int(os.getenv("EMBED_DIM", 768))
LLM_MODEL = os.getenv("LLM_MODEL", "arcee-ai/Arcee-VyLinh")

# Frontend base URL (nếu muốn tạo source_url)
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", None) 