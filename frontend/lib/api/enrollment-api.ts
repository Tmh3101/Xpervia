import authAxios from './axios-auth'
import { Enrollment } from '../types/enrollment'

export const getEnrollmentsApi = async (): Promise<Enrollment[]> => {
    const response = await authAxios.get(`courses/enrollments/`)
    return response.data.enrollments
}

export const getEnrollmentsByStudentApi = async (token: string): Promise<Enrollment[]> => {
    if (!token) {
      throw new Error("Token không tồn tại. Vui lòng đăng nhập lại.")
    }
  
    const response = await authAxios.get(`courses/enrollments/student/`)
    return response.data.enrollments
}

export const getEnrollmentsByCourseApi = async (courseId: number): Promise<Enrollment[]> => {
    const response = await authAxios.get(`courses/${courseId}/enrollments/`)
    return response.data.enrollments
}

export const enrollCourseApi = async (courseId: number): Promise<boolean> => {
    const response = await authAxios.post(`courses/${courseId}/enrollments/create/`, {})
    return response.data.success
}