import { SimpleCourseContent } from './course-content';
import { SimpleUser } from './user';
import { Course } from './course';

interface Payment {
    id: string;
    amount: number;
    payment_method: string;
    created_at: string;
    status: string;
}

export interface Enrollment {
    id: string;
    student: SimpleUser;
    course: Course;
    payment: Payment;
    created_at: string;
    progress: number;
}