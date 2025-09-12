from __future__ import annotations
import os
import json
from typing import Dict, List, Tuple, Optional
from scipy import sparse

def _pjoin(*xs) -> str: return os.path.join(*xs)

# Lưu ma trận item-item S vào thư mục artifact_dir
def save_item_item_matrix(artifact_dir: str,
                          S: "sparse.csr_matrix",
                          file_name: str = "cf_item_item_S.npz") -> None:
    os.makedirs(artifact_dir, exist_ok=True)
    sparse.save_npz(_pjoin(artifact_dir, file_name), S)

# Tải ma trận item-item S từ thư mục artifact_dir
def load_item_item_matrix(artifact_dir: str,
                          file_name: str = "cf_item_item_S.npz") -> Optional["sparse.csr_matrix"]:
    path = _pjoin(artifact_dir, file_name)
    if not os.path.exists(path):
        return None
    return sparse.load_npz(path)

# Lưu neighbors user-based.
def save_user_neighbors_json(
    artifact_dir: str,
    neighbors: Dict[str, List[Tuple[str, float]]],
    file_name: str = "cf_user_neighbors.json",
) -> None:
    os.makedirs(artifact_dir, exist_ok=True)
    path = os.path.join(artifact_dir, file_name)
    # json chỉ lưu list, nên chuyển tuple -> list cho an toàn
    serializable = {
        str(uid): [[str(n_uid), float(sim)] for (n_uid, sim) in neighs]
        for uid, neighs in neighbors.items()
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)

# Đọc neighbors user-based.
def load_user_neighbors_json(
    artifact_dir: str,
    file_name: str = "cf_user_neighbors.json",
) -> Dict[str, List[Tuple[str, float]]]:
    path = os.path.join(artifact_dir, file_name)
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # giữ nguyên key là string; list -> tuple để dùng tiện hơn trong code
    neighbors: Dict[str, List[Tuple[str, float]]] = {}
    for uid, neighs in data.items():
        neighbors[str(uid)] = [(str(n_uid), float(sim)) for n_uid, sim in neighs]
    return neighbors