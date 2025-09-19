from __future__ import annotations

import logging
import json
from django.db import transaction
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from api.models import CourseContent
from api.services.reco_service.cb.tfidf_builder import transform_single_course
from api.services.reco_service.io.cache import cache_invalidate, key_similar

logger = logging.getLogger(__name__)

def _schedule_tfidf_update(course_content_id: int):
    def _do():
        try:
            transform_single_course(course_content_id)
            cache_invalidate(key_similar(course_content_id))  # cache similar theo course
            logger.info(f"TF-IDF updated for course_content_id={course_content_id}")
        except Exception as ex:
            logger.exception(f"TF-IDF update failed for course_content_id={course_content_id}: {ex}")
    transaction.on_commit(_do)

@receiver(post_save, sender=CourseContent)
def coursecontent_post_save(sender, instance: CourseContent, created, **kwargs):
    # Khi tạo mới hoặc cập nhật nội dung, rebuild vector 1 dòng
    _schedule_tfidf_update(instance.id)

@receiver(m2m_changed, sender=CourseContent.categories.through)
def coursecontent_categories_changed(sender, instance: CourseContent, action, **kwargs):
    if action in {"post_add", "post_remove", "post_clear"}:
        _schedule_tfidf_update(instance.id)

@receiver(post_delete, sender=CourseContent)
def coursecontent_post_delete(sender, instance: CourseContent, **kwargs):
    """
    Tuỳ chính sách:
    - Phương án đơn giản: KHÔNG đụng ma trận (vẫn còn 1 dòng cũ) và
      luôn lọc bằng is_visible/ẩn ở tầng trả về; về sau chạy rebuild toàn bộ.
    - Nếu bạn có cờ is_visible: set is_visible=False trước, signals ở trên sẽ cập nhật TF-IDF của nội dung ẩn (ít thay đổi).
    """
    logger.info(f"CourseContent deleted id={instance.id} (consider full CB rebuild later)")