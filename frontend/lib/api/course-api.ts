import axios from 'axios'
import { Course, CourseWithDetailLessons } from '@/lib/types/course'
import { Response } from '@/lib/api/response'

const baseUrl = 'http://localhost:8000/api/'

interface CoursesResponse extends Response {
    courses: Course[];
}

interface CourseResponse extends Response {
    course: Course;
}

interface CourseWithDetailLessonsResponse extends Response {
    course: CourseWithDetailLessons;
}

export const getCoursesApi = async () : Promise<Course[]> => {
    const response = await axios.get<CoursesResponse>(
        `${baseUrl}courses/`
    )
    return response.data.courses
}

export const getCourseDetailApi = async (id: number) : Promise<Course> => {
    const response = await axios.get<CourseResponse>(
        `${baseUrl}courses/${id}/`
    )
    return response.data.course
}

export const getCourseByTeacherApi = async () : Promise<Course[]> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    const response = await axios.get<CoursesResponse>(
        `${baseUrl}courses/teacher/`,
        { headers }
    )
    return response.data.courses
}

export const getCourseWithDetailLessonsApi = async (id: number) : Promise<CourseWithDetailLessons> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    const response = await axios.get<CourseWithDetailLessonsResponse>(
        `${baseUrl}courses/${id}/detail-lessons/`,
        { headers }
    )
    return response.data.course
}