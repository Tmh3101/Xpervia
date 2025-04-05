"use client"

import { useParams, useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { Edit, Trash } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Plus } from "lucide-react"
import { Description } from "@/components/Description"
import { VideoPlayer } from "@/components/lesson/VideoPlayer"
import { LessonAttachment } from "@/components/lesson/LessonAttachment"
import { getAssignmentSubmissionsApi } from "@/lib/api/assignment-api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import type { LessonDetail } from "@/lib/types/lesson"
import type { AssignmentSubmissions } from "@/lib/types/assignment"
import { createAssignmentApi, deleteAssignmentApi, updateAssignmentApi } from "@/lib/api/assignment-api"
import { getLessonDetailApi } from "@/lib/api/lesson-api"
import { AssignmentFormDialog } from "@/components/course/AssignmentFormDialog"
import { SubmissionDialog } from "@/components/course/SubmissionDialog"

export default function TeacherLessonDetail() {
  const params = useParams()
  const router = useRouter()
  const [lesson, setLesson] = useState<LessonDetail | null>(null)
  const [assignments, setAssignments] = useState<AssignmentSubmissions[]>([])
  const [isAddAssignmentOpen, setIsAddAssignmentOpen] = useState(false)
  const [isEditingAssignment, setIsEditingAssignment] = useState(false)
  const [selectedAssignment, setSelectedAssignment] = useState<AssignmentSubmissions | null>(null)
  const [isViewingSubmissions, setIsViewingSubmissions] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (params.id && params.lessonId) {
      console.log("Fetching lesson detail:", params.lessonId)
      const fetchLessonDetail = async () => {
        setIsLoading(true)
        try {
          const lessonDetail = await getLessonDetailApi(Number.parseInt(params.lessonId))
          setLesson(lessonDetail)
          console.log("Lesson detail:", lessonDetail)
          if (lessonDetail) {
            const assignmentsData = await getAssignmentSubmissionsApi(lessonDetail.id)
            setAssignments(assignmentsData)
            console.log("AssignmentsData:", assignmentsData)
            console.log("Assignments:", assignments)
          }
        } catch (error) {
          console.error("Error fetching data:", error)
        } finally {
          setIsLoading(false)
        }
      }

      fetchLessonDetail()
    }
  }, [params.id, params.lessonId])

  const handleAddAssignment = async (data: any) => {
    try {
      if (!data || !selectedAssignment) return

      if (isEditingAssignment) {
        // Update assignment
        await updateAssignmentApi(selectedAssignment.id, data)
      } else {
        // Create assignment
        await createAssignmentApi(Number.parseInt(params.lessonId), data)
      }

      // Refresh assignments
      const assignmentsData = await getAssignmentSubmissionsApi(Number.parseInt(params.lessonId))
      setAssignments(assignmentsData)
      setIsEditingAssignment(false)
      setIsAddAssignmentOpen(false)
    } catch (error) {
      console.error("Error creating or editing assignment:", error)
    }
  }

  const handleDeleteAssignment = async () => {
    try {
      // Delete assignment
      if (!selectedAssignment) return
      const assignmentId = selectedAssignment.id
      await deleteAssignmentApi(assignmentId)
      // Refresh assignments
      setAssignments(assignments.filter((assignment) => assignment.id !== assignmentId))
    }
    catch (error) {
      console.error("Error deleting assignment:", error)
    }
  }

  const handleEditAssignment = (assignment: AssignmentSubmissions) => {
    setSelectedAssignment(assignment)
    setIsEditingAssignment(true)
    setIsAddAssignmentOpen(true)
  }

  const handleCloseAssignmentForm = () => {
    setIsEditingAssignment(false)
    setIsAddAssignmentOpen(false)
    setSelectedAssignment(null)
  }

  const handleViewSubmissions = (assignment: AssignmentSubmissions) => {
    setSelectedAssignment(assignment)
    setIsViewingSubmissions(true)
  }

  if (isLoading) {
    return <div className="container mx-auto py-8 text-center">Đang tải...</div>
  }

  if (!lesson) {
    return <div className="container mx-auto py-8 text-center">Không tìm thấy bài học</div>
  }

  return (
    <div className="container mx-auto py-8 mt-[80px]">
      <Button variant="ghost" onClick={() => router.push(`/teacher/courses/${params.id}/detail`)}>
        <ArrowLeft className="w-4 h-4 mr-2" />
        Trở về khóa học
      </Button>

      <div className="grid gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h1 className="text-2xl font-bold mb-4">{lesson.title}</h1>
          <div className="aspect-video relative rounded-lg overflow-hidden mb-4">
            <VideoPlayer videoId={lesson.video_id} />
          </div>

          <Description title="Nội dung bài học" description={lesson.content || "Không có nội dung."} />

          {lesson.attachment && (
            <div className="mt-4">
              <h2 className="text-lg font-semibold mb-2">Tài liệu đính kèm</h2>
              <LessonAttachment attachment={lesson.attachment} />
            </div>
          )}
        </div>

        {/* Assignments Section */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Bài tập</h2>
            <Button onClick={() => setIsAddAssignmentOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Thêm bài tập
            </Button>
          </div>

          {assignments.length === 0 ? (
            <div className="text-center py-8 text-gray-500">Chưa có bài tập nào cho bài học này</div>
          ) : (
            <div className="space-y-4">
              {assignments.map((assignment) => (
                <Card key={assignment.id} className="relative">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="mb-2">{assignment.title}</CardTitle>
                        <CardDescription>
                          Bắt đầu vào {new Date(assignment.start_at).toLocaleDateString()}
                          {assignment.due_at && ` - Hạn nộp: ${new Date(assignment.due_at).toLocaleDateString()}`}
                        </CardDescription>
                      </div>
                      <div>
                        <Button
                          variant="outline"
                          size="icon"
                          className="absolute top-2 right-14"
                          onClick={() => handleEditAssignment(assignment)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          className="absolute top-2 right-2 bg-red-200 text-red-500 hover:bg-red-300 hover:text-red-600"
                          onClick={() => handleEditAssignment(assignment)}
                        >
                          <Trash className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p>{assignment.content}</p>
                  </CardContent>
                  <CardFooter>
                    <Button
                      variant="outline"
                      className="border border-primary bg-primary/10 text-primary hover:bg-primary/20 hover:text-primary"
                      onClick={() => handleViewSubmissions(assignment)}>
                      Xem bài nộp ({assignment.submissions ? assignment.submissions.length : 0})
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Assignment Form Dialog */}
      <AssignmentFormDialog
        open={isAddAssignmentOpen}
        onOpenChange={handleCloseAssignmentForm}
        onSubmit={handleAddAssignment}
        onDelete={handleDeleteAssignment}
        mode={isEditingAssignment ? "edit" : "create"}
        initialData={selectedAssignment || undefined}
      />

      {/* Submission Dialog */}
      {selectedAssignment && (
        <SubmissionDialog
          open={isViewingSubmissions}
          onOpenChange={setIsViewingSubmissions}
          assignment={selectedAssignment}
        />
      )}
    </div>
  )
}