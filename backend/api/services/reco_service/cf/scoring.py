from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Iterable
from collections import defaultdict
from api.services.reco_service.data_access.interactions import fetch_user_events
from api.services.reco_service.cf.weighting import event_weight
from api.services.reco_service.io.cf_store import load_user_neighbors_json

"""
User-based CF scoring:
- Lấy neighbors của user u: [(v, sim_uv), ...] (đã build & lưu sẵn).
- Lấy vector tương tác (implicit weight) của từng láng giềng v: w(v, i).
- Cộng dồn: score[i] += sim_uv * w(v, i) cho mọi item i của v.
- Loại item user u đã seen (đã enroll/favorite).
- (Tuỳ chọn) lọc theo candidates; giới hạn số item lấy từ mỗi láng giềng.
- (Tuỳ chọn) chuẩn hoá min-max về [0,1] để phối Hybrid.

Public:
- user_seen_items(user_id, max_events=200) -> set[int]
- user_item_weights(user_id, max_events=200) -> dict[int, float]
- collab_scores_for_user(user_id, ...) -> dict[int, float]
- top_k_collab_for_user(user_id, k=12, ...) -> list[(course_id, score)]
"""

# Lấy tâp course_id mà user đã enroll -> để loại khỏi đề xuất.
def user_seen_items(user_id: str, max_events: int = 200) -> set[int]:
    evs = fetch_user_events(user_id, limit=max_events)
    return {int(e["course_id"]) for e in evs if e.get("event_type") == "enroll"}

# Trọng số implicit của user trên từng course đã tương tác:
#   w(u, i) = base_weight(event_type) * time_decay(days_ago)
def user_item_weights(user_id: str, max_events: int = 200) -> Dict[int, float]:
    evs = fetch_user_events(user_id, limit=max_events)
    acc: Dict[int, float] = defaultdict(float)
    for e in evs:
        cid = int(e["course_id"])
        acc[cid] += event_weight(e["type"], e.get("days_ago", 0.0)) # cộng dồn nếu có nhiều event
    return {cid: w for cid, w in acc.items() if w > 0.0}

# Chuẩn hoá score của các item về [0,1] theo min-max normalization.
def _min_max_normalize(scores: Dict[int, float]) -> Dict[int, float]:
    if not scores:
        return scores
    vals = list(scores.values())
    lo, hi = min(vals), max(vals)
    if hi <= lo:
        return {k: 0.0 for k in scores}
    rng = hi - lo
    return {k: (v - lo) / rng for k, v in scores.items()}

# Tính điểm CF user-based cho user_id.
def collab_scores_for_user(
    user_id: str,
    *,
    artifact_dir: str = "var/reco",
    k_neighbors: int = 200,
    max_items_per_neighbor: int = 500,
    candidates: Optional[Iterable[int]] = None,
    min_sim: float = 0.0,
    normalize_scores: bool = True,
    max_events_user: int = 200,
    max_events_neighbor: int = 500,
    sim_normalize: bool = False,
) -> Dict[int, float]:
    # Load user neighbors từ file JSON - ma trận user-user đã được tính sẵn.
    all_neighbors = load_user_neighbors_json(artifact_dir)
    neighs = all_neighbors.get(str(user_id), [])
    if not neighs:
        return {}

    # Tập seen (course_id của các course đã enroll) của user u (để loại khỏi đề xuất)
    seen_u = user_seen_items(user_id, max_events=max_events_user)

    # candidates → set
    if candidates is not None:
        candidates = set(int(c) for c in candidates)

    # Duyệt qua k láng giềng có sim cao nhất
    scores: Dict[int, float] = defaultdict(float)
    sim_denom = 0.0

    used = 0
    for (v_uid, sim_uv) in neighs:
        if used >= k_neighbors:
            break
        s = float(sim_uv)
        if s <= min_sim:
            continue
        used += 1
        sim_denom += s

        # Lấy vector item của láng giềng v
        w_vi = user_item_weights(v_uid, max_events=max_events_neighbor)
        if not w_vi:
            continue

        # Cộng dồn điểm cho các item của v
        count_i = 0
        for i, w in w_vi.items():
            if i in seen_u:
                continue
            if candidates is not None and i not in candidates:
                continue
            scores[i] += s * float(w)
            count_i += 1
            if count_i >= max_items_per_neighbor:
                break

    # Chuẩn hoá theo tổng sim láng giềng
    if sim_normalize and sim_denom > 0:
        for k in list(scores.keys()):
            scores[k] = scores[k] / sim_denom

    # Min-max normalize để phối Hybrid
    if normalize_scores:
        scores = _min_max_normalize(scores)
    else:
        scores = {k: float(v) for k, v in scores.items()}

    return scores

# Trả top-k (course_id, score) theo CF user-based.
def top_k_collab_for_user(
    user_id: str,
    k: int = 12,
    **kwargs,
) -> List[Tuple[int, float]]:
    scores = collab_scores_for_user(user_id, **kwargs)
    if not scores:
        return []
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
