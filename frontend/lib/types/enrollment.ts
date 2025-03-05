import { SimpleCourseContent } from './course-content';

interface Payment {
    id: string;
    amount: number;
    payment_method: string;
    created_at: string;
    status: string;
}

export interface Enrollment {
    id: string;
    course: SimpleCourseContent;
    payment: Payment;
    created_at: string;
    progress: number;
}