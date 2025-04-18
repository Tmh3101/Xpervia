import authAxios from './axios-auth'
import { Chapter, CreateChapterRequest } from '@/lib/types/chapter'

export const createChapterApi = async (courseId: number, chapter: CreateChapterRequest) : Promise<Chapter> => {
    if (chapter.order === null) {
        delete chapter.order
    }

    const response = await authAxios.post(
        `courses/${courseId}/chapters/create/`,
        chapter
    )
    return response.data.chapter
}

export const updateChapterApi = async (chapterId: number, chapter: CreateChapterRequest) : Promise<Chapter> => {
    if (chapter.order === null) {
        delete chapter.order
    }

    const response = await authAxios.put(
        `courses/chapters/${chapterId}/update/`,
        chapter
    )
    return response.data.chapter
}

export const deleteChapterApi = async (chapterId: number) : Promise<boolean> => {
    const response = await authAxios.delete(
        `courses/chapters/${chapterId}/delete/`
    )
    return response.data.success
}