import type { User } from "./user";
import type { Course } from "./course";

interface Payment {
  id: number;
  amount: number;
  payment_method: string;
  created_at: string;
  status: string;
}

export interface Enrollment {
  id: number;
  student: User;
  course: Course;
  payment: Payment;
  created_at: string;
  progress: number;
}
