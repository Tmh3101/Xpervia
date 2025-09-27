from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class RetrievedChunk:
    id: int
    chunk_uid: str
    course_id: Optional[int]
    doc_type: str
    lang: str
    content: str
    score: float
    metadata: Dict[str, Any]

@dataclass
class HybridRetrieved:
    id: int
    chunk_uid: str
    course_id: Optional[int]
    doc_type: str
    lang: str
    content: str
    score_semantic: float
    score_lexical: float
    score_final: float
    metadata: Dict[str, Any]