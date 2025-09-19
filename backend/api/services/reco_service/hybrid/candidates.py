from __future__ import annotations
from typing import List, Set, Dict, Optional, Tuple
import numpy as np
from api.services.reco_service.cb.tfidf_builder import load_tfidf
from api.services.reco_service.cb.user_profile import build_user_vector
from api.services.reco_service.cf.scoring import user_item_weights
from api.services.reco_service.io.cf_store import load_user_neighbors_json
from api.services.reco_service.data_access.courses import list_visible_course_ids
from api.services.reco_service.config import (
    CF_K_NEIGHBORS,
    CB_USER_MAX_ITEMS,
    MIN_SIM_CB,
    CF_K_ITEM_PER_NEIGHBOR
)

"""
Ứng viên (candidates) cho Hybrid Recommender: Home (user đã đăng nhập) - union( CB-quick topM, CF-neighbor items )
"""

# Hỗ trợ đảo row_map {course_id: row_idx} -> inv[row_idx] = course_id
def _invert_row_map(row_map: Dict[str, int]) -> List[Optional[int]]:
    if not row_map:
        return []
    n = max(int(v) for v in row_map.values()) + 1
    inv: List[Optional[int]] = [None] * n
    for k, v in row_map.items():
        try:
            inv[int(v)] = int(k)
        except Exception:
            inv[int(v)] = int(k) if str(k).isdigit() else None
    return inv

# Sắp xếp chỉ số trong mảng theo giá trị (giảm dần)
def _topk_indices(arr: np.ndarray, k: int) -> np.ndarray:
    return np.argpartition(-arr, k-1)[:k]

# CB: tìm nhanh top-n candidates theo cosine similarity
def _cb_quick_candidates(
    user_id: str,
    topk: int = CB_USER_MAX_ITEMS,
    min_sim: float = MIN_SIM_CB,
) -> Dict[int, float]:
    vec, X, row_map = load_tfidf()
    u_vec = build_user_vector(user_id)
    if u_vec is None or u_vec.nnz == 0:
        return {}

    sims = (X @ u_vec.T).toarray().ravel()  # Tính cosine similarity giữa u_vec và tất cả các course -> (N,)
    idx = _topk_indices(sims, topk)  # Lấy chỉ số top-n theo similarity
    inv = _invert_row_map(row_map)

    out: Dict[int, float] = {}
    for r in idx.tolist():
        if r < 0 or r >= len(inv) or inv[r] is None:
            continue
        cid = int(inv[r])
        if sims[r] < min_sim:
            continue
        out[cid] = float(sims[r])
    return out

# CF: hợp item mà láng giềng đã tương tác
def _cf_neighbor_items_candidates(
    user_id: str,
    k_neighbors: int = CF_K_NEIGHBORS,
    top_items_per_neighbor: int = CF_K_ITEM_PER_NEIGHBOR,
    exclude_ids: Optional[Set[int]] = None,
    artifact_dir: str = "api/var/reco",
) -> Dict[int, float]:
    all_neighbors = load_user_neighbors_json(artifact_dir)
    neighs = all_neighbors.get(str(user_id), [])
    if not neighs:
        return {}

    res: Dict[int, float] = {}
    picked: Set[int] = set()
    used = 0
    for v_uid, sim in neighs:
        if used >= k_neighbors:
            break
        used += 1

        w_vi = user_item_weights(v_uid, max_events=top_items_per_neighbor)
        # chọn theo weight giảm dần
        k = k_neighbors * top_items_per_neighbor
        for cid, _w in sorted(w_vi.items(), key=lambda x: x[1], reverse=True):
            c = int(cid)

            if exclude_ids and c in exclude_ids:
                continue
            if c in picked:
                continue

            picked.add(c)
            res[c] = float(_w)

            if len(res.keys()) >= k:
                break
        if len(res.keys()) >= k:
            break
    return res

# Popular: lấy top-n course phổ biến nhất (theo enroll/fav trong 30-90d) - fallback
def _popular_candidates() -> Dict[int, float]:
    return {cid: 0.0 for cid in list_visible_course_ids()}

# Ứng viên cho trang Home (user đã đăng nhập)
def build_candidates_for_home(
    user_id: str,
    include_popular: bool = True,
) -> Tuple[Dict[int, float], Dict[int, float], Dict[int, float]]:
    # CB quick top-n
    cb_cands = _cb_quick_candidates(user_id)

    # CF neighbor items
    cf_cands = _cf_neighbor_items_candidates(user_id)

    # Popular fallback
    pop_cands = _popular_candidates() if include_popular else {}

    return (cb_cands, cf_cands, pop_cands)
