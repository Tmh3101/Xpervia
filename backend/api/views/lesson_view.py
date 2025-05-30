import logging
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from api.exceptions.custom_exceptions import FileUploadException
from api.models import Chapter, Lesson, Course, File
from api.serializers import LessonSerializer, FileSerializer
from api.permissions import IsCourseOwner, WasCourseEnrolled
from api.services.google_drive_service import upload_file, delete_file
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)

# Lessons API to list all lessons for a course
class LessonListByCourseAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled | IsCourseOwner]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        if not Course.objects.filter(id=course_id).exists():
            raise NotFound("Course does not exist")
        course = Course.objects.get(id=course_id)
        return Lesson.objects.filter(course_content_id=course.course_content.id)

    def list(self, request, *args, **kwargs):
        logger.info(f"Listing lessons for course ID: {self.kwargs.get('course_id')}")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.info("Successfully listed lessons for course")
        return Response({
            'success': True,
            'message': 'Lessons for the course have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        

# Lessons API to list all lessons by chapter
class LessonListByChapterAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled | IsCourseOwner]

    def get_queryset(self):
        chapter_id = self.kwargs.get('chapter_id')
        if not Chapter.objects.filter(id=chapter_id).exists():
            raise Http404("Chapter does not exist or does not belong to the specified course")
        return Lesson.objects.filter(chapter_id=chapter_id)

    def list(self, request, *args, **kwargs):
        logger.info(f"Listing lessons for chapter ID: {self.kwargs.get('chapter_id')}")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        logger.info("Successfully listed lessons for chapter")
        return Response({
            'success': True,
            'message': 'Lessons for the course and chapter have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        

# Lesson API to create a lesson
class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating lesson for course ID: {self.kwargs.get('course_id')}")
        # Check if the course_id
        course = Course.objects.filter(id=self.kwargs.get('course_id')).first()
        if not course:
            raise NotFound('Course not found')
        request.data['course_content_id'] = course.course_content.id

        chapter_id = self.request.data.get('chapter_id')
        if chapter_id:
            chapter = Chapter.objects.filter(id=chapter_id).first()
            if not chapter:
                raise NotFound('Chapter not found')
            
            course = Course.objects.filter(id=self.kwargs.get('course_id')).first()
            if course and (chapter.course_content.id != course.course_content.id):
                raise NotFound('Chapter does not belong to the specified course')

        # Upload the video, subtitle, and attachment to Google Drive
        file_id_list = []
        for file_type in ['video', 'subtitle_vi']:
            if request.FILES.get(file_type):
                try:
                    file = upload_file(request.FILES.get(file_type))
                except Exception as e:
                    for file_id in file_id_list:
                        delete_file(file_id)
                    raise FileUploadException(f'Error uploading {file}: {str(e)}')
                file_id = file.get('file_id')
                request.data[f'{file_type}_id'] = file_id
                file_id_list.append(file_id)

        if request.FILES.get('attachment'):
            try:
                file = upload_file(request.FILES.get('attachment'))
                file_serializer = FileSerializer(data=file)
                if not file_serializer.is_valid():
                    raise FileUploadException(f'Error uploading {file}: {file_serializer.errors}')
                attachment = file_serializer.save()
            except Exception as e:
                for file_id in file_id_list:
                    delete_file(file_id)
                raise FileUploadException(f'Error uploading {file}: {str(e)}')
            request.data['attachment_id'] = attachment.id
            file_id_list.append(attachment.id)
    
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            for file_id in file_id_list:
                delete_file(file_id)
            raise ValidationError(f'Error creating lesson: {serializer.errors}')
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        logger.info("Lesson created successfully")
        return Response({
            'success': True,
            'message': 'Lesson created successfully',
            'lesson': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    

# Lesson API to retrieve a lesson
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled | IsCourseOwner]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving lesson with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Lesson not found')
        
        serializer = self.get_serializer(instance)
        logger.info("Lesson retrieved successfully")
        return Response({
            'success': True,
            'message': 'Lesson retrieved successfully',
            'lesson_detail': serializer.data
        }, status=status.HTTP_200_OK)


# Lesson API to update a lesson
class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating lesson with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Lesson not found')

        # Upload the video, subtitle, and attachment to Google Drive
        file_id_list = []
        old_file_ids = []
        
        for file_type in ['video', 'subtitle_vi']:
            if request.FILES.get(file_type):
                try:
                    file = upload_file(request.FILES.get(file_type))
                except Exception as e:
                    for file_id in file_id_list:
                        delete_file(file_id)
                    raise FileUploadException(f'Error uploading {file}: {str(e)}')
                file_id = file.get('file_id')
                request.data[f'{file_type}_id'] = file_id
                file_id_list.append(file_id)
                old_file_ids.append(getattr(instance, f'{file_type}_id'))
            
        if request.FILES.get('attachment'):
            try:
                file = upload_file(request.FILES.get('attachment'))
                file_serializer = FileSerializer(data=file)
                if not file_serializer.is_valid():
                    raise FileUploadException(f'Error uploading {file}: {file_serializer.errors}')
                attachment = file_serializer.save()
            except Exception as e:
                for file_id in file_id_list:  
                    delete_file(file_id) 
                raise FileUploadException(f'Error uploading {file}: {str(e)}')
            request.data['attachment_id'] = attachment.id
            file_id_list.append(attachment.file_id)
            old_attachment_id = getattr(instance, 'attachment_id')
            old_attachment_file_ids = File.objects.get(id=old_attachment_id).file_id
            old_file_ids.append(old_attachment_file_ids)
 
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            for file_id in file_id_list:
                delete_file(file_id)
            raise ValidationError(f'Error updating lesson: {serializer.errors}')
        
        self.perform_update(serializer)

        # Delete the old video, subtitle, and attachment from Google Drive
        for old_file_id in old_file_ids:
            delete_file(old_file_id)

        logger.info("Lesson updated successfully")
        return Response({
            'success': True,
            'message': 'Lesson updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

# Lesson API to delete a lesson
class LessonDeleteAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        logger.info(f"Deleting lesson with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Lesson not found')
        
        try: 
            if instance.video_id:
                delete_file(instance.video_id)
            if instance.subtitle_vi_id:
                delete_file(instance.subtitle_vi_id)
            if instance.attachment:
                delete_file(instance.attachment.file_id)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error deleting lesson files: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        self.perform_destroy(instance)
        logger.info("Lesson deleted successfully")
        return Response({
            'success': True,
            'message': f'Lesson {instance} deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)