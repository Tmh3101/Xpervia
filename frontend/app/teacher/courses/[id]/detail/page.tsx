"use client"

import { useParams, useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Plus, Edit, User } from "lucide-react"
import Image from "next/image"
import { getGoogleDriveImageUrl } from "@/lib/google-drive-url"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { Submission } from "@/lib/types/submission"
import type { CourseWithDetailLessons } from "@/lib/types/course"
import type { AssignmentDetail } from "@/lib/types/assignment"
import { getCourseWithDetailLessonsApi } from "@/lib/api/course-api"
import { CourseCategories } from "@/components/course/CourseCategories"
import { ChapterFormDialog } from "@/components/course/ChapterFormDialog"
import { LessonFormDialog } from "@/components/course/LessonFormDialog"
import { createChapterApi, updateChapterApi, deleteChapterApi } from "@/lib/api/chapter-api"
import type { Chapter, CreateChapterRequest } from "@/lib/types/chapter"
import type { LessonDetail, CreateLessonRequest } from "@/lib/types/lesson"
import { createLessonApi, updateLessonApi, deleteLessonApi } from "@/lib/api/lesson-api"
import { getEnrollmentsByCourseApi } from "@/lib/api/enrollment-api"
import type { Enrollment } from "@/lib/types/enrollment"
import { ScrollArea } from "@/components/ui/scroll-area"

export default function CourseDetail() {
  const params = useParams()
  const router = useRouter()
  const [course, setCourse] = useState<CourseWithDetailLessons | null>(null)
  const [assignmentDetails, setAssignmentDetails] = useState<AssignmentDetail[]>([])
  const [selectedLesson, setSelectedLesson] = useState<{
    title: string
    submissions: Submission[]
  } | null>(null)

  const [isChapterFormOpen, setIsChapterFormOpen] = useState(false)
  const [isLessonFormOpen, setIsLessonFormOpen] = useState(false)
  const [selectedChapter, setSelectedChapter] = useState<Chapter | null>(null)
  const [editingChapter, setEditingChapter] = useState<Chapter | null>(null)
  const [editingLesson, setEditingLesson] = useState<LessonDetail | null>(null)
  const [enrollments, setEnrollments] = useState<Enrollment[]>([])
  const [isLoadingEnrollments, setIsLoadingEnrollments] = useState(false)

  useEffect(() => {
    if (params.id) {
      const fetchCourseDetail = async () => {
        const courseDetail = await getCourseWithDetailLessonsApi(Number.parseInt(params.id))
        setCourse(courseDetail)
      }

      fetchCourseDetail()
    }
  }, [params.id])

  useEffect(() => {
    if (params.id) {
      const fetchEnrollments = async () => {
        setIsLoadingEnrollments(true)
        try {
          const enrollmentData = await getEnrollmentsByCourseApi(Number.parseInt(params.id))
          setEnrollments(enrollmentData)
        } catch (error) {
          console.error("Error fetching enrollments:", error)
        } finally {
          setIsLoadingEnrollments(false)
        }
      }

      fetchEnrollments()
    }
  }, [params.id])

  const handleCreateChapter = async (data: CreateChapterRequest) => {
    if (editingChapter) {
      // Update chapter
      await updateChapterApi(editingChapter.id, data)
    } else {
      // Create chapter
      await createChapterApi(Number.parseInt(params.id), data)
    }
    setIsChapterFormOpen(false)

    getCourseWithDetailLessonsApi(Number.parseInt(params.id)).then((courseDetail) => {
      setCourse(courseDetail)
    })
  }

  const handleDeleteChapter = async () => {
    if (!editingChapter) return

    await deleteChapterApi(editingChapter.id)
    setIsChapterFormOpen(false)
    setEditingChapter(null)

    getCourseWithDetailLessonsApi(Number.parseInt(params.id)).then((courseDetail) => {
      setCourse(courseDetail)
    })
  }

  const handleEditChapter = (chapter: Chapter) => {
    setEditingChapter(chapter)
    setIsChapterFormOpen(true)
  }

  const handleCreateLesson = async (data: CreateLessonRequest) => {
    if (course) {
      if (editingLesson) {
        await updateLessonApi(editingLesson.id, data)
      } else {
        await createLessonApi(course.id, selectedChapter?.id ? selectedChapter.id : null, data)
      }
    }
    setIsLessonFormOpen(false)

    getCourseWithDetailLessonsApi(Number.parseInt(params.id)).then((courseDetail) => {
      setCourse(courseDetail)
    })
  }

  const handleDeleteLesson = async () => {
    if (!editingLesson) return

    await deleteLessonApi(editingLesson.id)
    setIsLessonFormOpen(false)
    setEditingLesson(null)

    getCourseWithDetailLessonsApi(Number.parseInt(params.id)).then((courseDetail) => {
      setCourse(courseDetail)
    })
  }

  const handleEditLesson = (lesson: LessonDetail) => {
    setEditingLesson(lesson)
    setIsLessonFormOpen(true)
  }

  const handleAddLesson = (chapter: Chapter | null) => {
    setSelectedChapter(chapter)
    setEditingLesson(null)
    setIsLessonFormOpen(true)
  }

  const handleViewLessonDetail = (lessonId: number) => {
    router.push(`/teacher/courses/${params.id}/lessons/${lessonId}`)
  }

  if (!course) {
    return <div>Loading...</div>
  }

  return (
    <div className="container mx-auto py-8">
      <Button variant="ghost" className="mb-6" onClick={() => router.push("/teacher")}>
        <ArrowLeft className="w-4 h-4 mr-2" />
        Trở về
      </Button>

      <div className="grid gap-6">
        {/* Course Info */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-2xl font-bold mb-2">{course.course_content.title}</h1>
              <div className="flex items-center gap-2">
                <CourseCategories categories={course.course_content.categories.map((c) => c.name)} />
              </div>
            </div>
          </div>
          <div className="aspect-video relative rounded-lg overflow-hidden mb-4">
            <Image
              src={getGoogleDriveImageUrl(course.course_content.thumbnail_id) || "/placeholder.svg"}
              alt={course.course_content.title}
              fill
              className="object-cover"
            />
          </div>
        </div>
        <div className="space-y-4">
          <div className="bg-white rounded-xl shadow-sm p-2 pb-0">
            <div className="flex justify-between items-center">
              <div className="flex gap-2">
                <Button
                  onClick={() => {
                    setEditingChapter(null)
                    setIsChapterFormOpen(true)
                  }}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Thêm chương
                </Button>
                <Button onClick={() => handleAddLesson(null)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Thêm bài học
                </Button>
              </div>
            </div>
          </div>

          {/* Course Content and Submissions */}
          <Tabs defaultValue="content" className="w-full">
            <TabsList>
              <TabsTrigger value="content">Nội dung khóa học</TabsTrigger>
              <TabsTrigger value="students">Học viên</TabsTrigger>
            </TabsList>

            <TabsContent value="content">
              <div className="space-y-4">
                {course.course_content.chapters?.map((chapter: any, chapterIndex: number) => (
                  <Card key={chapter.id}>
                    <CardHeader className="flex flex-row items-center justify-between">
                      <div>
                        <CardTitle>{chapter.title}</CardTitle>
                        {/* <CardDescription>
                          {chapter.totalVideos} bài học • {chapter.totalDuration}
                        </CardDescription> */}
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => handleEditChapter(chapter)}>
                          <Edit className="w-4 h-4 mr-2" />
                          Sửa
                        </Button>
                        <Button size="sm" onClick={() => handleAddLesson(chapter)}>
                          <Plus className="w-4 h-4 mr-2" />
                          Thêm bài học
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {chapter.lessons.map((lesson: any) => (
                          <div
                            key={lesson.id}
                            className="flex justify-between items-center p-3 rounded-lg bg-primary/10"
                          >
                            <div>
                              <h4 className="font-medium">{lesson.title}</h4>
                              {/* <p className="text-sm text-gray-500">{lesson.duration}</p> */}
                            </div>
                            <div className="flex items-center gap-2">
                              {assignmentDetails[lesson.id] && (
                                <Badge color="success" className="text-sm">
                                  {assignmentDetails[lesson.id].content}
                                </Badge>
                              )}
                              <Button variant="outline" size="sm" onClick={() => handleViewLessonDetail(lesson.id)}>
                                Xem chi tiết
                              </Button>
                              <Button variant="outline" size="sm" onClick={() => handleEditLesson(lesson)}>
                                <Edit className="w-4 h-4 mr-2" />
                                Sửa
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}

                {course.course_content.lessons_without_chapter?.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Bài học không thuộc chương nào</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {course.course_content.lessons_without_chapter.map((lesson: any) => (
                          <div
                            key={lesson.id}
                            className="flex justify-between items-center p-3 rounded-lg bg-primary/10"
                          >
                            <div>
                              <h4 className="font-medium">{lesson.title}</h4>
                            </div>
                            <div className="flex items-center gap-2">
                              {assignmentDetails[lesson.id] && (
                                <Badge color="success" className="text-sm">
                                  {assignmentDetails[lesson.id].content}
                                </Badge>
                              )}
                              <Button variant="outline" size="sm" onClick={() => handleViewLessonDetail(lesson.id)}>
                                Xem chi tiết
                              </Button>
                              <Button variant="outline" size="sm" onClick={() => handleEditLesson(lesson)}>
                                <Edit className="w-4 h-4 mr-2" />
                                Sửa
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>

            <TabsContent value="students">
              <Card>
                <CardHeader>
                  <CardTitle>Danh sách học viên đã đăng ký</CardTitle>
                  <CardDescription>Tổng số: {enrollments.length} học viên</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoadingEnrollments ? (
                    <div className="text-center py-4">Đang tải danh sách học viên...</div>
                  ) : enrollments.length === 0 ? (
                    <div className="text-center py-4 text-muted-foreground">
                      Chưa có học viên nào đăng ký khóa học này
                    </div>
                  ) : (
                    <ScrollArea className="">
                      <div className="space-y-2">
                        {enrollments.map((enrollment) => (
                          <div key={enrollment.id} className="flex items-center p-3 rounded-lg bg-gray-50">
                            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center mr-3">
                              <User className="w-5 h-5 text-primary" />
                            </div>
                            <div className="flex-1">
                              <h4 className="font-medium">
                                {enrollment.student.first_name + " " + enrollment.student.last_name}
                              </h4>
                              <p className="text-sm text-gray-500">{enrollment.student.email}</p>
                            </div>
                            <div className="flex items-center gap-4">
                              <div className="text-sm text-gray-500">
                                Đăng ký ngày: {new Date(enrollment.created_at).toLocaleDateString()}
                              </div>
                              <div className="relative w-16 h-16">
                                {/* Circular progress bar */}
                                <svg className="w-full h-full" viewBox="0 0 100 100">
                                  {/* Background circle */}
                                  <circle
                                    className="text-gray-200"
                                    strokeWidth="8"
                                    stroke="currentColor"
                                    fill="transparent"
                                    r="40"
                                    cx="50"
                                    cy="50"
                                  />
                                  {/* Progress circle */}
                                  <circle
                                    className="text-primary"
                                    strokeWidth="8"
                                    strokeLinecap="round"
                                    stroke="currentColor"
                                    fill="transparent"
                                    r="40"
                                    cx="50"
                                    cy="50"
                                    strokeDasharray={`${2 * Math.PI * 40}`}
                                    strokeDashoffset={`${2 * Math.PI * 40 * (1 - (enrollment.progress || 0) / 100)}`}
                                    transform="rotate(-90 50 50)"
                                  />
                                </svg>
                                {/* Percentage text */}
                                <div className="absolute inset-0 flex items-center justify-center">
                                  <span className="text-sm font-medium">{enrollment.progress || 0}%</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Chapter Form */}
      {course && (
        <ChapterFormDialog
          open={isChapterFormOpen}
          onOpenChange={setIsChapterFormOpen}
          onSubmit={handleCreateChapter}
          onDelete={handleDeleteChapter}
          mode={editingChapter ? "edit" : "create"}
          initialData={
            editingChapter
              ? {
                  id: editingChapter.id,
                  title: editingChapter.title,
                }
              : null
          }
        />
      )}

      {/* Lesson Form */}
      {course && (
        <LessonFormDialog
          open={isLessonFormOpen}
          onOpenChange={setIsLessonFormOpen}
          onSubmit={handleCreateLesson}
          onDelete={handleDeleteLesson}
          chapterTitle={selectedChapter?.title ? selectedChapter.title : null}
          mode={editingLesson ? "edit" : "create"}
          initialData={editingLesson ? editingLesson : undefined}
        />
      )}
    </div>
  )
}

