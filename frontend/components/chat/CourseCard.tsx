"use client";

import React, { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { getCourseDetailApi } from "@/lib/api/course-api";
import type { Course } from "@/lib/types/course";

const ChatCourseCard: React.FC<{ courseId: number }> = ({ courseId }) => {
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError(null);
    getCourseDetailApi(courseId)
      .then((c) => {
        if (!mounted) return;
        setCourse(c);
      })
      .catch((err) => {
        if (!mounted) return;
        console.error("Failed to load course detail", err);
        setError("Không thể tải thông tin khóa học");
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [courseId]);

  if (loading) {
    return (
      <div className="mt-1 w-full max-w-xs p-2 rounded-lg bg-white border border-gray-200 shadow-sm">
        <div className="animate-pulse flex items-center gap-3">
          <div className="w-16 h-10 bg-gray-200 rounded-md" />
          <div className="flex-1 space-y-2">
            <div className="h-3 bg-gray-200 rounded w-3/4" />
            <div className="h-3 bg-gray-200 rounded w-1/2" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !course) {
    return null;
  }

  const thumb = course.course_content.thumbnail_url || "/placeholder.svg";
  const teacher = course.course_content.teacher;

  return (
    <div className="mt-1 w-full max-w-xs p-2 rounded-lg bg-white border border-primary">
      <Link href={`/courses/${course.id}`} className="flex items-start gap-3">
        <div className="w-16 h-10 relative flex-shrink-0 rounded-md overflow-hidden bg-gray-100">
          <Image src={thumb} alt={course.course_content.title} fill className="object-cover" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-foreground line-clamp-2 hover:text-primary">
            {course.course_content.title}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {teacher?.first_name || ""} {teacher?.last_name || ""}
          </div>
        </div>
      </Link>
    </div>
  );
};

export default ChatCourseCard;
