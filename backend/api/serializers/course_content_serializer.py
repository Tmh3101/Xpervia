from rest_framework import serializers
from api.models import CourseContent
from .category_serializer import CategorySerializer
from api.models import User
from .user_serializer import UserSerializer


class CourseContentSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    teacher = UserSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='teacher',
        write_only=True
    )

    class Meta:
        model = CourseContent
        fields = '__all__'
        extra_kwargs = {
            'categories': {'required': False}
        }


class SimpleCourseContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseContent
        fields = ['id', 'title', 'teacher', 'categories']