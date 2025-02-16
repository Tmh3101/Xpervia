from rest_framework import serializers
from api.models import Chapter, Course
from .course_serializer import CourseSerializer


class ChapterSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True
    )


    class Meta:
        model = Chapter
        fields = '__all__'
        extra_kwargs = {
            'course': {'read_only': True},
            'order': {'required': False}
        }

    def create(self, validated_data):
        if not validated_data.get('order'):
            validated_data['order'] = Chapter.objects.filter(course=validated_data['course']).count() + 1
        return Chapter.objects.create(**validated_data)


class SimpleChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order']