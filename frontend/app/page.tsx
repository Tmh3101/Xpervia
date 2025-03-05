"use client"

import { useAuth } from "@/lib/auth-context"
import { useEffect, useState } from "react"
import { HeroSection } from "@/components/HeroSection"
import { SearchBar } from "@/components/SearchBar"
import { CourseCard } from "@/components/course/CourseCard"
import { getCoursesApi } from "@/lib/api/course-api"
import { Course } from "@/lib/types/course"

export default function Home() {
  const [courses, setCourses] = useState<Course[]>([])
  const { enrollments, fetchEnrollments, token } = useAuth()

  const checkCourseEnrollment = (courseId: number) => {
    const enrolledCourseIds = enrollments.map(enrollment => enrollment.course.id)
    return enrolledCourseIds.includes(courseId)
  }

  const getCourseProgress = (courseId: number) => {
    const enrollment = enrollments.find(enrollment => enrollment.course.id === courseId)
    return enrollment?.progress
  }

  useEffect(() => {
    getCoursesApi().then(data => setCourses(data))
    if (token) {
      fetchEnrollments()
    }
  }, [])

  useEffect(() => {
    if (token) {
      fetchEnrollments()
    }
  }, [token])

  return (
    <main>
      <HeroSection />
      <SearchBar />
      <section className="container mx-auto pb-12">
        <h2 className="text-3xl text-destructive font-bold mb-8 text-center">Khóa học hàng đầu</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {courses.map(course => (
            <CourseCard
              key={course.id}
              {...course}
              mode={checkCourseEnrollment(course.id) ? 'enrolled' : 'student'}
              progress={getCourseProgress(course.id) || 0}
            />
          ))}
        </div>
      </section>
    </main>
  )
}

