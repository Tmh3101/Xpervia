from rest_framework import serializers
from api.models import LessonCompletion, Lesson
from .lesson_serializer import SimpleLessonSerializer 
from api.models import User
from .user_serializer import UserSerializer


class LessonCompletionSerializer(serializers.ModelSerializer):
    lesson = SimpleLessonSerializer(read_only=True)
    lesson_id = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(),
        source='lesson',
        write_only=True
    )

    student = UserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='student',
        write_only=True
    )

    class Meta:
        model = LessonCompletion
        fields = '__all__'