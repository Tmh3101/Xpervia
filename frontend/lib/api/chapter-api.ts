import axios from 'axios'
import { Response } from '@/lib/api/response'
import { Chapter, CreateChapterRequest } from '@/lib/types/chapter'

const baseUrl = 'http://localhost:8000/api/'


interface ChaptersResponse extends Response {
    chapters: Chapter[];
}

interface ChapterResponse extends Response {
    chapter: Chapter;
}

export const createChapterApi = async (courseId: number, chapter: CreateChapterRequest) : Promise<Chapter> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    
    if (chapter.order === null) {
        delete chapter.order
    }

    const response = await axios.post<ChapterResponse>(
        `${baseUrl}courses/${courseId}/chapters/create/`,
        chapter,
        { headers }
    )
    return response.data.chapter
}

export const updateChapterApi = async (chapterId: number, chapter: CreateChapterRequest) : Promise<Chapter> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }

    if (chapter.order === null) {
        delete chapter.order
    }

    const response = await axios.put<ChapterResponse>(
        `${baseUrl}courses/chapters/${chapterId}/update/`,
        chapter,
        { headers }
    )
    return response.data.chapter
}