from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from api.exceptions.custom_exceptions import FileUploadException
from api.models import Assignment, Submission
from api.serializers import SubmissionSerializer, FileSerializer
from api.permissions import IsSubmissionOwner, IsCourseOwner, WasCourseEnrolled
from api.services.google_drive_service import upload_file, delete_file


# Submissions API to list all submissions by assignment
class SubmissionListByAssignmentAPIView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]

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
            'submissions': serializer.data
        }, status=status.HTTP_200_OK)
    

# Submission API to create a submission
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
            file = upload_file(request.FILES.get('file'))
            file_serializer = FileSerializer(data=file)
            if not file_serializer.is_valid():
                raise ValidationError(file_serializer.errors)
            file = file_serializer.save()
            request.data['file_id'] = file.id
            request.data.pop('file')
        except Exception as e:
            raise FileUploadException(f'File upload failed: {str(e)}')
        
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            delete_file(request.data['file_id'])
            raise ValidationError(serializer.errors)
        
        try:
            self.perform_create(serializer)
        except Exception as e:
            delete_file(request.data['file_id'])
            raise ValidationError(str(e))
        
        return Response({
            'success': True,
            'message': 'Submission has been created successfully',
            'submission': serializer.data
        }, status=status.HTTP_201_CREATED)
    

# Submission API to retrieve a submission
class SubmissionRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsSubmissionOwner | IsCourseOwner]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            raise NotFound('Submission does not exist')
        
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Submission has been retrieved successfully',
            'submission': serializer.data
        }, status=status.HTTP_200_OK)
    

# Submission API to update a submission
class SubmissionUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsSubmissionOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            raise NotFound('Submission does not exist')

        old_file_id = instance.file_id
        try:
            file = upload_file(request.FILES.get('file'))
            file_serializer = FileSerializer(data=file)
            if not file_serializer.is_valid():
                raise ValidationError(file_serializer.errors)
            file = file_serializer.save()
            request.data['file_id'] = file.id
            request.data.pop('file')
        except Exception as e:
            raise FileUploadException(f'File upload failed: {str(e)}')

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            delete_file(request.data['file_id'])
            raise ValidationError(serializer.errors)
        
        self.perform_update(serializer)
        delete_file(old_file_id)
        return Response({
            'success': True,
            'message': 'Submission has been updated successfully',
            'submission': serializer.data
        }, status=status.HTTP_200_OK)
    

# Submission API to delete a submission
class SubmissionDeleteAPIView(generics.DestroyAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsSubmissionOwner | IsCourseOwner]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            raise NotFound('Submission does not exist')
        
        self.perform_destroy(instance)
        delete_file(instance.file.id)
        return Response({
            'success': True,
            'message': 'Submission has been deleted successfully',
        }, status=status.HTTP_204_NO_CONTENT)
    

