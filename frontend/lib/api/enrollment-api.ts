import authAxios from "./axios-auth";
import type { Enrollment } from "../types/enrollment";

export const getEnrollmentsApi = async (): Promise<Enrollment[]> => {
  const response = await authAxios.get(`courses/enrollments/`);
  return response.data.enrollments;
};

export const getEnrollmentsByStudentApi = async (): Promise<Enrollment[]> => {
  const response = await authAxios.get(`courses/enrollments/student/`);
  return response.data.enrollments;
};

export const getEnrollmentsByCourseApi = async (
  courseId: number
): Promise<Enrollment[]> => {
  const response = await authAxios.get(`courses/${courseId}/enrollments/`);
  return response.data.enrollments;
};

export const enrollCourseApi = async (
  courseId: number
): Promise<Enrollment> => {
  const response = await authAxios.post(`courses/${courseId}/enroll/`, {});
  return response.data.enrollment;
};
