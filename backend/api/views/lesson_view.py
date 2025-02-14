from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.exceptions.custom_exceptions import FileUploadException
from api.models.lesson_model import Lesson
from api.models.chapter_model import Chapter
from api.models.course_model import Course
from api.serializers.lesson_serializer import LessonSerializer
from api.permissions.teacher_permissions_checker import IsCourseOwner
from api.permissions.student_permissions_checker import WasCourseEnrolled
from api.services.google_drive_service import upload_file, delete_file

# Lessons list API view for listing all lessons by course_id
class LessonListByCourseAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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
        

# Lessons list API view for listing all lessons by course_id and chapter_id
class LessonListByChapterAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        chapter_id = self.kwargs.get('chapter_id')
        if not Course.objects.filter(id=course_id).exists():
            raise Http404("Course does not exist")
        if not Chapter.objects.filter(id=chapter_id, course_id=course_id).exists():
            raise Http404("Chapter does not exist or does not belong to the specified course")
        return Lesson.objects.filter(course_id=course_id, chapter_id=chapter_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Lessons for the course and chapter have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        

# Lesson create API view for creating a new lesson
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
    

# Lesson retrieve API view for retrieving a lesson
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled or IsCourseOwner]
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


# Lesson update API view for updating a lesson
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
        old_files = []
        for file in files:
            if request.FILES.get(file):
                try:
                    file_id = upload_file(request.FILES.get(file))
                    request.data[f'{file}_id'] = file_id
                    file_id_list.append(file_id)
                    request.data.pop(file)
                    old_files.append({
                        'name': file,
                        'id': getattr(instance, f'{file}_id')
                    })
                except Exception as e:
                    for file_id in file_id_list:  
                        delete_file(file_id) 
                    raise FileUploadException(f'Error uploading {file}: {str(e)}')

        serializer = self.get_serializer(instance, data=request.data)
        if not serializer.is_valid():
            for file_id in file_id_list:
                delete_file(file_id)
            raise ValidationError(f'Error updating lesson: {serializer.errors}')
        
        self.perform_update(serializer)
        # Delete the old video, subtitle, and attachment from Google Drive
        for file in old_files:
            try:
                delete_file(file['id'])
            except Exception as e:
                raise FileUploadException(f'Error deleting {file["name"]}: {str(e)}')

        return Response({
            'success': True,
            'message': 'Lesson updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

# Lesson delete API view for deleting a lesson
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
        files = ['video', 'subtitle', 'attachment']
        for file in files:
            if getattr(instance, f'{file}_id'):
                delete_file(getattr(instance, f'{file}_id'))

        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Lesson deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)