from rest_framework import serializers
from api.models import CourseContent, Course
from .course_content_serializer import CourseContentSerializer, SimpleCourseContentSerializer


class CourseSerializer(serializers.ModelSerializer):
    course_content = CourseContentSerializer(read_only=True)
    course_content_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseContent.objects.all(),
        source='course_content',
        write_only=True
    )

    num_students = serializers.IntegerField(read_only=True)
    num_favorites = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

class SimpleCourseSerializer(serializers.ModelSerializer):
    course_content = SimpleCourseContentSerializer(read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'course_content']

class CourseListItemSerializer(serializers.ModelSerializer):
    # Các trường annotate (read_only)
    num_students = serializers.IntegerField(read_only=True)
    num_favorites = serializers.IntegerField(read_only=True)
    progress = serializers.SerializerMethodField()
    course_content = CourseContentSerializer(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

    def get_progress(self, obj):
        # Lấy từ progress_map do view truyền vào context
        mp = self.context.get("progress_map") or {}
        return mp.get(obj.course_content_id, 0.0)
