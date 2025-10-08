import logging
from typing import List, Dict, Any, Optional
from langchain_huggingface import ChatHuggingFace
from langchain_core.messages import HumanMessage, AIMessage

from .prompt import (
    create_rag_prompt_template, 
    format_context_from_chunks, 
    format_chat_history,
    create_simple_prompt_template
)

logger = logging.getLogger(__name__)

def generate_answer(
    chat: ChatHuggingFace,
    question: str,
    retrieved_chunks: List[Dict[str, Any]],
    history: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    use_simple_prompt: bool = False
) -> str:
    """
    Sinh câu trả lời từ mô hình dựa trên question, context và history
    
    Args:
        chat: ChatHuggingFace model instance
        question: Câu hỏi của người dùng
        retrieved_chunks: Chunks đã retrieve từ RAG system
        history: Lịch sử hội thoại [{"role": "user/assistant", "content": "..."}]
        system_prompt: Custom system prompt
        use_simple_prompt: Sử dụng simple string format thay vì ChatPromptTemplate
        
    Returns:
        Generated answer string
        
    Raises:
        ValueError: Nếu input không hợp lệ
        RuntimeError: Nếu generation thất bại
    """
    
    # Validate inputs
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    if not retrieved_chunks:
        logger.warning("No retrieved chunks provided, generating answer without context")
    
    try:
        # Format context từ chunks
        context = format_context_from_chunks(retrieved_chunks)
        logger.info(f"Formatted context length: {len(context)} characters")
        
        if use_simple_prompt:
            return _generate_with_simple_prompt(chat, question, context, system_prompt)
        else:
            return _generate_with_chat_template(chat, question, context, history, system_prompt)
    
    except Exception as e:
        logger.error(f"Answer generation failed: {e}")
        
        # Fallback: thử simple prompt
        if not use_simple_prompt:
            logger.info("Falling back to simple prompt format...")
            try:
                context = format_context_from_chunks(retrieved_chunks)
                return _generate_with_simple_prompt(chat, question, context, system_prompt)
            except Exception as e2:
                logger.error(f"Fallback also failed: {e2}")
                raise RuntimeError(f"Both prompt methods failed: {e}, {e2}")
        else:
            raise RuntimeError(f"Answer generation failed: {e}")

def _generate_with_chat_template(
    chat: ChatHuggingFace,
    question: str,
    context: str, 
    history: Optional[List[Dict[str, str]]],
    system_prompt: Optional[str]
) -> str:
    """Generate sử dụng ChatPromptTemplate (phương pháp chính)"""
    
    logger.info("Using ChatPromptTemplate for generation")
    
    # Tạo prompt template
    include_history = history is not None and len(history) > 0
    prompt_template = create_rag_prompt_template(
        system_prompt=system_prompt,
        include_history=include_history
    )
    
    # Chuẩn bị input variables
    input_vars = {
        "question": question,
        "context": context,
    }
    
    # Thêm history nếu có
    if include_history:
        chat_history = format_chat_history(history)
        input_vars["history"] = chat_history
        logger.info(f"Using chat history with {len(chat_history)} messages")
    
    # Tạo chain và invoke
    chain = prompt_template | chat
    
    logger.info("Invoking chat model...")
    response = chain.invoke(input_vars)
    
    # Trích xuất content từ response
    if hasattr(response, 'content'):
        answer = response.content
    elif isinstance(response, str):
        answer = response
    else:
        answer = str(response)
    
    return _clean_generated_answer(answer)

def _generate_with_simple_prompt(
    chat: ChatHuggingFace,
    question: str,
    context: str,
    system_prompt: Optional[str]
) -> str:
    """Generate sử dụng simple string format (fallback)"""
    
    logger.info("Using simple string prompt for generation")
    
    # Tạo prompt string
    prompt_template = create_simple_prompt_template(system_prompt)
    formatted_prompt = prompt_template.format(
        question=question,
        context=context
    )
    
    # Invoke với HumanMessage
    message = HumanMessage(content=formatted_prompt)
    
    logger.info("Invoking chat model with simple prompt...")
    response = chat.invoke([message])
    
    # Trích xuất content
    if hasattr(response, 'content'):
        answer = response.content
    elif isinstance(response, str):
        answer = response
    else:
        answer = str(response)
    
    return _clean_generated_answer(answer)

def _clean_generated_answer(answer: str) -> str:
    """
    Làm sạch output từ model (loại bỏ artifacts, format lại)
    
    Args:
        answer: Raw answer từ model
        
    Returns:
        Cleaned answer string
    """
    if not answer:
        return "Xin lỗi, tôi không thể tạo câu trả lời lúc này."
    
    # Loại bỏ whitespace thừa
    answer = answer.strip()
    
    # Loại bỏ các artifacts thường gặp
    artifacts_to_remove = [
        "Trả lời:",
        "Assistant:",
        "AI:",
        "<|im_start|>",
        "<|im_end|>", 
        "<|assistant|>",
        "<|user|>",
        "<|system|>",
    ]
    
    for artifact in artifacts_to_remove:
        if answer.startswith(artifact):
            answer = answer[len(artifact):].strip()
    
    # Loại bỏ repetition patterns (nếu có)
    answer = _remove_repetitive_patterns(answer)
    
    # Đảm bảo kết thúc câu đúng cách
    if answer and not answer.endswith(('.', '!', '?', ':', ';')):
        answer += '.'
    
    return answer

def _remove_repetitive_patterns(text: str, max_repeat: int = 3) -> str:
    """
    Loại bỏ pattern lặp lại trong text
    
    Args:
        text: Input text
        max_repeat: Số lần lặp tối đa cho phép
        
    Returns:
        Text đã loại bỏ repetition
    """
    if not text:
        return text
    
    # Simple approach: loại bỏ câu giống nhau liên tiếp
    sentences = text.split('.')
    if len(sentences) <= 1:
        return text
    
    cleaned_sentences = []
    last_sentence = ""
    repeat_count = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if sentence == last_sentence:
            repeat_count += 1
            if repeat_count < max_repeat:
                cleaned_sentences.append(sentence)
        else:
            repeat_count = 0
            cleaned_sentences.append(sentence)
            last_sentence = sentence
    
    return '. '.join(cleaned_sentences)

def batch_generate_answers(
    chat: ChatHuggingFace,
    questions_with_context: List[Dict[str, Any]],
    **kwargs
) -> List[str]:
    """
    Generate batch answers (cho performance cao hơn nếu cần)
    
    Args:
        chat: ChatHuggingFace model
        questions_with_context: List of {"question": str, "chunks": [...], "history": [...]}
        **kwargs: Additional arguments cho generate_answer
        
    Returns:
        List of generated answers
    """
    answers = []
    
    for i, item in enumerate(questions_with_context):
        logger.info(f"Processing batch item {i+1}/{len(questions_with_context)}")
        
        try:
            answer = generate_answer(
                chat=chat,
                question=item["question"],
                retrieved_chunks=item["chunks"],
                history=item.get("history"),
                **kwargs
            )
            answers.append(answer)
            
        except Exception as e:
            logger.error(f"Failed to generate answer for batch item {i+1}: {e}")
            answers.append("Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi này.")
    
    return answers