from rest_framework import serializers
from api.models import LessonCompletion, Lesson
from .lesson_serializer import SimpleLessonSerializer
from api.models import User


class LessonCompletionSerializer(serializers.ModelSerializer):
    lesson = SimpleLessonSerializer(read_only=True)
    lesson_id = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(),
        source='lesson',
        write_only=True
    )

    student = serializers.SerializerMethodField()
    
    class Meta:
        model = LessonCompletion
        fields = '__all__'
        extra_kwargs = {
            'student_id': {'write_only': True},
            'created_at': {'read_only': True}
        }

    def get_student(self, obj):
        if obj.student_id:
            return User.objects.get(id=obj.student_id).to_dict()
        return None