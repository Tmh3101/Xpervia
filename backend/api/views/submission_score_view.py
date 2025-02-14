from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.exceptions.custom_exceptions import FileUploadException
from api.models.submission_model import Submission
from api.models.submission_score_model import SubmissionScore
from api.models.assignment_model import Assignment
from api.serializers.submission_score_serializer import SubmissionScoreSerializer
from api.serializers.submission_serializer import SubmissionSerializer
from api.permissions.teacher_permissions_checker import IsCourseOwner
from api.permissions.student_permissions_checker import WasCourseEnrolled
from api.services.google_drive_service import upload_file, delete_file

# Submission score API view for get submission score by submission_id
class SubmissionScoreDetailAPIView(generics.RetrieveAPIView):
    serializer_class = SubmissionScoreSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        submission_id = self.kwargs.get('submission_id')
        if not Submission.objects.filter(id=submission_id).exists():
            raise NotFound("Submission does not exist")
        if not SubmissionScore.objects.filter(submission_id=submission_id).exists():
            raise NotFound("Submission score does not exist")
        return SubmissionScore.objects.get(submission_id=submission_id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Submission score has been retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

# Submission score API view for creating
class SubmissionScoreCreateAPIView(generics.CreateAPIView):
    queryset = SubmissionScore.objects.all()
    serializer_class = SubmissionScoreSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]

    def create(self, request, *args, **kwargs):
        submission_id = self.kwargs.get('submission_id')
        if not Submission.objects.filter(id=submission_id).exists():
            raise NotFound("Submission does not exist")
        request.data['submission_id'] = submission_id

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
            
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'Submission score has been created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


