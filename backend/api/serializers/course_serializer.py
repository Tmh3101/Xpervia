from api.models.course_model import Course
from rest_framework import serializers
from api.serializers.category_serializer import SimpleCategorySerializer
from api.serializers.user_serializer import SimpleUserSerializer

class CourseSerializer(serializers.ModelSerializer):
    teacher = SimpleUserSerializer(read_only=True)
    categories = SimpleCategorySerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = '__all__'

class SimpleCourseSerializer(serializers.ModelSerializer):
    teacher = SimpleUserSerializer(read_only=True)
    categories = SimpleCategorySerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'title', 'teacher', 'categories']

    