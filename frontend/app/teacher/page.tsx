"use client"

import { useEffect, useState } from "react"
import { CourseCard } from "@/components/CourseCard"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { getCourseByTeacherApi } from "@/lib/api/course-api"
import { Course } from "@/lib/types/course"
// import { CourseFormDialog } from "@/components/teacher/CourseFormDialog"

export default function TeacherDashboard() {
  const { user } = useAuth()
  const [courses, setCourses] = useState<Course[]>([])
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [editingCourse, setEditingCourse] = useState<Course | null>(null)

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const courses = await getCourseByTeacherApi()
        setCourses(courses)
      } catch (error) {
        console.error("Failed to fetch courses", error)
      }
    }

    fetchCourses()
  }, [])

  const handleCreateCourse = (courseData: Partial<Course>) => {
    // Mock course creation - in a real app, this would be an API call
    // const newCourse = {
    //   ...courseData,
    //   id: courses.length + 1,
    //   teacher_id: user?.id || "",
    //   teacher: `${user?.first_name} ${user?.last_name}`,
    //   students_enrolled: 0
    // } as Course

    // setCourses((prev) => [...prev, newCourse])
    // setIsCreateModalOpen(false)
  }

  const handleUpdateCourse = (courseData: Partial<Course>) => {
    // Mock course update - in a real app, this would be an API call
    // setCourses((prev) =>
    //   prev.map((course) => (course.id === editingCourse?.id ? { ...course, ...courseData } : course)),
    // )
    // setEditingCourse(null)
  }

  return (
    <div className="container mx-auto py-[90px] px-4">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold mb-2">My Courses</h1>
          <p className="text-gray-600">
            {courses.length} course{courses.length !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="flex items-center gap-4 w-full md:w-auto">
          <Button className="bg-primary hover:bg-primary/90 rounded-full" onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="mr-2 h-4 w-4" /> Create Course
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {courses.map((course) => (
          <CourseCard
            key={course.id}
            {...course}
            mode="teacher"
            onEditClick={() => setEditingCourse(course)}
          />
        ))}
      </div>
    </div>
  )
}

