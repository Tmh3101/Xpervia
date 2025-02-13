from rest_framework import serializers
from api.models.lesson_model import Lesson
from api.models.course_model import Course
from api.models.chapter_model import Chapter
from .course_serializer import SimpleCourseSerializer
from .chapter_serializer import SimpleChapterSerializer

class LessonSerializer(serializers.ModelSerializer):
    course = SimpleCourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True
    )

    chapter = SimpleChapterSerializer(read_only=True)
    chapter_id = serializers.PrimaryKeyRelatedField(
        queryset=Chapter.objects.all(),
        source='chapter',
        write_only=True
    )
    class Meta:
        model = Lesson
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True}
        }

class SimpleLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'order', 'created_at']