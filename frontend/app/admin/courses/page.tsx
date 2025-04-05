"use client"

import { useState, useEffect } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { EyeOff } from "lucide-react"
import { Loading } from "@/components/Loading"
import { getCoursesApi } from "@/lib/api/course-api"
import { formatCurrency, formatDate } from "@/lib/utils"
import type { Course } from "@/lib/types/course"

export default function CoursesManagement() {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(false)
  
  useEffect(() => {
    setLoading(true)
    getCoursesApi().then((data) => {
      setCourses(data)
      setLoading(false)
    })
  }, [])

  if (loading) {
    return <Loading />
  }

  console.log(courses)

  const handleHideCourse = (courseId: number) => {
    // In a real app, this would call an API to hide the course
    console.log(`Hide course with ID: ${courseId}`)
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Quản lý khóa học</h1>
      <Card>
        <CardHeader>
          <CardTitle>Danh sách khóa học</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Tên khóa học</TableHead>
                <TableHead>Giảng viên</TableHead>
                <TableHead>Giá</TableHead>
                <TableHead>Học viên</TableHead>
                <TableHead>Ngày tạo</TableHead>
                <TableHead>Trạng thái</TableHead>
                <TableHead className="text-right">Thao tác</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {courses.map((course) => (
                <TableRow key={course.id}>
                  <TableCell>{course.id}</TableCell>
                  <TableCell className="font-medium">{course.course_content.title}</TableCell>
                  <TableCell>{course.course_content.teacher.first_name + " " + course.course_content.teacher.last_name}</TableCell>
                  <TableCell>{formatCurrency(course.price)}</TableCell>
                  <TableCell>{course.num_students}</TableCell>
                  <TableCell>{formatDate(course.created_at)}</TableCell>
                  <TableCell>
                    <span className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                      {course.is_visible ? "Đang hoạt động" : "Đã ẩn"}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleHideCourse(course.id)}
                      className="text-amber-500 hover:text-amber-700 hover:bg-amber-50"
                    >
                      <EyeOff className="h-4 w-4 mr-1" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

