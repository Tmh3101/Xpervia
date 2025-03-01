from rest_framework import serializers
from api.models import CourseContent, User
from .category_serializer import CategorySerializer
from .user_serializer import SimpleUserSerializer


class CourseContentSerializer(serializers.ModelSerializer):
    teacher = SimpleUserSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='teacher',
        write_only=True
    )
    categories = CategorySerializer(many=True, read_only=True)


    class Meta:
        model = CourseContent
        fields = '__all__'
        extra_kwargs = {
            'categories': {'required': False}
        }
    

class SimpleCourseContentSerializer(serializers.ModelSerializer):
    teacher = SimpleUserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = CourseContent
        fields = ['id', 'title', 'teacher', 'categories']
        extra_kwargs = {
            'categories': {'required': False}
        }