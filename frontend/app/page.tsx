"use client"

import { useEffect, useState } from "react"
import { HeroSection } from "@/components/HeroSection"
import { SearchBar } from "@/components/SearchBar"
import { CourseCard } from "@/components/CourseCard"
import { getCoursesApi } from "@/lib/api/course-api"
import { Course } from "@/lib/types/course"

export default function Home() {

  const [courses, setCourses] = useState<Course[]>([])
  useEffect(() => {
    getCoursesApi().then((data) => setCourses(data))
  }, [])

  return (
    <main>
      <HeroSection />
      <SearchBar />
      <section className="container mx-auto py-12">
        <h2 className="text-3xl text-destructive font-bold mb-8 text-center">Browse Our Top Courses</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {courses.filter((course) => course.is_visible).map((course) => (
            <CourseCard key={course.id} {...course} />
          ))}
        </div>
      </section>
    </main>
  )
}

