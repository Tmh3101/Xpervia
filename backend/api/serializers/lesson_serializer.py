from rest_framework import serializers
from api.models.lesson_model import Lesson
from api.serializers.chapter_serializer import SimpleChapterSerializer
from api.serializers.course_serializer import SimpleCourseSerializer

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'course': {'read_only': True},
            'created_at': {'read_only': True}
        }

class SimpleLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'order', ]