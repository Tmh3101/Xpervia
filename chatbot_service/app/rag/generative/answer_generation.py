import json
import re
import requests
from typing import List, Dict, Any, Optional
from langchain_huggingface import ChatHuggingFace
from langchain_core.messages import HumanMessage

from app.core.model.model import GenerativeConfig, build_chat_model
from .prompt import (
    create_rag_prompt_template, 
    format_context_from_chunks, 
    format_chat_history,
    create_simple_prompt_template
)
from app.config import COLAB_LLM_URL, IS_COLAB_LLM

def _call_colab_generate(
    prompt: str,
    max_new_tokens: int = 320,
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
        print("Sending request to Colab LLM service...")
        print("==> payload:", json.dumps(payload)[:1000])  # limit log size
        resp = requests.post(url, json=payload, timeout=timeout)
    except Exception as e:
        raise RuntimeError(f"Colab LLM request failed: {e}")

    if resp.status_code != 200:
        raise RuntimeError(f"Colab LLM error: status={resp.status_code} body={resp.text}")

    try:
        data = resp.json()
    except Exception:
        return resp.text

    val = data.get("text", data.get("result", data))
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
            out.append({"content": content, "metadata": metadata, "course_id": item.get("course_id")})
        else:
            content = getattr(item, "page_content", None)\
                        or getattr(item, "content", None)\
                        or getattr(item, "text", None)

            metadata = getattr(item, "metadata", None)\
                        or getattr(item, "meta", None) or {}
            
            course_id = getattr(item, "course_id", None)
            out.append({"content": content or str(item), "metadata": metadata or {}, "course_id": course_id})
    return out

def generate_answer(
    chat: ChatHuggingFace,
    question: str,
    retrieved_chunks: List[Dict[str, Any]],
    history: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    use_simple_prompt: bool = False,
    chat_model_config: GenerativeConfig = None
) -> Dict[str, Any]:
    """
    Return dict:
      { "answer": <cleaned answer string>, "resources": [course_id, ...] }

    - Extract course ids from retrieved_chunks (if present)
    - Normalize retrieved_chunks for building context
    - Generate answer (Colab or local model) and clean it
    """
    # Extract course ids early (raw items may contain course_id at top-level)
    resource_ids = []
    try:
        for item in retrieved_chunks or []:
            if isinstance(item, dict):
                cid = item.get("course_id")
            else:
                cid = getattr(item, "course_id", None)
            if cid is not None:
                try:
                    resource_ids.append(int(cid))
                except Exception:
                    continue
        # dedupe preserving order
        seen = set()
        resources = []
        for v in resource_ids:
            if v not in seen:
                seen.add(v)
                resources.append(v)
    except Exception:
        resources = []

    try:
        normalized = _normalize_retrieved_chunks(retrieved_chunks)
    except Exception as e:
        print(f"Failed to normalize retrieved_chunks: {e}")
        normalized = []

    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    try:
        context = format_context_from_chunks(normalized)
        print(f"Formatted context length: {len(context)} characters")
        
        if use_simple_prompt:
            print("Using simple prompt format as requested")
            raw_answer = _generate_with_simple_prompt(chat, question, context, system_prompt, chat_model_config)
        else:
            print("Using ChatPromptTemplate format for generation")
            raw_answer = _generate_with_chat_template(chat, question, context, history, system_prompt, chat_model_config)
    
    except Exception as e:
        print(f"Answer generation failed: {e}")
        # Fallback: try simple prompt
        try:
            raw_answer = _generate_with_simple_prompt(chat, question, context, system_prompt, chat_model_config)
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            raise RuntimeError(f"Both prompt methods failed: {e}, {e2}")

    cleaned = _clean_generated_answer(raw_answer)
    # Finalize
    final_answer = _finalize_answer(cleaned)
    return {"answer": final_answer, "resources": resources}

# Generate using ChatPromptTemplate (primary)
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
    
    # Add history if present
    if include_history:
        chat_history = format_chat_history(history)
        input_vars["history"] = chat_history
        print(f"Using chat history with {len(chat_history)} messages")
    
    print("Invoking chat model...")
    if IS_COLAB_LLM:
        print("Detected IS_COLAB_LLM=True, calling external Colab LLM service...")
        formatted_prompt = prompt_template.format(**input_vars)
        answer = _call_colab_generate(prompt=formatted_prompt)
        print("==> formatted_prompt (truncated):", formatted_prompt[:1000])
        print("Received response from Colab LLM service")
        return str(answer or "")

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
    
    return answer

# Generate using simple string prompt (fallback)
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
        return str(answer or "")
    
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
    
    return answer

def _extract_assistant_block(text: str) -> str:
    # attempt to find explicit assistant block (case-insensitive)
    m = re.search(r"(?:\n|\A)(?:\s*(?:assistant|answer)\s*[:\-]\s*)(.*)$", text, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).strip()
    return text

def _remove_bracketed_contexts(text: str) -> str:
    # remove [Context ...] or [Source: ...] blocks to avoid leaking context markers into answer
    return re.sub(r"\[.*?(?:Context|Source|Context\s*\d|Answer).*?\]", " ", text, flags=re.IGNORECASE | re.DOTALL)

def _clean_generated_answer(answer: str) -> str:
    """
    Clean raw generated text from model / external service:
    - remove bracketed context sections
    - extract assistant/answer block if present
    - strip repeated context markers and excessive whitespace
    - ensure punctuation at the end
    """
    if not answer:
        return "Xin lỗi, tôi không thể tạo câu trả lời lúc này."

    text = str(answer)

    # 0) Quick try: if the model returned a JSON object (or wrapped JSON),
    # extract common keys like "answer" or "text".
    try:
        # try to find a JSON substring containing "answer" or "text"
        m = re.search(r"(\{.*\"answer\".*\})", text, flags=re.DOTALL)
        if not m:
            m = re.search(r"(\{.*\"text\".*\})", text, flags=re.DOTALL)
        if m:
            try:
                obj = json.loads(m.group(1))
                if isinstance(obj, dict):
                    if "answer" in obj:
                        text = str(obj.get("answer") or "")
                    elif "text" in obj:
                        text = str(obj.get("text") or "")
            except Exception:
                # fallthrough to plain-text cleaning
                pass
    except Exception:
        pass

    # remove common context markers or sections in brackets
    text = _remove_bracketed_contexts(text)

    # remove markdown/code fences entirely (```...``` and ```) and inline backticks
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`+", "", text)

    # remove headings (lines that are just #, ##, ### ...)
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)

    # remove common labeled blocks like "### Assistant" or "### Answer"
    text = re.sub(r"^\s*(assistant|answer|response|kết luận)\s*[:\-]*\s*", "", text, flags=re.IGNORECASE | re.MULTILINE)

    # remove inline citations like [1], [2,3]
    text = re.sub(r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]", "", text)
    # remove (Source: ...), (Nguồn: ...)
    text = re.sub(r"\(\s*(Source|Nguồn)\s*[:\-].*?\)", "", text, flags=re.IGNORECASE)

    # normalize DOS/Windows newlines and trim
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # try extract assistant/answer section if present (fallback)
    extracted = _extract_assistant_block(text)
    if extracted:
        text = extracted

    # Line-by-line cleanup: drop noise lines and remove echoed prompts
    lines = []
    for ln in text.split("\n"):
        tln = ln.strip()
        if not tln:
            continue
        # Drop lines that start like "Human:" or variants
        if re.match(r"^human[:\-]", tln, flags=re.IGNORECASE):
            continue
        # If a line starts with assistant: keep the remainder after the label
        if re.match(r"^assistant[:\-]", tln, flags=re.IGNORECASE):
            parts = re.split(r"assistant[:\-]\s*", tln, flags=re.IGNORECASE)
            if len(parts) > 1 and parts[1]:
                lines.append(parts[1].strip())
            continue
        # If a line starts with answer: keep the remainder
        if re.match(r"^answer[:\-]", tln, flags=re.IGNORECASE):
            parts = re.split(r"answer[:\-]\s*", tln, flags=re.IGNORECASE)
            if len(parts) > 1 and parts[1]:
                lines.append(parts[1].strip())
            continue
        # discard lines that only state "Context" or "Source"
        if re.match(r"^\[?context\b", tln, flags=re.IGNORECASE):
            continue
        if re.match(r"^\[?source\b", tln, flags=re.IGNORECASE):
            continue

        lines.append(tln)

    cleaned = "\n".join(lines).strip()

    # Collapse multiple spaces but preserve paragraphs
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Remove repetitive sentence patterns
    cleaned = _remove_repetitive_patterns(cleaned)

    # Remove leftover bracketed citations again just in case
    cleaned = re.sub(r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]", "", cleaned)

    # ensure sentence ends with punctuation
    if cleaned and cleaned[-1] not in (".", "?", "!", ":", ";"):
        cleaned = cleaned + "."

    # final trim
    cleaned = cleaned.strip()

    # safety: if cleaned is still too short, fallback to a friendly message
    if not cleaned or len(cleaned) < 3:
        return "Xin lỗi, tôi không thể tạo câu trả lời lúc này."

    return cleaned

def _remove_repetitive_patterns(text: str, max_repeat: int = 3) -> str:
    if not text:
        return text

    # Best-effort: split into sentences using punctuation marks
    sentences = re.split(r'(?<=[\.\?\!])\s+', text)
    if len(sentences) <= 1:
        return text
    
    cleaned = []
    last = ""
    repeat = 0
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if s == last:
            repeat += 1
            if repeat < max_repeat:
                cleaned.append(s)
        else:
            repeat = 0
            cleaned.append(s)
            last = s
    return " ".join(cleaned)


def _finalize_answer(text: str, max_sentences: int = 4, max_words: int = 64) -> str:
    """
    Post-process a cleaned answer to enforce a concise length and preserve any
    trailing source lines. Behavior:
    - Detect and extract trailing source lines beginning with 'Nguồn' or 'SOURCES'.
    - Keep up to `max_sentences` sentences from the main answer body.
    - Truncate to `max_words` words if still too long.
    - Re-attach the source lines (if any) at the end separated by a blank line.
    """
    if not text:
        return "Xin lỗi, tôi không thể tạo câu trả lời lúc này."

    # Split into lines and pull off trailing source lines like 'Nguồn:' or 'SOURCES:'
    lines = [ln.rstrip() for ln in text.strip().splitlines()]
    source_lines = []
    i = len(lines) - 1
    while i >= 0:
        if re.match(r"^\s*(Nguồn|SOURCES)\b", lines[i], flags=re.IGNORECASE):
            source_lines.insert(0, lines[i].strip())
            i -= 1
            continue
        break

    main_lines = lines[: i + 1] if i >= 0 else []
    main = "\n".join(main_lines).strip()

    # If we didn't find source lines by line scan, try to find inline SOURCE patterns
    if not source_lines:
        m = re.search(r"(Nguồn\s*:\s*[^\n]+)", text, flags=re.IGNORECASE)
        if m:
            source_lines = [m.group(1).strip()]
            main = re.sub(re.escape(m.group(1)), "", text, flags=re.IGNORECASE).strip()

    # Sentence-split the main text
    sentences = re.split(r'(?<=[\.\?\!])\s+', main)
    # Filter out small administrative fragments
    filtered = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if re.match(r'^(Truy vấn|Phản hồi|Câu trả lời)\b', s, flags=re.IGNORECASE):
            continue
        filtered.append(s)

    if not filtered:
        filtered = [main] if main else []

    selected = filtered[:max_sentences]
    result = " ".join(selected).strip()

    # Word-limit safety
    words = result.split()
    if len(words) > max_words:
        result = " ".join(words[:max_words]).rstrip(" ,.;") + "."

    # Ensure final punctuation
    if result and result[-1] not in (".", "?", "!"):
        result = result + "."

    # Re-attach sources if present
    if source_lines:
        result = result + "\n\n" + "\n".join(source_lines)

    # Fallback
    if not result or len(result.strip()) < 3:
        return "Xin lỗi, tôi không thể tạo câu trả lời lúc này."

    return result