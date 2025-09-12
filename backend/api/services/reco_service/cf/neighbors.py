from __future__ import annotations
from typing import Dict, List, Tuple, Optional
import numpy as np
from scipy import sparse
from api.services.reco_service.cf.user_user import cosine_row_against_all
from api.services.reco_service.io.cf_store import (
    save_user_neighbors_json,
    load_user_neighbors_json,
)

# Chọn chỉ số top‑k theo giá trị giảm dần
def _argpartition_topk(values: np.ndarray, k: int) -> np.ndarray:
    n = values.size
    if k >= n:
        return np.argsort(-values)
    part = np.argpartition(-values, k)[:k]
    return part[np.argsort(-values[part])]

# Đảo ngược user_index {user_id(str) -> row_index(int)} thành list inv sao cho inv[row_index] = user_id (str)
# Tiện lợi cho việc tra cứu ngược id từ index.
def _invert_user_index(user_index: Dict[str, int]) -> List[Optional[str]]:
    if not user_index:
        return []
    inv: List[Optional[str]] = [None] * (max(user_index.values()) + 1)
    for uid, r in user_index.items():
        inv[r] = uid
    return inv


# -------------- cách 1: từ full U --------------
# Dựng full ma trận U (user×user) rồi rút top‑K láng giềng cho mỗi user.
# Thích hợp khi số user không quá lớn, có đủ RAM để dựng U.
def topk_neighbors_from_U(
    U: sparse.csr_matrix,
    user_index: Dict[str, int],
    *,
    k: int = 200,
    min_sim: float = 0.0,
) -> Dict[str, List[Tuple[str, float]]]:
    n_users = U.shape[0]
    inv = _invert_user_index(user_index)

    out: Dict[str, List[Tuple[str, float]]] = {}
    for u in range(n_users):
        row = U.getrow(u)
        if row.nnz == 0:
            uid = inv[u] if inv and inv[u] is not None else None
            if uid is not None:
                out[uid] = []
            continue

        sims = row.toarray().ravel()
        idx = _argpartition_topk(sims, k)
        uid = inv[u] if inv and inv[u] is not None else None
        if uid is None:
            continue

        neighs: List[Tuple[str, float]] = []
        for v in idx:
            s = float(sims[v])
            if s <= min_sim:
                continue
            vid = inv[v] if inv[v] is not None else None
            if vid is None:
                continue
            neighs.append((vid, s))
        out[uid] = neighs
    return out


# ------ cách 2: streaming trực tiếp từ R ------
# Không dựng full U. Với từng user u:
#   sims_u = cosine_row_against_all(R, u, shrink_beta=...) -> lấy top‑K theo sims_u
# Phù hợp khi số user lớn, muốn tiết kiệm RAM.
def topk_neighbors_from_R_streaming(
    R: sparse.csr_matrix,
    user_index: Dict[str, int],
    *,
    k: int = 200,
    min_sim: float = 0.0,
    shrink_beta: Optional[float] = 50.0,
) -> Dict[str, List[Tuple[str, float]]]:
    n_users = R.shape[0]
    inv = _invert_user_index(user_index)

    out: Dict[str, List[Tuple[str, float]]] = {}
    for u in range(n_users):
        sims_col = cosine_row_against_all(
            R,
            u_idx=u,
            l2_on_user_rows=True,
            shrink_beta=shrink_beta,
        )  # (U × 1)
        if sims_col.nnz == 0:
            uid = inv[u] if inv and inv[u] is not None else None
            if uid is not None:
                out[uid] = []
            continue

        sims = sims_col.toarray().ravel()
        idx = _argpartition_topk(sims, k)
        uid = inv[u] if inv and inv[u] is not None else None
        if uid is None:
            continue

        neighs: List[Tuple[str, float]] = []
        for v in idx:
            s = float(sims[v])
            if s <= min_sim:
                continue
            vid = inv[v] if inv[v] is not None else None
            if vid is None:
                continue
            neighs.append((vid, s))
        out[uid] = neighs
    return out

# Lưu neighbors user-based.
def save_neighbors(
    artifact_dir: str,
    neighbors: Dict[str, List[Tuple[str, float]]],
    file_name: str = "cf_user_neighbors.json",
) -> None:
    save_user_neighbors_json(artifact_dir, neighbors, file_name=file_name)

# Đọc neighbors user-based.
def load_neighbors(
    artifact_dir: str,
    file_name: str = "cf_user_neighbors.json",
) -> Dict[str, List[Tuple[str, float]]]:
    return load_user_neighbors_json(artifact_dir, file_name=file_name)
