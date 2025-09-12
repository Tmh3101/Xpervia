from __future__ import annotations
from typing import Dict, Tuple
from datetime import datetime, timezone
from scipy import sparse
from api.services.reco_service.data_access.interactions import fetch_all_interactions
from api.services.reco_service.cf.weighting import event_weight

"""
Xây ma trận R (user × item) dạng sparse (CSR) từ Enrollments + Favorites:
- Lấy events từ data_access.interactions (timestamp included)
- Quy đổi thành trọng số implicit + time-decay
- Trả:
    R (csr_matrix), user_index (user_id -> row), item_index (course_id -> col)
"""

# Tính số ngày đã qua từ timestamp ts đến 'bây giờ' (UTC).
def _days_ago(ts: datetime) -> float:
    if ts is None:
        return 0.0
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    return max(0.0, (now - ts).total_seconds() / 86400.0)

# Xây ma trận user-item R (CSR) từ events.
# Các cột là course_id (int) và các hàng là user_id (str).
def build_user_item_matrix() -> Tuple[sparse.csr_matrix, Dict[str, int], Dict[int, int]]:
    events = fetch_all_interactions()  # [(student_id, course_id, type, timestamp), ...]
    if not events:
        return sparse.csr_matrix((0, 0)), {}, {}

    user_index: Dict[str, int] = {}
    item_index: Dict[int, int] = {}

    rows, cols, data = [], [], []

    # Có thể dùng dict tạm để cộng dồn (u,i) -> weight
    # Cộng dồn vì có thể user có thể vừa enroll vừa favorite 1 course.
    accum: Dict[Tuple[int, int], float] = {}

    for (user_id, course_id, ev_type, ts) in events:
        # map id -> index
        u = user_index.setdefault(user_id, len(user_index))
        i = item_index.setdefault(course_id, len(item_index))

        w = event_weight(ev_type, _days_ago(ts))
        if w <= 0:
            continue

        key = (u, i)
        accum[key] = accum.get(key, 0.0) + w # cộng dồn trọng số nếu đã có, nếu chưa có thì khởi tạo

    if not accum:
        # không có tương tác > 0
        return sparse.csr_matrix((len(user_index), len(item_index))), user_index, item_index

    # đổ về 3 list để tạo CSR
    for (u, i), w in accum.items():
        rows.append(u)
        cols.append(i)
        data.append(w)

    n_users = len(user_index)
    n_items = len(item_index)
    R = sparse.csr_matrix((data, (rows, cols)), shape=(n_users, n_items))
    return R, user_index, item_index
