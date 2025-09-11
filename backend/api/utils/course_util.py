import logging
import uuid
from django.conf import settings
from api.exceptions.custom_exceptions import FileUploadException
from api.services.supabase.storage import upload_file, delete_file, get_file_url
from api.models import CourseContent, Lesson, LessonCompletion
from api.serializers import ChapterSerializer, SimpleLessonSerializer

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
        course_content['thumbnail_url'] = get_file_url(
            bucket=settings.SUPABASE_STORAGE_PUBLIC_BUCKET,
            path=thumbnail_path,
            is_public=True
        )
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
        chapter_data = ChapterSerializer(chapter).data.copy()
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

def get_course_progress(course_content, student_id):
    total_lessons = course_content.lessons.count()
    completed_lessons = LessonCompletion.objects.filter(
        lesson__course_content=course_content, student_id=student_id
    ).count()
    return round(completed_lessons / total_lessons * 100, 2) if total_lessons > 0 else 0