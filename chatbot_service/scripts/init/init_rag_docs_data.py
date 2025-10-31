import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.rag.indexing.upsert import embed_all_courses

if __name__ == "__main__":
    embed_all_courses()