"use client";

import { useAuth } from "@/lib/auth-context";
import { CourseCard } from "./CourseCard";
import { Loading } from "@/components/Loading";
import type { Course } from "@/lib/types/course";

interface CourseListProps {
  mode?: "teacher" | "student";
  courses: Course[];
  handleEditCourse?: (course: Course) => void;
  isLoading?: boolean;
}

export const CourseList = ({
  mode = "student",
  courses,
  handleEditCourse,
  isLoading = false,
}: CourseListProps) => {
  const { enrolledCourseIds } = useAuth();

  const isEnrolled = (courseId: number) => {
    if (!enrolledCourseIds) return false;
    return enrolledCourseIds.includes(courseId);
  };

  const getCourseCardProps = (course: Course) => {
    if (mode === "teacher") {
      return {
        ...course,
        mode,
        onEditClick: () => {
          handleEditCourse && handleEditCourse(course);
        },
      };
    }

    return {
      ...course,
      mode: isEnrolled(course.id) ? "enrolled" : "student",
      isEnrolled: isEnrolled(course.id),
    };
  };

  if (isLoading) {
    return <Loading />;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
      {courses.map((course) => (
        <CourseCard key={course.id} {...getCourseCardProps(course)} />
      ))}
    </div>
  );
};
