from __future__ import annotations
import io
import os
from functools import lru_cache
from typing import Dict, Set, Tuple

# Đổi lại nếu bạn để file ở nơi khác
DEFAULT_ALIAS_1GRAM_PATH = "alias_map_1gram.txt"
DEFAULT_PHRASE_MAP_PATH = "phrase_map.txt"
DEFAULT_TECH_WHITELIST_PATH = "tech_whitelist.txt"
DEFAULT_STOPWORDS_PATH = "vietnamese_stopwords_dash.txt"

def _read_lines(path: str) -> list[str]:
    full_path = os.path.join(os.path.dirname(__file__), path)
    with io.open(full_path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.lstrip().startswith("#")]

@lru_cache(maxsize=1)
def load_alias_map_1gram(path: str = DEFAULT_ALIAS_1GRAM_PATH) -> Dict[str, str]:
    m: Dict[str, str] = {}
    for ln in _read_lines(path):
        if "\t" not in ln:
            continue
        alias, canon = ln.split("\t", 1)
        m[alias.strip().lower()] = canon.strip().lower()
    return m

@lru_cache(maxsize=1)
def load_phrase_map(path: str = DEFAULT_PHRASE_MAP_PATH) -> Dict[Tuple[str, ...], str]:
    m: Dict[Tuple[str, ...], str] = {}
    for ln in _read_lines(path):
        if "\t" not in ln:
            continue
        left, canon = ln.split("\t", 1)
        tokens = tuple(t for t in left.strip().lower().split(" ") if t)
        if tokens:
            m[tokens] = canon.strip().lower()
    return m

@lru_cache(maxsize=1)
def load_tech_whitelist(path: str = DEFAULT_TECH_WHITELIST_PATH) -> Set[str]:
    return {ln.lower() for ln in _read_lines(path)}

@lru_cache(maxsize=1)
def load_stopwords(path: str = DEFAULT_STOPWORDS_PATH) -> Set[str]:
    return {ln.lower() for ln in _read_lines(path)}

# Helper: build text từ các field (title/description/categories)
def build_document_text(title: str, description: str, categories: list[str]) -> str:
    title = title or ""
    description = description or ""
    cat = " ".join(categories or [])
    return f"{title} {description} {cat}"
