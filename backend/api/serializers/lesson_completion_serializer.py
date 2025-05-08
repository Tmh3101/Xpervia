from rest_framework import serializers
from api.models import LessonCompletion, Lesson
from .lesson_serializer import SimpleLessonSerializer
from supabase_service.auth import get_user_info_by_id


class LessonCompletionSerializer(serializers.ModelSerializer):
    lesson = SimpleLessonSerializer(read_only=True)
    lesson_id = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(),
        source='lesson',
        write_only=True
    )

    student = serializers.SerializerMethodField()
    
    class Meta:
        model = LessonCompletion
        fields = '__all__'
        extra_kwargs = {
            'student_id': {'write_only': True},
            'created_at': {'read_only': True}
        }

    def get_student(self, obj):
        if obj.student_id:
            return get_user_info_by_id(str(obj.student_id))
        return None