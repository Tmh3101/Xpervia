from rest_framework import serializers
from api.models import Lesson, CourseContent, Chapter, File
from .course_content_serializer import SimpleCourseContentSerializer
from .chapter_serializer import SimpleChapterSerializer
from .file_serializer import FileSerializer


class LessonSerializer(serializers.ModelSerializer):
    course_content = SimpleCourseContentSerializer(read_only=True)
    course_content_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseContent.objects.all(),
        source='course_content',
        write_only=True
    )

    chapter = SimpleChapterSerializer(read_only=True)
    chapter_id = serializers.PrimaryKeyRelatedField(
        queryset=Chapter.objects.all(),
        source='chapter',
        write_only=True,
        required=False
    )

    attachment = FileSerializer(read_only=True)
    attachment_id = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        source='attachment',
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
            validated_data['order'] = Lesson.objects.filter(course_content=validated_data['course_content']).count() + 1
        return super().create(validated_data)


class SimpleLessonSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'order', 'is_visible', 'created_at']