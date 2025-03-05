"use client"

import { useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { getCourseDetailApi } from "@/lib/api/course-api"

export default function CoursePage() {
  const router = useRouter()
  const params = useParams()

  useEffect(() => {
    const fetchCourseDetail = async () => {
      try {
        const courseId = params.courseId[0]
        const courseDetail = await getCourseDetailApi(parseInt(courseId))
        const lessons = courseDetail.course_content.chapters
          .flatMap((chapter) => chapter.lessons)
          .concat(courseDetail.course_content.lessons_without_chapter)
        const firstLessonId = lessons[0].id
        router.push(`/student/lessons/${courseId}/${firstLessonId}`)
      } catch (error) {
        console.error("Failed to fetch course detail", error)
      }
    }

    fetchCourseDetail()
  }, [params.courseId, router])

  return <div>Loading...</div>
}