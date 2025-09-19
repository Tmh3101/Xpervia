import React from "react";
import { cn } from "@/lib/utils";
import { Lesson } from "@/lib/types/lesson";
import { Lock, CircleCheckBig, EyeOff } from "lucide-react";

interface LessonsProps {
  lessons: Lesson[];
  currentLessonId: string | null;
  completedLessonIds: string[] | null;
  status: "enrolled" | "notEnrolled";
  onLessonSelect: (lessonId: string) => void;
}

export function Lessons({
  lessons,
  currentLessonId,
  completedLessonIds,
  status,
  onLessonSelect,
}: LessonsProps) {
  const getLessonStatusIcon = (lessonId: string) => {
    if (status === "notEnrolled") {
      return <Lock className="w-5 h-5 text-gray-400 mr-2" />;
    }

    if (completedLessonIds?.includes(lessonId)) {
      return <CircleCheckBig className="w-5 h-5 mr-2 text-success" />;
    }

    if (lessons.find((l) => l.id === lessonId)?.is_visible === false) {
      return <EyeOff className="w-5 h-5 text-gray-400 mr-2" />;
    }
  };

  return (
    <>
      {lessons
        .sort((a, b) => a.order - b.order)
        .map((lesson, index) => (
          <button
            key={lesson.id}
            onClick={() => status === "enrolled" && onLessonSelect(lesson.id)}
            className={cn(
              "w-full flex items-center justify-between p-3 rounded-lg border border-white",
              lesson.id === currentLessonId && "border-primary font-medium",
              status === "enrolled" || lesson.is_visible
                ? "hover:bg-gray-100"
                : "cursor-not-allowed"
            )}
            disabled={status === "notEnrolled" || !lesson.is_visible}
          >
            <div className="flex items-center gap-3">
              <span
                className={cn(
                  "text-sm text-destructive text-align-left",
                  status === "notEnrolled" || !lesson.is_visible
                    ? "text-gray-400"
                    : "text-gray-700",
                  lesson.id === currentLessonId && "text-primary"
                )}
              >
                {index + 1}. {lesson.title}
              </span>
            </div>
            {getLessonStatusIcon(lesson.id.toString())}
          </button>
        ))}
    </>
  );
}
