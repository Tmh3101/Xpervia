from rest_framework import serializers
from api.models import Submission, Assignment, File
from .assignment_serializer import SimpleAssignmentSerializer
from .file_serializer import FileSerializer
from api.models import User
from .user_serializer import UserSerializer


class SubmissionSerializer(serializers.ModelSerializer):
    assignment = SimpleAssignmentSerializer(read_only=True)
    assignment_id = serializers.PrimaryKeyRelatedField(
        queryset=Assignment.objects.all(),
        source='assignment',
        write_only=True
    )

    student = UserSerializer(read_only=True)
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