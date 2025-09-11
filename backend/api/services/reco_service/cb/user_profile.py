import math
import numpy as np
from __future__ import annotations
from typing import Dict, Optional, Iterable
from scipy import sparse
from sklearn.preprocessing import normalize
from api.services.reco_service.data_access.interactions import fetch_user_events
from api.services.reco_service.cb.tfidf_builder import load_tfidf
from api.services.reco_service.config import WEIGHT_ENROLL, WEIGHT_FAVORITE, TAU_DAYS

# Trọng số cơ bản cho từng loại sự kiện
def _base_weight(ev_type: str,
                 w_enroll: float = WEIGHT_ENROLL,
                 w_favorite: float = WEIGHT_FAVORITE) -> float:
    if ev_type == "enroll":
        return float(w_enroll)
    if ev_type == "favorite":
        return float(w_favorite)
    return 0.0

# Hệ số giảm theo thời gian: exp(-days_ago / tau). Mỗi tau_days ngày thì giảm e lần.
def _time_decay(days_ago: float, tau_days: int = TAU_DAYS) -> float:
    if tau_days is None or tau_days <= 0:
        return 1.0
    d = max(0.0, float(days_ago or 0.0))
    return math.exp(-d / float(tau_days))

# Xây dựng vector người dùng từ các sự kiện tương tác
def build_user_vector(user_id: str,
                      max_events: int = 50,
                      w_enroll: float = WEIGHT_ENROLL,
                      w_favorite: float = WEIGHT_FAVORITE,
                      tau_days: int = TAU_DAYS):
    """
    Vector user là tổng các vector TF-IDF (đã L2 theo hàng) của courses user từng tương tác,
    rồi L2-normalize kết quả.

    Trả:
      - csr_matrix shape (1, D), đã L2
      - hoặc None nếu user không có sự kiện hợp lệ

    Ghi chú: Nếu một course_id chưa có trong row_map (course mới chưa transform), sẽ bỏ qua.
    """
    # Load artifacts TF-IDF
    vec, X, row_map = load_tfidf()

    # Lấy các sự kiện mới nhất
    events = fetch_user_events(user_id, limit=max_events)
    if not events or X.shape[0] == 0:
        return None

    acc: Optional[sparse.csr_matrix] = None

    for ev in events:
        cid = ev.get("course_id")
        if cid not in row_map:
            continue
        base = _base_weight(ev.get("type", ""), w_enroll=w_enroll, w_favorite=w_favorite)
        if base <= 0:
            continue
        decay = _time_decay(ev.get("days_ago", 0.0), tau_days=tau_days)
        w = base * decay
        if w <= 0:
            continue

        # lấy hàng TF-IDF của course này và nhân trọng số
        row_idx = row_map[cid]
        v = X.getrow(row_idx).multiply(w)  # 1 x D

        acc = v if acc is None else (acc + v)

    if acc is None:
        return None

    # L2-normalize hồ sơ
    acc = normalize(acc, norm="l2", axis=1)
    # Nếu norm = 0 (nhỡ tất cả w=0) thì trả None
    if acc.nnz == 0:
        return None
    return acc

# Tính điểm content_score cho user trên các khoá học ứng viên
def content_scores_for_user(user_id: str,
                            candidate_ids: Optional[Iterable[int]] = None) -> Dict[int, float]:
    """
    Tính content_score = cosine(u, v_course) cho user.
    - Nếu candidate_ids=None → tính cho toàn corpus.
    - Ngược lại → chỉ tính cho những course trong candidate_ids.

    Trả dict {course_id: score>0}
    """
    u = build_user_vector(user_id)
    if u is None:
        return {}

    _, X, row_map = load_tfidf()
    if X.shape[0] == 0:
        return {}

    # cosine(u, X) = u @ X.T
    sims = (u @ X.T)  # (1 x N) sparse
    sims = np.asarray(sims.todense()).ravel()

    if candidate_ids is None:
        inv = {v: k for k, v in row_map.items()}
        return {inv[j]: float(sims[j]) for j in range(X.shape[0]) if sims[j] > 0 and j in inv}

    out: Dict[int, float] = {}
    for cid in candidate_ids:
        ridx = row_map.get(cid)
        if ridx is None:
            continue
        s = float(sims[ridx])
        if s > 0:
            out[cid] = s
    return out
