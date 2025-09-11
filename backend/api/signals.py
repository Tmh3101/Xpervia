from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import CourseContent
from api.services.reco_service.cb.tfidf_builder import transform_single_course

# Chỉ gọi khi thay đổi title/description (nếu tracking được)
def has_text_changed(instance):
    if not instance.id:
        return True  # mới tạo
    try:
        old = CourseContent.objects.get(id=instance.id)
        return (old.title != instance.title) or (old.description != instance.description)
    except CourseContent.DoesNotExist:
        return True

@receiver(post_save, sender=CourseContent)
def on_course_created_or_updated(sender, instance, created, **kwargs):
    if has_text_changed(instance):
        transform_single_course(course_id=instance.id)
        print(f"Vector updated for course {instance.id}")
