"use client"

import { useAuth } from "@/lib/auth-context"
import { useEffect, useState } from "react"
import { HeroSection } from "@/components/HeroSection"
import { SearchBar } from "@/components/SearchBar"
import { CourseCard } from "@/components/course/CourseCard"
import { getCoursesApi } from "@/lib/api/course-api"
import type { Course } from "@/lib/types/course"

export default function Home() {
  const [courses, setCourses] = useState<Course[]>([])
  const [filteredCourses, setFilteredCourses] = useState<Course[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null)
  const { enrollments, fetchEnrollments, token } = useAuth()

  const checkCourseEnrollment = (courseId: number) => {
    const enrolledCourseIds = enrollments.map((enrollment) => enrollment.course.id)
    return enrolledCourseIds.includes(courseId)
  }

  const getCourseProgress = (courseId: number) => {
    const enrollment = enrollments.find((enrollment) => enrollment.course.id === courseId)
    return enrollment?.progress
  }

  useEffect(() => {
    getCoursesApi().then((data) => {
      setCourses(data)
      setFilteredCourses(data)
    })
  }, [])

  useEffect(() => {
    if (token) {
      fetchEnrollments()
    }
  }, [token])

  useEffect(() => {
    let result = courses

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      result = result.filter(
        (course) => course.course_content.title.toLowerCase().includes(query) || course.course_content.description.toLowerCase().includes(query),
      )
    }

    // Filter by category
    if (selectedCategory !== null) {
      result = result.filter((course) => course.course_content.categories.some((category) => category.id === selectedCategory))
    }

    setFilteredCourses(result)
  }, [searchQuery, selectedCategory, courses])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
  }

  const handleCategorySelect = (categoryId: number | null) => {
    setSelectedCategory(categoryId)
  }

  return (
    <main>
      <HeroSection />
      <SearchBar onSearch={handleSearch} onCategorySelect={handleCategorySelect} />
      <section className="container mx-auto pb-12 min-h-[400px]">
        <h2 className="text-3xl text-destructive font-bold mb-8 text-center">Khóa học hàng đầu</h2>
        {filteredCourses.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {filteredCourses.map((course) => (
              <CourseCard
                key={course.id}
                {...course}
                mode={checkCourseEnrollment(course.id) ? "enrolled" : "student"}
                progress={getCourseProgress(course.id) || 0}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-lg text-gray-500">Không tìm thấy khóa học phù hợp.</p>
          </div>
        )}
      </section>
    </main>
  )
}

