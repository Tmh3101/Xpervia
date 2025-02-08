from rest_framework import serializers
from api.models.chapter_model import Chapter

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'course': {'read_only': True},
        }