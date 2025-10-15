import json
import requests
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
from app.config import COLAB_LLM_URL, IS_COLAB_LLM

def _call_colab_generate(
    prompt: str,
    max_new_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = None,
    stop: Optional[List[str]] = None,
    timeout: int = 60
) -> str:
    if not COLAB_LLM_URL:
        raise RuntimeError("COLAB_LLM_URL not configured")

    url = f"{COLAB_LLM_URL}/generate"

    payload = { "prompt": prompt }
    if max_new_tokens:
        payload["max_new_tokens"] = max_new_tokens
    if temperature:
        payload["temperature"] = temperature
    if top_p:
        payload["top_p"] = top_p
    if stop:
        payload["stop"] = stop

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
    except Exception as e:
        raise RuntimeError(f"Colab LLM request failed: {e}")

    if resp.status_code != 200:
        raise RuntimeError(f"Colab LLM error: status={resp.status_code} body={resp.text}")

    try:
        data = resp.json()
    except Exception:
        return resp.text

    val = data["text"]
    if isinstance(val, list):
        return " ".join([str(x) for x in val])
    return str(val)

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
    use_simple_prompt: bool = False,
    chat_model_config: GenerativeConfig = None
) -> str:
    try:
        retrieved_chunks = _normalize_retrieved_chunks(retrieved_chunks)
    except Exception as e:
        print(f"Failed to normalize retrieved_chunks: {e}")
        return "Tôi không tìm thấy thông tin này trong dữ liệu khóa học"

    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    try:
        context = format_context_from_chunks(retrieved_chunks)
        print(f"Formatted context length: {len(context)} characters")
        
        if use_simple_prompt:
            print("Using simple prompt format as requested")
            return _generate_with_simple_prompt(chat, question, context, system_prompt, chat_model_config)
        else:
            print("Using ChatPromptTemplate format for generation")
            return _generate_with_chat_template(chat, question, context, history, system_prompt, chat_model_config)
    
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
def _generate_with_chat_template(
    chat: ChatHuggingFace,
    question: str,
    context: str, 
    history: Optional[List[Dict[str, str]]],
    system_prompt: Optional[str],
    chat_model_config: GenerativeConfig = None
) -> str:
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
    
    print("Invoking chat model...")
    if IS_COLAB_LLM:
        print("Detected IS_COLAB_LLM=True, calling external Colab LLM service...")
        formatted_prompt = prompt_template.format(**input_vars)
        answer = _call_colab_generate(prompt=formatted_prompt)
        print("==> formatted_prompt:", formatted_prompt)
        print("Received response from Colab LLM service")
        print("==> answer:", answer)
        return _clean_generated_answer(answer)

    if chat is None:
        print("Chat model is None, attempting to build a default CPU model...")
        try:
            cfg = chat_model_config or GenerativeConfig()
            cfg.load_in_4bit = False
            chat = build_chat_model(cfg)
        except Exception as e:
            print(f"Cannot build default chat model lazily: {e}")
            raise RuntimeError(f"Chat model unavailable and lazy build failed: {e}")

    chain = prompt_template | chat
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
    system_prompt: Optional[str],
    chat_model_config: GenerativeConfig = None
) -> str:    
    print("Using simple string prompt for generation")
    prompt_template = create_simple_prompt_template(system_prompt)
    formatted_prompt = prompt_template.format(
        question=question,
        context=context
    )
    
    message = HumanMessage(content=formatted_prompt)
    print("Invoking chat model with simple prompt...")

    if IS_COLAB_LLM:
        print("Detected IS_COLAB_LLM=True, calling external Colab LLM service...")
        gen_kwargs = chat_model_config.gen_kwargs if chat_model_config else {}
        max_new_tokens = gen_kwargs.get("max_new_tokens", None)
        temperature = gen_kwargs.get("temperature", None)
        top_p = gen_kwargs.get("top_p", None)
        stop = gen_kwargs.get("stop", None)
        
        answer = _call_colab_generate(
            prompt=formatted_prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop
        )
        print("Received response from Colab LLM service")
        return _clean_generated_answer(answer)
    
    if chat is None:
        print("Chat model is None, attempting to build a default CPU model...")
        try:
            cfg = chat_model_config or GenerativeConfig()
            cfg.load_in_4bit = False
            chat = build_chat_model(cfg)
        except Exception as e:
            print(f"Cannot build default chat model lazily: {e}")
            raise RuntimeError(f"Chat model unavailable and lazy build failed: {e}")


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
    return text.split("Assistant:")[-1]

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