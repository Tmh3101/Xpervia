from rest_framework import serializers
from api.models import SubmissionScore, Submission
from .submission_serializer import SubmissionSerializer


class SubmissionScoreSerializer(serializers.ModelSerializer):
    submission = SubmissionSerializer(read_only=True)
    submission_id = serializers.PrimaryKeyRelatedField(
        queryset=Submission.objects.all(),
        source='submission',
        write_only=True
    )
    
    
    class Meta:
        model = SubmissionScore
        fields = '__all__'