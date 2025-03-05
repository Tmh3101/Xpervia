from rest_framework import serializers
from api.models import Submission, Assignment, User, File
from .user_serializer import SimpleUserSerializer
from .assignment_serializer import SimpleAssignmentSerializer
from .file_serializer import FileSerializer


class SubmissionSerializer(serializers.ModelSerializer):
    assignment = SimpleAssignmentSerializer(read_only=True)
    assignment_id = serializers.PrimaryKeyRelatedField(
        queryset=Assignment.objects.all(),
        source='assignment',
        write_only=True
    )

    student = SimpleUserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='student',
        write_only=True
    )

    file = FileSerializer(read_only=True)
    file_id = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        source='file',
        write_only=True
    )

    class Meta:
        model = Submission
        fields = '__all__'

class SimpleSubmissionSerializer(serializers.ModelSerializer):
    file = FileSerializer(read_only=True)
    class Meta:
        model = Submission
        fields = ['id', 'file', 'created_at']