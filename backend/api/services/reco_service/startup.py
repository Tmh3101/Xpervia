import os
import json
from contextlib import contextmanager
from django.db import connection
from .cb.tfidf_builder import fit_tfidf_and_save, load_tfidf

ARTIFACT_DIR = os.getenv("RECO_ARTIFACT_DIR", "api/var/reco")
MAP_PATH = os.path.join(ARTIFACT_DIR, "course_row_map.json")
LOCK_PATH = os.path.join(ARTIFACT_DIR, "build.lock")

@contextmanager
def file_lock(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    f = open(path, "w+")
    try:
        if os.name == "nt":
            # Windows: best-effort; tránh phụ thuộc lib ngoài
            import msvcrt
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        f.close()

def _course_count() -> int:
    # Không thay schema, đếm số course qua CourseContents
    with connection.cursor() as cur:
        cur.execute('SELECT COUNT(*) FROM "CourseContents"')
        return cur.fetchone()[0]

def _artifact_ok() -> bool:
    # 1) tồn tại file  2) load được  3) số hàng khớp số course hiện có
    if not os.path.exists(MAP_PATH):
        return False
    try:
        vec, X, row_map = load_tfidf()
        if X.shape[0] <= 0:
            return False
        with open(MAP_PATH, "r", encoding="utf-8") as f:
            m = json.load(f)
        mapped = len(m)
        return (mapped == _course_count())
    except Exception:
        return False

def ensure_tfidf_artifacts(force: bool = False) -> dict | None:
    """
    Gọi ở startup. An toàn khi nhiều worker nhờ file-lock:
    - Nếu artifacts hợp lệ: return None (không làm gì)
    - Nếu thiếu/hỏng hoặc force=True: fit và lưu
    """
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    if not force and _artifact_ok():
        return None

    try:
        with file_lock(LOCK_PATH):
            # Double-check sau khi chiếm lock (tránh 2 tiến trình cùng build)
            if not force and _artifact_ok():
                return None
            info = fit_tfidf_and_save()
            return info
    except BlockingIOError:
        # Có tiến trình khác đang build; bỏ qua
        return None
