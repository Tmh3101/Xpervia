import logging
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.models import Submission, SubmissionScore
from api.serializers import SubmissionScoreSerializer
from api.permissions import IsCourseOwner

logger = logging.getLogger(__name__)

# Submission API to create a submission score
class SubmissionScoreCreateAPIView(generics.CreateAPIView):
    queryset = SubmissionScore.objects.all()
    serializer_class = SubmissionScoreSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating submission score for submission ID: {self.kwargs.get('submission_id')}")
        submission_id = self.kwargs.get('submission_id')
        if not Submission.objects.filter(id=submission_id).exists():
            raise NotFound("Submission does not exist")
        request.data['submission_id'] = submission_id

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
            
        self.perform_create(serializer)
        logger.info("Submission score created successfully")
        return Response({
            'success': True,
            'message': 'Submission score has been created successfully',
            'submission': serializer.data
        }, status=status.HTTP_201_CREATED)


# Submission score API view for updating
class SubmissionScoreUpdateAPIView(generics.UpdateAPIView):
    queryset = SubmissionScore.objects.all()
    serializer_class = SubmissionScoreSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating submission score with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404:
            raise NotFound('Submission score does not exist')
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
            
        self.perform_update(serializer)
        logger.info("Submission score updated successfully")
        return Response({
            'success': True,
            'message': 'Submission score has been updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

# Submission score API view for deleting
class SubmissionScoreDeleteAPIView(generics.DestroyAPIView):
    queryset = SubmissionScore.objects.all()
    serializer_class = SubmissionScoreSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        logger.info(f"Deleting submission score with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404:
            raise NotFound('Submission score does not exist')
        
        self.perform_destroy(instance)
        logger.info("Submission score deleted successfully")
        return Response({
            'success': True,
            'message': 'Submission score has been deleted successfully'
        }, status=status.HTTP_200_OK)