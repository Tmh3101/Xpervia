import axios from 'axios'
import { Enrollment } from '../types/enrollment'

const baseUrl = process.env.NEXT_PUBLIC_API_URL

export const getEnrollmentsApi = async (): Promise<Enrollment[]> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.get(
        `${baseUrl}courses/enrollments/`,
        { headers }
    )
    return response.data.enrollments
}

export const getEnrollmentsByStudentApi = async (token: string): Promise<Enrollment[]> => {
    if (!token) {
      throw new Error("Token không tồn tại. Vui lòng đăng nhập lại.")
    }
  
    const headers = {
      'Authorization': `Token ${token}`
    }
  
    const response = await axios.get(
      `${baseUrl}courses/enrollments/student/`,
      { headers }
    )
    return response.data.enrollments
}

export const getEnrollmentsByCourseApi = async (courseId: number) : Promise<Enrollment[]> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.get(
        `${baseUrl}courses/${courseId}/enrollments/`,
        { headers }
    )
    return response.data.enrollments
}

export const enrollCourseApi = async (courseId: number) : Promise<boolean> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.post(
        `${baseUrl}courses/${courseId}/enrollments/create/`,
        {},
        { headers }
    )
    return response.data.success
}