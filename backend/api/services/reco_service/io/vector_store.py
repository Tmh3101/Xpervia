from __future__ import annotations
import os, json
from typing import Dict
import joblib
from scipy import sparse

"""
Lưu/tải artifacts TF-IDF: vectorizer (joblib), matrix (npz sparse), row_map (json).
"""

def _pjoin(*xs) -> str: return os.path.join(*xs)

# Lưu artifacts TF-IDF vào thư mục artifact_dir
def save_artifacts(artifact_dir: str,
                   vectorizer,
                   matrix: "sparse.csr_matrix",
                   row_map: Dict[int, int],
                   vect_name: str = "tfidf_vectorizer.joblib",
                   matrix_name: str = "tfidf_matrix.npz",
                   map_name: str = "course_row_map.json") -> None:
    os.makedirs(artifact_dir, exist_ok=True)
    joblib.dump(vectorizer, _pjoin(artifact_dir, vect_name))
    sparse.save_npz(_pjoin(artifact_dir, matrix_name), matrix)

    with open(_pjoin(artifact_dir, map_name), "w", encoding="utf-8") as f:
        json.dump({str(k): int(v) for k, v in row_map.items()}, f, ensure_ascii=False)

# Tải artifacts TF-IDF từ thư mục artifact_dir
def load_artifacts(artifact_dir: str,
                   vect_name: str = "tfidf_vectorizer.joblib",
                   matrix_name: str = "tfidf_matrix.npz",
                   map_name: str = "course_row_map.json"):
    vectorizer = joblib.load(_pjoin(artifact_dir, vect_name))
    matrix = sparse.load_npz(_pjoin(artifact_dir, matrix_name))

    with open(_pjoin(artifact_dir, map_name), "r", encoding="utf-8") as f:
        row_map_raw = json.load(f)

    row_map = {int(k): int(v) for k, v in row_map_raw.items()}
    return vectorizer, matrix, row_map
