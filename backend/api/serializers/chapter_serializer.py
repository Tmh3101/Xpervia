from rest_framework import serializers
from api.models import Chapter, CourseContent
from .course_content_serializer import CourseContentSerializer


class ChapterSerializer(serializers.ModelSerializer):
    course_content = CourseContentSerializer(read_only=True)
    course_content_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseContent.objects.all(),
        source='course_content',
        write_only=True
    )

    class Meta:
        model = Chapter
        fields = '__all__'
        extra_kwargs = {
            'course_content': {'read_only': True},
            'order': {'required': False}
        }

    def create(self, validated_data):
        if not validated_data.get('order'):
            validated_data['order'] = Chapter.objects.filter(course_content=validated_data['course_content']).count() + 1
        return Chapter.objects.create(**validated_data)


class SimpleChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order']