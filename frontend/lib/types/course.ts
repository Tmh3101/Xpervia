import { SimpleUser } from './user';
import { Chapter, ChapterDetail } from './chapter';
import { Lesson, LessonDetail } from './lesson';

interface Category {
    id: number;
    name: string;
    description: string;
}

interface CourseContent {
    id: number;
    teacher: SimpleUser;
    categories: Category[];
    title: string;
    description: string;
    thumbnail_id: string;
}

export interface Course {
    id: number;
    course_content: CourseContent;
    price: number;
    discount: number;
    is_visible: boolean;
    created_at: string;
    start_date: string;
    regis_start_date: string;
    regis_end_date: string;
    max_students: number;
}

interface CourseContentDetail extends CourseContent {
    chapters: Chapter[];
    lessons_without_chapter: Lesson[];
}

interface CourseContentWithDetailLessons extends CourseContent {
    chapters: ChapterDetail[];
    lessons_without_chapter: LessonDetail[];
}    

export interface CourseDetail extends Course {
    course_content: CourseContentDetail;
}

export interface CourseWithDetailLessons extends Course {
    course_content: CourseContentWithDetailLessons;
}