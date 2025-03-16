import axios from 'axios'
import { Response } from './response'
import { LessonCompletion } from '../types/lesson-completion'
import { CreateLessonRequest } from '../types/lesson'

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

export const createLessonApi = async (courseId: number, chapterId: number | null, data: CreateLessonRequest) : Promise<boolean> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`,
        'Content-Type': 'multipart/form-data'
    }

    let formData = new FormData()
    formData.append('title', data.title)
    formData.append('content', data.content)
    
    formData.append('video', data.video)
    formData.append('is_visible', data.is_visible.toString())

    if (data.subtitle_vi) {
        formData.append('subtitle_vi', data.subtitle_vi)
    }
    if (data.attachment) {
        formData.append('attachment', data.attachment)
    }

    if (chapterId) {
        formData.append('chapter_id', chapterId.toString())
    }

    const response = await axios.post(
        `${baseUrl}courses/${courseId}/lessons/create/`,
        formData,
        { headers }
    )
    return response.data.success
}

export const updateLessonApi = async (lessonId: number, data: CreateLessonRequest) : Promise<boolean> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`,
        'Content-Type': 'multipart/form-data'
    }

    let formData = new FormData()
    if (data.title) {
        formData.append('title', data.title)
    }
    
    if (data.content) {
        formData.append('content', data.content)
    }

    if (data.video) {
        formData.append('video', data.video)
    }

    if (data.is_visible) {
        formData.append('is_visible', data.is_visible.toString())
    }

    if (data.subtitle_vi) {
        formData.append('subtitle_vi', data.subtitle_vi)
    }

    if (data.attachment) {
        formData.append('attachment', data.attachment)
    }

    const response = await axios.put(
        `${baseUrl}courses/lessons/${lessonId}/update/`,
        formData,
        { headers }
    )
    return response.data.success
}
