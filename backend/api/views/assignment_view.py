import logging
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from api.models import Assignment, Lesson, Submission, SubmissionScore
from api.serializers import AssignmentSerializer, SimpleSubmissionSerializer, SubmissionScoreSerializer
from api.permissions import IsCourseOwner, WasCourseEnrolled
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)

# Assignment API to list all assignments of a lesson
class AssignmentListAPIView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled | IsCourseOwner]

    def get_queryset(self):
        lesson_id = self.kwargs.get('lesson_id')
        if not Lesson.objects.filter(id=lesson_id).exists():
            raise NotFound('Lesson does not exist')
        return Assignment.objects.filter(lesson_id=lesson_id)

    def list(self, request, *args, **kwargs):
        logger.info(f"Listing assignments for lesson ID: {self.kwargs.get('lesson_id')}")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        assingments_serializer = serializer.data.copy()

        for assignment in assingments_serializer:
            submissions = Submission.objects.filter(assignment_id=assignment['id'])
            if submissions:
                assignment['submissions'] = SimpleSubmissionSerializer(submissions, many=True).data.copy()
                for submission in assignment['submissions']:
                    if SubmissionScore.objects.filter(submission_id=submission['id']).exists():
                        submission_score = SubmissionScore.objects.get(submission_id=submission['id'])
                        submission['submission_score'] = SubmissionScoreSerializer(submission_score).data.copy()
                    else:
                        submission['submission_score'] = None
            else:
                assignment['submissions'] = None

        logger.info("Successfully listed assignments")
        return Response({
            'success': True,
            'message': 'All assignments have been listed successfully',
            'assignments': assingments_serializer
        }, status=status.HTTP_200_OK)


# Assignment API to list all assignments of a lesson by a student
class AssignmentListByStudentAPIView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled | IsCourseOwner]

    def get_queryset(self):
        lesson_id = self.kwargs.get('lesson_id')
        if not Lesson.objects.filter(id=lesson_id).exists():
            raise NotFound('Lesson does not exist')
        return Assignment.objects.filter(lesson_id=lesson_id)

    def list(self, request, *args, **kwargs):
        logger.info(f"Listing assignments for student ID: {request.user.id} and lesson ID: {self.kwargs.get('lesson_id')}")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        assingments_serializer = serializer.data.copy()
        for assignment in assingments_serializer:
            submission = Submission.objects.filter(assignment_id=assignment['id'], student_id=request.user.id).first()
            if submission:
                assignment['submission'] = SimpleSubmissionSerializer(submission).data.copy()
                if SubmissionScore.objects.filter(submission_id=submission.id).exists():
                    submission_score = SubmissionScore.objects.get(submission_id=submission.id)
                    submission_score = SubmissionScoreSerializer(submission_score).data.copy()
                    submission_score.pop('submission')
                    assignment['submission']['submission_score'] = submission_score
                else:
                    assignment['submission']['submission_score'] = None
            else:
                assignment['submission'] = None

        logger.info("Successfully listed assignments for student")
        return Response({
            'success': True,
            'message': 'All assignments have been listed successfully',
            'assignments': assingments_serializer
        }, status=status.HTTP_200_OK)


# Assignment API to create a assignment
class AssignmentCreateAPIView(generics.CreateAPIView):
    serializer_class = AssignmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating assignment for lesson ID: {self.kwargs.get('lesson_id')}")
        lesson_id = self.kwargs.get('lesson_id')
        if not Lesson.objects.filter(id=lesson_id).exists():
            raise NotFound('Lesson does not exist')
        request.data['lesson_id'] = lesson_id

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(f'Assignment not created: {serializer.errors}')

        try:
            self.perform_create(serializer)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Debugging',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info("Assignment created successfully")
        header = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Assignment has been created successfully',
            'assignment': serializer.data
        }, status=status.HTTP_201_CREATED, headers=header)
    

# Assignment API to retrieve a assignment
class AssignmentRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, WasCourseEnrolled | IsCourseOwner]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving assignment with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Assignment does not exist')
        
        serializer = self.get_serializer(instance)
        logger.info("Assignment retrieved successfully")
        return Response({
            'success': True,
            'message': 'Assignment has been retrieved successfully',
            'assignment': serializer.data
        }, status=status.HTTP_200_OK)
    

# View for handling assignment update
class AssignmentUpdateAPIView(generics.UpdateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating assignment with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'Assignment does not exist: {str(e)}')

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(f'Assignment not updated: {serializer.errors}')
        
        self.perform_update(serializer)
        logger.info("Assignment updated successfully")
        return Response({
            'success': True,
            'message': 'Assignment has been updated successfully',
            'assignment': serializer.data
        }, status=status.HTTP_200_OK)
    

# View for handling assignment delete
class AssignmentDeleteAPIView(generics.DestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        logger.info(f"Deleting assignment with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Assignment does not exist')

        self.perform_destroy(instance)
        logger.info("Assignment deleted successfully")
        return Response({
            'success': True,
            'message': 'Assignment has been deleted successfully',
            'assignment': self.get_serializer(instance).data
        }, status=status.HTTP_204_NO_CONTENT)


