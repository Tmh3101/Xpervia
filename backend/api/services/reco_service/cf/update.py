from __future__ import annotations
from typing import Dict, Optional
from datetime import datetime
from api.services.reco_service.cf.build_matrix import build_user_item_matrix
from api.services.reco_service.cf.weighting import apply_bm25
from api.services.reco_service.cf.user_user import compute_user_user_cosine, apply_shrinkage
from api.services.reco_service.cf.neighbors import (
    topk_neighbors_from_U,
    topk_neighbors_from_R_streaming,
    save_neighbors,
)
from api.services.reco_service.io.misc_store import save_json

"""
Update pipeline cho CF (user-based):
- FULL: build toàn bộ neighbors từ ma trận user-user U
- STREAMING: không dựng full U; tính theo từng user (phù hợp dữ liệu lớn)

Có thể gọi các hàm này trong management command (vd. reco_init) để
khởi tạo/làm mới artifacts CF.
"""

# Xây dựng lại neighbors của user (user-based CF) và lưu về artifact_dir.
# Trả về dict tóm tắt thông tin quá trình build.
def rebuild_user_neighbors_full(
    *,
    artifact_dir: str = "var/reco",
    use_bm25: bool = False,
    bm25_k1: float = 1.2,
    bm25_b: float = 0.75,
    shrink_beta: Optional[float] = 50.0,
    k_neighbors: int = 200,
    min_sim: float = 0.0,
    save_indices: bool = True,
) -> Dict:
    # R + index maps
    R, user_index, item_index = build_user_item_matrix()
    n_users, n_items = R.shape

    # BM25
    if use_bm25 and n_users > 0 and n_items > 0:
        R = apply_bm25(R, k1=bm25_k1, b=bm25_b)

    # cosine U
    U = compute_user_user_cosine(R)  # csr (U×U) zero-diagonal

    # shrinkage 
    if shrink_beta is not None and shrink_beta > 0:
        U = apply_shrinkage(U, R, beta=shrink_beta)

    # neighbors
    neighbors = topk_neighbors_from_U(
        U, user_index, k=k_neighbors, min_sim=min_sim
    )

    save_neighbors(artifact_dir, neighbors, file_name="cf_user_neighbors.json")

    if save_indices:
        save_json(f"{artifact_dir}/cf_user_index.json", {uid: int(idx) for uid, idx in user_index.items()})
        save_json(f"{artifact_dir}/cf_item_index.json", {int(cid): int(idx) for cid, idx in item_index.items()})

    return {
        "mode": "full",
        "users": n_users,
        "items": n_items,
        "neighbors_users": len(neighbors),
        "k_neighbors": k_neighbors,
        "use_bm25": use_bm25,
        "shrink_beta": shrink_beta,
        "min_sim": min_sim,
        "artifact_dir": artifact_dir,
        "ts": datetime.utcnow().isoformat() + "Z",
    }

# Xây dựng lại neighbors của user (user-based CF) và lưu về artifact_dir.
# Trả về dict tóm tắt thông tin quá trình build.
def rebuild_user_neighbors_streaming(
    *,
    artifact_dir: str = "var/reco",
    use_bm25: bool = False,
    bm25_k1: float = 1.2,
    bm25_b: float = 0.75,
    shrink_beta: Optional[float] = 50.0,
    k_neighbors: int = 200,
    min_sim: float = 0.0,
    save_indices: bool = True,
) -> Dict:
    R, user_index, item_index = build_user_item_matrix()
    n_users, n_items = R.shape

    if use_bm25 and n_users > 0 and n_items > 0:
        R = apply_bm25(R, k1=bm25_k1, b=bm25_b)

    neighbors = topk_neighbors_from_R_streaming(
        R, user_index, k=k_neighbors, min_sim=min_sim, shrink_beta=shrink_beta
    )
    save_neighbors(artifact_dir, neighbors, file_name="cf_user_neighbors.json")

    if save_indices:
        save_json(f"{artifact_dir}/cf_user_index.json", {uid: int(idx) for uid, idx in user_index.items()})
        save_json(f"{artifact_dir}/cf_item_index.json", {int(cid): int(idx) for cid, idx in item_index.items()})

    return {
        "mode": "streaming",
        "users": n_users,
        "items": n_items,
        "neighbors_users": len(neighbors),
        "k_neighbors": k_neighbors,
        "use_bm25": use_bm25,
        "shrink_beta": shrink_beta,
        "min_sim": min_sim,
        "artifact_dir": artifact_dir,
        "ts": datetime.utcnow().isoformat() + "Z",
    }
