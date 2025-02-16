from rest_framework import serializers
from api.models import CourseDetail, Course
from .course_serializer import CourseSerializer


class CourseDetailSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True
    )


    class Meta:
        model = CourseDetail
        fields = '__all__'
        extra_kwargs = {
            'course': {'read_only': True},
        }


class CourseDetailDetailSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    class Meta:
        model = CourseDetail
        fields = '__all__'
