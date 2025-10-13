from typing import Optional, List, Dict, Any
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Default system prompt cho RAG chatbot
DEFAULT_SYSTEM_PROMPT = """Bạn là trợ lý AI thông minh cho hệ thống học trực tuyến Xpervia. Nhiệm vụ của bạn là trả lời câu hỏi của học viên dựa trên thông tin khóa học được cung cấp.

HƯỚNG DẪN:
1. Chỉ trả lời với thông tin có được từ context
2. Nếu không tìm thấy thông tin trong context, hãy chỉ nói "Tôi không tìm thấy thông tin này trong dữ liệu khóa học", không suy đoán
3. Trả lời bằng tiếng Việt, ngắn gọn và dễ hiểu
4. Tập trung vào thông tin hữu ích
5. Không trả lời theo kiểu "Theo context" ở đầu câu trả lời

ĐỊNH DẠNG CONTEXT:
- Mỗi đoạn context bắt đầu bằng [Nguồn: ...] 
- Sau đó là nội dung thông tin khóa học
- Sử dụng thông tin này để trả lời câu hỏi"""

def create_rag_prompt_template(
    system_prompt: Optional[str] = DEFAULT_SYSTEM_PROMPT,
    include_history: bool = True
) -> ChatPromptTemplate:
    # Tạo các thành phần prompt
    messages = [
        ("system", system_prompt),
    ]
    
    # Thêm lịch sử hội thoại nếu cần
    if include_history:
        messages.append(MessagesPlaceholder(variable_name="history"))
    
    # Thêm context và câu hỏi hiện tại
    messages.extend([
        ("user", """Context thông tin khóa học:
{context}

Câu hỏi: {question}""")
    ])

    return ChatPromptTemplate.from_messages(messages)

def format_context_from_chunks(chunks: List[Dict[str, Any]]) -> str:
    if not chunks:
        return "Không có thông tin liên quan được tìm thấy."
    
    context_parts = []
    
    for i, chunk in enumerate(chunks, 1):
        # Lấy thông tin metadata để tạo source info
        metadata = chunk.get("metadata", {})
        source_info = _extract_source_info(metadata)
        
        # Format từng chunk
        chunk_text = f"[Nguồn {i}: {source_info}]\n{chunk.get('content', '')}"
        context_parts.append(chunk_text)
    
    return "\n\n".join(context_parts)

def _extract_source_info(metadata: Dict[str, Any]) -> str:
    course_title = metadata.get("title", "Khóa học")
    teacher_name = metadata.get("teacher_name", "Giảng viên chưa xác định")
    if teacher_name:
        return f"{course_title} (Giảng viên: {teacher_name})"
    return course_title

def create_simple_prompt_template(system_prompt: Optional[str] = None) -> str:
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    
    template = f"""{system_prompt}

Context thông tin khóa học:
{{context}}

Câu hỏi: {{question}}

Trả lời:"""
    
    return template

def format_chat_history(history: Optional[List[Dict[str, str]]]) -> List:
    if not history:
        return []
    
    messages = []
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    
    return messages