from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from api.exceptions.custom_exceptions import Existed
from api.models import LessonCompletion, Course, CourseContent
from api.serializers import LessonCompletionSerializer
from api.permissions import (
    IsAdmin, IsCourseOwner, WasCourseEnrolled, IsStudent
)


# LessonCompletion API to list lesson completions of a course
class LessonCompletionListAPIView(generics.ListAPIView):
    queryset = LessonCompletion.objects.all()
    serializer_class = LessonCompletionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsCourseOwner]

    def list(self, request, *args, **kwargs):
        lesson_id = self.kwargs.get('lesson_id')
        queryset = self.get_queryset().filter(lesson_id=lesson_id)
        serializer = LessonCompletionSerializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'All lesson completions have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
# LessonCompletion API to list all lesson completions of a student 
class LessonCompletionListByStudentAPIView(generics.ListAPIView):
    queryset = LessonCompletion.objects.all()
    serializer_class = LessonCompletionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

    def list(self, request, *args, **kwargs):
        student_id = request.user.id
        course_id = self.kwargs.get('course_id')
        course = Course.objects.filter(id=course_id).first()
        if not course:
            raise NotFound('Course not found')

        course_content = course.course_content
        queryset = self.get_queryset().filter(student_id=student_id, lesson__course_content=course_content)
        serializer = LessonCompletionSerializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'All lesson completions have been listed successfully',
            'lesson_completions': serializer.data
        }, status=status.HTTP_200_OK)
    

# LessonCompletion API to create a lesson completion
class LessonCompletionCreateAPIView(generics.CreateAPIView):
    queryset = LessonCompletion.objects.all()
    serializer_class = LessonCompletionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled]

    def create(self, request, *args, **kwargs):
        lesson_id = self.kwargs.get('lesson_id')
        lesson_completion = LessonCompletion.objects.filter(student=request.user, lesson_id=lesson_id).first()
        if lesson_completion:
            raise Existed('Lesson completion already exists')
        request.data['student_id'] = request.user.id
        request.data['lesson_id'] = lesson_id

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(f'Lesson completion not created: {serializer.errors}')
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'Lesson completion has been created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    

# LessonCompletion API to delete a lesson completion
class LessonCompletionDeleteAPIView(generics.DestroyAPIView):
    queryset = LessonCompletion.objects.all()
    serializer_class = LessonCompletionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled]

    def destroy(self, request, *args, **kwargs):
        lesson_id = self.kwargs.get('lesson_id')
        lesson_completion = LessonCompletion.objects.filter(student=request.user, lesson_id=lesson_id).first()
        if not lesson_completion:
            raise NotFound('Lesson completion not found')
        self.perform_destroy(lesson_completion)
        return Response({
            'success': True,
            'message': 'Lesson completion has been deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)