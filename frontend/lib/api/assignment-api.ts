import axios from 'axios'
import { AssignmentDetail } from '../types/assignment'

const baseUrl = 'http://localhost:8000/api/'

interface AssignmentResponse {
    assignments: AssignmentDetail[]
}

export const getLessonAssignmentsApi = async (lessonId: number) : Promise<AssignmentDetail[]> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    const response = await axios.get<AssignmentResponse>(
        `${baseUrl}courses/lessons/${lessonId}/assignments/student/`,
        { headers }
    )
    return response.data.assignments
}