from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.models.chapter_model import Chapter
from api.models.course_model import Course
from api.models.lesson_model import Lesson
from api.serializers.chapter_serializer import ChapterSerializer
from api.serializers.lesson_serializer import SimpleLessonSerializer
from api.roles.teacher_role import IsTeacher, IsCourseOwner
from api.roles.student_role import WasCourseEnrolled

# Chapters list API view for listing all chapters
class ChapterListAPIView(generics.ListAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        if not Course.objects.filter(id=course_id).exists():
            raise NotFound("Course does not exist")
        return Chapter.objects.filter(course_id=course_id)

    def list(self, request, *args, **kwargs):    
        queryset = self.get_queryset()    
        serializer = ChapterSerializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'All chapters have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


# Chapter create API view for creating a chapter
class ChapterCreateAPIView(generics.CreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]

    def perform_create(self, serializer):
        try:
            course = Course.objects.get(id=self.kwargs.get('course_id'))
        except Course.DoesNotExist:
            raise NotFound("Course does not exist")
        
        if course.teacher != self.request.user:
            raise PermissionDenied("You are not allowed to create chapter for this course")

        serializer.save(course=course)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(f'Chapter not created: {serializer.errors}')
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Chapter created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    

# Chapter retrieve API view for retrieving a chapter with all lessons
class ChapterRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:    
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'Chapter not found: {str(e)}')

        lessons = Lesson.objects.filter(chapter=instance)
        lessons_serializer = SimpleLessonSerializer(lessons, many=True)
        
        serializer = self.get_serializer(instance)
        chapter_detail_data = serializer.data.copy()
        chapter_detail_data['lessons'] = lessons_serializer.data

        return Response({
            'success': True,
            'message': 'Chapter retrieved successfully',
            'data': chapter_detail_data
        }, status=status.HTTP_200_OK)
    
# Chapter update API view for updating and deleting a chapter
class ChapterUpdateAPIView(generics.UpdateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        try:    
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'Chapter not found: {str(e)}')

        serializer = self.get_serializer(instance, data=request.data)
        if not serializer.is_valid():
            raise ValidationError(f'Chapter not updated: {serializer.errors}')
        
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Chapter updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

# Chapter delete API view for deleting a chapter
class ChapterDeleteAPIView(generics.DestroyAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'Chapter not found: {str(e)}')
        
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Chapter deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)