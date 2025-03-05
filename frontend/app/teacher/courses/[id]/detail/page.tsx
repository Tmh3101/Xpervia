"use client"

import { useParams, useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import coursesData from "@/data/courses.json"
import courseDetails from "@/data/course-details.json"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Users } from "lucide-react"
import Image from "next/image"
import { getGoogleDriveImageUrl } from "@/lib/google-drive-url"
import { Badge } from "@/components/ui/badge"
// import { SubmissionsDialog } from "@/components/teacher/SubmissionsDialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Submission } from "@/lib/types/submission"

export default function CourseDetail() {
  const params = useParams()
  const router = useRouter()
  const [course, setCourse] = useState<any>(null)
  const [selectedLesson, setSelectedLesson] = useState<{
    title: string
    submissions: Submission[]
  } | null>(null)

  useEffect(() => {
    if (params.id) {
      // Merge course data with course details
      const basicInfo = coursesData.courses.find((c) => c.id === Number(params.id))
      const details = courseDetails.courses.find((c) => c.id === Number(params.id))

      if (basicInfo) {
        setCourse({
          ...basicInfo,
          chapters: details?.chapters || [],
        })
      }
    }
  }, [params.id])

  const handleUpdateSubmission = (submissionId: string, score: number, feedback: string) => {
    // In a real app, this would make an API call to update the submission
    console.log("Updating submission:", { submissionId, score, feedback })
  }

  if (!course) {
    return <div>Loading...</div>
  }

  return (
    <div className="container mx-auto py-8">
      <Button variant="ghost" className="mb-6" onClick={() => router.push("/teacher")}>
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Courses
      </Button>

      <div className="grid gap-6">
        {/* Course Info */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-2xl font-bold mb-2">{course.title}</h1>
              <div className="flex gap-2 mb-4">
                {course.categories.map((category: string) => (
                  <Badge key={category} variant="secondary">
                    {category}
                  </Badge>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-muted-foreground" />
              <span className="font-medium">{course.students_enrolled} students enrolled</span>
            </div>
          </div>
          <div className="aspect-video relative rounded-lg overflow-hidden mb-4">
            <Image
              src={getGoogleDriveImageUrl(course.thumnail_id) || "/placeholder.svg"}
              alt={course.title}
              fill
              className="object-cover"
            />
          </div>
        </div>

        {/* Course Content and Submissions */}
        <Tabs defaultValue="content" className="w-full">
          <TabsList>
            <TabsTrigger value="content">Course Content</TabsTrigger>
            <TabsTrigger value="submissions">Student Submissions</TabsTrigger>
          </TabsList>

          <TabsContent value="content">
            <div className="space-y-6">
              {course.chapters?.map((chapter: any, chapterIndex: number) => (
                <Card key={chapter.id}>
                  <CardHeader>
                    <CardTitle>{chapter.title}</CardTitle>
                    <CardDescription>
                      {chapter.totalVideos} lessons • {chapter.totalDuration}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {chapter.lessons.map((lesson: any) => (
                        <div key={lesson.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <div>
                            <h4 className="font-medium">{lesson.title}</h4>
                            <p className="text-sm text-gray-500">{lesson.duration}</p>
                          </div>
                          {lesson.assignment && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() =>
                                setSelectedLesson({
                                  title: lesson.title,
                                  submissions: mockSubmissions, // In a real app, fetch this data
                                })
                              }
                            >
                              View Submissions
                            </Button>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="submissions">
            <Card>
              <CardHeader>
                <CardTitle>All Submissions</CardTitle>
                <CardDescription>View and grade all student submissions for this course</CardDescription>
              </CardHeader>
              <CardContent>
                {/* Add a comprehensive submissions view here */}
                <div className="text-muted-foreground">Coming soon: Comprehensive submissions dashboard</div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {selectedLesson && (
        <SubmissionsDialog
          open={!!selectedLesson}
          onOpenChange={() => setSelectedLesson(null)}
          lessonTitle={selectedLesson.title}
          submissions={selectedLesson.submissions}
          onUpdateSubmission={handleUpdateSubmission}
        />
      )}
    </div>
  )
}

