"use client";

import { useAuth } from "@/lib/auth-context";
import { CourseCard } from "@/components/course/CourseCard";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function StudentFavoritesPage() {
  const { favorites, enrollments, toggleFavorite } = useAuth();
  const router = useRouter();
  const [localFavorites, setLocalFavorites] = useState(favorites);
  useEffect(() => {
    setLocalFavorites(favorites);
  }, [favorites]);

  // Xử lý toggle: chỉ cập nhật UI khi reload
  const handleToggle = (courseId: number) => {
    toggleFavorite(courseId);
    // Không cập nhật localFavorites ngay, chỉ khi reload mới cập nhật
  };

  const isEnrolled = (courseId: number) => {
    return enrollments.some((enrollment) => enrollment.course.id === courseId);
  };

  const extractCourseData = (course: any) => {
    if (isEnrolled(course.id)) {
      return {
        ...course,
        progress:
          enrollments.find((enrollment) => enrollment.course.id === course.id)
            ?.progress || 0,
      };
    }
    return course;
  };

  return (
    <main className="pt-24">
      <section className="container mx-auto py-12">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Khóa học yêu thích</h1>
        </div>
        {localFavorites.length === 0 ? (
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
            {localFavorites.map((fav) => (
              <CourseCard
                key={fav.course.id}
                {...extractCourseData(fav.course)}
                mode={isEnrolled(fav.course.id) ? "enrolled" : "student"}
              />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
