from __future__ import annotations
import re
from html import unescape

CODE_PATTERN = re.compile(r"(```.*?```|`[^`]+`)", flags=re.DOTALL)  # block & inline code
TAG_PATTERN  = re.compile(r"<[^>]+>")
WS_PATTERN   = re.compile(r"\s+")

def strip_markup(text: str) -> str:
    if not text:
        return ""
    code_spans = {}
    def _hold(m):
        key = f"__CODESPAN_{len(code_spans)}__"
        code_spans[key] = m.group(0)
        return key

    text = unescape(text)
    text = CODE_PATTERN.sub(_hold, text)   # giữ chỗ code span
    text = TAG_PATTERN.sub(" ", text)      # bỏ tag HTML
    text = text.replace("\u00a0", " ")
    text = WS_PATTERN.sub(" ", text).strip()

    # trả code span về chỗ cũ
    for k, v in code_spans.items():
        text = text.replace(k, v)
    return text
