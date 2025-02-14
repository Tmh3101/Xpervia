from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from api.exceptions.custom_exceptions import FileUploadException
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.models.course_detail_model import CourseDetail
from api.models.course_model import Course
from api.models.lesson_model import Lesson
from api.serializers.course_serializer import CourseSerializer
from api.serializers.course_detail_serializer import CourseDetailSerializer
from api.serializers.chapter_serializer import ChapterSerializer
from api.serializers.lesson_serializer import SimpleLessonSerializer
from api.permissions.teacher_permissions_checker import IsTeacher, IsCourseOwner
from api.services.google_drive_service import upload_file, delete_file    

def create_course(request):
    # Upload the thumbnail
    try:
        thumbnail_id = upload_file(request.FILES.get('thumbnail'))
        request.data['thumbnail_id'] = thumbnail_id
    except Exception as e:
        raise FileUploadException(f'Error uploading thumbnail: {str(e)}')

    # Chuyển đổi categories thành danh sách nếu nó là một chuỗi
    categories = request.data.get('categories')
    if isinstance(categories, str):
        categories = categories.split(',')

    # Create the course
    course_data = {
        'title': request.data.get('title'),
        'description': request.data.get('description'),
        'thumbnail_id': request.data.get('thumbnail_id'),
        'teacher_id': request.user.id
    }
    course_serializer = CourseSerializer(data=course_data)
    if not course_serializer.is_valid():
        delete_file(request.data.get('thumbnail_id'))
        raise ValidationError(f'Error creating course: {course_serializer.errors}')
    
    course = course_serializer.save()
    course.categories.set(categories)
    return course

def delete_course(course_id):
    course = Course.objects.get(id=course_id)
    if course:
        delete_file(course.thumbnail_id)
        course.delete()

# Course Detail API View to create a course detail
class CourseDetailCreateAPIView(generics.CreateAPIView):
    queryset = CourseDetail.objects.all()
    serializer_class = CourseDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher]

    def create(self, request, *args, **kwargs):

        # Create the course
        course = create_course(request)

        # Create the course detail
        course_detail_data = {  
            'course_id': course.id,
            'price': request.data.get('price'),
            'discount': request.data.get('discount') or '0',
            'is_visible': request.data.get('is_visible'),
            'start_date': request.data.get('start_date'),
            'regis_start_date': request.data.get('regis_start_date'),
            'regis_end_date': request.data.get('regis_end_date'),
            'max_students': request.data.get('max_students'),
        }

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
        
    
# Course Detail API View to list all course details
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
    

# Course Detail API View to retrieve a course detail with all its chapters and lessons
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
        
        # Lấy tất cả các chapters liên quan đến course của course detail hiện tại
        chapters = instance.course.chapters.all()
        chapters_data = []
        for chapter in chapters:
            chapter_data = ChapterSerializer(chapter).data
            lessons = Lesson.objects.filter(chapter=chapter)
            lessons_serializer = SimpleLessonSerializer(lessons, many=True)
            chapter_data['lessons'] = lessons_serializer.data
            chapter_data.pop('course')
            chapters_data.append(chapter_data)

        # Lọc tất cả các lessons không thuộc bất kỳ chapter nào
        lessons_without_chapter = Lesson.objects.filter(course=instance.course, chapter__isnull=True)
        lessons_without_chapter_serializer = SimpleLessonSerializer(lessons_without_chapter, many=True)

        serializer = self.get_serializer(instance)
        course_detail_data = serializer.data.copy()
        course_data = course_detail_data['course']

        course_data['chapters'] = chapters_data
        course_data['lessons_without_chapter'] = lessons_without_chapter_serializer.data

        course_detail_data['course'] = course_data

        return Response({
            'success': True,
            'message': 'Course detail retrieved successfully',
            'data': course_detail_data
        }, status=status.HTTP_200_OK)
    

# Course Detail API View to update a course detail
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
        
        # Update the thumbnail
        old_thumbnail_id = None
        if request.FILES.get('thumbnail'):
            try:
                thumbnail_id = upload_file(request.FILES.get('thumbnail'))
                request.data['thumbnail_id'] = thumbnail_id
                old_thumbnail_id = instance.course.thumbnail_id
            except Exception as e:
                raise FileUploadException(f'Error uploading thumbnail: {str(e)}')
            
        # Update the course detail
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            delete_file(serializer.data.get('thumbnail_id'))
            raise ValidationError(f'Error updating course detail: {serializer.errors}')
        
        # Delete the old thumbnail
        if old_thumbnail_id:
            delete_file(old_thumbnail_id)

        serializer.save()
        return Response({
            'success': True,
            'message': 'Course detail updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
            
        
# Course Detail API View to delete a course detail
class CourseDetailDeleteAPIView(generics.DestroyAPIView):
    queryset = CourseDetail.objects.all()
    serializer_class = CourseDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacher & IsCourseOwner]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound('Course detail not found')
        
        # Delete the course detail
        course_id = instance.course.id
        instance.delete()
        delete_course(course_id)
        return Response({
            'success': True,
            'message': 'Course detail deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)