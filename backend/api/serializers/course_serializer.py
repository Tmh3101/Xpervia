from rest_framework import serializers
from api.models import CourseContent, Course
from .course_content_serializer import CourseContentSerializer, SimpleCourseContentSerializer


class CourseSerializer(serializers.ModelSerializer):
    course_content = CourseContentSerializer(read_only=True)
    course_content_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseContent.objects.all(),
        source='course_content',
        write_only=True
    )

    class Meta:
        model = Course
        fields = '__all__'

class SimpleCourseSerializer(serializers.ModelSerializer):
    course_content = SimpleCourseContentSerializer(read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'course_content']

class CourseDetailSerializer(serializers.ModelSerializer):
    course_content = CourseContentSerializer(read_only=True)
    
    class Meta:
        model = Course
        fields = '__all__'
