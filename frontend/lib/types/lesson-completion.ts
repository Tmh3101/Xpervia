import type { Lesson } from "./lesson";
import type { User } from "./user";

export interface LessonCompletion {
  id: number;
  lesson: Lesson;
  user: User;
  complete_at: string;
}
