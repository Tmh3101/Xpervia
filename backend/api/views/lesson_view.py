import logging
import uuid
from django.conf import settings
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from api.exceptions.custom_exceptions import FileUploadException
from api.models import Chapter, Lesson, Course, File
from api.serializers import LessonSerializer, FileSerializer
from api.permissions import IsCourseOwner, WasCourseEnrolled
from api.middlewares.authentication import SupabaseJWTAuthentication
from api.services.supabase.storage import upload_file, delete_file

logger = logging.getLogger(__name__)

# Lessons API to list all lessons for a course
class LessonListByCourseAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    authentication_classes = [SupabaseJWTAuthentication]
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
    authentication_classes = [SupabaseJWTAuthentication]
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
    authentication_classes = [SupabaseJWTAuthentication]
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
        uuid = str(uuid.uuid4())
        file_path_list = []
        for file_type in ['video', 'subtitle_vi']:
            if request.FILES.get(file_type):
                try:
                    # file = upload_file(request.FILES.get(file_type))
                    file = request.FILES.get(file_type)
                    file_path = f'lessons/{uuid}/{uuid}.{file.name.split(".")[-1]}'
                    logger.info(f'Uploading {file_type} file to Supabase: {file_path}')
                    upload_file(
                        bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                        path=file_path,
                        file_data=file,
                        content_type=file.content_type
                    )
                except Exception as e:
                    logger.error(f'Error uploading {file_type} file: {str(e)}')
                    for file_path in file_path_list:
                        delete_file(
                            bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                            path=file_path
                        )
                    raise FileUploadException(f'Error uploading {file}: {str(e)}')
                request.data[f'{file_type}_path'] = file_path
                file_path_list.append(file_path)

        attachment = request.data.get('attachment')
        if attachment:
            try:
                file_name = attachment.name
                file_path = f'lessons/{uuid}/{uuid}.{file_name.split(".")[-1]}'
                logger.info(f'Uploading attachment file to Supabase: {file_path}')
                upload_file(
                    bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                    path=file_path,
                    file_data=attachment,
                    content_type=attachment.content_type
                )
                file_serializer = FileSerializer(data={
                    'file_name': file_name,
                    'file_path': file_path,
                })
                if not file_serializer.is_valid():
                    logger.error(f'Error uploading attachment file: {file_serializer.errors}')
                    for file_path in file_path_list:
                        delete_file(
                            bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                            path=file_path
                        )
                    raise FileUploadException(f'Error uploading attachment file: {file_serializer.errors}')
                attachment = file_serializer.save()
            except Exception as e:
                logger.error(f'Error uploading attachment file: {str(e)}')
                for file_path in file_path_list:
                    delete_file(
                        bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                        path=file_path
                    )
                raise FileUploadException(f'Error uploading {file}: {str(e)}')
            request.data['attachment_id'] = attachment.id
            file_path_list.append(file_path)
    
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f'Error creating lesson: {serializer.errors}')
            for file_path in file_path_list:
                delete_file(
                    bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                    path=file_path
                )
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
    authentication_classes = [SupabaseJWTAuthentication]
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
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating lesson with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Lesson not found')

        # Upload the video, subtitle, and attachment to Supabase
        file_path_list = []
        old_file_paths = []
        
        for file_type in ['video', 'subtitle_vi']:
            if request.FILES.get(file_type):
                try:
                    file = request.FILES.get(file_type)
                    file_path = f'lessons/{instance.id}/{instance.id}.{file.name.split(".")[-1]}'
                    logger.info(f'Uploading {file_type} file to Supabase: {file_path}')
                    upload_file(
                        bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                        path=file_path,
                        file_data=file,
                        content_type=file.content_type
                    )
                except Exception as e:
                    logger.error(f'Error uploading {file_type} file: {str(e)}')
                    for file_path in file_path_list:
                        delete_file(
                            bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                            path=file_path
                        )
                    raise FileUploadException(f'Error uploading {file}: {str(e)}')
                request.data[f'{file_type}_path'] = file_path
                file_path_list.append(file_path)
                old_file_paths.append(getattr(instance, f'{file_type}_path'))

        attachment = request.data.get('attachment')    
        if attachment:
            try:
                file_name = attachment.name
                file_path = f'lessons/{instance.id}/{instance.id}.{file_name.split(".")[-1]}'
                logger.info(f'Uploading attachment file to Supabase: {file_path}')
                upload_file(
                    bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                    path=file_path,
                    file_data=attachment,
                    content_type=attachment.content_type
                )
                file_serializer = FileSerializer(data={
                    'file_name': file_name,
                    'file_path': file_path,
                })
                if not file_serializer.is_valid():
                    logger.error(f'Error uploading attachment file: {file_serializer.errors}')
                    for file_path in file_path_list:
                        delete_file(
                            bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                            path=file_path
                        )
                    raise FileUploadException(f'Error uploading {file}: {file_serializer.errors}')
                attachment = file_serializer.save()
            except Exception as e:
                logger.error(f'Error uploading attachment file: {str(e)}')
                for file_path in file_path_list:
                    delete_file(
                        bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                        path=file_path
                    )
                raise FileUploadException(f'Error uploading {file}: {str(e)}')
            request.data['attachment_id'] = attachment.id
            file_path_list.append(attachment.file_path)
            old_attachment_path = getattr(instance, 'attachment_path')
            old_attachment_file_paths = File.objects.filter(file_path=old_attachment_path).first().file_path
            old_file_paths.append(old_attachment_file_paths)
 
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            logger.error(f'Error updating lesson: {serializer.errors}')
            for file_path in file_path_list:
                delete_file(
                    bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                    path=file_path
                )
            raise ValidationError(f'Error updating lesson: {serializer.errors}')
        
        self.perform_update(serializer)

        # Delete the old video, subtitle, and attachment from Supabase
        for file_path in old_file_paths:
            delete_file(
                bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                path=file_path
            )

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
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        logger.info(f"Deleting lesson with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Lesson not found')
        
        try: 
            if instance.video_path:
                delete_file(
                    bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                    path=instance.video_path
                )
            if instance.subtitle_vi_path:
                delete_file(
                    bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                    path=instance.subtitle_vi_path
                )
            if instance.attachment:
                delete_file(
                    bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                    path=instance.attachment.file_path
                )
        except Exception as e:
            logger.error(f'Error deleting lesson files: {str(e)}')
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