import type { User } from "./user";
import type { Course } from "./course";

export interface Favorite {
  id: number;
  student: User;
  course: Course;
  created_at: string;
}
