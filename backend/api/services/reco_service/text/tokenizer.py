from __future__ import annotations
from typing import List
import re
from underthesea import word_tokenize
from .preprocess import strip_markup
from .helpers import load_alias_map_1gram, load_phrase_map, load_tech_whitelist, load_stopwords

# Chuyển các ký tự đặc biệt thành '_'
def _canonical_token_safe(token: str) -> str:
    t = token.replace(" ", "_").replace(".", "_").replace("-", "_").replace("/", "_")
    t = re.sub(r"_+", "_", t).strip("_")
    return t

# Áp dụng alias 1-gram vào token
def _apply_alias_1gram(token: str, alias_map: dict) -> str:
    return alias_map.get(token, token)

# Áp dụng phrase map (multi-word) vào danh sách token đã lowercase
def _apply_phrase_map(tokens: List[str], phrase_map: dict) -> List[str]:
    if not phrase_map:
        return tokens
    
    out: List[str] = []
    i, n = 0, len(tokens)
    max_len = max((len(k) for k in phrase_map.keys()), default=1)
    while i < n:
        matched = False
        for L in range(min(max_len, n - i), 1, -1):
            tup = tuple(tokens[i:i+L])
            if tup in phrase_map:
                out.append(phrase_map[tup])
                i += L
                matched = True
                break
        if not matched:
            out.append(tokens[i])
            i += 1
    return out

# Tokenizer với dash giữa từ sử dụng underthesea
def vn_tokenize(text: str,
                alias_map_1gram: dict | None = None,
                phrase_map: dict | None = None,
                tech_whitelist: set | None = None,
                stopwords: set | None = None) -> List[str]:
    if not text:
        return []

    # Nạp cấu hình nếu chưa truyền vào
    alias_map_1gram = alias_map_1gram or load_alias_map_1gram()
    phrase_map      = phrase_map      or load_phrase_map()
    tech_whitelist  = tech_whitelist  or load_tech_whitelist()
    stopwords       = stopwords       or load_stopwords()   

    # Tiền xử lý: strip markup
    text = strip_markup(text)

    # tokenize với word_tokenize của underthesea
    raw = word_tokenize(text, format="text").split()

    # lowercase + alias 1-gram + bỏ stopword
    lowered: List[str] = []
    for tk in raw:
        # giữ code inline `...` nhưng vẫn lowercase để đồng nhất
        if tk.startswith("`") and tk.endswith("`"):
            lowered.append(tk.strip("`").lower())
            continue
        t = tk.lower()
        t = _apply_alias_1gram(t, alias_map_1gram)  # alias đơn
        if t in stopwords and t not in tech_whitelist:
            continue
        lowered.append(t)

    # phrase merge (alias đa từ: ví dụ ["asp",".net","core"] -> "asp.net core")
    merged = _apply_phrase_map(lowered, phrase_map)

    # chuẩn hoá token an toàn, lọc rỗng
    final: List[str] = []
    for t in merged:
        if not t or t.isspace():
            continue
        safe = _canonical_token_safe(t)
        final.append(safe)

    # (tuỳ chọn) ưu tiên whitelist: hiện tại ta chỉ giữ để tham khảo.
    # Nếu muốn tăng "trọng số" whitelist, có thể nhân bản token whitelist (e.g., append thêm lần nữa).
    # example:
    # boosted = []
    # for t in final:
    #     boosted.append(t)
    #     if t.replace("_", " ") in tech_whitelist:
    #         boosted.append(t)   # nhân đôi tần suất
    # return boosted

    # Loại bỏ ký tự đặc biệt
    final = [t for t in final if t and t[0].isalnum()]
    return final
