from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ChunkRecord(BaseModel):
    course_id: Optional[int]
    doc_type: str
    lang: str
    content: str
    content_tokens: Optional[int] = None
    embedding: List[float]
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = {}
