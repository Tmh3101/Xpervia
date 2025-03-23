"use client"

import { useParams, useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Plus, Download, User } from "lucide-react"
import { Description } from "@/components/Description"
import { VideoPlayer } from "@/components/lesson/VideoPlayer"
import { LessonAttachment } from "@/components/lesson/LessonAttachment"
import { getAssignmentSubmissionsApi } from "@/lib/api/assignment-api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { LessonDetail } from "@/lib/types/lesson"
import type { AssignmentSubmissions } from "@/lib/types/assignment"
import type { SubmissionDetail } from "@/lib/types/submission"
import { createAssignmentApi } from "@/lib/api/assignment-api"
import { getLessonDetailApi } from "@/lib/api/lesson-api"
import { getGoogleDriveDownloadFileUrl, getGoogleDriveFileUrl } from "@/lib/google-drive-url"

export default function TeacherLessonDetail() {
  const params = useParams()
  const router = useRouter()
  const [lesson, setLesson] = useState<LessonDetail | null>(null)
  const [assignments, setAssignments] = useState<AssignmentSubmissions[]>([])
  const [isAddAssignmentOpen, setIsAddAssignmentOpen] = useState(false)
  const [assignmentTitle, setAssignmentTitle] = useState("")
  const [assignmentContent, setAssignmentContent] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [selectedAssignment, setSelectedAssignment] = useState<AssignmentSubmissions | null>(null)
  const [isViewingSubmissions, setIsViewingSubmissions] = useState(false)

  useEffect(() => {
    if (params.id && params.lessonId) {
      console.log("Fetching lesson detail:", params.lessonId)
      const fetchLessonDetail = async () => {
        try {
          const lessonDetail = await getLessonDetailApi(Number.parseInt(params.lessonId))
          setLesson(lessonDetail)
          console.log("Lesson detail:", lessonDetail)
          if (lessonDetail){
            const assignmentsData = await getAssignmentSubmissionsApi(lessonDetail.id)
            setAssignments(assignmentsData)
            console.log("Assignments:", assignmentsData)
          }
        } catch (error) {
          console.error("Error fetching data:", error)
        }
      }

      fetchLessonDetail()
    }
  }, [params.id, params.lessonId])

  const handleAddAssignment = async () => {
    // if (!assignmentTitle.trim() || !assignmentContent.trim()) return

    // setIsSubmitting(true)

    // try {
    //   // In a real app, this would make an API call to create a new assignment
    //   console.log("Creating new assignment:", {
    //     lessonId: lesson?.id,
    //     title: assignmentTitle,
    //     content: assignmentContent,
    //   })

    //   // Mock response
    //   const newAssignment: AssignmentDetail = {
    //     id: Math.floor(Math.random() * 1000),
    //     title: assignmentTitle,
    //     content: assignmentContent,
    //     lesson_id: lesson?.id || 0,
    //     created_at: new Date().toISOString(),
    //     submission: null,
    //   }

    //   setAssignments([...assignments, newAssignment])
    //   setAssignmentTitle("")
    //   setAssignmentContent("")
    //   setIsAddAssignmentOpen(false)
    // } catch (error) {
    //   console.error("Error creating assignment:", error)
    // } finally {
    //   setIsSubmitting(false)
    // }
  }

  const handleViewSubmissions = (assignment: AssignmentSubmissions) => {
    setSelectedAssignment(assignment)
    setIsViewingSubmissions(true)
  }

  if (!lesson) {
    return <div>Loading...</div>
  }

  return (
    <div className="container mx-auto py-8">
      <Button variant="ghost" className="mb-6" onClick={() => router.push(`/teacher/courses/${params.id}/detail`)}>
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

        <Tabs defaultValue="assignments" className="w-full">
          <TabsList>
            <TabsTrigger value="assignments">Bài tập</TabsTrigger>
          </TabsList>

          <TabsContent value="assignments">
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
                    <Card key={assignment.id}>
                      <CardHeader>
                        <CardTitle>{assignment.title}</CardTitle>
                        <CardDescription>
                          Bắt đầu vào {new Date(assignment.start_at).toLocaleDateString()}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p>{assignment.content}</p>
                      </CardContent>
                      <CardFooter>
                        <Button variant="outline" onClick={() => handleViewSubmissions(assignment)}>
                          Xem bài nộp
                        </Button>
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Add Assignment Dialog */}
      <Dialog open={isAddAssignmentOpen} onOpenChange={setIsAddAssignmentOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Thêm bài tập mới</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="assignment-title">Tiêu đề bài tập</Label>
              <Input
                id="assignment-title"
                placeholder="Nhập tiêu đề bài tập"
                value={assignmentTitle}
                onChange={(e) => setAssignmentTitle(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="assignment-content">Nội dung bài tập</Label>
              <Textarea
                id="assignment-content"
                placeholder="Nhập nội dung bài tập"
                value={assignmentContent}
                onChange={(e) => setAssignmentContent(e.target.value)}
                className="min-h-[150px]"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddAssignmentOpen(false)}>
              Hủy
            </Button>
            <Button onClick={handleAddAssignment} disabled={isSubmitting}>
              {isSubmitting ? "Đang tạo..." : "Tạo bài tập"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Submissions Dialog */}
      <Dialog open={isViewingSubmissions} onOpenChange={setIsViewingSubmissions}>
        <DialogContent className="sm:max-w-[700px]">
          <DialogHeader>
            <DialogTitle>Bài nộp cho: {selectedAssignment?.title}</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            {selectedAssignment?.submissions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">Chưa có bài nộp nào cho bài tập này</div>
            ) : (
              <ScrollArea className="h-[400px]">
                <div className="space-y-4">
                  {selectedAssignment?.submissions.map((submission) => (
                    <Card key={submission.id}>
                      <CardHeader>
                        <div className="flex items-center">
                          <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center mr-3">
                            <User className="w-5 h-5 text-primary" />
                          </div>
                          <div>
                            <CardTitle className="text-base">{`${submission.student.first_name} ${submission.student.last_name}`}</CardTitle>
                            <CardDescription>{submission.student.email}</CardDescription>
                          </div>
                          <div className="ml-auto text-sm text-gray-500">
                            Nộp vào: {new Date(submission.created_at).toLocaleString()}
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        {/* <div className="flex items-center">
                          <Button variant="outline" size="sm" asChild>
                            <a href={submission.file.url} target="_blank" rel="noopener noreferrer">
                              <Download className="w-4 h-4 mr-2" />
                              {submission.file.file_name}
                            </a>
                          </Button>
                        </div> */}
                      </CardContent>
                      <CardFooter className="flex flex-col items-start">
                        <div className="w-full space-y-2">
                          <Label htmlFor={`score-${submission.id}`}>Điểm số</Label>
                          <Input
                            id={`score-${submission.id}`}
                            type="number"
                            min="0"
                            max="10"
                            placeholder="Nhập điểm số (0-10)"
                            defaultValue={submission.submission_score?.score || ""}
                          />
                        </div>
                        <div className="w-full space-y-2 mt-4">
                          <Label htmlFor={`feedback-${submission.id}`}>Nhận xét</Label>
                          <Textarea
                            id={`feedback-${submission.id}`}
                            placeholder="Nhập nhận xét cho bài nộp"
                            defaultValue={submission.submission_score?.feedback || ""}
                            className="min-h-[100px]"
                          />
                        </div>
                        <Button className="mt-4">Lưu đánh giá</Button>
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewingSubmissions(false)}>
              Đóng
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

