import { SimpleUser } from './user';
import { Chapter, ChapterDetail } from './chapter';
import { Lesson, LessonDetail } from './lesson';

interface Category {
    id: number;
    name: string;
    description: string;
}

export interface SimpleCourseContent {
    id: number;
    title: string;
    teacher: SimpleUser;
    categories: Category[];
}

export interface CourseContent {
    id: number;
    teacher: SimpleUser;
    categories: Category[];
    title: string;
    description: string;
    thumbnail_id: string;
    chapters: Chapter[];
    lessons_without_chapter: Lesson[];
}

export interface CourseContentWithDetailLessons extends CourseContent {
    chapters: ChapterDetail[];
    lessons_without_chapter: LessonDetail[];
} 