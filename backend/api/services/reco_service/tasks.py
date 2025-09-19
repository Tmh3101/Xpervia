from celery import shared_task
from services.reco_service.startup import maybe_refresh_cf_artifacts_on_new_events
from api.services.reco_service.config import CF_K_NEIGHBORS, MIN_SIM_CF

@shared_task
def update_cf_neighbors_task():
    maybe_refresh_cf_artifacts_on_new_events(
        mode="streaming",
        shrink_beta=50.0,
        k_neighbors=CF_K_NEIGHBORS,
        min_sim=MIN_SIM_CF
    )