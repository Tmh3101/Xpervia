import axios from 'axios'
import { Enrollment } from '../types/enrollment'

const baseUrl = 'http://localhost:8000/api/'
// const baseUrl = 'http://192.168.1.4:8000/api/'

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