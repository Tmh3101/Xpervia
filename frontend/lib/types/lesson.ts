import { File } from './file';
import { Submission } from './submission';

export interface Lesson {
    id: number;
    title: string;
    order: number;
    is_visible: boolean;
    created_at: string;
}

export interface LessonDetail extends Lesson {
    content: string;
    video_id: string;
    subtitle_vi_id: string;
    attachment: File;
}

export interface LessonWithSubmission extends LessonDetail {
    submissions: Submission[];
}