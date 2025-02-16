from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from api.exceptions.custom_exceptions import FileUploadException
from api.models import Course, CourseDetail, Lesson
from api.serializers import (
    CourseSerializer, CourseDetailSerializer, ChapterSerializer, SimpleLessonSerializer
)
from api.permissions import IsTeacher, IsCourseOwner
from api.services.google_drive_service import upload_file, delete_file    

# Create a course data from request
def get_course_data(request):
    course_data = {}
    course_data['teacher_id'] = request.user.id

    if request.FILES.get('thumbnail'):
        try:
            thumbnail_id = upload_file(request.FILES.get('thumbnail'))
        except Exception as e:
            raise FileUploadException(f'Error uploading thumbnail: {str(e)}')
        course_data['thumbnail_id'] = thumbnail_id
    if request.data.get('title'):
        course_data['title'] = request.data.get('title')
    if request.data.get('description'):
        course_data['description'] = request.data.get('description')

    return course_data

# Create a course detail data from request
def get_course_detail_data(request):
    course_detail_data = {}

    if request.data.get('price'):
        course_detail_data['price'] = request.data.get('price')
    if request.data.get('discount'):
        course_detail_data['discount'] = request.data.get('discount')
    if request.data.get('is_visible'):
        course_detail_data['is_visible'] = request.data.get('is_visible')
    if request.data.get('start_date'):
        course_detail_data['start_date'] = request.data.get('start_date')
    if request.data.get('regis_start_date'):
        course_detail_data['regis_start_date'] = request.data.get('regis_start_date')
    if request.data.get('regis_end_date'):
        course_detail_data['regis_end_date'] = request.data.get('regis_end_date')
    if request.data.get('max_students'):
        course_detail_data['max_students'] = request.data.get('max_students')

    return course_detail_data

# Delete a course if course detail creation fails
def delete_course(course_id):
    course = Course.objects.get(id=course_id)
    if course:
        delete_file(course.thumbnail_id)
        course.delete()


# Course Detail API to list all course details
class CourseDetailListAPIView(generics.ListAPIView):
    queryset = CourseDetail.objects.all()
    serializer_class = CourseDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(is_visible=True)      
        serializer = CourseDetailSerializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'All course details have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


# Course Detail API to create a course detail
class CourseDetailCreateAPIView(generics.CreateAPIView):
    queryset = CourseDetail.objects.all()
    serializer_class = CourseDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher]

    def create(self, request, *args, **kwargs):
        # Check & create the course
        course_data = get_course_data(request)
        course_serializer = CourseSerializer(data=course_data)
        if not course_serializer.is_valid():
            delete_file(request.data.get('thumbnail_id'))
            raise ValidationError(f'Error creating course: {course_serializer.errors}')
        course = course_serializer.save()

        categories = request.data.get('categories')
        if isinstance(categories, str):
            categories = categories.split(',')
        course.categories.set(categories)

        # Check & create the course detail
        course_detail_data = get_course_detail_data(request)
        course_detail_data['course_id'] = course.id

        course_detail_serializer = CourseDetailSerializer(data=course_detail_data)
        if not course_detail_serializer.is_valid():
            delete_course(course.id)
            raise ValidationError(f'Error creating course detail: {course_detail_serializer.errors}')
        
        try:
            self.perform_create(course_detail_serializer)
        except Exception as e:
            delete_course(course.id)
            raise ValidationError(f'Error creating course detail: {str(e)}')
        
        headers = self.get_success_headers(course_detail_serializer.data)
        return Response({
            'success': True,
            'message': 'Course and course detail created successfully',
            'data': course_detail_serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    

# Course Detail API to retrieve a course detail
class CourseDetailRetrieveAPIView(generics.RetrieveAPIView):
    queryset = CourseDetail.objects.all()
    serializer_class = CourseDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Course detail not found')
        
        # Get all chapters and lessons of the course
        chapters = instance.course.chapters.all()
        chapters_data = []
        for chapter in chapters:
            chapter_data = ChapterSerializer(chapter).data
            lessons = Lesson.objects.filter(chapter=chapter)
            lessons_serializer = SimpleLessonSerializer(lessons, many=True)
            chapter_data['lessons'] = lessons_serializer.data
            chapter_data.pop('course')
            chapters_data.append(chapter_data)

        # Get all lessons without chapter
        lessons_without_chapter = Lesson.objects.filter(course=instance.course, chapter__isnull=True)
        lessons_without_chapter_serializer = SimpleLessonSerializer(lessons_without_chapter, many=True)

        serializer = self.get_serializer(instance)
        course_detail_data = serializer.data.copy()
        course_data = course_detail_data['course']

        # Add chapters and lessons to the course data
        course_data['chapters'] = chapters_data
        course_data['lessons_without_chapter'] = lessons_without_chapter_serializer.data
        course_detail_data['course'] = course_data

        return Response({
            'success': True,
            'message': 'Course detail retrieved successfully',
            'data': course_detail_data
        }, status=status.HTTP_200_OK)
    

# Course Detail API to update a course detail
class CourseDetailUpdateAPIView(generics.UpdateAPIView):
    queryset = CourseDetail.objects.all()
    serializer_class = CourseDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Course detail not found')
        
        # Get the course data
        course_data = get_course_data(request)
        course_data['id'] = instance.course.id

        # Check the course data
        course_serializer = CourseSerializer(instance.course, data=course_data, partial=True)
        if not course_serializer.is_valid():
            if course_data.get('thumbnail_id'):
                delete_file(course_data.get('thumbnail_id'))
            raise ValidationError(f'Error updating course: {course_serializer.errors}')

        # Get the course detail data
        course_detail_data = get_course_detail_data(request)
        course_detail_data['course_id'] = instance.course.id

        # Check the course detail data
        course_detail_serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not course_detail_serializer.is_valid():
            if course_data.get('thumbnail_id'):
                delete_file(course_data.get('thumbnail_id'))
            raise ValidationError(f'Error updating course detail: {course_detail_serializer.errors}')

        # Update the course and course detail
        old_thumbnail_id = instance.course.thumbnail_id
        course = course_serializer.save()
        if request.data.get('categories'):
            categories = request.data.get('categories')
            if isinstance(categories, str):
                categories = categories.split(',')
            course.categories.set(categories)
        self.perform_update(course_detail_serializer)

        # Delete the old thumbnail
        if course_data.get('thumbnail_id'):
            delete_file(old_thumbnail_id)
        
        return Response({
            'success': True,
            'message': 'Course detail updated successfully',
            'data': course_detail_serializer.data
        }, status=status.HTTP_200_OK)
            
        
# Course Detail API to delete a course detail
class CourseDetailDeleteAPIView(generics.DestroyAPIView):
    queryset = CourseDetail.objects.all()
    serializer_class = CourseDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Course detail not found')
        
        # Delete the course detail
        course_id = instance.course.id
        self.perform_destroy(instance)
        delete_course(course_id)
        return Response({
            'success': True,
            'message': f'Course detail "{instance}" deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)