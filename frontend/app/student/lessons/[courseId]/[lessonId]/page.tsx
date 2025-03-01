"use client"

import { VideoPlayer } from "@/components/lesson/VideoPlayer"
import { LessonCurriculum } from "@/components/lesson/LessonCurriculum"
import { Description } from "@/components/Description"
import { LessonAttachments } from "@/components/lesson/LessonAttachments"
import { LessonAssignment } from "@/components/lesson/LessonAssignment"
import { LessonSubmission } from "@/components/lesson/LessonSubmission"
import { useParams } from "next/navigation"
import { useEffect, useState } from "react"
import { getCourseWithDetailLessonsApi } from "@/lib/api/course-api"
import { getLessonAssignmentsApi } from "@/lib/api/course-api"
import { ChapterDetail } from "@/lib/types/chapter"
import { LessonDetail } from "@/lib/types/lesson"
import { Assignment } from "@/lib/types/assignment"

export default function LessonPage() {
  const params = useParams()
  const [courseData, setCourseData] = useState<any>(null)
  const [currentLesson, setCurrentLesson] = useState<any>(null)
  const [assignments, setAssignments] = useState<Assignment[] | null>(null)
  // const [submission, setSubmission] = useState<any>(null)

  useEffect(() => {
    if (params.courseId) {
      getCourseWithDetailLessonsApi(Number(params.courseId)).then((data) => {
        setCourseData(data)

        if (data && params.lessonId) {

          const lessons = data.course_content.chapters
            .flatMap((chapter) => chapter.lessons)
            .concat(data.course_content.lessons_without_chapter)
          const lesson = lessons.find((l) => l.id === parseInt(params.lessonId[0]))
          setCurrentLesson(lesson)
        }
      })
    }
  }, [params.lessonId])

  useEffect(() => {
    if (currentLesson) {
      getLessonAssignmentsApi(currentLesson.id).then((data) => {
        setAssignments(data)
        console.log(data)
      })
    }
  }, [currentLesson])

  if (!courseData || !currentLesson) {
    return <div>Loading...</div>
  }

  const handleLessonChange = (lessonId: number) => {
    // Update URL and fetch new lesson data
    window.history.pushState({}, "", `/student/lessons/${params.courseId}/${lessonId}`)

    // Find and set the new lesson
    const lessons = courseData.course_content.chapters
      .flatMap((chapter: ChapterDetail) => chapter.lessons)
      .concat(courseData.course_content.lessons_without_chapter)
    const lesson = lessons.find((l: LessonDetail) => l.id === lessonId)
    setCurrentLesson(lesson)
  }

  return (
    <main className="pt-4">
      <div className="container mx-auto py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="mt-[40px]">
              <VideoPlayer videoId={currentLesson.video_id} />
            </div>
            <div className="my-8 p-2">
              <Description
                title={currentLesson.title}
                description={currentLesson.content || "No description available."}
              />
              <LessonAttachments attachments={[currentLesson.attachment_id]} />
            </div>
            <div>
              { assignments && (
                <div className="mt-8 p-2">
                  <h1 className="text-2xl text-destructive font-bold mb-4">Lesson Assignments</h1>
                  <div className="bg-white rounded-xl px-6 py-4 border space-y-6">
                    {
                      assignments?.map((assignment) => (
                        <>
                          <LessonAssignment
                            key={assignment.id}
                            title={assignment.title}
                            content={assignment.content}
                          />
                          <LessonSubmission submission={assignment.submission} />
                        </>
                      ))
                    }
                  </div>
                </div>
              )}
            </div>
          </div>
          <div className="lg:col-span-1">
            <div className="mt-[40px]">
              <LessonCurriculum
                courseTitle={courseData.course_content.title}
                chapters={courseData.course_content.chapters}
                lessonsWithoutChapter={courseData.course_content.lessons_without_chapter}
                currentLessonId={currentLesson.id}
                status="enrolled"
                onLessonSelect={handleLessonChange}
              />
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

