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
    attachment_id: string;
}