import json
import logging
from django.conf import settings
from django.http import Http404
from api.enums import RoleEnum
from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, ValidationError
from api.pagination import CoursePagination
from api.models import Course, Lesson, User
from api.serializers import (
    CourseSerializer,
    CourseContentSerializer,
    ChapterSerializer,
    LessonSerializer,
    CourseListItemSerializer
)
from api.permissions import IsTeacher, IsCourseOwner, IsAdmin   
from api.middlewares.authentication import SupabaseJWTAuthentication
from api.services.supabase.storage import delete_file
from api.utils import (
    get_course_content,
    delete_course_content,
    get_course_content_lessons,
    add_file_url_for,
    get_progress_map_bulk
)

logger = logging.getLogger(__name__)

# Course List API with filtering and pagination
class CourseListAPIView(generics.ListAPIView):
    serializer_class = CourseListItemSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [AllowAny]
    pagination_class = CoursePagination

    def get_queryset(self):
        qs = (
            Course.objects
            .select_related("course_content")
            .annotate(
                num_students=Count("enrollments", distinct=True),
                num_favorites=Count("favorites", distinct=True),
                num_lessons=Count("course_content__lessons", distinct=True),
            )
            .order_by("-created_at")
        )

        request = self.request
        params = request.query_params

        title = params.get("title")
        categories = params.getlist("categories") or params.get("categories")
        is_visible = params.get("is_visible")

        if title:
            qs = qs.filter(course_content__title__icontains=title)

        if categories:
            if isinstance(categories, str):
                categories = [categories]
            qs = qs.filter(course_content__categories__id__in=categories).distinct()

        if is_visible:
            qs = qs.filter(is_visible=is_visible)

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    
# Course Detail API to list all course of a teacher
class CourseListByTeacherAPIView(generics.ListAPIView):
    serializer_class = CourseListItemSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher]
    pagination_class = CoursePagination

    def get_queryset(self):
        teacher = User.objects.get(id=self.request.user.id)
        return (
            Course.objects
            .filter(course_content__teacher=teacher)
            .select_related("course_content")
            .annotate(
                num_students=Count("enrollments", distinct=True),
                num_favorites=Count("favorites", distinct=True),
                num_lessons=Count("course_content__lessons", distinct=True),
            )
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


# Enroled Course list for student without pagination
class EnrolledCourseListAPIView(generics.ListAPIView):
    serializer_class = CourseListItemSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination

    def get_queryset(self):
        student = User.objects.get(id=self.request.user.id)
        return (
            Course.objects
            .filter(enrollments__student=student)
            .select_related("course_content")
            .annotate(
                num_students=Count("enrollments", distinct=True),
                num_favorites=Count("favorites", distinct=True),
                num_lessons=Count("course_content__lessons", distinct=True),
            )
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        logger.info(f"Listing enrolled courses for student ID: {request.user.id}")
        queryset = self.filter_queryset(self.get_queryset())

        progress_map = {}
        user = getattr(request, "user", None)
        if queryset and getattr(user, "is_authenticated", False):
            content_ids = [c.course_content_id for c in queryset]
            progress_map = get_progress_map_bulk(content_ids, user.id)

        serializer = self.get_serializer(queryset, many=True, context={"progress_map": progress_map})

        logger.info("Successfully listed enrolled courses")
        return Response({
            'success': True,
            'message': 'Enrolled courses retrieved successfully',
            'courses': serializer.data
        }, status=status.HTTP_200_OK) 
    

# Favorited Course list of student without pagination
class FavoritedCourseListAPIView(generics.ListAPIView):
    serializer_class = CourseListItemSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination

    def get_queryset(self):
        student = User.objects.get(id=self.request.user.id)
        return (
            Course.objects
            .filter(favorites__student=student)
            .select_related("course_content")
            .annotate(
                num_students=Count("enrollments", distinct=True),
                num_favorites=Count("favorites", distinct=True),
                num_lessons=Count("course_content__lessons", distinct=True),
            )
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        logger.info(f"Listing enrolled courses for student ID: {request.user.id}")
        queryset = self.filter_queryset(self.get_queryset())

        progress_map = {}
        user = getattr(request, "user", None)
        if queryset and getattr(user, "is_authenticated", False):
            content_ids = [c.course_content_id for c in queryset]
            progress_map = get_progress_map_bulk(content_ids, user.id)

        serializer = self.get_serializer(queryset, many=True, context={"progress_map": progress_map})

        logger.info("Successfully listed enrolled courses")
        return Response({
            'success': True,
            'message': 'Enrolled courses retrieved successfully',
            'courses': serializer.data
        }, status=status.HTTP_200_OK)


# Course Detail API to create a course detail
class CourseCreateAPIView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher]

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating course for teacher ID: {request.user.id}")
        course_content = get_course_content(request)
        logger.info(f"Course content data: {course_content}")

        course_content_serializer = CourseContentSerializer(data=course_content)

        if not course_content_serializer.is_valid():
            logger.error(f"Course content serializer errors: {course_content_serializer.errors}")
            delete_file(
                bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
                path=course_content.get('thumbnail_path')
            )
            raise ValidationError(f'Error creating course: {course_content_serializer.errors}')
        
        course_content = course_content_serializer.save()

        # Set the categories (categories: ['1', '2', '3'])
        if request.data.get('categories'):
            categories = request.data.get('categories')
            if isinstance(categories, str):
                try:
                    categories = json.loads(categories)
                except json.JSONDecodeError:
                    categories = categories.split(',')
            course_content.categories.set(categories)
            course_content.save()

        course_data = request.data
        course_data['course_content_id'] = course_content.id

        course_serializer = CourseSerializer(data=course_data)
        if not course_serializer.is_valid():
            logger.error(f"Course serializer errors: {course_serializer.errors}")
            delete_course_content(course_content.id)
            raise ValidationError(f'Error creating course: {course_serializer.errors}')
        
        try:
            self.perform_create(course_serializer)
        except Exception as e:
            logger.error(f"Error creating course: {str(e)}")
            delete_course_content(course_content.id)
            raise ValidationError(f'Error creating course: {str(e)}')
        
        logger.info("Course created successfully")
        headers = self.get_success_headers(course_serializer.data)
        return Response({
            'success': True,
            'message': 'Course created successfully',
            'course': course_serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
# Course API to retrieve a course detail
class CourseRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def get_object(self):
        qs = (
            Course.objects
            .select_related("course_content")
            .annotate(
                num_students=Count("enrollments", distinct=True),
                num_favorites=Count("favorites", distinct=True),
                num_lessons=Count("course_content__lessons", distinct=True),
            )
        )
        return get_object_or_404(qs, **{self.lookup_field: self.kwargs[self.lookup_field]})

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving course with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Course not found')
        
        course_content = instance.course_content
        course_content_data = CourseContentSerializer(course_content).data.copy()
        chapters_data, lessons_without_chapter_data = get_course_content_lessons(course_content)
        course_content_data['chapters'] = chapters_data
        course_content_data['lessons_without_chapter'] = lessons_without_chapter_data

        course_data = self.get_serializer(instance).data.copy()
        course_data['course_content'] = course_content_data
        course_data['num_students'] = instance.num_students
        course_data['num_favorites'] = instance.num_favorites

        logger.info("Course retrieved successfully")
        return Response({
            'success': True,
            'message': 'Course retrieved successfully',
            'course': course_data
        }, status=status.HTTP_200_OK)
    

# Course API to retrieve a course detail
class CourseRetrieveWithDetailLessonsAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving course with detailed lessons for ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Course not found')
        
        # Get all chapters and lessons of the course
        chapters = instance.course_content.chapters.all()
        chapters_data = []
        for chapter in chapters:
            chapter_data = ChapterSerializer(chapter).data
            lessons = Lesson.objects.filter(chapter=chapter)
            lessons_serializer = LessonSerializer(lessons, many=True)
            for lesson in lessons_serializer.data:
                lesson.pop('chapter', None)
                lesson.pop('course_content', None)
                add_file_url_for(lesson)    
            chapter_data['lessons'] = lessons_serializer.data
            chapter_data.pop('course_content')
            chapters_data.append(chapter_data)

        # Get all lessons without chapter
        lessons_without_chapter = Lesson.objects.filter(course_content=instance.course_content, chapter__isnull=True)
        lessons_without_chapter_serializer = LessonSerializer(lessons_without_chapter, many=True)
        for lesson in lessons_without_chapter_serializer.data:
            lesson.pop('chapter', None)
            lesson.pop('course_content', None)

        serializer = self.get_serializer(instance)
        course_data = serializer.data.copy()
        course_content = course_data['course_content']

        # Add chapters and lessons to the course data
        course_content['chapters'] = chapters_data
        course_content['lessons_without_chapter'] = lessons_without_chapter_serializer.data
        course_data['course_content'] = course_content

        logger.info("Course with detailed lessons retrieved successfully")
        return Response({
            'success': True,
            'message': 'Course retrieved successfully',
            'course': course_data
        }, status=status.HTTP_200_OK)
    

# Course Detail API to update a course detail
class CourseUpdateAPIView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating course with ID: {kwargs.get('id')} with data: {request.data}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Course not found')
        
        # Get the course data
        course_content = get_course_content(request)

        # Check the course data
        course_content_serializer = CourseContentSerializer(instance.course_content, data=course_content, partial=True)
        if not course_content_serializer.is_valid():
            if course_content.get('thumbnail_path'):
                delete_file(
                    bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
                    path=course_content.get('thumbnail_path')
                )
            raise ValidationError(f'Error updating course: {course_content_serializer.errors}')

        # Get the course detail data
        course_data = request.data.copy()
        course_data['course_content_id'] = instance.course_content.id

        # Update the course and course detail
        old_thumbnail_path = instance.course_content.thumbnail_path
        course_content = course_content_serializer.save()
        if request.data.get('categories'):
            categories = request.data.get('categories')
            if isinstance(categories, str):
                try:
                    categories = json.loads(categories)
                except json.JSONDecodeError:
                    categories = categories.split(',')
                except Exception as e:
                    raise ValidationError(f'Error updating course: {str(e)}')
            course_content.categories.set(categories)


        # Check the course detail data
        course_serializer = self.get_serializer(instance, data=course_data, partial=True)
        if not course_serializer.is_valid():
            if course_content.get('thumbnail_path'):
                delete_file(
                    bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
                    path=course_content.get('thumbnail_path')
                )
            raise ValidationError(f'Error updating course: {course_serializer.errors}')
            
        self.perform_update(course_serializer)

        # Delete the old thumbnail
        if request.FILES.get('thumbnail'):
            delete_file(
                bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
                path=old_thumbnail_path
            )
        
        logger.info("Course updated successfully")
        return Response({
            'success': True,
            'message': 'Course updated successfully',
            'course': course_serializer.data
        }, status=status.HTTP_200_OK)
            
        
# Course Detail API to delete a course detail
class CourseDeleteAPIView(generics.DestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        course_id = kwargs.get('id')
        logger.info(f"Deleting course with ID: {course_id}")
        try:
            course = Course.objects.get(id=course_id)
        except Http404 as e:
            raise NotFound('Course not found')

        # Delete the course detail
        course_content_id = course.course_content.id
        self.perform_destroy(course)
        delete_course_content(course_content_id)

        logger.info("Course deleted successfully")
        return Response({
            'success': True,
            'message': f'Course "{course}" deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    

# Course API to hide a course
class CourseHideAPIView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner | IsAdmin]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Hiding course with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Course not found')
        
        instance.is_visible = False
        instance.save()

        logger.info("Course hidden successfully")
        return Response({
            'success': True,
            'message': f'Course "{instance}" hidden successfully',
            'course': CourseSerializer(instance).data
        }, status=status.HTTP_200_OK)
    
# Course API to show a course
class CourseShowAPIView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner | IsAdmin]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Showing course with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Course not found')
        
        instance.is_visible = True
        instance.save()

        logger.info("Course shown successfully")
        return Response({
            'success': True,
            'message': f'Course "{instance}" shown successfully',
            'course': CourseSerializer(instance).data
        }, status=status.HTTP_200_OK)