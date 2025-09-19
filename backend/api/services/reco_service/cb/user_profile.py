from __future__ import annotations
from typing import Optional
from scipy import sparse
from sklearn.preprocessing import normalize
from api.services.reco_service.data_access.interactions import fetch_user_events
from api.services.reco_service.cb.tfidf_builder import load_tfidf
from api.services.reco_service.cf.weighting import event_weight
from api.services.reco_service.config import WEIGHT_ENROLL, WEIGHT_FAVORITE, TAU_DAYS

# Xây dựng vector người dùng từ các sự kiện tương tác
# Trả về dạng csr_matrix (1 × d) đã L2-normalize
def build_user_vector(user_id: str,
                      max_events: int = 50,
                      w_enroll: float = WEIGHT_ENROLL,
                      w_favorite: float = WEIGHT_FAVORITE,
                      tau_days: int = TAU_DAYS):
    
    vec, X, row_map = load_tfidf()
    events = fetch_user_events(user_id, limit=max_events) # Lấy các sự kiện mới nhất

    if not events or X.shape[0] == 0:
        return None

    acc: Optional[sparse.csr_matrix] = None
    for ev in events:
        cid = ev.get("course_id")
        if cid not in row_map:
            continue

        # tính trọng số event
        w = event_weight(ev.get("type", ""), ev.get("days_ago", 0.0),
                         w_enroll=w_enroll, w_favorite=w_favorite, tau_days=tau_days)
        
        if w <= 0.0:
            continue

        # lấy hàng TF-IDF của course này và nhân trọng số vừa tính được
        row_idx = row_map[cid]
        v = X.getrow(row_idx).multiply(w)  # 1 x D

        acc = v if acc is None else (acc + v) # cộng dồn các vector

    if acc is None or acc.nnz == 0:
        return None

    acc = normalize(acc, norm="l2", axis=1) # L2-normalize
    return acc
