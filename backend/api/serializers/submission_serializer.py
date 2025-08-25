from rest_framework import serializers
from api.models import Submission, Assignment, File
from .assignment_serializer import SimpleAssignmentSerializer
from .file_serializer import FileSerializer
from api.models import User


class SubmissionSerializer(serializers.ModelSerializer):
    assignment = SimpleAssignmentSerializer(read_only=True)
    assignment_id = serializers.PrimaryKeyRelatedField(
        queryset=Assignment.objects.all(),
        source='assignment',
        write_only=True
    )

    student = serializers.SerializerMethodField()

    file = FileSerializer(read_only=True)
    file_id = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        source='file',
        write_only=True
    )

    class Meta:
        model = Submission
        fields = '__all__'
        extra_kwargs = {
            'student_id': {'write_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }
    
    def get_student(self, obj):
        if obj.student_id:
            return User.objects.get(id=obj.student_id).to_dict()
        return None
    

class SimpleSubmissionSerializer(serializers.ModelSerializer):
    file = FileSerializer(read_only=True)
    student = serializers.SerializerMethodField()
    
    class Meta:
        model = Submission
        fields = ['id', 'file', 'student', 'created_at']
        extra_kwargs = {
            'student_id': {'write_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def get_student(self, obj):
        if obj.student_id:
            return User.objects.get(id=obj.student_id).to_dict()
        return None