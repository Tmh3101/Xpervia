from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..models.course_model import Course
from ..serializers.course_serializer import CourseSerializer
from ..roles import IsTeacher, IsTeacherAndOwner
from ..service.google_drive_service import upload_file_to_drive, delete_file_from_drive
from django.core.files.storage import default_storage
import os
from django.conf import settings

# Course API View to list all courses
class CourseListAPIView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = CourseSerializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'All courses have been listed successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'No courses found'
        }, status=status.HTTP_404_NOT_FOUND)
    

def upload_thumbnail(thumbnail_file):
    try:
        # Save the thumbnail file temporarily on the server
        file_path = os.path.join(settings.MEDIA_ROOT, thumbnail_file.name)
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in thumbnail_file.chunks():
                destination.write(chunk)

        # Upload the thumbnail file to Google Drive
        file_id = upload_file_to_drive(file_path, thumbnail_file.name)
    except Exception as e:
        raise "Error uploading thumbnail to Google Drive"
    
    # Remove the temporary file
    os.remove(file_path)
    return file_id

# Course API View to create a course
class CourseCreateAPIView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    def create(self, request, *args, **kwargs):

        # Upload the thumbnail to Google Drive
        try:
            thumbnail_id = upload_thumbnail(request.FILES.get('thumbnail'))
            request.data['thumbnail_id'] = thumbnail_id
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error uploading thumbnail',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)    

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({
                'success': True,
                'message': 'Course created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED, headers=headers)
        
        return Response({
            'success': False,
            'message': 'Course not created',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class CourseRetrievelAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs.get(lookup_url_kwarg)

        try:
            obj = queryset.get(**{self.lookup_field: lookup_value})
        except (Course.DoesNotExist, ValidationError, ValueError):
            raise Http404("Course not found")

        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Course retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

class CourseUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherAndOwner]
    lookup_field = 'id'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs.get(lookup_url_kwarg)

        try:
            obj = queryset.get(**{self.lookup_field: lookup_value})
        except (Course.DoesNotExist, ValidationError, ValueError):
            raise Http404("Course not found")

        self.check_object_permissions(self.request, obj)
        return obj
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_thumbnail_id = None

        # Upload the thumbnail to Google Drive
        if request.FILES.get('thumbnail'):
            try:
                thumbnail_id = upload_thumbnail(request.FILES.get('thumbnail'))
                request.data['thumbnail_id'] = thumbnail_id
                old_thumbnail_id = instance.thumbnail_id
            except Exception as e:
                return Response({
                    'success': False,
                    'message': 'Error uploading thumbnail',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)

            if request.FILES.get('thumbnail'):
                try:
                    delete_file_from_drive(old_thumbnail_id)
                except Exception as e:
                    return Response({
                        'success': False,
                        'message': 'Error deleting old thumbnail',
                        'error': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({
                'success': True,
                'message': 'Course updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Course not updated',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            delete_file_from_drive(instance.thumbnail_id)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error deleting thumbnail',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)

        return Response({
            'success': True,
            'message': 'Course deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)