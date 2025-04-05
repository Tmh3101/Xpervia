import axios from 'axios'
import { Chapter, CreateChapterRequest } from '@/lib/types/chapter'

const baseUrl = 'http://localhost:8000/api/'
// const baseUrl = 'http://192.168.1.4:8000/api/'
export const createChapterApi = async (courseId: number, chapter: CreateChapterRequest) : Promise<Chapter> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    
    if (chapter.order === null) {
        delete chapter.order
    }

    const response = await axios.post(
        `${baseUrl}courses/${courseId}/chapters/create/`,
        chapter,
        { headers }
    )
    return response.data.chapter
}

export const updateChapterApi = async (chapterId: number, chapter: CreateChapterRequest) : Promise<Chapter> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }

    if (chapter.order === null) {
        delete chapter.order
    }

    const response = await axios.put(
        `${baseUrl}courses/chapters/${chapterId}/update/`,
        chapter,
        { headers }
    )
    return response.data.chapter
}

export const deleteChapterApi = async (chapterId: number) : Promise<boolean> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.delete(
        `${baseUrl}courses/chapters/${chapterId}/delete/`,
        { headers }
    )
    return response.data.success
}