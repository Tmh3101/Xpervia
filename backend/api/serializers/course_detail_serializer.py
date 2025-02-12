from rest_framework import serializers
from api.models.course_detail_model import CourseDetail
from api.models.course_model import Course
from api.serializers.course_serializer import CourseSerializer

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
            'id': {'read_only': True},
            'course': {'read_only': True},
            'discount': {'required': False}
        }

# Course detail detail serializer
class CourseDetailDetailSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    class Meta:
        model = CourseDetail
        fields = '__all__'
