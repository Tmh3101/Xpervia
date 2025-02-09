from rest_framework import serializers
from api.models.chapter_model import Chapter
from api.serializers.course_serializer import SimpleCourseSerializer

class ChapterSerializer(serializers.ModelSerializer):
    course = SimpleCourseSerializer(read_only=True)
    class Meta:
        model = Chapter
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'course': {'read_only': True},
        }

class SimpleChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order']