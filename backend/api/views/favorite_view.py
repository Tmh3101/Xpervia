import logging
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from api.exceptions.custom_exceptions import Existed
from api.models import Enrollment, Course,Favorite
from api.serializers import FavoriteSerializer
from api.permissions import IsAdmin, IsStudent
from api.middlewares.authentication import SupabaseJWTAuthentication
from api.services.supabase.storage import get_file_url

logger = logging.getLogger(__name__)


# Favorite API to list all favorites
class FavoriteListAPIView(generics.ListAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request, *args, **kwargs):
        logger.info("Listing all favorites")
        queryset = self.get_queryset()
        favorites = FavoriteSerializer(queryset, many=True).data.copy()

        for favorite in favorites:
            favorite['course']['course_content']['thumbnail_url'] = get_file_url(
                bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
                path=favorite['course']['course_content']['thumbnail_path'],
                is_public=True
            )

        logger.info("Successfully listed all favorites")
        return Response({
            'success': True,
            'message': 'All favorites have been listed successfully',
            'favorites': serializer.data
        }, status=status.HTTP_200_OK)

# Favorite API to list all favorites of a course
class FavoriteListByCourseAPIView(generics.ListAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request, *args, **kwargs):
        logger.info(f"Listing favorites for course ID: {self.kwargs.get('course_id')}")
        course = Course.objects.filter(id=self.kwargs.get('course_id')).first()
        if not course:
            raise NotFound('Course not found')
        
        queryset = course.favorites.all()
        favorites = FavoriteSerializer(queryset, many=True).data.copy()

        for favorite in favorites:
            favorite['course']['course_content']['thumbnail_url'] = get_file_url(
                bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
                path=favorite['course']['course_content']['thumbnail_path'],
                is_public=True
            )

        logger.info("Successfully listed favorites for course")
        return Response({
            'success': True,
            'message': 'All favorite students have been listed successfully',
            'favorites': favorites
        }, status=status.HTTP_200_OK)

# Favorite API to list all favorites of a student
class FavoriteListByStudentAPIView(generics.ListAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsStudent | IsAdmin]

    def list(self, request, *args, **kwargs):
        logger.info(f"Listing favorites for student ID: {request.user.id}")
        queryset = self.get_queryset().filter(student_id=request.user.id)
        favorites = FavoriteSerializer(queryset, many=True).data.copy()

        for favorite in favorites:
            favorite['course']['course_content']['thumbnail_url'] = get_file_url(
                bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
                path=favorite['course']['course_content']['thumbnail_path'],
                is_public=True
            )

        logger.info("Successfully listed favorites for student")
        return Response({
            'success': True,
            'message': 'All favorite courses have been listed successfully',
            'favorites': favorites
        }, status=status.HTTP_200_OK)


# Favorite API to create a favorite
class FavoriteCreateAPIView(generics.CreateAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating favorite for course ID: {self.kwargs.get('course_id')} by student ID: {request.user.id}")
        course_id = self.kwargs.get('course_id')
        course = Course.objects.filter(id=course_id).first()
        if not course:
            raise NotFound('Course not found')
        request.data['course_id'] = course.id

        if course.favorites.filter(student_id=request.user.id).exists():
            logger.warning(f"Favorite already exists for student ID: {request.user.id} in course ID: {course.id}")
            raise Existed('You have already favorited this course')
        request.data['student_id'] = request.user.id

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Favorite creation failed: {serializer.errors}")
            raise ValidationError(f'Favorite not created: {serializer.errors}')
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        favorite = serializer.data.copy()
        favorite['course']['course_content']['thumbnail_url'] = get_file_url(
            bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
            path=favorite['course']['course_content']['thumbnail_path'],
            is_public=True
        )

        logger.info("Favorite created successfully")
        return Response({
            'success': True,
            'message': 'Favorite created successfully',
            'favorite': favorite
        }, status=status.HTTP_201_CREATED, headers=headers)
    

# Favorite API to retrieve a favorite
class FavoriteRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsStudent]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving favorite with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Favorite.DoesNotExist:
            raise NotFound('Favorite not found')

        serializer = self.get_serializer(instance)
        favorite = serializer.data.copy()
        favorite['course']['course_content']['thumbnail_url'] = get_file_url(
            bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
            path=favorite['course']['course_content']['thumbnail_path'],
            is_public=True
        )

        logger.info("Favorite retrieved successfully")
        return Response({
            'success': True,
            'message': 'Favorite retrieved successfully',
            'favorite': favorite
        }, status=status.HTTP_200_OK)


# Favorite API to delete a favorite
class FavoriteDeleteAPIView(generics.DestroyAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsStudent]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        logger.info(f"Deleting enrollment with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Enrollment.DoesNotExist:
            raise NotFound('Enrollment not found')
        
        self.perform_destroy(instance)
        logger.info("Enrollment deleted successfully")
        return Response({
            'success': True,
            'message': 'Enrollment deleted successfully',
        }, status=status.HTTP_204_NO_CONTENT)
