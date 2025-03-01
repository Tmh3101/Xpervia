from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from api.models import Chapter, Course, Lesson
from api.serializers import ChapterSerializer, SimpleLessonSerializer
from api.permissions import IsCourseOwner, WasCourseEnrolled


# Chapters API to list all chapters of a course
class ChapterListAPIView(generics.ListAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        if not Course.objects.filter(id=course_id).exists():
            raise NotFound("Course does not exist")
        course = Course.objects.get(id=course_id)
        return Chapter.objects.filter(course_content_id=course.course_content.id)

    def list(self, request, *args, **kwargs):    
        queryset = self.get_queryset()    
        serializer = ChapterSerializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'All chapters have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


# Chapter API to create a chapter
class ChapterCreateAPIView(generics.CreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]

    def create(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        if not Course.objects.filter(id=course_id).exists():
            raise NotFound("Course does not exist")
        course = Course.objects.get(id=course_id)
        request.data['course_content_id'] = course.course_content.id

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
    

# Chapter API to retrieve a chapter
class ChapterRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
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
    

# Chapter API to update a chapter
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

        request.data['course_content_id'] = instance.course_content.id
        serializer = self.get_serializer(instance, data=request.data)
        if not serializer.is_valid():
            raise ValidationError(f'Chapter not updated: {serializer.errors}')
        
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Chapter updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

# Chapter API to delete a chapter
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
            'message': f'Chapter "{instance}" deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)