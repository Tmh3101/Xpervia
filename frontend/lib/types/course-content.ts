import type { User } from "./user";
import type { Chapter, ChapterDetail } from "./chapter";
import type { Lesson, LessonDetail } from "./lesson";

export interface Category {
  id: number;
  name: string;
  description: string;
}

export interface SimpleCourseContent {
  id: number;
  title: string;
  teacher: User;
  categories: Category[];
}

export interface CourseContent {
  id: number;
  teacher: User;
  categories: Category[];
  title: string;
  description: string;
  thumbnail_url: string;
  chapters: Chapter[];
  lessons_without_chapter: Lesson[];
  num_lessons?: number;
}

export interface CourseContentWithDetailLessons extends CourseContent {
  chapters: ChapterDetail[];
  lessons_without_chapter: LessonDetail[];
}
