from __future__ import annotations

import re
import requests
from typing import List, Dict, Optional

from app import config
from app.core.model.model import QwenLoraLoader

IS_COLAB_LLM = config.IS_COLAB_LLM
COLAB_LLM_URL = config.COLAB_LLM_URL

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

def build_prompt(query: str, with_keywords: bool = True, max_words: int = 64) -> str:
    kw_line = ('Thêm vào cuối phần trả lời (dòng cuối): "Keywords: ..." gồm 2–4 từ khóa, phân tách dấu phẩy.'
               if with_keywords else 'Không cần dòng Keywords.')
    prompt = f"""
Bạn là trợ lý tạo “câu trả lời giả định” phục vụ truy xuất thông tin trong kiến trúc HyDE RAG.
Hãy viết MỘT đoạn trả lời GIẢ ĐỊNH ngắn gọn (khoảng {max_words} từ) mô tả câu trả lời hợp lý cho truy vấn, dựa trên kiến thức nền tảng và các giả định phổ biến.
KHÔNG nêu nguồn, KHÔNG bịa chi tiết cụ thể (tên, số liệu).

YÊU CẦU:
- Văn phong trung lập, súc tích.
- Trình bày câu trả lời dưới dạng đoạn văn.
- {kw_line}
- Trả lời bằng Tiếng Việt.

Truy vấn:
"{query}"
""".strip()
    return prompt

def load_hyde_model_and_tokenizer():
    loader = QwenLoraLoader()
    model = loader.load_model_only()
    tokenizer = loader.load_tokenizer_only()
    return model, tokenizer

def generate_hypothetical(
    query: str,
    tokenizer = None,
    model = None,
    with_keywords: bool = True,
    max_new_tokens: int = 32,
    temperature: float = 0.6,
    top_p: float = 0.9,
    repetition_penalty: float = 1.05,
) -> Dict:
    prompt = build_prompt(query, with_keywords=with_keywords)

    if not IS_COLAB_LLM:
        if model is None or tokenizer is None:
            model, tokenizer = load_hyde_model_and_tokenizer()

        input_ids = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)

        out = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            pad_token_id=tokenizer.eos_token_id
        )

        text = tokenizer.decode(out[0], skip_special_tokens=True)
    else:
        text = _call_colab_generate(prompt)

    print("[HyDE] Text Generated:", text)

    # cắt phần sau prompt
    raw_gen = text.split("assistant\n")[-1].strip()
    print("[HyDE] Raw Extracted generation:", raw_gen)

    # Clean up the HyDE-generated text: remove trailing instructions, repeated prompts,
    # markdown/code fences, and keep only the main assistant paragraph.
    def _clean_hyde_generation(s: str) -> str:
        if not s:
            return s
        # remove code fences and inline ticks
        s = re.sub(r"```.*?```", " ", s, flags=re.DOTALL)
        s = re.sub(r"`+", "", s)

        # If Keywords: exists, cut it (we'll extract keywords separately before calling this)
        s = re.split(r"\n\s*Keywords\s*:\s*", s, flags=re.IGNORECASE)[0]

        # Remove any trailing administrative or meta sections like 'Phản hồi', 'Truy vấn:', 'Câu trả lời:'
        s = re.split(r"\n\s*(Phản hồi|Truy vấn|Câu trả lời)\b.*", s, flags=re.IGNORECASE | re.DOTALL)[0]

        # Keep the first meaningful paragraph only
        parts = [p.strip() for p in re.split(r"\n\s*\n", s) if p.strip()]
        if parts:
            s = parts[0]

        # Remove leading labels like 'Câu trả lời:' if present
        s = re.sub(r"^\s*(Câu trả lời[:\-]\s*)", "", s, flags=re.IGNORECASE)

        # Collapse whitespace
        s = re.sub(r"[ \t]{2,}", " ", s).strip()

        # Ensure it ends with punctuation
        if s and s[-1] not in (".", "?", "!", ":", ";"):
            s = s + "."

        # Truncate to ~160 words as a safety bound (like HyDE elsewhere)
        words = s.split()
        if len(words) > 160:
            s = " ".join(words[:160]).rstrip(" ,.;") + "."

        return s

    gen = _clean_hyde_generation(raw_gen)
    print("[HyDE] Cleaned generation:", gen)

    # tách keywords (nếu có) — extract from raw_gen before cleaning to be robust
    kws: List[str] = []
    if with_keywords:
        m = re.search(r"Keywords\s*:\s*(.+)$", raw_gen, re.IGNORECASE | re.DOTALL)
        if m:
            raw = m.group(1).strip()
            # cắt ở dòng đầu tiên, tránh model nói tiếp
            raw = raw.splitlines()[0]
            kws = [k.strip(" .,;:–-") for k in raw.split(",") if k.strip()]

    words = gen.split()
    if len(words) > 160:
        gen = " ".join(words[:160]).rstrip(" ,.;") + "."

    return {"draft": gen, "keywords": kws, "used_prompt": prompt}
