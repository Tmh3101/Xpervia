import logging
from celery import shared_task
from api.services.reco_service.startup import maybe_refresh_cf_artifacts_on_new_events

logger = logging.getLogger(__name__)

@shared_task
def refresh_cf_neighbors(mode="streaming", shrink_beta=50.0, k_neighbors=200, min_sim=0.0):
    logger.info("Only 10 minutes between runs. Starting refresh of collaborative filtering neighbors...")
    return maybe_refresh_cf_artifacts_on_new_events(
        mode=mode,
        shrink_beta=shrink_beta,
        k_neighbors=k_neighbors,
        min_sim=min_sim,
    )
