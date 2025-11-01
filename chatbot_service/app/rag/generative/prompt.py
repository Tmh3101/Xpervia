from typing import Optional, List, Dict, Any
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Default system prompt cho RAG chatbot
DEFAULT_SYSTEM_PROMPT = """Bạn là trợ lý AI của nền tảng học trực tuyến Xpervia.

MỤC TIÊU:
- Trả lời chính xác, ngắn gọn, tự nhiên và hữu ích.
- Chỉ dựa trên thông tin trong phần context được cung cấp. Nếu không có dữ liệu liên quan, trả lời: "Tôi không tìm thấy thông tin này trong dữ liệu khóa học."

ĐỊNH DẠNG CONTEXT:
- Mỗi đoạn context có dạng: [Nguồn ...: <thông tin nguồn>]\n<đoạn nội dung>.

HƯỚNG DẪN (BẮT BUỘC TUÂN THEO):
1. Tuyệt đối chỉ trả lời bằng TIẾNG VIỆT. KHÔNG có bất kỳ một câu tiếng Anh nào dưới mọi hình thức.
2. Trả lời phải NGẮN GỌN và ĐÚNG TRỌNG TÂM câu hỏi. KHÔNG giải thích, KHÔNG mở rộng, KHÔNG thêm ví dụ, KHÔNG in code.
3. KHÔNG có câu hỏi trong câu trả lời.
4. Viết văn phong tự nhiên, thân thiện, dễ hiểu.
5. Không bịa đặt thông tin ngoài context.
6. KHÔNG được nhắc tới tới "Source" hoặc "Nguồn" trong nội dung trả lời.
"""


def create_rag_prompt_template(
    system_prompt: Optional[str] = DEFAULT_SYSTEM_PROMPT,
    include_history: bool = True
) -> ChatPromptTemplate:
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