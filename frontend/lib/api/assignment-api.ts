import axios from 'axios'
import { AssignmentDetail, AssignmentSubmissions, CreateAssignmentRequest } from '../types/assignment'

const baseUrl = process.env.NEXT_PUBLIC_API_URL

export const getLessonAssignmentsApi = async (lessonId: number) : Promise<AssignmentDetail[]> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.get(
        `${baseUrl}courses/lessons/${lessonId}/assignments/student/`,
        { headers }
    )
    return response.data.assignments
}

export const getAssignmentSubmissionsApi = async (lessonId: number) : Promise<AssignmentSubmissions[]> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.get(
        `${baseUrl}courses/lessons/${lessonId}/assignments/`,
        { headers }
    )
    return response.data.assignments
}

export const createAssignmentApi = async (lessonId: number, data: CreateAssignmentRequest) : Promise<void> => {
    if (data.due_at === "") {
        delete data.due_at
    }
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    await axios.post(
        `${baseUrl}courses/lessons/${lessonId}/assignments/create/`,
        data,
        { headers }
    )
}

export const deleteAssignmentApi = async (assignmentId: number) : Promise<void> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    await axios.delete(
        `${baseUrl}courses/lessons/assignments/${assignmentId}/delete/`,
        { headers }
    )
}

export const updateAssignmentApi = async (assignmentId: number, data: CreateAssignmentRequest) : Promise<AssignmentDetail> => {
    if (data.due_at === "") {
        delete data.due_at
    }
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.put(
        `${baseUrl}courses/lessons/assignments/${assignmentId}/update/`,
        data,
        { headers }
    )
    return response.data.assignment
}