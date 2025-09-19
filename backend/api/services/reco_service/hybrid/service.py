from __future__ import annotations
from typing import List
from api.services.reco_service.hybrid.candidates import build_candidates_for_home
from api.services.reco_service.hybrid.blend import blend_weighted
from api.services.reco_service.data_access.interactions import fetch_user_events
from api.services.reco_service.data_access.courses import fetch_popular_course_ids
from api.services.reco_service.config import ALPHA_HOME

def _get_course_seen_ids(user_id: str) -> List[int]:
    seen = []
    for ev in fetch_user_events(user_id, limit=100):
        seen.append(int(ev.get("course_id")))
    return seen

# Trả về danh sách đề xuất cho trang Home (người dùng đã đăng nhập).
def hybrid_recommend_home(
    user_id: str,
    alpha: float = ALPHA_HOME,
) -> List[dict]:
    """
    Hybrid cho trang Home (người dùng đã đăng nhập).
    - candidates = union(CF-neighbor items, CB-quick, Popular)
    - CB & CF scoring chỉ trên candidates
    - Blend (switch hoặc weighted)
    """
    if not user_id:
        course_ids = fetch_popular_course_ids(limit=-1)
        return [{"course_id": cid, "score": 0.0} for cid in course_ids]

    # Candidates - tuple(cb, cf, popular)
    candidates = build_candidates_for_home(user_id)
    if not candidates:
        return []
    
    cb_cands = candidates[0]
    cf_cands = candidates[1]
    pop_cands = candidates[2]

    # Blend - Nếu một nhánh rỗng hoàn toàn, vẫn tiếp tục với nhánh còn lại
    scores_blend = blend_weighted(cb_cands, cf_cands, alpha=alpha)

    # Kết hợp với popular candidates
    combined_cands = set(scores_blend.keys()).union(set(pop_cands))

    seen = _get_course_seen_ids(user_id)
    scores_combined = {}
    for cid in combined_cands:
        scores_combined[cid] = scores_blend.get(cid, 0.0) / 10 if cid in seen else scores_blend.get(cid, 0.0)
        
    ranked = sorted(scores_combined.items(), key=lambda x: x[1], reverse=True)
    return [{"course_id": cid, "score": score} for (cid, score) in ranked]
