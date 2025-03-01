import { CheckCircle2, Lock, PlayCircle } from "lucide-react"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { cn } from "@/lib/utils"
import { Chapter } from "@/lib/types/chapter"
import { Lesson } from "@/lib/types/lesson"

interface LessonCurriculumProps {
  courseTitle: string
  chapters: Chapter[]
  lessonsWithoutChapter: Lesson[]
  currentLessonId: number | null
  status: "enrolled" | "notEnrolled"
  onLessonSelect: (lessonId: number) => void
}

export function LessonCurriculum({
  courseTitle,
  chapters,
  lessonsWithoutChapter,
  currentLessonId,
  status,
  onLessonSelect
}: LessonCurriculumProps) {

  const getStatusIcon = (status: string) => {
    if (status === "notEnrolled") {
      return <Lock className="w-4 h-4 text-gray-400" />
    }
  }

  return (
    <div className="bg-gray-50 rounded-xl p-4">
      <h2 className="text-xl text-destructive font-bold mb-2">{courseTitle}</h2>
      <Accordion type="multiple" className="w-full space-y-1">
        {chapters.map((chapter) => (
          <AccordionItem key={chapter.id} value={chapter.id.toString()}>
            <AccordionTrigger className="bg-primary text-white p-3 rounded-lg hover:bg-secondary">
              <div className="flex flex-col items-start">
                <span className="text-sm">{chapter.title}</span>
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <div className="mt-1 space-y-1">
                {chapter.lessons.map((lesson) => (
                  <button
                    key={lesson.id}
                    onClick={() => status === "enrolled" && onLessonSelect(lesson.id)}
                    className={cn(
                      "w-full flex items-center justify-between p-3 rounded-lg border border-white",
                      lesson.id === currentLessonId && "border-secondary bg-primary/10",
                      status === "enrolled" && "hover:bg-gray-100",
                      status !== "enrolled" && "cursor-not-allowed",
                    )}
                    disabled={status === "notEnrolled"}
                  >
                    <div className="flex items-center gap-3">
                      {getStatusIcon(status)}
                      <span
                        className={cn(
                          "text-sm text-destructive",
                          status === "notEnrolled" ? "text-gray-400" : "text-gray-700",
                          lesson.id === currentLessonId && "text-primary",
                        )}
                      >
                        {lesson.title}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>
        ))}
        <div className="space-y-2">
          {lessonsWithoutChapter.map((lesson) => (
            <button
              key={lesson.id}
              onClick={() => status === "enrolled" && onLessonSelect(lesson.id)}
              className={cn(
                "w-full flex items-center justify-between p-3 rounded-lg border border-white",
                lesson.id === currentLessonId && "border-secondary bg-primary/10",
                status === "enrolled" && "hover:bg-gray-100",
                status !== "enrolled" && "cursor-not-allowed",
              )}
              disabled={status === "notEnrolled"}
            >
              <div className="flex items-center gap-3">
                {getStatusIcon(status)}
                <span
                  className={cn(
                    "text-sm text-destructive",
                    status === "notEnrolled" ? "text-gray-400" : "text-gray-700",
                    lesson.id === currentLessonId && "text-primary",
                  )}
                >
                  {lesson.title}
                </span>
              </div>
            </button>
          ))}  
        </div>
      </Accordion>
    </div>
  )
}

