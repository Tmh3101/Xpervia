"use client";

import { useAuth } from "@/lib/auth-context";
import { useEffect, useState } from "react";
import { Course } from "@/lib/types/course";
import { Loading } from "@/components/Loading";
import { CourseList } from "@/components/course/CourseList";

export default function MyCourses() {
  const { enrollments } = useAuth();
  const [enrolledCourses, setEnrolledCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEnrolledCourses = async () => {
      try {
        const enrolledCourses = enrollments.map(
          (enrollment) => enrollment.course
        );
        setEnrolledCourses(enrolledCourses);
      } catch (error) {
        console.error("Failed to fetch enrolled courses", error);
      } finally {
        setLoading(false);
      }
    };
    fetchEnrolledCourses();
  }, [enrollments]);

  if (loading) {
    return <Loading />;
  }

  return (
    <main className="pt-24">
      <section className="container mx-auto py-12">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Khóa học của tôi</h1>
          <p className="text-gray-600">{enrolledCourses.length} khóa học</p>
        </div>
        {enrolledCourses.length > 0 ? (
          <CourseList courses={enrolledCourses} mode="student" />
        ) : (
          <div className="text-center py-16">
            <h2 className="text-2xl font-semibold text-gray-600 mb-4">
              Chưa tham gia khóa học nào
            </h2>
            <p className="text-gray-500">
              Hãy tham gia các khóa học và bắt đầu học ngay hôm nay!
            </p>
            <a
              href="/"
              className="inline-block mt-4 px-6 py-3 bg-primary text-white rounded-xl"
            >
              Quay về trang chủ
            </a>
          </div>
        )}
      </section>
    </main>
  );
}
