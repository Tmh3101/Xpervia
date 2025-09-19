from __future__ import annotations
import os
from typing import List, Tuple, Dict
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from api.services.reco_service.text.tokenizer import vn_tokenize
from api.services.reco_service.text.helpers import build_document_text
from api.services.reco_service.io.vector_store import save_artifacts, load_artifacts
from api.services.reco_service.data_access.courses import (
    fetch_courses_with_categories, fetch_course_by_id
)
from api.services.reco_service.config import (
    TFIDF_MIN_DF, TFIDF_MAX_FEATURES, WORD_NGRAM
)

# Đường dẫn artifacts
ARTIFACT_DIR = os.getenv("RECO_ARTIFACT_DIR", "api/var/reco")
VECT_NAME = "tfidf_vectorizer.joblib"
MATRIX_NAME = "tfidf_matrix.npz"
MAP_NAME = "course_row_map.json"

# Chuyển dữ liệu khóa học thành đoạn văn bản với token đã tiền xử lý
def _course_to_text(row: Dict) -> str:
    text = build_document_text(row["title"], row["description"], row["categories"])
    tokens = vn_tokenize(text)
    return " ".join(tokens)

# Xậy dựng corpus từ toàn bộ khóa học - trả về (ids, docs)
def _build_corpus() -> Tuple[List[int], List[str]]:
    """
    Trả:
    - ids: [course_id, ...]
    - docs: ["token1 token2 ...", ...]
    """
    rows = fetch_courses_with_categories()
    ids, docs = [], []
    for r in rows:
        ids.append(int(r["id"]))
        docs.append(_course_to_text(r))
    return ids, docs


# Xậy dụng vectorizer TF-IDF (word tf-idf với ngram)
def _build_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="word",
        ngram_range=WORD_NGRAM or (1, 2), # unigrams + bigrams
        min_df=TFIDF_MIN_DF or 1, # loại bỏ từ xuất hiện dưới 1% văn bản
        max_df=0.95, # loại bỏ từ xuất hiện trên 95% văn bản
        max_features=TFIDF_MAX_FEATURES or 50000, # giới hạn số từ đặc trưng (độ dài vector)
        tokenizer=str.split, # vì đã tokenize rồi
        lowercase=False, # đã lowercase ở tokenizer
        token_pattern=r"(?u)\b\w+\b" # định nghĩa token là \w+ (không có dấu gạch ngang, vì đã tokenize rồi)
    )


# Fit toàn bộ corpus - fit toàn bộ dữ liệu khóa học và lưu artifacts
def fit_tfidf_and_save() -> Dict:
    """
    Fit TF-IDF toàn bộ course corpus:
    - vectorizer, matrix, row_map
    - L2-normalize theo hàng
    """
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    ids, docs = _build_corpus()
    if not ids:
        raise RuntimeError("Không có course nào để fit TF-IDF.")

    vec = _build_vectorizer()
    X = vec.fit_transform(docs) # X là ma trận sparse N x D (N = số course, D = số từ đặc trưng)
    X = normalize(X, norm="l2", axis=1) # L2-normalize theo hàng - chuẩn hóa về độ dài 1 (để tính cosine similarity dễ dàng)

    row_map = {cid: i for i, cid in enumerate(ids)} # Tạo map course_id → row index trong ma trận
    save_artifacts(ARTIFACT_DIR, vec, X, row_map, VECT_NAME, MATRIX_NAME, MAP_NAME)
    return {
        "n_courses": len(ids),
        "n_features": int(X.shape[1]),
        "artifact_dir": ARTIFACT_DIR,
    }

# Transform 1 khóa học mới hoặc cập nhật khóa học (KHÔNG refit) - thêm hoặc cập nhật vào ma trận
def transform_single_course(course_id: int) -> None:
    # Load các artifacts
    vec, X, row_map = load_artifacts(ARTIFACT_DIR, VECT_NAME, MATRIX_NAME, MAP_NAME)

    # Lấy dữ liệu khóa học từ DB theo course_id
    r = fetch_course_by_id(course_id)
    if not r:
        return

    doc = _course_to_text(r)
    v = vec.transform([doc])  # v là vector sparse 1 x D - có được bằng cách transform văn bản với matrix đã fit
    v = normalize(v, norm="l2", axis=1)

    # Cập nhật vào ma trận X và row_map
    # Nếu course_id đã có thì cập nhật lại, nếu chưa có thì thêm mới vào cuối
    if course_id in row_map:
        i = row_map[course_id]
        X_lil = X.tolil(copy=True)
        X_lil[i, :] = v
        X = X_lil.tocsr()
    else:
        X = sparse.vstack([X, v], format="csr")
        row_map[course_id] = X.shape[0] - 1

    # Lưu lại artifacts
    save_artifacts(ARTIFACT_DIR, vec, X, row_map, VECT_NAME, MATRIX_NAME, MAP_NAME)


# Load TF-IDF artifacts
def load_tfidf():
    return load_artifacts(ARTIFACT_DIR, VECT_NAME, MATRIX_NAME, MAP_NAME)
