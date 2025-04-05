"use client"

import { useAuth } from "@/lib/auth-context"
import { useEffect, useState } from "react"
import { EnrolledCourse } from "@/lib/types/course"
import { Loading } from "@/components/Loading"
import { CourseCard } from "@/components/course/CourseCard"
import { getCoursesApi } from "@/lib/api/course-api"

export default function MyCourses() {
  const { enrollments } = useAuth()
  const [enrolledCourses, setEnrolledCourses] = useState<EnrolledCourse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEnrolledCourses = async () => {
      try {
        const courses = await getCoursesApi();
        const enrolledCourseIds = enrollments.map((enrollment) => enrollment.course.id);
        const coursesData = courses.filter((course) => enrolledCourseIds.includes(course.id));
        const enrolledCoursesData : EnrolledCourse[] = coursesData.map((course) => {
          const enrollment = enrollments.find((enrollment) => enrollment.course.id === course.id);
          return {
            ...course,
            progress: enrollment?.progress || 0
          };
        });
        setEnrolledCourses(enrolledCoursesData);
      } catch (error) {
        console.error("Failed to fetch enrolled courses", error);
      } finally {
        setLoading(false);
      }
    };

    fetchEnrolledCourses();
  }, []);

  if (loading) {
    return <Loading />
  }

  return (
    <main className="pt-24">
      <section className="container mx-auto py-12">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">My Courses</h1>
          <p className="text-gray-600">{enrolledCourses.length} courses</p>
        </div>
        {enrolledCourses.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {enrolledCourses.map((course) => (
              <CourseCard
                key={course.id}
                {...course}
                mode="enrolled"
                progress={course.progress}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <h2 className="text-2xl font-semibold text-gray-600 mb-4">Chưa tham gia khóa học nào</h2>
            <p className="text-gray-500">Hãy tham gia các khóa học và bắt đầu học ngay hôm nay!</p>
          </div>
        )}
      </section>
    </main>
  )
}

