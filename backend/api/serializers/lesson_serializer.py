from rest_framework import serializers
from api.models import Lesson, Course, Chapter
from .course_serializer import SimpleCourseSerializer
from .chapter_serializer import SimpleChapterSerializer


class LessonSerializer(serializers.ModelSerializer):
    course = SimpleCourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True
    )

    chapter = SimpleChapterSerializer(read_only=True)
    chapter_id = serializers.PrimaryKeyRelatedField(
        queryset=Chapter.objects.all(),
        source='chapter',
        write_only=True,
        required=False
    )


    class Meta:
        model = Lesson
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'order': {'required': False}
        }

    def create(self, validated_data):
        if not validated_data.get('order'):
            validated_data['order'] = Lesson.objects.filter(course=validated_data['course']).count() + 1
        return super().create(validated_data)


class SimpleLessonSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'order', 'created_at']