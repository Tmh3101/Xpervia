import axios from 'axios'
import { Enrollment } from '../types/enrollment'
import { Response } from '@/lib/api/response'

const baseUrl = 'http://localhost:8000/api/'

interface EnrollmentsResponse extends Response {
    enrollments: Enrollment[];
}

export const getEnrollmentsApi = async () : Promise<Enrollment[]> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    const response = await axios.get<EnrollmentsResponse>(
        `${baseUrl}courses/enrollments/student/`,
        { headers }
    )
    return response.data.enrollments
}

export const enrollCourseApi = async (courseId: number) : Promise<boolean> => {
    console.log('token', sessionStorage.getItem("token"))
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    const response = await axios.post(
        `${baseUrl}courses/${courseId}/enrollments/create/`,
        {},
        { headers }
    )
    return response.data.success
}