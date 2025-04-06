"use client"

import { Loading } from "@/components/Loading"
import { useState, useEffect } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { EyeOff, Eye, Search } from "lucide-react"
import { getCoursesByAdminApi, hideCourseApi, showCourseApi } from "@/lib/api/course-api"
import { formatCurrency, formatDate } from "@/lib/utils"
import type { Course } from "@/lib/types/course"

export default function CoursesManagement() {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [confirmHideCourse, setConfirmHideCourse] = useState(false)
  const [courseToHide, setCourseToHide] = useState<Course | null>(null)

  useEffect(() => {
    setLoading(true)
    getCoursesByAdminApi().then((data) => {
      setCourses(data)
      setLoading(false)
    })
  }, [])

  if (loading) {
    return <Loading />
  }

  const showComfirmDialogHideCourse = (course: Course) => {
    setCourseToHide(course)
    setConfirmHideCourse(true)
  }

  const handleCancelHideCourse = () => {
    setConfirmHideCourse(false)
  }

  const handleConfirmHideCourse = () => {
    if (courseToHide) {
      handleToggleHideCourse(courseToHide)
    }
    setConfirmHideCourse(false)
  }

  const handleToggleHideCourse = (course: Course) => {
    if (course.is_visible) {
      hideCourseApi(course.id).then(() => {
        setCourses((prev) => prev.map((c) => (c.id === course.id ? { ...c, is_visible: false } : c)))
      })
    } else {
      showCourseApi(course.id).then(() => {
        setCourses((prev) => prev.map((c) => (c.id === course.id ? { ...c, is_visible: true } : c)))
      })
    }
  }

  const filterCoursesBySearch = (courses: Course[]) => {
    if (!searchQuery) return courses
    return courses.filter((course) => course.course_content.title.toLowerCase().includes(searchQuery.toLowerCase()))
  }

  const filterCoursesByStatus = (courses: Course[]) => {
    if (statusFilter === "all") return courses
    const isVisible = statusFilter === "active"
    return courses.filter((course) => course.is_visible === isVisible)
  }

  const getFilteredCourses = () => {
    return filterCoursesByStatus(filterCoursesBySearch(courses))
  }

  return (
    <div className="py-6">
      <h1 className="text-3xl uppercase font-bold mb-6">Quản lý khóa học</h1>
      <Card>
        <CardHeader className="pb-0">
          <CardTitle className="mb-4">Danh sách khóa học</CardTitle>
          <div className="flex flex-col sm:flex-row gap-4 mt-4">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Tìm kiếm theo tên khóa học..."
                className="pl-8"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Trạng thái" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tất cả</SelectItem>
                <SelectItem value="active">Đang hiện</SelectItem>
                <SelectItem value="hidden">Đang ẩn</SelectItem>
              </SelectContent>
            </Select>
          </div>
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
              {getFilteredCourses().length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center">
                    Không có dữ liệu
                  </TableCell>
                </TableRow>
              ) : (
                getFilteredCourses().map((course) => (
                  <TableRow key={course.id}>
                    <TableCell>{course.id}</TableCell>
                    <TableCell className="font-medium">{course.course_content.title}</TableCell>
                    <TableCell>
                      {course.course_content.teacher.first_name + " " + course.course_content.teacher.last_name}
                    </TableCell>
                    <TableCell>{formatCurrency(course.price)}</TableCell>
                    <TableCell>{course.num_students}</TableCell>
                    <TableCell>{formatDate(course.created_at)}</TableCell>
                    <TableCell>
                      <span
                        className={`px-2 py-1 rounded-full text-xs ${
                          course.is_visible ? "bg-green-100 text-green-800" : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        {course.is_visible ? "Đang hiện" : "Đang ẩn"}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => showComfirmDialogHideCourse(course)}
                        className={
                          course.is_visible
                            ? "text-amber-500 hover:text-amber-700 hover:bg-amber-50"
                            : "text-green-500 hover:text-green-700 hover:bg-green-50"
                        }
                      >
                        {course.is_visible
                          ? <><EyeOff className="h-4 w-4 mr-1" />Ẩn</>
                          : <><Eye className="h-4 w-4 mr-1" />Hiện</>
                        }
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      
      <AlertDialog open={confirmHideCourse} onOpenChange={setConfirmHideCourse}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Bạn có chắc chắn muốn {courseToHide?.is_visible ? "ẩn" : "hiển thị"} khóa học này?</AlertDialogTitle>
            <AlertDialogDescription>
              Tài khoản {courseToHide?.course_content.title} sẽ được {courseToHide?.is_visible ? "ẩn" : "hiển thị"}.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={handleCancelHideCourse}>Hủy</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmHideCourse} className={courseToHide?.is_visible ? "bg-red-600 hover:bg-red-700" : "bg-success hover:bg-success/80"}>
              {courseToHide?.is_visible ? "Ẩn" : "Hiển thị"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

