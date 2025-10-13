import re
from typing import List, Dict, Any, Optional
from langchain_huggingface import ChatHuggingFace
from langchain_core.messages import HumanMessage

from .model import GenerativeConfig, build_chat_model
from .prompt import (
    create_rag_prompt_template, 
    format_context_from_chunks, 
    format_chat_history,
    create_simple_prompt_template
)

def _normalize_retrieved_chunks(raw: Any) -> List[Dict[str, Any]]:
    if raw is None:
        return []

    out = []
    for item in raw:
        if isinstance(item, dict):
            content =   item.get("content")\
                        or item.get("page_content")\
                        or item.get("text")\
                        or item.get("answer")\
                        or ""
            
            metadata = item.get("metadata") or item.get("meta") or {}
            out.append({"content": content, "metadata": metadata})
        else:
            content = getattr(item, "page_content", None)\
                        or getattr(item, "content", None)\
                        or getattr(item, "text", None)

            metadata = getattr(item, "metadata", None)\
                        or getattr(item, "meta", None) or {}
            
            out.append({"content": content or str(item), "metadata": metadata or {}})
    return out

def generate_answer(
    chat: ChatHuggingFace,
    question: str,
    retrieved_chunks: List[Dict[str, Any]],
    history: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    use_simple_prompt: bool = False
) -> str:
    try:
        retrieved_chunks = _normalize_retrieved_chunks(retrieved_chunks)
    except Exception as e:
        print(f"Failed to normalize retrieved_chunks: {e}")
        return "Tôi không tìm thấy thông tin này trong dữ liệu khóa học"

    # If chat is None, lazy-build a default CPU model to avoid crashes
    if chat is None:
        print("Chat model is None, attempting to build a default CPU model...")
        try:
            cfg = GenerativeConfig()
            cfg.load_in_4bit = False
            chat = build_chat_model(cfg)
        except Exception as e:
            print(f"Cannot build default chat model lazily: {e}")
            raise RuntimeError(f"Chat model unavailable and lazy build failed: {e}")


    # Validate inputs
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    try:
        context = format_context_from_chunks(retrieved_chunks)
        print(f"Formatted context length: {len(context)} characters")
        
        if use_simple_prompt:
            print("Using simple prompt format as requested")
            return _generate_with_simple_prompt(chat, question, context, system_prompt)
        else:
            print("Using ChatPromptTemplate format for generation")
            return _generate_with_chat_template(chat, question, context, history, system_prompt)
    
    except Exception as e:
        print(f"Answer generation failed: {e}")
        
        # Fallback: thử simple prompt
        if not use_simple_prompt:
            print("Falling back to simple prompt format...")
            try:
                context = format_context_from_chunks(retrieved_chunks)
                return _generate_with_simple_prompt(chat, question, context, system_prompt)
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                raise RuntimeError(f"Both prompt methods failed: {e}, {e2}")
        else:
            raise RuntimeError(f"Answer generation failed: {e}")

# Generate sử dụng ChatPromptTemplate (phương pháp chính)
async def _generate_with_chat_template(
    chat: ChatHuggingFace,
    question: str,
    context: str, 
    history: Optional[List[Dict[str, str]]],
    system_prompt: Optional[str]
) -> str:
    print("Using ChatPromptTemplate for generation")
    include_history = history is not None and len(history) > 0
    prompt_template = create_rag_prompt_template(
        system_prompt=system_prompt,
        include_history=include_history
    )
    
    input_vars = {
        "question": question,
        "context": context,
    }
    
    # Thêm history nếu có
    if include_history:
        chat_history = format_chat_history(history)
        input_vars["history"] = chat_history
        print(f"Using chat history with {len(chat_history)} messages")
    
    chain = prompt_template | chat
    print("Invoking chat model...")
    response = chain.invoke(input_vars)
    
    if hasattr(response, 'content'):
        answer = response.content
    elif isinstance(response, str):
        answer = response
    else:
        answer = str(response)
    
    return _clean_generated_answer(answer)

# Generate sử dụng simple string format (fallback)
def _generate_with_simple_prompt(
    chat: ChatHuggingFace,
    question: str,
    context: str,
    system_prompt: Optional[str]
) -> str:    
    print("Using simple string prompt for generation")
    prompt_template = create_simple_prompt_template(system_prompt)
    formatted_prompt = prompt_template.format(
        question=question,
        context=context
    )
    
    message = HumanMessage(content=formatted_prompt)
    print("Invoking chat model with simple prompt...")
    response = chat.invoke([message])
    
    if hasattr(response, 'content'):
        answer = response.content
    elif isinstance(response, str):
        answer = response
    else:
        answer = str(response)
    
    return _clean_generated_answer(answer)

# Nếu model trả về toàn bộ conversation với markers, trích xuất phần assistant.
def _extract_assistant_block(text: str) -> str:
    return text.split("assistant\n")[-1]

def _clean_generated_answer(answer: str) -> str:
    if not answer:
        return "Xin lỗi, tôi không thể tạo câu trả lời lúc này."

    # Extract assistant block first
    answer = _extract_assistant_block(answer).strip()
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

    answer = _remove_repetitive_patterns(answer)
    if answer and not answer.endswith(('.', '!', '?', ':', ';')):
        answer += '.'

    return answer

def _remove_repetitive_patterns(text: str, max_repeat: int = 3) -> str:
    if not text:
        return text

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