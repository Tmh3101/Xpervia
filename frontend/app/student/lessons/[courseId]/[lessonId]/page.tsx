"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Loader2, CircleAlert } from "lucide-react";
import { Loading } from "@/components/Loading";
import { Description } from "@/components/Description";
import { VideoPlayer } from "@/components/lesson/VideoPlayer";
import { LessonCurriculum } from "@/components/lesson/LessonCurriculum";
import { LessonAttachment } from "@/components/lesson/LessonAttachment";
import { LessonAssignment } from "@/components/lesson/LessonAssignment";
import { LessonSubmission } from "@/components/lesson/LessonSubmission";
import { getCourseWithDetailLessonsApi } from "@/lib/api/course-api";
import { getLessonAssignmentsApi } from "@/lib/api/assignment-api";
import {
  getLessonCompletionsApi,
  completeLessonApi,
  uncompleteLessonApi,
} from "@/lib/api/lesson-api";
import type { CheckedState } from "@radix-ui/react-checkbox";
import type { ChapterDetail } from "@/lib/types/chapter";
import type { LessonDetail } from "@/lib/types/lesson";
import type { AssignmentDetail } from "@/lib/types/assignment";
import type { CourseWithDetailLessons } from "@/lib/types/course";

export default function LessonPage() {
  const params = useParams();
  const [courseData, setCourseData] = useState<CourseWithDetailLessons | null>(
    null
  );
  const [currentLesson, setCurrentLesson] = useState<any>(null);
  const [assignments, setAssignments] = useState<AssignmentDetail[] | null>(
    null
  );
  const [completedLessonIds, setCompletedLessonIds] = useState<string[]>([]);
  const [isCompletingLesson, setIsCompletingLesson] = useState(false);

  useEffect(() => {
    if (params.courseId) {
      getCourseWithDetailLessonsApi(Number(params.courseId)).then((data) => {
        setCourseData(data);
        if (data && params.lessonId) {
          const lessons = data.course_content.chapters
            .flatMap((chapter) => chapter.lessons)
            .concat(data.course_content.lessons_without_chapter);
          const lesson = lessons.find((l) => l.id === params.lessonId);
          setCurrentLesson(lesson);
        }
      });

      getLessonCompletionsApi(Number(params.courseId)).then((data) => {
        setCompletedLessonIds(data.map((lc) => lc.lesson.id));
      });
    }
  }, [params.lessonId]);

  useEffect(() => {
    if (currentLesson) {
      getLessonAssignmentsApi(currentLesson.id).then((data) => {
        setAssignments(data);
      });
    }
  }, [currentLesson]);

  if (!courseData) {
    return <Loading />;
  }

  if (!currentLesson) {
    return (
      <div className="flex items-center justify-center h-screen">
        <CircleAlert className="w-8 h-8 text-red-500" />
        <span>Không tìm thấy bất cứ bài học nào!</span>
      </div>
    );
  }

  const handleLessonChange = (lessonId: string) => {
    // Update URL and fetch new lesson data
    window.history.pushState(
      {},
      "",
      `/student/lessons/${params.courseId}/${lessonId}`
    );

    // Find and set the new lesson
    const lessons = courseData.course_content.chapters
      .flatMap((chapter: ChapterDetail) => chapter.lessons)
      .concat(courseData.course_content.lessons_without_chapter);
    const lesson = lessons.find((l: LessonDetail) => l.id === lessonId);
    setCurrentLesson(lesson);
  };

  const handleCheckboxChange = async (checked: CheckedState) => {
    if (!currentLesson?.id) return;

    setIsCompletingLesson(true);
    try {
      if (checked) {
        await completeLessonApi(currentLesson.id);
        setCompletedLessonIds((prev) => [...prev, currentLesson.id]);
      } else {
        await uncompleteLessonApi(currentLesson.id);
        setCompletedLessonIds((prev) =>
          prev.filter((id) => id !== currentLesson.id)
        );
      }
    } catch (error) {
      console.error("Failed to update lesson completion status:", error);
    } finally {
      setIsCompletingLesson(false);
    }
  };

  return (
    <main className="pt-4">
      <div className="container mx-auto py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="mt-[40px]">
              <VideoPlayer videoUrl={currentLesson.video_url} />
              <div className="pt-2 space-x-2 w-full flex justify-end items-center">
                {isCompletingLesson ? (
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Checkbox
                    id="complete"
                    name="complete"
                    onCheckedChange={handleCheckboxChange}
                    checked={completedLessonIds.includes(currentLesson.id)}
                  />
                )}
                <label
                  htmlFor="complete"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Đánh dấu hoàn thành
                </label>
              </div>
            </div>
            <div className="mb-4 p-2">
              <Description
                title={currentLesson.title}
                description={
                  currentLesson.content || "No description available."
                }
              />
              {currentLesson.attachments?.length != 0 && (
                <LessonAttachment attachment={currentLesson.attachment} />
              )}
            </div>
            <div>
              {assignments?.length != 0 && (
                <div className="mt-8 p-2 space-y-2">
                  <h1 className="text-2xl text-destructive font-bold mb-4">
                    Bài tập
                  </h1>
                  {assignments?.map((assignment) => (
                    <div
                      key={assignment.id}
                      className="bg-white rounded-xl px-6 py-4 border space-y-6"
                    >
                      <LessonAssignment
                        title={assignment.title}
                        content={assignment.content}
                      />
                      <LessonSubmission
                        assignmentId={assignment.id}
                        submission={assignment.submission}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          <div className="lg:col-span-1">
            <div className="mt-[40px]">
              <LessonCurriculum
                courseTitle={courseData.course_content.title}
                chapters={courseData.course_content.chapters}
                lessonsWithoutChapter={
                  courseData.course_content.lessons_without_chapter
                }
                currentLessonId={currentLesson.id}
                completedLessonIds={completedLessonIds}
                status="enrolled"
                onLessonSelect={handleLessonChange}
              />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
