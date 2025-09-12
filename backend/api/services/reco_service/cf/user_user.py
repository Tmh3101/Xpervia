from __future__ import annotations
from typing import Optional
import numpy as np
from scipy import sparse
from sklearn.preprocessing import normalize

# Tính ma trận cosine user-user từ ma trận R (user-item).
def compute_user_user_cosine(
    R: sparse.csr_matrix,
    *,
    l2_on_user_rows: bool = True,
    dtype = np.float32,
    zero_diagonal: bool = True,
) -> sparse.csr_matrix:
    U, I = R.shape
    if U == 0 or I == 0:
        return sparse.csr_matrix((U, U), dtype=dtype)

    X = R
    if l2_on_user_rows:
        X = normalize(X, norm="l2", axis=1, copy=True)

    U_mat = (X @ X.T).astype(dtype) # R @ R_T -> user-user cosine

    # zero self-similarity, xóa các phần tử trên đường chéo
    if zero_diagonal:
        U_mat.setdiag(0.0)
        U_mat.eliminate_zeros()
    return U_mat 

# Đếm số item 'chung' giữa các user (U × U), dùng ma trận nhị phân:
#   B = binarize(R); C = B @ B.T
def _pairwise_common_counts(R: sparse.csr_matrix) -> sparse.csr_matrix:
    if not sparse.isspmatrix_csr(R):
        R = R.tocsr()
    B = R.copy()
    # binarize: mọi phần tử > 0 → 1
    B.data[:] = 1.0
    C = B @ B.T  # (U × U), số item chung
    return C.tocsr()

# Áp dụng shrinkage lên ma trận cosine user-user để giảm ảnh hưởng của các cặp user có ít item chung.
#  sim' = (n_common / (n_common + beta)) * sim, trong đó n_common là số item chung giữa 2 user.
def apply_shrinkage(
    U_cosine: sparse.csr_matrix,
    R: sparse.csr_matrix,
    *,  
    beta: float = 50.0,
    in_place: bool = False,
) -> sparse.csr_matrix:
    if beta <= 0:
        return U_cosine

    Uc = U_cosine if in_place else U_cosine.copy()

    # ma trận số item chung
    C = _pairwise_common_counts(R)  # (U × U)
    C = C.tocsr()

    # Áp dụng hệ số scale trên từng phần tử khác 0 của U
    # Duyệt theo cấu trúc CSR của Uc
    Uc = Uc.tocsr()
    indptr, indices, data = Uc.indptr, Uc.indices, Uc.data
    C_csr = C.tocsr()

    for u in range(Uc.shape[0]):
        start, end = indptr[u], indptr[u + 1]
        if start == end:
            continue
        cols = indices[start:end]
        sims = data[start:end]
        # lấy n_common(u, cols) từ C
        c_row = C_csr.getrow(u)
        # map col → n_common
        # cách nhanh: convert row sparse thành dict tạm
        c_idx = c_row.indices
        c_dat = c_row.data
        common_map = {c_idx[k]: c_dat[k] for k in range(len(c_idx))}
        # scale
        for k in range(len(cols)):
            v = cols[k]
            n_common = float(common_map.get(v, 0.0))
            if n_common <= 0.0:
                sims[k] = 0.0
            else:
                sims[k] = sims[k] * (n_common / (n_common + beta))

    Uc.eliminate_zeros()
    return Uc

# Tính similarity giữa user u_idx với toàn bộ user khác (vector cột/ hàng).
def cosine_row_against_all(
    R: sparse.csr_matrix,
    u_idx: int,
    *,
    l2_on_user_rows: bool = True,
    dtype = np.float32,
    zero_diagonal: bool = True,
    shrink_beta: Optional[float] = None,
) -> sparse.csr_matrix:
    U, I = R.shape
    if U == 0 or I == 0:
        return sparse.csr_matrix((U, 1), dtype=dtype)

    X = R
    if l2_on_user_rows:
        X = normalize(X, norm="l2", axis=1, copy=True)

    u_vec = X.getrow(u_idx).T                  # (I × 1)
    sims = (X @ u_vec).astype(dtype)           # (U × 1)

    if shrink_beta is not None and shrink_beta > 0:
        # n_common với u_idx
        B = R.copy()
        B.data[:] = 1.0
        nc = (B @ B.getrow(u_idx).T)           # (U × 1)
        # scale: sims *= n / (n + beta)
        nc = nc.tocoo()
        sims = sims.tolil(copy=True)
        for r, c, n in zip(nc.row, nc.col, nc.data):
            scale = float(n) / (float(n) + float(shrink_beta))
            if scale <= 0:
                sims[r, 0] = 0.0
            else:
                sims[r, 0] = float(sims[r, 0]) * scale
        sims = sims.tocsr()

    # zero self
    if zero_diagonal and 0 <= u_idx < sims.shape[0]:
        sims[u_idx, 0] = 0.0

    sims.eliminate_zeros()
    return sims
