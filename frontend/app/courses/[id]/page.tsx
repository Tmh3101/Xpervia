"use client";

import { CourseHero } from "@/components/course/CourseHero";
import { Description } from "@/components/Description";
import { LessonCurriculum } from "@/components/lesson/LessonCurriculum";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { useEffect, useState } from "react";
import { Course } from "@/lib/types/course";
import { Loading } from "@/components/Loading";
import { getCourseDetailApi } from "@/lib/api/course-api";
import { getSimilarCoursesApi } from "@/lib/api/course-api";
import { CourseSlider } from "@/components/course/CourseSlider";
import { Chapter } from "@/lib/types/chapter";

export default function CourseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const [courseDetailData, setCourseDetailData] = useState<Course | null>(null);
  const [firstLessonId, setFirstLessonId] = useState<string | null>(null);
  const [similarCourses, setSimilarCourses] = useState<Course[]>([]);

  useEffect(() => {
    const fetchCourseDetail = async () => {
      if (params.id) {
        const courseId = parseInt(params.id + "");
        const courseDetail = await getCourseDetailApi(courseId);
        setCourseDetailData(courseDetail);
        const lessons = courseDetail.course_content.chapters
          .flatMap((chapter: Chapter) => chapter.lessons)
          .concat(courseDetail.course_content.lessons_without_chapter);
        setFirstLessonId(lessons[0]?.id + "" || null);
        // Lấy khóa học tương đồng
        const similar = await getSimilarCoursesApi(courseId);
        setSimilarCourses(similar);
      }
    };

    fetchCourseDetail();
  }, [params.id]);

  if (!courseDetailData) {
    return <Loading />;
  }

  const handleEnrollSuccess = () => {
    if (user?.role === "student") {
      router.push(`/student/lessons/${courseDetailData.id}/${firstLessonId}`);
    }
  };

  const courseConent = courseDetailData.course_content;
  const teacher = courseConent.teacher;

  return (
    <main className="pt-16 min-h-[400px]">
      <CourseHero
        id={courseDetailData.id}
        title={courseConent.title}
        currentPrice={courseDetailData.price * (1 - courseDetailData.discount)}
        originalPrice={courseDetailData.price}
        discount={courseDetailData.discount}
        teacher={teacher.first_name + " " + teacher.last_name}
        bannerImageUrl={courseConent.thumbnail_url}
        categories={courseDetailData.course_content.categories.map(
          (c) => c.name
        )}
        onEnrollSuccess={handleEnrollSuccess}
      />
      <div className="container mx-auto px-4 pt-10">
        {courseConent.chapters.length > 0 ||
        courseConent.lessons_without_chapter.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <Description
                title={"Thông tin khóa học"}
                description={courseConent.description}
              />
            </div>
            <div className="lg:col-span-1">
              <LessonCurriculum
                courseTitle={courseConent.title}
                chapters={courseConent.chapters}
                lessonsWithoutChapter={courseConent.lessons_without_chapter}
                currentLessonId={null}
                status="notEnrolled"
                completedLessonIds={null}
                onLessonSelect={() => {}}
              />
            </div>
          </div>
        ) : (
          <Description
            title={"Thông tin khóa học"}
            description={courseConent.description}
          />
        )}
      </div>

      {/* Khóa học tương đồng */}
      <div className="container mx-auto px-4 pt-4 pb-12">
        <CourseSlider courses={similarCourses} />
      </div>
    </main>
  );
}
