import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Chapter } from "@/lib/types/chapter";
import { Lesson } from "@/lib/types/lesson";
import { Lessons } from "@/components/lesson/Lessons";

interface LessonCurriculumProps {
  courseTitle: string;
  chapters: Chapter[];
  lessonsWithoutChapter: Lesson[];
  currentLessonId: string | null;
  completedLessonIds: string[] | null;
  status: "enrolled" | "notEnrolled";
  onLessonSelect: (lessonId: string) => void;
}

export function LessonCurriculum({
  courseTitle,
  chapters,
  lessonsWithoutChapter,
  currentLessonId,
  completedLessonIds = null,
  status,
  onLessonSelect,
}: LessonCurriculumProps) {
  return (
    <div className="bg-gray-50 rounded-xl p-4">
      {status === "enrolled" && (
        <h2 className="text-xl text-destructive font-bold mb-2">
          {courseTitle}
        </h2>
      )}
      <Accordion type="multiple" className="w-full space-y-1">
        {chapters.map((chapter, index) => (
          <AccordionItem key={chapter.id} value={chapter.id.toString()}>
            <AccordionTrigger className="bg-primary/20 text-primary p-3 rounded-lg hover:bg-primary/30">
              <div className="flex flex-col items-start">
                <span className="text-sm">
                  Chương {index + 1}: {chapter.title}
                </span>
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <div className="mt-1 space-y-1">
                <Lessons
                  lessons={chapter.lessons}
                  currentLessonId={currentLessonId}
                  completedLessonIds={completedLessonIds}
                  status={status}
                  onLessonSelect={onLessonSelect}
                />
              </div>
            </AccordionContent>
          </AccordionItem>
        ))}
        <div className="space-y-2">
          <Lessons
            lessons={lessonsWithoutChapter}
            currentLessonId={currentLessonId}
            completedLessonIds={completedLessonIds}
            status={status}
            onLessonSelect={onLessonSelect}
          />
        </div>
      </Accordion>
    </div>
  );
}
