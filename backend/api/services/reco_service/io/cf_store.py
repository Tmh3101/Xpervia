from __future__ import annotations
import os
from typing import Optional
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
