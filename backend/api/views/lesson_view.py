from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.exceptions.custom_exceptions import FileUploadException
from api.models import Course, Chapter, Lesson
from api.serializers import LessonSerializer
from api.permissions import IsCourseOwner, WasCourseEnrolled
from api.services.google_drive_service import upload_file, delete_file


# Lessons API to list all lessons for a course
class LessonListByCourseAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled | IsCourseOwner]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        if not Course.objects.filter(id=course_id).exists():
            raise NotFound("Course does not exist")
        return Lesson.objects.filter(course_id=course_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Lessons for the course have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        

# Lessons API to list all lessons by chapter
class LessonListByChapterAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled | IsCourseOwner]

    def get_queryset(self):
        chapter_id = self.kwargs.get('chapter_id')
        if not Chapter.objects.filter(id=chapter_id).exists():
            raise Http404("Chapter does not exist or does not belong to the specified course")
        return Lesson.objects.filter(chapter_id=chapter_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Lessons for the course and chapter have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        

# Lesson API to create a lesson
class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]

    def create(self, request, *args, **kwargs):
        # Check if the course_id
        course = Course.objects.filter(id=self.kwargs.get('course_id')).first()
        if not course:
            raise NotFound('Course not found')
        request.data['course_id'] = course.id

        chapter_id = self.request.data.get('chapter_id')
        if chapter_id:
            chapter = Chapter.objects.filter(id=chapter_id).first()
            if not chapter:
                raise NotFound('Chapter not found')

            if chapter.course.id != self.kwargs.get('course_id'):
                raise NotFound('Chapter does not belong to the specified course')

        # Upload the video, subtitle, and attachment to Google Drive
        file_id_list = []
        for file in ['video', 'subtitle', 'attachment']:
            if request.FILES.get(file):
                try:
                    file_id = upload_file(request.FILES.get(file))
                except Exception as e:
                    for file_id in file_id_list:
                        delete_file(file_id)
                    raise FileUploadException(f'Error uploading {file}: {str(e)}')
                file_id_list.append(file_id)
                request.data[f'{file}_id'] = file_id

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            for file_id in file_id_list:
                delete_file(file_id)
            raise ValidationError(f'Error creating lesson: {serializer.errors}')
        
        try:
            self.perform_create(serializer)
        except Http404 as e:
            for file_id in file_id_list:
                delete_file(file_id)
            raise ValidationError(f'Error creating lesson: {str(e)}')
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Lesson created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    

# Lesson API to retrieve a lesson
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled | IsCourseOwner]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Lesson not found')
        
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Lesson retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


# Lesson API to update a lesson
class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Lesson not found')

        # Upload the video, subtitle, and attachment to Google Drive
        files = ['video', 'subtitle', 'attachment']
        file_id_list = []
        old_file_ids = []
        for file in files:
            if request.FILES.get(file):
                try:
                    file_id = upload_file(request.FILES.get(file))
                    request.data[f'{file}_id'] = file_id
                    file_id_list.append(file_id)
                    old_file_ids.append(getattr(instance, f'{file}_id'))
                except Exception as e:
                    for file_id in file_id_list:  
                        delete_file(file_id) 
                    raise FileUploadException(f'Error uploading {file}: {str(e)}')
 
    
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            for file_id in file_id_list:
                delete_file(file_id)
            raise ValidationError(f'Error updating lesson: {serializer.errors} ===> {instance}')
        self.perform_update(serializer)

        # Delete the old video, subtitle, and attachment from Google Drive
        for old_file_id in old_file_ids:
            delete_file(old_file_id)

        return Response({
            'success': True,
            'message': 'Lesson updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

# Lesson API to delete a lesson
class LessonDeleteAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Lesson not found')

        # Delete the video, subtitle, and attachment from Google Drive
        file_ids = ['video_id', 'subtitle_vi_id', 'attachment_id']
        for file_id in file_ids:
            if getattr(instance, file_id):
                delete_file(getattr(instance, file_id))

        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': f'Lesson {instance} deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)