import json
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, ValidationError
from api.exceptions.custom_exceptions import FileUploadException
from api.models import Course, Lesson, CourseContent, Enrollment
from api.serializers import (
    CourseSerializer,
    CourseContentSerializer,
    ChapterSerializer,
    SimpleLessonSerializer,
    LessonSerializer
)
from api.permissions import IsTeacher, IsCourseOwner
from api.services.google_drive_service import upload_file, delete_file    

# Create a course data from request
def get_course_content(request):
    course_content = {}
    course_content['teacher_id'] = request.user.id

    if request.FILES.get('thumbnail'):
        try:
            thumbnail_id = upload_file(request.FILES.get('thumbnail'))
            thumbnail_id = thumbnail_id.get('file_id')
        except Exception as e:
            raise FileUploadException(f'Error uploading thumbnail: {str(e)}')
        course_content['thumbnail_id'] = thumbnail_id
    if request.data.get('title'):
        course_content['title'] = request.data.get('title')
    if request.data.get('description'):
        course_content['description'] = request.data.get('description')
    

    return course_content

# Create a course detail data from request
def get_course_data(request):
    course_data = {}

    if request.data.get('price'):
        course_data['price'] = request.data.get('price')
    if request.data.get('discount'):
        course_data['discount'] = request.data.get('discount')
    if request.data.get('is_visible'):
        course_data['is_visible'] = request.data.get('is_visible')
    if request.data.get('start_date'):
        course_data['start_date'] = request.data.get('start_date')
    if request.data.get('regis_start_date'):
        course_data['regis_start_date'] = request.data.get('regis_start_date')
    if request.data.get('regis_end_date'):
        course_data['regis_end_date'] = request.data.get('regis_end_date')
    if request.data.get('max_students'):
        course_data['max_students'] = request.data.get('max_students')

    return course_data

# Delete a course if course detail creation fails
def delete_course_content(course_content_id):
    course_content = CourseContent.objects.get(id=course_content_id)
    if course_content:
        delete_file(course_content.thumbnail_id)
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


# Course Detail API to list all course
class CourseListAPIView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(is_visible=True)
        courses_data = CourseSerializer(queryset, many=True).data.copy()

        for course in courses_data:
            course_content = Course.objects.get(id=course['id']).course_content
            course_content_data = CourseContentSerializer(course_content).data.copy()
            chapters_data, lessons_without_chapter = get_course_content_lessons(course_content)
            course_content_data['chapters'] = chapters_data
            course_content_data['lessons_without_chapter'] = lessons_without_chapter
            course['course_content'] = course_content_data
            # Add num_students to each course
            enrollments = Enrollment.objects.filter(course=course['id'])
            course['num_students'] = enrollments.count()
        
        return Response({
            'success': True,
            'message': 'All courses have been listed successfully',
            'courses': courses_data
        }, status=status.HTTP_200_OK)
    
# Course Detail API to list all course of a teacher
class CourseListByTeacherAPIView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(course_content__teacher=request.user)
        courses_serializer = CourseSerializer(queryset, many=True)
        courses_data = courses_serializer.data.copy()

        # Add num_students to each course
        for course in courses_data:
            enrollments = Enrollment.objects.filter(course=course['id'])
            course['num_students'] = enrollments.count()

        return Response({
            'success': True,
            'message': 'All courses have been listed successfully',
            'courses': courses_data
        }, status=status.HTTP_200_OK)


# Course Detail API to create a course detail
class CourseCreateAPIView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher]

    def create(self, request, *args, **kwargs):
        # Check & create the course
        course_content = get_course_content(request)
        course_content_serializer = CourseContentSerializer(data=course_content)
        if not course_content_serializer.is_valid():
            delete_file(request.data.get('thumbnail_id'))
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

        # Check & create the course detail
        course_data = get_course_data(request)
        course_data['course_content_id'] = course_content.id

        course_serializer = CourseSerializer(data=course_data)
        if not course_serializer.is_valid():
            delete_course_content(course_content.id)
            raise ValidationError(f'Error creating course: {course_serializer.errors}')
        
        try:
            self.perform_create(course_serializer)
        except Exception as e:
            delete_course_content(course_content.id)
            raise ValidationError(f'Error creating course: {str(e)}')
        
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
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

        return Response({
            'success': True,
            'message': 'Course retrieved successfully',
            'course': course_data
        }, status=status.HTTP_200_OK)
    

# Course API to retrieve a course detail
class CourseRetrieveWithDetailLessonsAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
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

        return Response({
            'success': True,
            'message': 'Course retrieved successfully',
            'course': course_data
        }, status=status.HTTP_200_OK)

    

# Course Detail API to update a course detail
class CourseUpdateAPIView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Course not found')
        
        # Get the course data
        course_content = get_course_content(request)

        # Check the course data
        course_content_serializer = CourseContentSerializer(instance.course_content, data=course_content, partial=True)
        if not course_content_serializer.is_valid():
            if course_content.get('thumbnail_id'):
                delete_file(course_content.get('thumbnail_id'))
            raise ValidationError(f'Error updating course: {course_content_serializer.errors}')

        # Get the course detail data
        course_data = get_course_data(request)
        course_data['course_content_id'] = instance.course_content.id

        # Check the course detail data
        course_serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not course_serializer.is_valid():
            if course_content.get('thumbnail_id'):
                delete_file(course_content.get('thumbnail_id'))
            raise ValidationError(f'Error updating course: {course_serializer.errors}')

        # Update the course and course detail
        old_thumbnail_id = instance.course_content.thumbnail_id
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
        self.perform_update(course_serializer)

        # Delete the old thumbnail
        if request.FILES.get('thumbnail'):
            delete_file(old_thumbnail_id)
        
        return Response({
            'success': True,
            'message': 'Course updated successfully',
            'data': course_serializer.data
        }, status=status.HTTP_200_OK)
            
        
# Course Detail API to delete a course detail
class CourseDeleteAPIView(generics.DestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Course not found')
        
        # Delete the course detail
        course_content_id = instance.course_content.id
        self.perform_destroy(instance)
        delete_course_content(course_content_id)

        return Response({
            'success': True,
            'message': f'Course "{instance}" deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)