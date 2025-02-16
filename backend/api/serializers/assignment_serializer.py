from rest_framework import serializers
from api.models import Assignment, Lesson
from .lesson_serializer import SimpleLessonSerializer


class AssignmentSerializer(serializers.ModelSerializer):
    lesson = SimpleLessonSerializer(read_only=True)
    lesson_id = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(),
        source='lesson',
        write_only=True)


    class Meta:
        model = Assignment
        fields = '__all__'


class SimpleAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'start_at', 'due_at']