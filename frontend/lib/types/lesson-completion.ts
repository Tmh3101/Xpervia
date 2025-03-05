import { Lesson } from './lesson';
import { SimpleUser } from './user';

export interface LessonCompletion {
    id: number;
    lesson: Lesson;
    user: SimpleUser;
    complete_at: string;
}