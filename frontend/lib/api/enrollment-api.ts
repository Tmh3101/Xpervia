import axios from 'axios'
import { Enrollment } from '../types/enrollment'
import { Response } from '@/lib/api/response'

const baseUrl = 'http://localhost:8000/api/'

interface EnrollmentsResponse extends Response {
    enrollments: Enrollment[];
}

export const getEnrollmentsByStudentApi = async () : Promise<Enrollment[]> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.get<EnrollmentsResponse>(
        `${baseUrl}courses/enrollments/student/`,
        { headers }
    )
    return response.data.enrollments
}

export const getEnrollmentsByCourseApi = async (courseId: number) : Promise<Enrollment[]> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.get<EnrollmentsResponse>(
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