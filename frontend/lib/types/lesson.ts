import type { File } from "./file";

export interface Lesson {
  id: string;
  title: string;
  order: number;
  is_visible: boolean;
  created_at: string;
}

export interface LessonDetail extends Lesson {
  content: string;
  video_url: string;
  subtitle_vi_url: string;
  attachment: File;
}

export interface CreateLessonRequest {
  title: string;
  content: string;
  video: File | Blob;
  subtitle_vi?: File | Blob;
  attachment?: File | Blob;
  is_visible: boolean;
}
