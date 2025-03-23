import axios from 'axios'
import {
    Course,
    CourseWithDetailLessons,
    CreateCourseRequest
} from '@/lib/types/course'
import { Category } from '@/lib/types/course-content'
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

interface CategoriesResponse extends Response {
    categories: Category[];
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
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.get<CoursesResponse>(
        `${baseUrl}courses/teacher/`,
        { headers }
    )
    return response.data.courses
}

export const getCourseWithDetailLessonsApi = async (id: number) : Promise<CourseWithDetailLessons> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.get<CourseWithDetailLessonsResponse>(
        `${baseUrl}courses/${id}/detail-lessons/`,
        { headers }
    )
    return response.data.course
}

export const createCourseApi = async (data: CreateCourseRequest) : Promise<Course> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`,
        'Content-Type': 'multipart/form-data'
    }

    let formData = new FormData()
    formData.append('thumbnail', data.thumbnail)
    formData.append('title', data.title)
    formData.append('description', data.description)
    formData.append('price', data.price.toString())
    formData.append('start_date', data.start_date || '')
    formData.append('regis_start_date', data.regis_start_date || '')
    formData.append('regis_end_date', data.regis_end_date || '')
    formData.append('max_students', data.max_students.toString())
    formData.append('is_visible', data.is_visible.toString())
    formData.append('categories', JSON.stringify(data.categories))
    formData.append('discount', data.discount?.toString() || '')
 
    const response = await axios.post<CourseResponse>(
        `${baseUrl}courses/create/`,
        formData,
        { headers }
    )
    return response.data.course
}

export const updateCourseApi = async (id: number, data: CreateCourseRequest) : Promise<Course> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`,
        'Content-Type': 'multipart/form-data'
    }

    let formData = new FormData()
    formData.append('thumbnail', data.thumbnail)
    formData.append('title', data.title)
    formData.append('description', data.description)
    formData.append('price', data.price.toString())

    if (data.start_date){
        formData.append('start_date', data.start_date)
    }

    if (data.regis_start_date){
        formData.append('regis_start_date', data.regis_start_date)
    }

    if (data.regis_end_date){
        formData.append('regis_end_date', data.regis_end_date)
    }

    formData.append('max_students', data.max_students.toString())
    formData.append('is_visible', data.is_visible.toString())
    formData.append('categories', JSON.stringify(data.categories))

    if (data.discount) {
        formData.append('discount', data.discount.toString())
    }

    const response = await axios.put<CourseResponse>(
        `${baseUrl}courses/${id}/update/`,
        formData,
        { headers }
    )
    return response.data.course
}

export const deleteCourseApi = async (id: number) : Promise<boolean> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.delete(
        `${baseUrl}courses/${id}/delete/`,
        { headers }
    )
    return response.data.success
}

export const getCategoriesApi = async () : Promise<Category[]> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem("token")}`
    }
    const response = await axios.get<CategoriesResponse>(
        `${baseUrl}courses/categories/`,
        { headers }
    )
    return response.data.categories
}
