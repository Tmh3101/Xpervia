from __future__ import annotations
from typing import Dict
from api.services.reco_service.config import ALPHA_HOME # Trọng số CB trong weighted blend

"""
Chiến lược trộn điểm cho Hybrid: blend_weighted: alpha * CB + (1-alpha) * CF
"""

# Kết hợp keys của 2 dict (cb, cf)
def _merge_keys(cb: Dict[int, float], cf: Dict[int, float]) -> set[int]:
    return set(cb.keys()) | set(cf.keys())

# Trộn kết quả CB và CF theo trọng số alpha
# final[i] = alpha * cb[i] + (1 - alpha) * cf[i]
def blend_weighted(
    cb: Dict[int, float],
    cf: Dict[int, float],
    alpha: float = ALPHA_HOME,
) -> Dict[int, float]:
    alpha = float(max(0.0, min(1.0, alpha)))
    out: Dict[int, float] = {}
    keys = _merge_keys(cb, cf)
    for k in keys:
        v_cb = cb.get(k, 0.0)
        v_cf = cf.get(k, 0.0)
        out[k] = alpha * v_cb + (1.0 - alpha) * v_cf
    return out
