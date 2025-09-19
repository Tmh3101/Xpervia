import logging
from django.conf import settings
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from api.exceptions.custom_exceptions import FileUploadException
from api.models import Assignment, Submission, File
from api.serializers import SubmissionSerializer, FileSerializer
from api.permissions import IsSubmissionOwner, IsCourseOwner, WasCourseEnrolled
from api.middlewares.authentication import SupabaseJWTAuthentication
from api.services.supabase.storage import upload_file, delete_file

logger = logging.getLogger(__name__)

# Submissions API to list all submissions by assignment
class SubmissionListByAssignmentAPIView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]

    def get_queryset(self):
        assignment_id = self.kwargs.get('assignment_id')
        if not Assignment.objects.filter(id=assignment_id).exists():
            raise NotFound("Assignment does not exist")
        return Submission.objects.filter(assignment_id=assignment_id)

    def list(self, request, *args, **kwargs):
        logger.info(f"Listing submissions for assignment ID: {self.kwargs.get('assignment_id')}")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.info("Successfully listed submissions")
        return Response({
            'success': True,
            'message': 'Submissions for the assignment have been listed successfully',
            'submissions': serializer.data
        }, status=status.HTTP_200_OK)
    

# Submission API to create a submission
class SubmissionCreateAPIView(generics.CreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled]

    def create(self, request, *args, **kwargs):
        assignment_id = self.kwargs.get('assignment_id')
        logger.info(f"Creating submission for assignment ID: {assignment_id}")
        assignment = Assignment.objects.filter(id=assignment_id).first()
        if not assignment:
            raise NotFound("Assignment does not exist")
        request.data['assignment_id'] = assignment.id
        request.data['student_id'] = request.user.id

        try:
            file = request.FILES.get('file')
            file_name = file.name
            file_path = f'submissions/{assignment.id}/{request.user.id}.{file_name.split(".")[-1]}'
            logger.info(f"Uploading file to Supabase storage at path: {file_path}")
            upload_file(
                bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                path=file_path,
                file_data=file,
                content_type=file.content_type,
            )
            file_serializer = FileSerializer(data={
                'file_name': file_name,
                'file_path': file_path,
            })
            if not file_serializer.is_valid():
                logger.error(f"File serializer validation failed: {file_serializer.errors}")
                delete_file(
                    bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                    path=file_path,
                )
                raise ValidationError(file_serializer.errors)
            file = file_serializer.save()
            request.data['file_id'] = file.id
            request.data.pop('file')
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            delete_file(
                bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                path=file_path,
            )
            raise FileUploadException(f'File upload failed: {str(e)}')
        
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            logger.error(f"Submission serializer validation failed: {serializer.errors}")
            delete_file(
                bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                path=file_path,
            )
            File.objects.filter(id=request.data.get('file_id')).delete()
            raise ValidationError(serializer.errors)
        
        try:
            self.perform_create(serializer)
        except Exception as e:
            logger.error(f"Submission creation failed: {str(e)}")
            delete_file(
                bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                path=file_path,
            )
            File.objects.filter(id=request.data.get('file_id')).delete()
            raise ValidationError(str(e))
        
        logger.info("Submission created successfully")
        return Response({
            'success': True,
            'message': 'Submission has been created successfully',
            'submission': serializer.data
        }, status=status.HTTP_201_CREATED)
    

# Submission API to retrieve a submission
class SubmissionRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsSubmissionOwner | IsCourseOwner]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving submission with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404:
            raise NotFound('Submission does not exist')
        
        serializer = self.get_serializer(instance)
        logger.info("Submission retrieved successfully")
        return Response({
            'success': True,
            'message': 'Submission has been retrieved successfully',
            'submission': serializer.data
        }, status=status.HTTP_200_OK)
    

# Submission API to update a submission
class SubmissionUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsSubmissionOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating submission with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404:
            raise NotFound('Submission does not exist')

        old_file = instance.file
        try:
            new_file = request.FILES.get('file')
            new_file_name = file.name
            new_file_path = f'submissions/{instance.assignment.id}/{request.user.id}.{file_name.split(".")[-1]}'
            logger.info(f"Uploading new file to Supabase storage at path: {new_file_path}")
            upload_file(
                bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                path=new_file_path,
                file_data=new_file,
                content_type=new_file.content_type,
            )
            # Update file serializer
            file = {
                'file_name': new_file_name,
                'file_path': new_file_path,
            }
            file_serializer = FileSerializer(old_file, data=file, partial=True)
            if not file_serializer.is_valid():
                logger.error(f"File serializer validation failed: {file_serializer.errors}")
                delete_file(
                    bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                    path=new_file_path,
                )
                raise ValidationError(file_serializer.errors)
            file = file_serializer.save()
            request.data['file_id'] = file.id
            request.data.pop('file')
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            delete_file(
                bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                path=new_file_path,
            )
            raise FileUploadException(f'File upload failed: {str(e)}')

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            logger.error(f"Submission serializer validation failed: {serializer.errors}")
            delete_file(
                bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                path=new_file_path,
            )
            raise ValidationError(serializer.errors)
        
        self.perform_update(serializer)
        delete_file(
            bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
            path=old_file.file_path,
        )
        logger.info("Submission updated successfully")
        return Response({
            'success': True,
            'message': 'Submission has been updated successfully',
            'submission': serializer.data
        }, status=status.HTTP_200_OK)
    

# Submission API to delete a submission
class SubmissionDeleteAPIView(generics.DestroyAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsSubmissionOwner | IsCourseOwner]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        logger.info(f"Deleting submission with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404:
            raise NotFound('Submission does not exist')
        
        self.perform_destroy(instance)
        delete_file(
            bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
            path=instance.file.file_path,
        )
        instance.file.delete()
        logger.info("Submission deleted successfully")
        return Response({
            'success': True,
            'message': 'Submission has been deleted successfully',
        }, status=status.HTTP_204_NO_CONTENT)


