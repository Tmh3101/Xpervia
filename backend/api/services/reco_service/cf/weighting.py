from __future__ import annotations
from typing import Literal
import math
import numpy as np
from scipy import sparse
from api.services.reco_service.config import WEIGHT_ENROLL, WEIGHT_FAVORITE, TAU_DAYS

"""
Quy đổi implicit feedback -> trọng số:
- base_weight theo loại sự kiện (enroll/favorite)
- time-decay theo ngày: exp(-days_ago / tau_days)
- BM25-like weighting để giảm bias item phổ biến / user "tham"
"""

EventType = Literal["enroll", "favorite"]

# Trả về trọng số cơ bản theo loại sự kiện
def base_weight(ev_type: str,
                w_enroll: float = WEIGHT_ENROLL,
                w_favorite: float = WEIGHT_FAVORITE) -> float:
    if ev_type == "enroll":
        return float(w_enroll)
    if ev_type == "favorite":
        return float(w_favorite)
    return 0.0

# Hệ số giảm theo thời gian -> càng xa càng giảm nhiều (exp(-days_ago / tau_days)).
def time_decay(days_ago: float, tau_days: int = TAU_DAYS) -> float:
    if tau_days is None or tau_days <= 0:
        return 1.0
    d = max(0.0, float(days_ago or 0.0))
    return math.exp(-d / float(tau_days))

# Trọng số cuối cùng cho một event sau khi kết hợp base_weight và time_decay 
# event = base_weight * time_decay.
def event_weight(ev_type: str, days_ago: float,
                 w_enroll: float = WEIGHT_ENROLL,
                 w_favorite: float = WEIGHT_FAVORITE,
                 tau_days: int = TAU_DAYS) -> float:
    bw = base_weight(ev_type, w_enroll=w_enroll, w_favorite=w_favorite)
    if bw <= 0:
        return 0.0
    return bw * time_decay(days_ago, tau_days=tau_days)


# BM25 - like row scaling cho implicit feedback
# score = ((k1+1)*x) / (k1*(1 - b + b*len/avg_len) + x)
# Trong đó:
# - x = trọng số ban đầu (trong ma trận R)
# - len = tổng trọng số trên row (tổng trọng số user đã tương tác)
# - avg_len = trung bình len toàn tập (trung bình tổng trọng số user)
# Dùng để giảm ảnh hưởng user có quá nhiều tương tác hoặc item quá phổ biến.
# Tạo ra ma trận mới (CSR).
def apply_bm25(R: sparse.csr_matrix, k1: float = 1.2, b: float = 0.75) -> sparse.csr_matrix:
    if R.shape[0] == 0:
        return R

    R = R.tocsr(copy=True)
    row_sums = np.array(R.sum(axis=1)).ravel()  # len của mỗi user
    avg_len = float(row_sums.mean()) if R.shape[0] > 0 else 0.0
    if avg_len <= 0:
        return R

    # áp dụng theo từng row: x -> ((k1+1)*x) / (k1*(1-b+b*len/avg_len) + x)
    rows, _ = R.shape
    for i in range(rows):
        start, end = R.indptr[i], R.indptr[i+1]
        if start == end:
            continue
        x = R.data[start:end]
        denom = (k1 * (1.0 - b + b * (row_sums[i] / avg_len))) + x
        R.data[start:end] = ((k1 + 1.0) * x) / (denom + 1e-12) # +1e-12 để tranh chia 0
    return R
