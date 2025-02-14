from rest_framework import serializers
from api.models.submission_model import Submission
from api.models.assignment_model import Assignment
from api.models.user_model import User
from api.serializers.user_serializer import SimpleUserSerializer
from api.serializers.assignment_serializer import SimpleAssignmentSerializer

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

    class Meta:
        model = Submission
        fields = '__all__'