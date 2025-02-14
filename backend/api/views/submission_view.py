from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.exceptions.custom_exceptions import FileUploadException
from api.models.submission_model import Submission
from api.models.assignment_model import Assignment
from api.serializers.submission_serializer import SubmissionSerializer
from api.permissions.teacher_permissions_checker import IsCourseOwner
from api.permissions.student_permissions_checker import WasCourseEnrolled
from api.services.google_drive_service import upload_file, delete_file

# Submissions list API view for listing all submissions by assignment_id
class SubmissionListByAssignmentAPIView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        assignment_id = self.kwargs.get('assignment_id')
        if not Assignment.objects.filter(id=assignment_id).exists():
            raise NotFound("Assignment does not exist")
        return Submission.objects.filter(assignment_id=assignment_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Submissions for the assignment have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
# Submission detail API view for creating
class SubmissionCreateAPIView(generics.CreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled]

    def create(self, request, *args, **kwargs):

        assignment_id = self.kwargs.get('assignment_id')
        if not Assignment.objects.filter(id=assignment_id).exists():
            raise NotFound("Assignment does not exist")
        request.data['assignment_id'] = assignment_id

        request.data['student_id'] = request.user.id

        try:
            request.data['file_id'] = upload_file(request.FILES.get('file'))
            request.data.pop('file', None)
        except Exception as e:
            raise FileUploadException(f'File upload failed: {str(e)}')
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            delete_file(request.data['file_id'])
            raise ValidationError(serializer.errors)
        
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'Submission has been created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    

