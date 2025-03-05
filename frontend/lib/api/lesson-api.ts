import axios from 'axios'
import { Response } from './response'
import { LessonCompletion } from '../types/lesson-completion'

const baseUrl = 'http://localhost:8000/api/'

interface LessonCompletionsResponse extends Response {
    lesson_completions: LessonCompletion[];
}

export const getLessonCompletionsApi = async (courseId: number) : Promise<LessonCompletion[]> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    const response = await axios.get<LessonCompletionsResponse>(
        `${baseUrl}courses/${courseId}/lessons/completions/student/`,
        { headers }
    )
    return response.data.lesson_completions
}

export const completeLessonApi = async (lessonId: number) : Promise<boolean> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    const response = await axios.post(
        `${baseUrl}courses/lessons/${lessonId}/completions/create/`,
        {},
        { headers }
    )
    return response.data.success
}

export const uncompleteLessonApi = async (lessonId: number) : Promise<boolean> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    const response = await axios.delete(
        `${baseUrl}courses/lessons/${lessonId}/completions/delete/`,
        { headers }
    )
    return response.data.success
}