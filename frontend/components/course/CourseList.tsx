"use client";

import { useAuth } from "@/lib/auth-context";
import { CourseCard } from "./CourseCard";
import { useEffect, useState } from "react";
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
  const { enrollments, fetchEnrollments, accessToken, user } = useAuth();

  useEffect(() => {
    if (accessToken && user && user.role === "student") {
      fetchEnrollments();
    }
  }, [accessToken]);

  const checkCourseEnrollment = (courseId: number) => {
    const enrolledCourseIds = enrollments.map(
      (enrollment) => enrollment.course.id
    );
    return enrolledCourseIds.includes(courseId);
  };

  const getCourseProgress = (courseId: number) => {
    const enrollment = enrollments.find(
      (enrollment) => enrollment.course.id === courseId
    );
    return enrollment?.progress;
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
      mode: checkCourseEnrollment(course.id) ? "enrolled" : "student",
      isEnrolled: checkCourseEnrollment(course.id),
      progress: getCourseProgress(course.id) || 0,
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
