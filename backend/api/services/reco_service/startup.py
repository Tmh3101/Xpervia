import os
import json
from contextlib import contextmanager
from django.db import connection
from .cb.tfidf_builder import fit_tfidf_and_save, load_tfidf
from .cf.update import (
    rebuild_user_neighbors_full,
    rebuild_user_neighbors_streaming,
)
from .io.cf_store import load_user_neighbors_json

ARTIFACT_DIR = os.getenv("RECO_ARTIFACT_DIR", "api/var/reco")
MAP_PATH = os.path.join(ARTIFACT_DIR, "course_row_map.json")
LOCK_PATH = os.path.join(ARTIFACT_DIR, "build.lock")

CF_NEI_PATH = os.path.join(ARTIFACT_DIR, "cf_user_neighbors.json")
CF_LOCK_PATH = os.path.join(ARTIFACT_DIR, "cf_build.lock")
CF_META_PATH = os.path.join(ARTIFACT_DIR, "cf_meta.json")  # lưu last_build_ts

def _course_count() -> int:
    # Không thay schema, đếm số course qua course_contents
    with connection.cursor() as cur:
        cur.execute('SELECT COUNT(*) FROM "course_contents"')
        return cur.fetchone()[0]
    
def _user_count() -> int:
    # đếm user thực học (học viên), có thể đổi WHERE theo role nếu cần
    with connection.cursor() as cur:
        cur.execute('SELECT COUNT(*) FROM "users"')
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
    
def _latest_interaction_ts() -> str | None:
    """
    Lấy mốc thời gian mới nhất của enrollments/favorites (ISO string).
    """
    with connection.cursor() as cur:
        cur.execute("""
            SELECT GREATEST(
                COALESCE((SELECT MAX(created_at) FROM "enrollments"), TIMESTAMP 'epoch'),
                COALESCE((SELECT MAX(created_at)  FROM "favorites"),   TIMESTAMP 'epoch')
            )
        """)
        row = cur.fetchone()
    if not row or row[0] is None:
        return None
    # row[0] là datetime; chuẩn hoá ISO
    return row[0].isoformat()

def _cf_artifact_ok() -> bool:
    if not os.path.exists(CF_NEI_PATH):
        return False
    try:
        # file tồn tại và load được, có ít nhất 1 user có neighbors
        neighbors = load_user_neighbors_json(ARTIFACT_DIR)
        if not isinstance(neighbors, dict):
            return False
        # không bắt buộc phải đủ mọi user, nhưng tối thiểu có nội dung
        if len(neighbors) == 0:
            return False
        return True
    except Exception:
        return False
    
@contextmanager
def file_lock(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    f = open(path, "w+")
    try:
        if os.name == "nt":
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
    
def ensure_cf_artifacts(
    *,
    force: bool = False,
    mode: str = "full",          # "full" | "streaming"
    use_bm25: bool = False,
    shrink_beta: float | None = 50.0,
    k_neighbors: int = 200,
    min_sim: float = 0.0,
) -> dict | None:
    """
    Khởi tạo CF neighbors an toàn nhiều worker:
    - Nếu artifacts hợp lệ và không force -> return None
    - Ngược lại build theo mode, lưu meta {last_build_ts}
    """
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    try:
        with file_lock(CF_LOCK_PATH):
            if mode == "streaming":
                stats = rebuild_user_neighbors_streaming(
                    artifact_dir=ARTIFACT_DIR,
                    use_bm25=use_bm25,
                    shrink_beta=shrink_beta,
                    k_neighbors=k_neighbors,
                    min_sim=min_sim,
                )
            else:
                stats = rebuild_user_neighbors_full(
                    artifact_dir=ARTIFACT_DIR,
                    use_bm25=use_bm25,
                    shrink_beta=shrink_beta,
                    k_neighbors=k_neighbors,
                    min_sim=min_sim,
                )
            # cập nhật meta
            meta = {
                "last_build_ts": _latest_interaction_ts(),
                "mode": mode,
                "k_neighbors": k_neighbors,
                "use_bm25": use_bm25,
                "shrink_beta": shrink_beta,
                "min_sim": min_sim,
                "users_total": _user_count(),
            }
            with open(CF_META_PATH, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            return stats
    except BlockingIOError:
        return None

def maybe_refresh_cf_artifacts_on_new_events(
    *,
    minutes: int = 10,
    mode: str = "streaming",
    use_bm25: bool = False,
    shrink_beta: float | None = 50.0,
    k_neighbors: int = 200,
    min_sim: float = 0.0,
) -> dict | None:
    """
    Dùng trong cron/command chạy mỗi 10' :
    - Nếu có sự kiện Enroll/Favorite mới (sau last_build_ts) -> rebuild CF.
      Mặc định dùng 'streaming' để nhẹ RAM.
    """
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    latest = _latest_interaction_ts()
    if latest is None:
        return None

    last_build_ts = None
    if os.path.exists(CF_META_PATH):
        try:
            with open(CF_META_PATH, "r", encoding="utf-8") as f:
                last_build_ts = json.load(f).get("last_build_ts")
        except Exception:
            last_build_ts = None

    # Nếu chưa từng build hoặc có sự kiện mới hơn → refresh
    need = (last_build_ts is None) or (latest > last_build_ts)
    if not need:
        return None

    try:
        with file_lock(CF_LOCK_PATH):
            # check lại trong lock
            if os.path.exists(CF_META_PATH):
                try:
                    with open(CF_META_PATH, "r", encoding="utf-8") as f:
                        last_build_ts = json.load(f).get("last_build_ts")
                except Exception:
                    last_build_ts = None
            need = (last_build_ts is None) or (latest > last_build_ts)
            if not need:
                return None

            if mode == "streaming":
                stats = rebuild_user_neighbors_streaming(
                    artifact_dir=ARTIFACT_DIR,
                    use_bm25=use_bm25,
                    shrink_beta=shrink_beta,
                    k_neighbors=k_neighbors,
                    min_sim=min_sim,
                )
            else:
                stats = rebuild_user_neighbors_full(
                    artifact_dir=ARTIFACT_DIR,
                    use_bm25=use_bm25,
                    shrink_beta=shrink_beta,
                    k_neighbors=k_neighbors,
                    min_sim=min_sim,
                )
            meta = {
                "last_build_ts": latest,
                "mode": mode,
                "k_neighbors": k_neighbors,
                "use_bm25": use_bm25,
                "shrink_beta": shrink_beta,
                "min_sim": min_sim,
                "users_total": _user_count(),
            }
            with open(CF_META_PATH, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            return stats
    except BlockingIOError:
        return None
