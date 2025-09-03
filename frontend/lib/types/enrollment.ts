import type { User } from "./user";
import type { Course } from "./course";

interface Payment {
  id: string;
  amount: number;
  payment_method: string;
  created_at: string;
  status: string;
}

export interface Enrollment {
  id: string;
  student: User;
  course: Course;
  payment: Payment;
  created_at: string;
  progress: number;
}
