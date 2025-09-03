import type { Lesson, LessonDetail } from "./lesson";

export interface Chapter {
  id: number;
  title: string;
  order: number;
  lessons: Lesson[];
}

export interface ChapterDetail extends Chapter {
  lessons: LessonDetail[];
}

export interface CreateChapterRequest {
  title: string;
  order?: number | null;
}
