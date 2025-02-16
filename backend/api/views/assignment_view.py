from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from api.models import Assignment, Lesson
from api.serializers import AssignmentSerializer
from api.permissions import IsCourseOwner, WasCourseEnrolled


# Assignment API to list all assignments by lesson
class AssignmentListAPIView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled | IsCourseOwner]

    def get_queryset(self):
        lesson_id = self.kwargs.get('lesson_id')
        if not Lesson.objects.filter(id=lesson_id).exists():
            raise NotFound('Lesson does not exist')
        return Assignment.objects.filter(lesson_id=lesson_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'All assignments have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


# Assignment API to create a assignment
class AssignmentCreateAPIView(generics.CreateAPIView):
    serializer_class = AssignmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]

    def create(self, request, *args, **kwargs):
        lesson_id = self.kwargs.get('lesson_id')
        if not Lesson.objects.filter(id=lesson_id).exists():
            raise NotFound('Lesson does not exist')
        request.data['lesson_id'] = lesson_id

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(f'Assignment not created: {serializer.errors}')
        
        self.perform_create(serializer)
        header = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Assignment has been created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=header)
    

# Assignment API to retrieve a assignment
class AssignmentRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled | IsCourseOwner]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Assignment does not exist')
        
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
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'Assignment does not exist: {str(e)}')

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(f'Assignment not updated: {serializer.errors}')
        
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
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Assignment does not exist')

        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Assignment has been deleted successfully',
            'data': instance.id
        }, status=status.HTTP_204_NO_CONTENT)

        
