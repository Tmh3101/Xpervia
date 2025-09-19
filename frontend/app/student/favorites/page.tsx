"use client";

import { useAuth } from "@/lib/auth-context";
import { CourseCard } from "@/components/course/CourseCard";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getFavoritedCoursesApi } from "@/lib/api/course-api";
import type { Course } from "@/lib/types/course";

export default function StudentFavoritesPage() {
  const { favoritedCourseIds, enrolledCourseIds, toggleFavorite } = useAuth();
  const router = useRouter();
  const [localFavoriteCourseIds, setLocalFavoriteCourseIds] =
    useState(favoritedCourseIds);
  const [courses, setCourses] = useState<Course[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const favoritedCourses = await getFavoritedCoursesApi();
      setCourses(favoritedCourses);
    };

    fetchData();
  }, []);

  useEffect(() => {
    setLocalFavoriteCourseIds(favoritedCourseIds);
  }, [favoritedCourseIds]);

  // Xử lý toggle: chỉ cập nhật UI khi reload
  const handleToggle = (courseId: number) => {
    toggleFavorite(courseId);
    // Không cập nhật localFavorites ngay, chỉ khi reload mới cập nhật
  };

  const isEnrolled = (courseId: number) => {
    if (!enrolledCourseIds) return false;
    return enrolledCourseIds.includes(courseId);
  };

  return (
    <main className="pt-24">
      <section className="container mx-auto py-12">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Khóa học yêu thích</h1>
        </div>
        {courses.length === 0 ? (
          <div className="text-center py-16 pt-48">
            <h2 className="text-2xl font-semibold text-gray-600 mb-4">
              Chưa khóa học yêu thích nào
            </h2>
            <p className="text-gray-500">
              Hãy thêm các khóa học vào danh sách yêu thích để dễ dàng truy cập
            </p>
            <a
              href="/"
              className="inline-block mt-4 px-6 py-3 bg-primary text-white rounded-xl"
            >
              Quay về trang chủ
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {courses.map((c) => (
              <CourseCard
                key={c.id}
                {...c}
                mode={isEnrolled(c.id) ? "enrolled" : "student"}
              />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
