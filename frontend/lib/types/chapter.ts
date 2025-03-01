import { Lesson, LessonDetail } from './lesson';

export interface Chapter {
    id: number;
    title: string;
    order: number;
    lessons: Lesson[];
}

export interface ChapterDetail extends Chapter {
    lessons: LessonDetail[];
}