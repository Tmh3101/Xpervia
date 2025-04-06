"use client"

import { Loading } from "@/components/Loading"
import { useEffect, useState } from "react"
import { CourseCard } from "@/components/course/CourseCard"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import {
  getCourseByTeacherApi,
  createCourseApi,
  updateCourseApi,
  deleteCourseApi
} from "@/lib/api/course-api"
import type { Course } from "@/lib/types/course"
import { CourseFormDialog } from "@/components/course/CourseFormDialog"
import type { CreateCourseRequest } from "@/lib/types/course"
import { useRouter } from "next/navigation"

export default function TeacherDashboard() {
  const router = useRouter()
  const [courses, setCourses] = useState<Course[]>([])
  const [isCourseFormOpen, setIsCourseFormOpen] = useState(false)
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

  if (!courses) {
    return <Loading />
  }

  const handleEditCourse = (course: Course) => {
    setEditingCourse(course)
    setIsCourseFormOpen(true)
  }

  const handleCreateCourse = async (createCourseData: CreateCourseRequest) => {
    let newCourse = null
    if (editingCourse) {
      const course = await updateCourseApi(editingCourse.id, createCourseData)
      newCourse = course
      console.log("Updating course:", course)
    } else {
      const course = await createCourseApi(createCourseData)
      newCourse = course
      console.log("Creating course:", newCourse)
    }
    setIsCourseFormOpen(false)
    if (newCourse) {
      router.push(`/teacher/courses/${newCourse.id}/detail`)
    }
  }

  const handleDeleteCourse = async () => {
    if (!editingCourse) return
    await deleteCourseApi(editingCourse.id)
    setEditingCourse(null)
    setIsCourseFormOpen(false)
    const newCourses = courses.filter((course) => course.id !== editingCourse.id)
    setCourses(newCourses)
  }

  return (
    <div className="container mx-auto py-[90px] px-4 mt-[40px]">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold mb-2">Khóa học của tôi</h1>
          <p className="text-gray-600">
            {courses.length} khóa học
          </p>
        </div>
        <div className="flex items-center gap-4 w-full md:w-auto">
          <Button className="bg-primary hover:bg-primary/90 rounded-full" onClick={() => setIsCourseFormOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Tạo khóa học
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {courses.map((course) => (
          <CourseCard key={course.id} {...course} mode="teacher" onEditClick={() => handleEditCourse(course)} />
        ))}
      </div>

      <CourseFormDialog
        open={isCourseFormOpen}
        onOpenChange={setIsCourseFormOpen}
        onSubmit={handleCreateCourse}
        onDelete={handleDeleteCourse}
        mode={editingCourse ? "edit" : "create"}
        initialData={editingCourse ? editingCourse : undefined}
      />
    </div>
  )
}

