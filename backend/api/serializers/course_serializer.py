from api.models.course_model import Course
from rest_framework import serializers

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'teacher': {'read_only': True},
        }