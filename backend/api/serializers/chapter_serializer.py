from rest_framework import serializers
from api.models.chapter_model import Chapter
from api.serializers.course_serializer import CourseSerializer

class ChapterSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    class Meta:
        model = Chapter
        fields = '__all__'
        extra_kwargs = {
            'course': {'read_only': True},
        }

class SimpleChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order']