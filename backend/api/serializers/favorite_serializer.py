from api.models import Favorite, Course, User
from .user_serializer import UserSerializer
from .course_serializer import CourseSerializer
from rest_framework import serializers


class FavoriteSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='student',
        write_only=True
    )

    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True
    )
    
    class Meta:
        model = Favorite
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True}
        }