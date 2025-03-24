import axios from 'axios'
import { Submission, SubmissionScore } from '../types/submission'

const baseUrl = 'http://localhost:8000/api/'

export const submitAssignmentApi = async (assignmentId: number, fileData: File) : Promise<Submission> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`,
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
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response =  await axios.delete(
        `${baseUrl}courses/assignments/submissions/${submissionId}/delete/`,
        { headers }
    )
    return response.data.success
}

export const scoreSubmissionApi = async (submissionId: number, submissionScore: SubmissionScore) : Promise<Submission> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.post(
        `${baseUrl}courses/assignments/submissions/${submissionId}/score/`,
        {
            score: submissionScore.score,
            feedback: submissionScore.feedback
        },
        { headers }
    )
    return response.data.submission
}