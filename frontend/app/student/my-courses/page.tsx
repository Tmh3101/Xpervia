"use client"

import { useEffect, useState } from "react"
import { Course } from "@/lib/types/course"
import { CourseCard } from "@/components/CourseCard"
import { getEnrolledCoursesApi } from "@/lib/api/course-api"

export default function MyCourses() {

  const [enrolledCourses, setEnrolledCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEnrolledCourses = async () => {
      try {
        const courses = await getEnrolledCoursesApi();
        console.log("Enrolled courses", courses);
        setEnrolledCourses(courses);
      } catch (error) {
        console.error("Failed to fetch enrolled courses", error);
      } finally {
        setLoading(false);
      }
    };

    fetchEnrolledCourses();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
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
              <CourseCard key={course.id} {...course} mode="enrolled" />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <h2 className="text-2xl font-semibold text-gray-600 mb-4">No courses enrolled yet</h2>
            <p className="text-gray-500">Browse our courses and start learning today!</p>
          </div>
        )}
      </section>
    </main>
  )
}

