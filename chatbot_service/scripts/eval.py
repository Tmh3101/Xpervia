from __future__ import annotations

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).resolve().parent.parent))  # add project root

# from dotenv import load_dotenv
from tqdm import tqdm

# SQLAlchemy async engine
from sqlalchemy.ext.asyncio import create_async_engine

# LangChain pipeline của bạn
from app.rag.chain import RAGPipeline
from app.core.model.model import GenerativeConfig
from app import config

# Gemini
import google.generativeai as genai

# ---------- CONFIG ----------
# Resolve test file relative to this script to avoid cwd issues when run from different
# working directories (e.g., project root vs scripts/).
TEST_FILE = str(Path(__file__).resolve().parent / "qa_dataset_test.json")
OUTPUT_DIR = "./scripts/eval_outputs"
OUTPUT_JUDGMENTS = f"{OUTPUT_DIR}/judgments.jsonl"
MODEL_NAME = "gemini-2.5-flash"   # Judge model
SAMPLE_LIMIT = None             # đặt số integer để chạy nhanh, None = chạy toàn bộ
RATE_LIMIT_SLEEP = (0.6, 1.2)   # giãn cách gọi Gemini (min,max) giây

# ---------- PROMPT: Gemini Judge ----------
JUDGE_SYSTEM_MSG = """Bạn là một giám khảo nghiêm khắc cho hệ thống RAG. 
Nhiệm vụ của bạn là chấm điểm (0..1) theo 4 tiêu chí:
- faithfulness: Câu trả lời có được hậu thuẫn bởi các đoạn context được đưa ra không (không bịa)?
- answer_relevance: Câu trả lời có đúng trọng tâm, trả lời query không?
- context_precision: Tỉ lệ đoạn context (retrieved) thực sự liên quan đến câu hỏi.
- context_recall: Context có bao phủ đủ thông tin cần thiết để trả lời không?

Bạn cần trả về JSON hợp lệ với dạng:
{
  "faithfulness": float [0..1],
  "answer_relevance": float [0..1],
  "context_precision": float [0..1],
  "context_recall": float [0..1],
  "justification": "mô tả ngắn gọn vì sao chấm điểm như vậy"
}

Chấm điểm công bằng, ngắn gọn, không thêm bình luận ngoài JSON.
"""

JUDGE_USER_TEMPLATE = """[QUESTION]
{question}

[GROUND_TRUTH_ANSWER]
{gold_answer}

[PREDICTED_ANSWER]
{pred_answer}

[RETRIEVED_CONTEXTS]
{retrieved_contexts}

[OPTIONAL_GOLD_CONTEXT]
{gold_context}

Hãy chỉ trả về JSON như hướng dẫn.
"""

# ---------- HELPER: Gemini infer ----------
def init_gemini():
    api_key = "AIzaSyDuiDlNv1iDpEDyXSxGwUgdQ7nMtuDkK1c"
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set. Put it in env or .env")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(MODEL_NAME)

def call_gemini_judge(model, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gọi Gemini chấm điểm và parse JSON trả về.
    payload: {
      "question": str,
      "gold_answer": str,
      "pred_answer": str,
      "retrieved_contexts": List[str],
      "gold_context": Optional[str]
    }
    """
    user_msg = JUDGE_USER_TEMPLATE.format(
        question=payload["question"],
        gold_answer=payload.get("gold_answer", ""),
        pred_answer=payload.get("pred_answer", ""),
        retrieved_contexts="\n\n-----\n\n".join(payload.get("retrieved_contexts", [])) or "(empty)",
        gold_context=payload.get("gold_context") or "(optional)"
    )

    # Gemini không có system role y như OpenAI; ta prepend system vào phần content
    prompt = JUDGE_SYSTEM_MSG + "\n\n" + user_msg
    resp = model.generate_content(prompt)
    text = resp.text.strip()

    # Robust JSON parse
    # Nhiều khi LLM trả kèm ```json ...```
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    try:
        data = json.loads(text)
    except Exception as e:
        print(f"[WARN] JSON parse error: {e}. Raw text: {text[:400]}")
        # fallback: cố gắng trích JSON phần đầu tiên
        import re
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            data = json.loads(m.group(0))
        else:
            # nếu vẫn lỗi: trả điểm 0 cùng justification
            data = {
                "faithfulness": 0.0,
                "answer_relevance": 0.0,
                "context_precision": 0.0,
                "context_recall": 0.0,
                "justification": f"Parse JSON error. Raw: {text[:400]}"
            }
    # Clamp 0..1
    for k in ["faithfulness","answer_relevance","context_precision","context_recall"]:
        v = float(data.get(k, 0.0))
        data[k] = max(0.0, min(1.0, v))
    if "justification" not in data:
        data["justification"] = ""
    return data

# ---------- LOAD TEST SET ----------
def load_testset(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        arr = json.load(f)
    if not isinstance(arr, list):
        raise ValueError("Test file must be a JSON array")
    return arr

# ---------- BUILD RAG PIPELINE ----------
def build_pipeline() -> RAGPipeline:
    # Bạn có thể truyền GenerativeConfig phù hợp hệ thống của bạn:
    gen_conf = GenerativeConfig()
    return RAGPipeline(chat_model_config=gen_conf, return_chunks=True)

# ---------- MAIN EVAL LOOP (ASYNC) ----------
async def eval_once(model, pipeline: RAGPipeline, sample: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chạy 1 mẫu test:
      - pipeline.invoke/ainvoke → pred_answer + retrieved_chunks
      - gemini judge → trả về 4 metrics + justification
    """
    question = sample["question"]
    gold_answer = sample.get("answer", "")
    gold_context = sample.get("context", "")

    # 1) chạy RAG

    print("[EVAL] Running RAG for question:", question)
    res = await pipeline.ainvoke(question, history=None, system_prompt=None, use_simple_prompt=False)
    print(f"[EVAL] Q: {question} | Gold A: {gold_answer} | Pred A: {res.get('answer','')}")

    pred_answer = (res.get("answer") or "").strip()
    retrieved_chunks = res.get("retrieved_chunks", []) or []
    retrieved_texts = []
    for ch in retrieved_chunks:
        # mỗi chunk của bạn có thể là đối tượng/từ DB; cố gắng lấy ra .content hoặc .text
        text = ch.content if hasattr(ch, "content") else ch.get("content") if isinstance(ch, dict) else str(ch)
        retrieved_texts.append(text.strip()[:4000])  # cắt dài quá

    # 2) chấm điểm bằng Gemini
    payload = {
        "question": question,
        "gold_answer": gold_answer,
        "pred_answer": pred_answer,
        "retrieved_contexts": retrieved_texts,
        "gold_context": gold_context
    }

    judge = call_gemini_judge(model, payload)
    
    print("==> judge:", judge)

    return {
        "question": question,
        "gold_answer": gold_answer,
        "pred_answer": pred_answer,
        "faithfulness": judge["faithfulness"],
        "answer_relevance": judge["answer_relevance"],
        "context_precision": judge["context_precision"],
        "context_recall": judge["context_recall"],
        "justification": judge.get("justification", ""),
        "num_retrieved": len(retrieved_texts),
    }

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # DB engine cho pipeline
    engine = create_async_engine(config.DATABASE_URL_ASYNC, pool_pre_ping=True)

    # Gemini Judge
    gemini = init_gemini()

    # RAG pipeline
    pipeline = build_pipeline()

    # Test set
    data = load_testset(TEST_FILE)
    if SAMPLE_LIMIT:
        data = data[:SAMPLE_LIMIT]

    # Vòng lặp đánh giá
    results = []
    with open(OUTPUT_JUDGMENTS, "w", encoding="utf-8") as f_out:
        for sample in tqdm(data, desc="Evaluating (Gemini as Judge)"):
            try:
                item = await eval_once(gemini, pipeline, sample)
                results.append(item)
                f_out.write(json.dumps(item, ensure_ascii=False) + "\n")
                # rate limit nhẹ
                import random, time
                time.sleep(random.uniform(*RATE_LIMIT_SLEEP))
            except Exception as e:
                print(f"[ERROR] Evaluation error for question: {sample.get('question','')}. Error: {e}")
                print()
                # log lỗi và tiếp tục
                results.append({
                    "question": sample.get("question",""),
                    "error": str(e)
                })

    # Tổng hợp điểm
    def avg(key):
        vals = [x[key] for x in results if key in x and isinstance(x[key], (int, float))]
        return sum(vals)/len(vals) if vals else 0.0

    report = {
        "num_samples": len(data),
        "num_success": len([x for x in results if "faithfulness" in x]),
        "faithfulness_avg": round(avg("faithfulness"), 4),
        "answer_relevance_avg": round(avg("answer_relevance"), 4),
        "context_precision_avg": round(avg("context_precision"), 4),
        "context_recall_avg": round(avg("context_recall"), 4),
    }

    print("\n===== RAG Evaluation (Gemini Judge) =====")
    for k, v in report.items():
        print(f"{k}: {v}")

    # Lưu summary
    with open(f"{OUTPUT_DIR}/summary.json", "w", encoding="utf-8") as fsum:
        json.dump(report, fsum, ensure_ascii=False, indent=2)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
