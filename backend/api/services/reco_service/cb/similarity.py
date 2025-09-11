from __future__ import annotations
from typing import Dict, List, Tuple, Iterable, Optional
import numpy as np
from scipy import sparse
from api.services.reco_service.cb.tfidf_builder import load_tfidf

def _argpartition_topk(values: np.ndarray, k: int) -> np.ndarray:
    """
    Lấy chỉ số top-k theo giá trị giảm dần một cách hiệu quả.
    Trả về chỉ số đã sắp xếp đúng thứ tự từ cao xuống thấp.
    """
    n = values.size
    if k >= n:
        idx = np.argsort(-values)
        return idx
    part = np.argpartition(-values, k)[:k]
    # sắp xếp lại phần đã chọn
    return part[np.argsort(-values[part])]

# Tính cosine similarity của một hàng (row_idx) với toàn bộ các hàng khác trong ma trận X (bao gồm cả chính nó)
def _cosine_topk_from_row(
    X: sparse.csr_matrix,
    row_idx: int,
    k: int,
    exclude_rows: Optional[Iterable[int]] = None,
) -> List[Tuple[int, float]]:
    """
    Vì các hàng đã L2-normalize, cosine = dot. (thay vì cosine(u,v) = (u.v) / (||u||*||v||))

    - Loại chính hàng row_idx
    - Loại các hàng trong exclude_rows nếu có

    Return: danh sách (other_row_idx, score) cho top-k.
    """
    v = X.getrow(row_idx)
    sims = v @ X.T                # (1 x N) sparse
    sims = np.asarray(sims.todense()).ravel()  # về ndarray 1-D

    # loại chính nó
    sims[row_idx] = -1.0

    # loại các exclude_rows nếu có
    if exclude_rows:
        for r in exclude_rows:
            if 0 <= r < sims.size:
                sims[r] = -1.0

    # lọc top-k
    idx = _argpartition_topk(sims, k)
    out: List[Tuple[int, float]] = []
    for j in idx:
        s = float(sims[j])
        if s <= 0.0:
            continue
        out.append((int(j), s))
    return out

# Tìm top-k khoá học tương tự với course_id
def top_k_similar_from_course(
    course_id: int,
    k: int = 12,
    exclude_ids: Optional[Iterable[int]] = None,
) -> List[Tuple[int, float]]:
    """
    Trả: [(course_id_khac, score_cosine), ...]
    """
    _, X, row_map = load_tfidf()
    if X.shape[0] == 0 or course_id not in row_map:
        return []

    i = row_map[course_id]

    # map course_id cần exclude -> row index để loại
    exclude_rows = None
    if exclude_ids:
        exclude_rows = [row_map[c] for c in exclude_ids if c in row_map]

    top = _cosine_topk_from_row(X, i, k, exclude_rows=exclude_rows)

    # row_index -> course_id
    inv = {v: k for k, v in row_map.items()}
    return [(inv[j], score) for (j, score) in top if j in inv]

# Tính điểm content-based giữa user vector và ma trận khoá học
def content_scores_from_user_vector(
    u_vec: sparse.spmatrix,
    candidate_ids: Optional[Iterable[int]] = None,
) -> Dict[int, float]:
    """
    Tính điểm content-based giữa user vector (1 x D, đã L2) và:
      - toàn bộ khoá học (nếu candidate_ids=None), hoặc
      - chỉ tập ứng viên trong candidate_ids.

    Trả dict {course_id: score_cosine (>0)}.
    """
    if u_vec is None:
        return {}
    _, X, row_map = load_tfidf()
    if X.shape[0] == 0:
        return {}

    # cosine(u, X) = u @ X.T
    sims = u_vec @ X.T  # (1 x N)
    sims = np.asarray(sims.todense()).ravel()

    if candidate_ids is None:
        # map tất cả
        inv = {v: k for k, v in row_map.items()}
        return {inv[j]: float(sims[j]) for j in range(X.shape[0]) if sims[j] > 0 and j in inv}

    # chỉ các ứng viên
    out: Dict[int, float] = {}
    for cid in candidate_ids:
        ridx = row_map.get(cid)
        if ridx is None:
            continue
        s = float(sims[ridx])
        if s > 0:
            out[cid] = s
    return out

# Lấy top-k theo content_score từ user vector
def top_k_from_user_vector(
    u_vec: sparse.spmatrix,
    k: int = 12,
    exclude_ids: Optional[Iterable[int]] = None,
) -> List[Tuple[int, float]]:
    """
    Lấy top-k theo content_score từ user vector.
    - exclude_ids: loại các khóa không muốn đề xuất (đã học/đang xem/ẩn).
    """
    scores = content_scores_from_user_vector(u_vec, candidate_ids=None)
    if not scores:
        return []

    if exclude_ids:
        scores = {cid: sc for cid, sc in scores.items() if cid not in set(exclude_ids)}

    # sort giảm dần theo điểm
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]