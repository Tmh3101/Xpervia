from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any

Role = Literal["human", "ai", "user", "assistant"]

class ChatTurn(BaseModel):
    role: Role
    content: str

class AskDTO(BaseModel):
    question: str
    history: Optional[List[ChatTurn]] = None
    system_prompt: Optional[str] = None
    use_simple_prompt: bool = False
    return_chunks: bool = False

class AskResponse(BaseModel):
    answer: str
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None