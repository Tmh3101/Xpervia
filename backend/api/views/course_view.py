import json
import logging
import uuid
from django.conf import settings
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, ValidationError
from api.exceptions.custom_exceptions import FileUploadException
from api.models import Course, Lesson, CourseContent, Enrollment, User
from api.serializers import (
    CourseSerializer,
    CourseContentSerializer,
    ChapterSerializer,
    SimpleLessonSerializer,
    LessonSerializer
)
from api.permissions import IsTeacher, IsCourseOwner, IsAdmin   
from api.middlewares.authentication import SupabaseJWTAuthentication
from api.services.supabase.storage import upload_file, delete_file, get_file_url

logger = logging.getLogger(__name__)

# Create a course data from request
def get_course_content(request):
    course_content = {}
    course_content['teacher_id'] = request.user.id

    if request.FILES.get('thumbnail'):
        try:
            thumbnail = request.FILES.get('thumbnail')
            thumbnail_path = f'thumbnails/{uuid.uuid4()}.{thumbnail.name.split(".")[-1]}'
            logger.info(f"Uploading thumbnail to Supabase: {thumbnail_path}")
            upload_file(
                bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
                path=thumbnail_path,
                file_data=thumbnail,
                content_type=thumbnail.content_type
            )
        except Exception as e:
            logger.error(f"Error uploading thumbnail: {str(e)}")
            raise FileUploadException(f'Error uploading thumbnail: {str(e)}')
        course_content['thumbnail_path'] = thumbnail_path
    if request.data.get('title'):
        course_content['title'] = request.data.get('title')
    if request.data.get('description'):
        course_content['description'] = request.data.get('description')

    return course_content

# Delete a course if course detail creation fails
def delete_course_content(course_content_id):
    course_content = CourseContent.objects.get(id=course_content_id)
    if course_content:
        delete_file(
            bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
            path=course_content.thumbnail_path
        )
        course_content.delete()

def get_course_content_lessons(course_content):
    chapters = course_content.chapters.all()
    chapters_data = []
    for chapter in chapters:
        chapter_serializer = ChapterSerializer(chapter)
        chapter_data = chapter_serializer.data.copy()
        lessons = Lesson.objects.filter(chapter=chapter)
        lessons_data = SimpleLessonSerializer(lessons, many=True).data.copy()
        for lesson in lessons_data:
            lesson.pop('chapter', None)
            lesson.pop('course_content', None)
        chapter_data['lessons'] = lessons_data
        chapter_data.pop('course_content')
        chapters_data.append(chapter_data)

    lessons_without_chapter = Lesson.objects.filter(course_content=course_content, chapter__isnull=True)
    lessons_without_chapter_data = SimpleLessonSerializer(lessons_without_chapter, many=True).data.copy()
    for lesson in lessons_without_chapter_data:
        lesson.pop('chapter', None)
        lesson.pop('course_content', None)

    return chapters_data, lessons_without_chapter_data

def add_file_url_for(lesson):
    for file_type in ['video_path', 'subtitle_vi_path', 'attachment']:
        if not lesson.get(file_type):
            continue

        if file_type == 'attachment':
            lesson['attachment']['file_url'] = get_file_url(
                bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                path=lesson['attachment']['file_path'],
                is_public=True
            )
        else:
            lesson[f'{file_type.split("_path")[0]}_url'] = get_file_url(
                bucket=settings.SUPABASE_STORAGE_PRIVATE_BUCKET,
                path=lesson[file_type],
                is_public=True
            )


# Course Detail API to list all course
class CourseListAPIView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        logger.info("Listing all courses")
        queryset = self.get_queryset().filter()
        courses_data = CourseSerializer(queryset, many=True).data.copy()

        for course in courses_data:
            course_content = Course.objects.get(id=course['id']).course_content
            course_content_data = CourseContentSerializer(course_content).data.copy()
            course_content_data['thumbnail_url'] = get_file_url(
                bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
                path=course_content.thumbnail_path,
                is_public=True
            )
            chapters_data, lessons_without_chapter = get_course_content_lessons(course_content)
            course_content_data['chapters'] = chapters_data
            course_content_data['lessons_without_chapter'] = lessons_without_chapter
            course['course_content'] = course_content_data
            # Add num_students to each course
            enrollments = Enrollment.objects.filter(course=course['id'])
            course['num_students'] = enrollments.count()
        
        logger.info("Successfully listed all courses")
        return Response({
            'success': True,
            'message': 'All courses have been listed successfully',
            'courses': courses_data
        }, status=status.HTTP_200_OK)
    
# Course Detail API to list all course of a teacher
class CourseListByTeacherAPIView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher]

    def list(self, request, *args, **kwargs):
        logger.info(f"Listing courses for teacher ID: {request.user.id}")

        teacher = User.objects.get(id=request.user.id)

        queryset = self.get_queryset().filter(course_content__teacher=teacher)
        courses_serializer = CourseSerializer(queryset, many=True)
        courses_data = courses_serializer.data.copy()

        # Add num_students to each course
        for course in courses_data:
            enrollments = Enrollment.objects.filter(course=course['id'])
            course['num_students'] = enrollments.count()
            course['course_content']['thumbnail_url'] = get_file_url(
                bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
                path=course['course_content']['thumbnail_path'],
                is_public=True
            )

        logger.info("Successfully listed courses for teacher")
        return Response({
            'success': True,
            'message': 'All courses have been listed successfully',
            'courses': courses_data
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

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving course with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Course not found')
        
        course_content = instance.course_content
        course_content_data = CourseContentSerializer(course_content).data.copy()
        chapters_data, lessons_without_chapter_data = get_course_content_lessons(course_content)
        course_content_data['thumbnail_url'] = get_file_url(
            bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
            path=course_content.thumbnail_path,
            is_public=True
        )
        course_content_data['chapters'] = chapters_data
        course_content_data['lessons_without_chapter'] = lessons_without_chapter_data

        course_data = self.get_serializer(instance).data.copy()
        course_data['course_content'] = course_content_data

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
        course_data['course_content']['thumbnail_url'] = get_file_url(
            bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
            path=course_content['thumbnail_path'],
            is_public=True
        )

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

        course_data = course_serializer.data.copy()
        course_data['course_content']['thumbnail_url'] = get_file_url(
            bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
            path=course_content.thumbnail_path,
            is_public=True
        )

        return Response({
            'success': True,
            'message': 'Course updated successfully',
            'course': course_data
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