from api.models.course_model import Course
from api.models.user_model import User
from rest_framework import serializers
from api.serializers.category_serializer import CategorySerializer
from api.serializers.user_serializer import SimpleUserSerializer

class CourseSerializer(serializers.ModelSerializer):
    teacher = SimpleUserSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='teacher',
        write_only=True
    )
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        extra_kwargs = {
            'categories': {'required': False}
        }
    

class SimpleCourseSerializer(serializers.ModelSerializer):
    teacher = SimpleUserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'teacher', 'categories']
        extra_kwargs = {
            'categories': {'required': False}
        }