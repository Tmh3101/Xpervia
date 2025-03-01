import axios from 'axios'
import { Course, CourseDetail, CourseWithDetailLessons } from '@/lib/types/course'
import { Assignment } from '@/lib/types/assignment'

const baseUrl = 'http://localhost:8000/api/'

interface Response {
    success: boolean;
    message: string;
}

interface CoursesResponse extends Response {
    courses: Course[];
}

interface CourseDetailResponse extends Response {
    course: CourseDetail;
}

interface CourseWithDetailLessonsResponse extends Response {
    course: CourseWithDetailLessons;
}

interface AssignmentResponse extends Response {
    assignments: Assignment[];
}

export const getCoursesApi = async () : Promise<Course[]> => {
    const response = await axios.get<CoursesResponse>(
        `${baseUrl}courses/`
    )
    return response.data.courses
}

export const getCourseDetailApi = async (id: number) : Promise<CourseDetail> => {
    const response = await axios.get<CourseDetailResponse>(
        `${baseUrl}courses/${id}/`
    )
    return response.data.course
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

export const getEnrolledCoursesApi = async () : Promise<Course[]> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    const response = await axios.get<CoursesResponse>(
        `${baseUrl}courses/enrollments/student/`,
        { headers } )
    return response.data.courses
}

export const enrollCourseApi = async (courseId: number) : Promise<boolean> => {
    console.log('token', sessionStorage.getItem("token"))
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    const response = await axios.post(
        `${baseUrl}courses/${courseId}/enrollments/create/`,
        {},
        { headers }
    )
    return response.data.success
}

export const getLessonAssignmentsApi = async (lessonId: number) : Promise<Assignment[]> => {
    const headers = {
        'Authorization': `Token ${sessionStorage.getItem("token")}`
    }
    const response = await axios.get<AssignmentResponse>(
        `${baseUrl}courses/lessons/${lessonId}/assignments/`,
        { headers }
    )
    return response.data.assignments
}