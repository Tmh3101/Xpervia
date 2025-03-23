import axios from 'axios'
import { AssignmentDetail, AssignmentSubmissions, CreateAssignmentRequest } from '../types/assignment'

const baseUrl = 'http://localhost:8000/api/'

interface AssignmentResponse {
    assignments: AssignmentDetail[]
}

interface AssignmentSubmissionsResponse {
    assignments: AssignmentSubmissions[];
}

export const getLessonAssignmentsApi = async (lessonId: number) : Promise<AssignmentDetail[]> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.get<AssignmentResponse>(
        `${baseUrl}courses/lessons/${lessonId}/assignments/student/`,
        { headers }
    )
    return response.data.assignments
}

export const getAssignmentSubmissionsApi = async (lessonId: number) : Promise<AssignmentSubmissions[]> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.get<AssignmentSubmissionsResponse>(
        `${baseUrl}courses/lessons/${lessonId}/assignments/`,
        { headers }
    )
    return response.data.assignments
}

export const createAssignmentApi = async (lessonId: number, data: CreateAssignmentRequest) : Promise<void> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    await axios.post(
        `${baseUrl}courses/lessons/${lessonId}/assignments/`,
        data,
        { headers }
    )
}