from __future__ import annotations
from typing import Dict, List, Tuple, Iterable, Optional
import os
import numpy as np
from scipy import sparse
from api.services.reco_service.cb.tfidf_builder import load_tfidf

ARTIFACT_DIR = os.getenv("RECO_ARTIFACT_DIR", "api/var/reco")
COURSE_SIM_MATRIX_PATH = os.path.join(ARTIFACT_DIR, "course_similarity_matrix.npz")

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


def build_course_similarity_matrix() -> sparse.csr_matrix:
    """
    Xây dựng ma trận course-course similarity (N x N) từ ma trận TF-IDF.
    Mỗi phần tử [i, j] là cosine similarity giữa course i và course j.
    
    Returns:
        Ma trận sparse CSR (N x N) với giá trị cosine similarity.
    """
    _, X, _ = load_tfidf()
    if X.shape[0] == 0:
        return sparse.csr_matrix((0, 0))
    
    # Vì X đã L2-normalized, cosine similarity = X @ X.T
    sim_matrix = X @ X.T
    
    # Đặt diagonal = 0 (không so sánh course với chính nó)
    sim_matrix.setdiag(0)
    
    return sim_matrix.tocsr()


def save_course_similarity_matrix(sim_matrix: sparse.csr_matrix) -> None:
    """
    Lưu ma trận course-course similarity vào file.
    """
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    sparse.save_npz(COURSE_SIM_MATRIX_PATH, sim_matrix)


def load_course_similarity_matrix() -> Optional[sparse.csr_matrix]:
    """
    Load ma trận course-course similarity từ file.
    Trả về None nếu file không tồn tại.
    """
    if not os.path.exists(COURSE_SIM_MATRIX_PATH):
        return None
    try:
        return sparse.load_npz(COURSE_SIM_MATRIX_PATH)
    except Exception:
        return None


def build_and_save_course_similarity_matrix() -> Dict[str, int]:
    """
    Xây dựng và lưu ma trận course-course similarity.
    Được gọi khi server khởi động hoặc rebuild toàn bộ.
    
    Returns:
        Dict với thông tin về ma trận đã build.
    """
    sim_matrix = build_course_similarity_matrix()
    save_course_similarity_matrix(sim_matrix)
    return {
        "n_courses": sim_matrix.shape[0],
        "nnz": sim_matrix.nnz,
        "density": sim_matrix.nnz / (sim_matrix.shape[0] ** 2) if sim_matrix.shape[0] > 0 else 0
    }


def update_course_similarity_for_single(course_id: int) -> None:
    """
    Cập nhật ma trận similarity khi thêm/sửa 1 khóa học.
    - Load ma trận hiện tại
    - Tính similarity của course mới với tất cả courses
    - Cập nhật hàng và cột tương ứng trong ma trận
    """
    _, X, row_map = load_tfidf()
    if course_id not in row_map:
        return
    
    row_idx = row_map[course_id]
    
    # Load ma trận similarity hiện tại
    sim_matrix = load_course_similarity_matrix()
    
    # Nếu chưa có ma trận hoặc kích thước không khớp -> rebuild toàn bộ
    if sim_matrix is None or sim_matrix.shape[0] != X.shape[0]:
        build_and_save_course_similarity_matrix()
        return
    
    # Tính similarity của course này với tất cả courses
    v = X.getrow(row_idx)
    new_sims = v @ X.T  # (1 x N)
    new_sims = new_sims.tocsr()
    
    # Đặt similarity với chính nó = 0
    new_sims[0, row_idx] = 0
    
    # Cập nhật hàng và cột trong ma trận
    sim_matrix_lil = sim_matrix.tolil()
    
    # Cập nhật hàng row_idx
    sim_matrix_lil[row_idx, :] = new_sims
    
    # Cập nhật cột row_idx (ma trận đối xứng)
    sim_matrix_lil[:, row_idx] = new_sims.T
    
    # Chuyển về CSR và lưu
    sim_matrix = sim_matrix_lil.tocsr()
    save_course_similarity_matrix(sim_matrix)

def _cosine_topk_from_precomputed(
    sim_matrix: sparse.csr_matrix,
    row_idx: int,
    k: int,
    exclude_rows: Optional[Iterable[int]] = None,
) -> List[Tuple[int, float]]:
    """
    Lấy top-k similarity từ ma trận đã được tính trước.
    Nhanh hơn rất nhiều so với tính toán mỗi lần.
    
    Args:
        sim_matrix: Ma trận similarity đã tính (N x N)
        row_idx: Index của course cần tìm similar
        k: Số lượng top similar courses
        exclude_rows: Danh sách row indices cần loại trừ
    
    Returns:
        Danh sách (row_idx, score) của top-k courses tương tự
    """
    if sim_matrix is None or row_idx >= sim_matrix.shape[0]:
        return []
    
    # Lấy hàng similarity
    sims = sim_matrix.getrow(row_idx).toarray().ravel()
    
    # Loại các exclude_rows
    if exclude_rows:
        for r in exclude_rows:
            if 0 <= r < sims.size:
                sims[r] = -1.0
    
    # Lọc top-k
    idx = _argpartition_topk(sims, k)
    out: List[Tuple[int, float]] = []
    for j in idx:
        s = float(sims[j])
        if s <= 0.0:
            continue
        out.append((int(j), s))
    return out


# Tính cosine similarity của một hàng (row_idx) với toàn bộ các hàng khác trong ma trận X (bao gồm cả chính nó)
# CHÚ Ý: Hàm này giờ sử dụng ma trận đã tính trước nếu có
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
    
    NOTE: Hàm này giờ ưu tiên sử dụng ma trận similarity đã tính trước.
    """
    # Thử load ma trận similarity đã tính trước
    sim_matrix = load_course_similarity_matrix()
    
    if sim_matrix is not None and sim_matrix.shape[0] == X.shape[0]:
        # Sử dụng ma trận đã tính trước (nhanh hơn)
        return _cosine_topk_from_precomputed(sim_matrix, row_idx, k, exclude_rows)
    
    # Fallback: tính toán trực tiếp (nếu chưa có ma trận hoặc không khớp)
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