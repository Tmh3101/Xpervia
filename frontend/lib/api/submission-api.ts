import axios from 'axios'
import { Submission } from '../types/submission'

const baseUrl = 'http://localhost:8000/api/'

export const submitAssignmentApi = async (assignmentId: number, fileData: File) : Promise<Submission> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`,
        'Content-Type': 'multipart/form-data'
    }
    const response = await axios.post(
        `${baseUrl}courses/assignments/${assignmentId}/submissions/create/`,
        { file: fileData },
        { headers }
    )
    return response.data.submission
}

export const deleteSubmissionApi = async (submissionId: number) : Promise<boolean> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    const response =  await axios.delete(
        `${baseUrl}courses/assignments/submissions/${submissionId}/delete/`,
        { headers }
    )
    return response.data.success
}