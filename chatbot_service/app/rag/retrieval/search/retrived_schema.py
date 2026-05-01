from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class RetrievedChunk:
    id: int
    course_id: int
    doc_type: str
    lang: Optional[str]
    text: str
    score: float
    meta: Dict[str, Any]

@dataclass
class HybridRetrieved:
    id: int
    course_id: int
    doc_type: str
    lang: Optional[str]
    content: str  # keep name for compatibility with downstream (use text internally)
    score_semantic: float
    score_lexical: float
    score_final: float
    metadata: Dict[str, Any]