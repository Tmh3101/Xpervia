import os
from django.conf import settings
from django.http import Http404
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.models.course_model import Course
from api.models.chapter_model import Chapter
from api.models.lesson_model import Lesson
from api.serializers.course_serializer import CourseSerializer
from api.serializers.chapter_serializer import ChapterSerializer
from api.serializers.lesson_serializer import LessonSerializer
from api.roles import IsTeacher, IsCourseOwner
from api.services.google_drive_service import upload_file, delete_file

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


# Course API View to create a course
class CourseCreateAPIView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    def create(self, request, *args, **kwargs):

        # Upload the thumbnail
        try:
            thumbnail_id = upload_file(request.FILES.get('thumbnail'))
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
    

# Course API View to retrieve a course
class CourseRetrievelAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            return Response({
                'success': False,
                'message': 'Course not found',
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Course retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
# Course API View to update and delete a course
class CourseUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher & IsCourseOwner]
    lookup_field = 'id'
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            return Response({
                'success': False,
                'message': 'Course not found',
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)

        # Upload the thumbnail to Google Drive
        old_thumbnail_id = None
        if request.FILES.get('thumbnail'):
            try:
                thumbnail_id = upload_file(request.FILES.get('thumbnail'))
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
                    delete_file(old_thumbnail_id)
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
        try:
            instance = self.get_object()
        except Http404 as e:
            return Response({
                'success': False,
                'message': 'Course not found',
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            delete_file(instance.thumbnail_id)
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
    

# Course detail API view for retrieving a course with all chapters and lessons
class CourseDetailAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            return Response({
                'success': False,
                'message': 'Course not found',
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        course_detail_data = serializer.data.copy()

        # Get chapters and lessons
        chapters = Chapter.objects.filter(course=instance)
        if chapters.exists():
            chapters_serializer = ChapterSerializer(chapters, many=True)
            for chapter_data in chapters_serializer.data:
                chapter_id = chapter_data['id']
                lessons = Lesson.objects.filter(chapter_id=chapter_id)
                lessons_serializer = LessonSerializer(lessons, many=True)
                chapter_data['lessons'] = lessons_serializer.data
            course_detail_data['chapters'] = chapters_serializer.data
        else:
            lessons = Lesson.objects.filter(course=instance, chapter__isnull=True)
            lessons_serializer = LessonSerializer(lessons, many=True)
            course_detail_data['lessons'] = lessons_serializer.data

        return Response({
            'success': True,
            'message': 'Course retrieved successfully',
            'data': course_detail_data
        }, status=status.HTTP_200_OK)