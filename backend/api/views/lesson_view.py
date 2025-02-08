from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.models.lesson_model import Lesson
from api.models.chapter_model import Chapter
from api.models.course_model import Course
from api.serializers.lesson_serializer import LessonSerializer
from api.roles import IsTeacher, IsCourseOfLessonOwner
from api.services.google_drive_service import upload_file, delete_file

# Lessons list API view for listing all lessons by course_id
class LessonListByCourseAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        if not Course.objects.filter(id=course_id).exists():
            raise Http404("Course does not exist")
        return Lesson.objects.filter(course_id=course_id)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Lessons for the course have been listed successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Http404 as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        

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
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Lessons for the course and chapter have been listed successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Http404 as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        

# Lesson create API view for creating a new lesson
class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher & IsCourseOfLessonOwner]

    def perform_create(self, serializer):
        try:
            course_id = self.kwargs.get('course_id')
            course = Course.objects.get(id=course_id)
            serializer.save(course=course)
        except Course.DoesNotExist:
            raise Http404("Course does not exist")

    def create(self, request, *args, **kwargs):
        # Check if the course exists
        if request.data['chapter_id']:
            chapter = Chapter.objects.filter(id=request.data['chapter_id']).first()
            if not chapter:
                return Response({
                    'success': False,
                    'message': 'Chapter does not exist'
                }, status=status.HTTP_404_NOT_FOUND)
            request.data['chapter'] = chapter.id
            request.data.pop('chapter_id')

        # Upload the video, subtitle, and attachment to Google Drive
        files = ['video', 'subtitle', 'attachment']
        file_id_list = []
        for file in files:
            if request.FILES.get(file):
                try:
                    file_id = upload_file(request.FILES.get(file))
                    file_id_list.append(file_id)
                    request.data[f'{file}_id'] = file_id
                except Exception as e:
                    for file_id in file_id_list:
                        delete_file(file_id)
                    return Response({
                        'success': False,
                        'message': f'Error uploading {file}',
                        'error': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
            except Http404 as e:
                for file_id in file_id_list:
                    delete_file(file_id)
                return Response({
                    'success': False,
                    'message': str(e)
                }, status=status.HTTP_404_NOT_FOUND)
            headers = self.get_success_headers(serializer.data)
            return Response({
                'success': True,
                'message': 'Lesson created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED, headers=headers)
        
        for file_id in file_id_list:
            delete_file(file_id)
        return Response({
            'success': False,
            'message': 'Lesson not created',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

# Lesson retrieve API view for retrieving a lesson
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'success': True,
                'message': 'Lesson retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Http404 as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)


# Lesson update and delete API view for updating and deleting a lesson
class LessonUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher & IsCourseOfLessonOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

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
                    return Response({
                        'success': False,
                        'message': f'Error uploading {file}',
                        'error': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            self.perform_update(serializer)

            # Delete the old video, subtitle, and attachment from Google Drive
            for file in old_files:
                try:
                    delete_file(file['id'])
                except Exception as e:
                    return Response({
                        'success': False,
                        'message': f'Error deleting old {file["name"]}',
                        'error': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'success': True,
                'message': 'Lesson updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        for file_id in file_id_list:
            delete_file(file_id)
        return Response({
            'success': False,
            'message': 'Lesson not updated',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Delete the video, subtitle, and attachment from Google Drive
        files = ['video', 'subtitle', 'attachment']
        for file in files:
            if getattr(instance, f'{file}_id'):
                try:
                    delete_file(getattr(instance, f'{file}_id'))
                except Exception as e:
                    return Response({
                        'success': False,
                        'message': f'Error deleting {file}',
                        'error': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Lesson deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)