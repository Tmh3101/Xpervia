from typing import Optional, List, Dict, Any
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Default system prompt cho RAG chatbot
DEFAULT_SYSTEM_PROMPT = """Bạn là trợ lý AI thông minh cho hệ thống học trực tuyến Xpervia. Nhiệm vụ của bạn là trả lời câu hỏi của học viên dựa trên thông tin khóa học được cung cấp.

HƯỚNG DẪN:
1. Sử dụng CHÍNH XÁC thông tin từ context được cung cấp
2. Nếu không tìm thấy thông tin trong context, hãy nói rõ "Tôi không tìm thấy thông tin này trong dữ liệu khóa học"
3. Trả lời bằng tiếng Việt, ngắn gọn và dễ hiểu
4. Tập trung vào thông tin hữu ích cho học viên
5. Có thể đề xuất khóa học liên quan nếu phù hợp

ĐỊNH DẠNG CONTEXT:
- Mỗi đoạn context bắt đầu bằng [Nguồn: ...] 
- Sau đó là nội dung thông tin khóa học
- Sử dụng thông tin này để trả lời câu hỏi"""

def create_rag_prompt_template(
    system_prompt: Optional[str] = None,
    include_history: bool = True
) -> ChatPromptTemplate:
    """
    Tạo ChatPromptTemplate cho RAG với Qwen2.5
    
    Args:
        system_prompt: Custom system prompt, mặc định dùng DEFAULT_SYSTEM_PROMPT
        include_history: Có sử dụng lịch sử hội thoại không
        
    Returns:
        ChatPromptTemplate đã config
    """
    
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    
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
    """
    Format các chunks thành context string cho prompt
    
    Args:
        chunks: List các chunk từ retrieval system
        
    Returns:
        Formatted context string
    """
    if not chunks:
        return "Không có thông tin liên quan được tìm thấy."
    
    context_parts = []
    
    for i, chunk in enumerate(chunks, 1):
        # Lấy thông tin metadata để tạo source info
        metadata = chunk.get("metadata", {})
        source_info = _extract_source_info(metadata, chunk.get("doc_type", "unknown"))
        
        # Format từng chunk
        chunk_text = f"[Nguồn {i}: {source_info}]\n{chunk.get('content', '')}"
        context_parts.append(chunk_text)
    
    return "\n\n".join(context_parts)

def _extract_source_info(metadata: Dict[str, Any], doc_type: str) -> str:
    """
    Trích xuất thông tin nguồn từ metadata
    
    Args:
        metadata: Metadata từ chunk
        doc_type: Loại document (course_overview, lesson, etc.)
        
    Returns:
        Formatted source info string
    """
    # Ưu tiên course info nếu có
    if "course_overview" in metadata:
        course_info = metadata["course_overview"]
        course_title = course_info.get("course_title", "Khóa học")
        instructor = course_info.get("instructor")
        
        if instructor:
            return f"{course_title} (Giảng viên: {instructor})"
        return course_title
    
    # Lesson info
    elif "lesson" in metadata:
        lesson_info = metadata["lesson"]
        lesson_title = lesson_info.get("lesson_title", "Bài học")
        course_title = lesson_info.get("course_title")
        
        if course_title:
            return f"{course_title} - {lesson_title}"
        return lesson_title
    
    # Chapter info  
    elif "chapter" in metadata:
        chapter_info = metadata["chapter"]
        chapter_title = chapter_info.get("chapter_title", "Chương")
        course_title = chapter_info.get("course_title")
        
        if course_title:
            return f"{course_title} - {chapter_title}"
        return chapter_title
    
    # Assignment info
    elif "assignment" in metadata:
        assignment_info = metadata["assignment"]
        assignment_title = assignment_info.get("assignment_title", "Bài tập")
        lesson_title = assignment_info.get("lesson_title")
        
        if lesson_title:
            return f"{lesson_title} - {assignment_title}"
        return assignment_title
    
    # Fallback dựa trên doc_type
    doc_type_map = {
        "course_overview": "Tổng quan khóa học",
        "lesson": "Bài học", 
        "chapter": "Chương học",
        "assignment": "Bài tập",
        "course_detail": "Chi tiết khóa học",
    }
    
    return doc_type_map.get(doc_type, f"Tài liệu {doc_type}")

def create_simple_prompt_template(system_prompt: Optional[str] = None) -> str:
    """
    Tạo simple string template làm fallback nếu ChatPromptTemplate không hoạt động
    
    Args:
        system_prompt: Custom system prompt
        
    Returns:
        String template với placeholders
    """
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    
    template = f"""{system_prompt}

Context thông tin khóa học:
{{context}}

Câu hỏi: {{question}}

Trả lời:"""
    
    return template

def format_chat_history(history: Optional[List[Dict[str, str]]]) -> List:
    """
    Convert history list thành LangChain messages
    
    Args:
        history: List of {"role": "user/assistant", "content": "..."}
        
    Returns:
        List of LangChain message objects
    """
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