from rest_framework import serializers
from api.models import CourseContent
from .category_serializer import CategorySerializer
from api.models import User


class CourseContentSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = CourseContent
        fields = '__all__'
        extra_kwargs = {
            'teacher_id': {'write_only': True},
            'categories': {'required': False}
        }

    def get_teacher(self, obj):
        if obj.teacher_id:
            return User.objects.get(id=obj.teacher_id).to_dict()
        return None
    

class SimpleCourseContentSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = CourseContent
        fields = ['id', 'title', 'teacher', 'categories']
        extra_kwargs = {
            'teacher_id': {'write_only': True},
            'categories': {'required': False}
        }

    def get_teacher(self, obj):
        if obj.teacher_id:
            return User.objects.get(id=obj.teacher_id).to_dict()
        return None