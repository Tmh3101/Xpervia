import {
    CourseContent,
    CourseContentWithDetailLessons
} from './course-content';

export interface Course {
    id: number;
    course_content: CourseContent;
    price: number;
    discount: number;
    is_visible: boolean;
    created_at: string;
    start_date: string;
    regis_start_date: string;
    regis_end_date: string;
    max_students: number;
    num_students: number;
}   

export interface CourseWithDetailLessons extends Course {
    course_content: CourseContentWithDetailLessons;
}

export interface EnrolledCourse extends Course {
    progress: number;
}

export interface CreateCourseRequest {
    thumbnail: File;
    title: string;
    description: string;
    price: number;
    start_date: string | null;
    regis_start_date: string | null;
    regis_end_date: string | null;
    max_students: number;
    is_visible: boolean;
    categories: number[]; 
    discount: number | null;
}
  