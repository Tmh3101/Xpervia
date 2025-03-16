"use client"

import { useParams, useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Plus, Edit } from "lucide-react"
import Image from "next/image"
import { getGoogleDriveImageUrl } from "@/lib/google-drive-url"
import { Badge } from "@/components/ui/badge"
// import { SubmissionsDialog } from "@/components/teacher/SubmissionsDialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { Submission } from "@/lib/types/submission"
import type { CourseWithDetailLessons } from "@/lib/types/course"
import type { AssignmentDetail } from "@/lib/types/assignment"
import { getCourseWithDetailLessonsApi } from "@/lib/api/course-api"
import { CourseCategories } from "@/components/course/CourseCategories"
import { ChapterFormDialog } from "@/components/course/ChapterFormDialog"
import { LessonFormDialog } from "@/components/course/LessonFormDialog"
import { createChapterApi, updateChapterApi } from "@/lib/api/chapter-api"
import { Chapter, CreateChapterRequest } from "@/lib/types/chapter"
import { LessonDetail, CreateLessonRequest } from "@/lib/types/lesson"
import { createLessonApi, updateLessonApi } from "@/lib/api/lesson-api"

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


  useEffect(() => {
    if (params.id) {
      const fecthCourseDetail = async () => {
        const courseDetail = await getCourseWithDetailLessonsApi(parseInt(params.id))
        setCourse(courseDetail)
      }

      fecthCourseDetail()
    }
  }, [params.id])

  const handleUpdateSubmission = (submissionId: string, score: number, feedback: string) => {
    // // In a real app, this would make an API call to update the submission
    // console.log("Updating submission:", { submissionId, score, feedback })
  }

  const handleCreateChapter = async (data: CreateChapterRequest) => {  
    if(editingChapter) {
      // Update chapter
      await updateChapterApi(editingChapter.id, data)
    } else {
      // Create chapter
      await createChapterApi(parseInt(params.id), data)
    }
    setIsChapterFormOpen(false)

    getCourseWithDetailLessonsApi(parseInt(params.id)).then((courseDetail) => {
      setCourse(courseDetail);
    });
  }

  const handleEditChapter = (chapter: Chapter) => {
    setEditingChapter(chapter)
    setIsChapterFormOpen(true)
  }

  const handleCreateLesson = async (data: CreateLessonRequest) => {
    if (course) {
      if(editingLesson) {
        await updateLessonApi(editingLesson.id, data)
      } else {
        await createLessonApi(course.id, selectedChapter?.id ? selectedChapter.id : null, data)
      }
    }
    setIsLessonFormOpen(false)

    getCourseWithDetailLessonsApi(parseInt(params.id)).then((courseDetail) => {
      setCourse(courseDetail);
    });
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
            {/* <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-muted-foreground" />
              <span className="font-medium">{course.students_enrolled} students enrolled</span>
            </div> */}
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
                  Add Chapter
                </Button>
                <Button onClick={() => handleAddLesson(null)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Lesson
                </Button>
              </div>
            </div>
          </div>

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
                    Edit
                  </Button>
                  <Button size="sm" onClick={() => handleAddLesson(chapter)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Lesson
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {chapter.lessons.map((lesson: any) => (
                    <div key={lesson.id} className="flex justify-between items-center p-3 rounded-lg bg-primary/10">
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
                        <Button variant="outline" size="sm" onClick={() => handleEditLesson(lesson)}>
                          <Edit className="w-4 h-4 mr-2" />
                          Edit
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}

          {course.course_content.lessons_without_chapter?.map((lesson: any) => (
            <Card key={lesson.id}>
              <CardContent className="p-0">
                <div className="space-y-2">
                  <div className="flex justify-between items-center p-3 rounded-lg bg-primary/10">
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
                      <Button variant="outline" size="sm" onClick={() => handleEditLesson(lesson)}>
                        <Edit className="w-4 h-4 mr-2" />
                        Edit
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* {selectedLesson && (
        <SubmissionsDialog
          open={!!selectedLesson}
          onOpenChange={() => setSelectedLesson(null)}
          lessonTitle={selectedLesson.title}
          submissions={selectedLesson.submissions}
          onUpdateSubmission={handleUpdateSubmission}
        />
      )} */}

      {/* Chapter Form */}
      {course && (
        <ChapterFormDialog
          open={isChapterFormOpen}
          onOpenChange={setIsChapterFormOpen}
          onSubmit={handleCreateChapter}
          mode={editingChapter ? "edit" : "create"}
          initialData={
            editingChapter
              ? {
                  title: editingChapter.title
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
          chapterTitle={selectedChapter?.title ? selectedChapter.title : null}
          mode={editingLesson ? "edit" : "create"}
          initialData={editingLesson ? editingLesson : undefined}
        />
      )}
    </div>
  )
}

