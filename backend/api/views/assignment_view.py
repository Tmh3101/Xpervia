from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.models.assignment_model import Assignment
from api.models.lesson_model import Lesson
from api.serializers.assignment_serializer import AssignmentSerializer, SimpleAssignmentSerializer
from api.serializers.lesson_serializer import LessonSerializer
from api.roles.teacher_role import IsTeacher
from api.roles.student_role import WasCourseEnrolled

# View for handling assignment list
class AssignmentListAPIView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def permission_denied(self, request, message=None, code=None):
        response_data = {
            'success': False,
            'message': message or 'You do not have permission to perform this action.'
        }
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        lesson_id = self.kwargs.get('lesson_id')
        if not Lesson.objects.filter(id=lesson_id).exists():
            raise Http404("Lesson does not exist")
        return Assignment.objects.filter(lesson_id=lesson_id)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
        except Http404 as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Assignments have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

# View for handling assignment create
class AssignmentCreateAPIView(generics.CreateAPIView):
    serializer_class = AssignmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        lesson_id = self.kwargs.get('lesson_id')
        if not Lesson.objects.filter(id=lesson_id).exists():
            return Response({
                'success': False,
                'message': 'Lesson does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        request.data['lesson_id'] = lesson_id

        if Lesson.objects.get(id=lesson_id).course.teacher != request.user:
            return Response({
                'success': False,
                'message': 'You are not allowed to create assignment for this lesson'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Assignment not created',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        header = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Assignment has been created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=header)
    

# View for handling assignment retrieve
class AssignmentRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Assignment has been retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

# View for handling assignment update
class AssignmentUpdateAPIView(generics.UpdateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = self.get_object()
        except Http404 as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
        if instance.lesson.course.teacher != request.user:
            return Response({
                'success': False,
                'message': 'You are not allowed to update this assignment'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Assignment not updated',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Assignment has been updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

# View for handling assignment delete
class AssignmentDeleteAPIView(generics.DestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
        if instance.lesson.course.teacher != request.user:
            return Response({
                'success': False,
                'message': 'You are not allowed to delete this assignment'
            }, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Assignment has been deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

        
