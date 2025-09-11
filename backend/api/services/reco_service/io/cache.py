from __future__ import annotations
from typing import Any
from django.core.cache import cache

def cache_get(key: str) -> Any:
    return cache.get(key)

def cache_set(key: str, value: Any, ttl: int) -> None:
    cache.set(key, value, ttl)

def cache_invalidate(key: str) -> None:
    cache.delete(key)

def key_similar(course_id: int) -> str:
    return f"reco:similar:{course_id}"

def key_home(user_id: str) -> str:
    return f"reco:home:{user_id}"