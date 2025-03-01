"use client"

import Image from "next/image"
import { use, useState } from "react"
import { useEffect } from "react"
import { User, Edit2, Eye } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"
import { getGoogleDriveImageUrl } from "@/lib/google-drive-url"
import { Course } from "@/lib/types/course"
import { getCategoryColor } from "@/lib/category-color"
import { getCourseDetailApi } from "@/lib/api/course-api"
import { cn } from "@/lib/utils"

interface CourseCardProps extends Course {
  mode?: "enrolled" | "teacher" | "student"
  studentsEnrolled?: number
  onEditClick?: () => void
}

export function CourseCard({
  id,
  course_content,
  price,
  discount,
  is_visible,
  created_at,
  start_date,
  regis_start_date,
  regis_end_date,
  max_students,
  mode = "student",
  studentsEnrolled = 0,
  onEditClick,
}: CourseCardProps) {
  const router = useRouter()
  const currentPrice = price * (1 - discount)
  const [firstLessonId, setFirstLessonId] = useState(1)

  useEffect(() => {
    const fetchCourseDetail = async () => {
      try {
        const courseDetail = await getCourseDetailApi(id)
        const lessons = courseDetail.course_content.chapters
          .flatMap((chapter) => chapter.lessons)
          .concat(courseDetail.course_content.lessons_without_chapter)
        setFirstLessonId(lessons[0].id)
      } catch (error) {
        console.error("Failed to fetch course detail", error)
      }
    }

    fetchCourseDetail()
  }, [id])

  const handleClick = () => {
    if (mode === "teacher") {
      router.push(`/teacher/courses/${id}`)
    } else if (mode === "enrolled") {
      router.push(`/student/lessons/${id}/${firstLessonId}`)
    } else {
      router.push(`/courses/${id}`)
    }
  }

  return (
    <Card className="overflow-hidden rounded-2xl border-0 shadow-lg flex flex-col">
      <CardHeader className="p-0 relative">
        <Image
          src={getGoogleDriveImageUrl(course_content.thumbnail_id) || "/placeholder.svg"}
          alt="thumbnail"
          width={400}
          height={200}
          className="w-full h-38 object-cover"
        />
        <div className="absolute top-0 left-2 flex flex-wrap gap-1">
          {course_content.categories.map(c => c.name).map((category, index) => (
            <Badge
              key={index}
              variant="secondary"
              className={cn(
                "text-xs",
                `bg-${getCategoryColor(category)}`,
                "text-white",
                "hover:bg-white",
                `hover:text-${getCategoryColor(category)}`
              )}
            >
              {category}
            </Badge>
          ))}
        </div>
      </CardHeader>
      <CardContent className="px-4 py-2 flex-grow">
        <h3 className="font-bold text-lg/[1.5rem] text-destructive mb-2 line-clamp-2">{course_content.title}</h3>
        {mode === "student" ? (
          <div className="flex items-center mb-2">
            <User className="w-4 h-4 mr-2 text-primary" />
            <span className="text-sm font-medium text-primary">
              {course_content.teacher.first_name + " " + course_content.teacher.last_name}
            </span>
          </div>
        ) : (
          ""
        )}
        <p className="text-sm text-gray-600 line-clamp-2">{course_content.description}</p>
      </CardContent>
      <CardFooter className={`p-4 pt-0 ${mode !== "student" ? "" : "flex items-center justify-between"}`}>
        {mode === "teacher" ? (
          <div className="flex gap-2 w-full">
            <Button
              className="flex-1 bg-primary hover:bg-primary/90 rounded-full text-sm"
              onClick={() => router.push(`/teacher/courses/${id}/detail`)}
            >
              <Eye className="w-4 h-4 mr-2" />
              Detail
            </Button>
            <Button variant="outline" className="flex-1 hover:bg-primary/10 rounded-full text-sm" onClick={handleClick}>
              <Edit2 className="w-4 h-4 mr-2" />
              Edit
            </Button>
          </div>
        ) : mode === "enrolled" ? (
          <Button className="w-full bg-[#1ABC9C] hover:bg-[#1ABC9C]/90 rounded-full text-sm" onClick={handleClick}>
            Continue
          </Button>
        ) : (
          <>
            <div className="flex flex-col items-start">
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-500 line-through">{price.toLocaleString("vi-VN")}</span>
                <span className="text-[10px] font-semibold text-white bg-red-500 px-1 rounded-full">
                  -{discount * 100}%
                </span>
              </div>
              <span className="text-2xl text-destructive font-bold">{currentPrice.toLocaleString("vi-VN")}</span>
            </div>
            <Button className="bg-primary hover:bg-secondary rounded-full text-sm mt-auto" onClick={handleClick}>
              Enroll Now
            </Button>
          </>
        )}
      </CardFooter>
    </Card>
  )
}