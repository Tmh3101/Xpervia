import authAxios from './axios-auth'
import { LessonCompletion } from '../types/lesson-completion'
import { CreateLessonRequest, LessonDetail } from '../types/lesson'

export const getLessonDetailApi = async (lessonId: number): Promise<LessonDetail> => {
    const response = await authAxios.get(`courses/lessons/${lessonId}/`)
    return response.data.lesson_detail
}

export const getLessonCompletionsApi = async (courseId: number): Promise<LessonCompletion[]> => {
    const response = await authAxios.get(`courses/${courseId}/lessons/completions/student/`)
    return response.data.lesson_completions
}

export const completeLessonApi = async (lessonId: number): Promise<boolean> => {
    const response = await authAxios.post(`courses/lessons/${lessonId}/completions/create/`, {})
    return response.data.success
}

export const uncompleteLessonApi = async (lessonId: number): Promise<boolean> => {
    const response = await authAxios.delete(`courses/lessons/${lessonId}/completions/delete/`)
    return response.data.success
}

export const createLessonApi = async (courseId: number, chapterId: number | null, data: CreateLessonRequest): Promise<boolean> => {
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

    const response = await authAxios.post(`courses/${courseId}/lessons/create/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data.success
}

export const updateLessonApi = async (lessonId: number, data: CreateLessonRequest): Promise<boolean> => {
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

    const response = await authAxios.put(`courses/lessons/${lessonId}/update/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data.success
}

export const deleteLessonApi = async (lessonId: number): Promise<boolean> => {
    const response = await authAxios.delete(`courses/lessons/${lessonId}/delete/`)
    return response.data.success
}
