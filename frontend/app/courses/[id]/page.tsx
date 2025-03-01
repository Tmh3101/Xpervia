"use client"

import { CourseHero } from "@/components/course/CourseHero"
import { Badge } from "@/components/ui/badge"
import { Description } from "@/components/Description"
import { LessonCurriculum } from "@/components/lesson/LessonCurriculum"
import { useParams, useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { useEffect, useState } from "react"
import { CourseDetail } from "@/lib/types/course"
import { getCourseDetailApi } from "@/lib/api/course-api"
import { getCategoryColor } from "@/lib/category-color"

export default function CourseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const [courseDetailData, setCourseDetailData] = useState<CourseDetail>()
  const [firstLessonId, setFirstLessonId] = useState(1)

  useEffect(() => {
    const fetchCourseDetail = async () => {
      if (params.id) {
        const courseId = parseInt(params.id[0], 10)
        const courseDetail = await getCourseDetailApi(courseId)
        setCourseDetailData(courseDetail)
        const lessons = courseDetail.course_content.chapters
          .flatMap((chapter) => chapter.lessons)
          .concat(courseDetail.course_content.lessons_without_chapter)
        setFirstLessonId(lessons[0].id)
      }
    }

    fetchCourseDetail()
  }, [params.id, user?.id])

  if (!courseDetailData) {
    return <div>Loading...</div>
  }

  const handleEnrollSuccess = () => {
    if (user?.role === "student") {
      router.push(`/student/lessons/${courseDetailData.id}/${firstLessonId}`)
    }
  }

  const courseConent = courseDetailData.course_content
  const teacher = courseConent.teacher

  return (
    <main className="pt-16">
        <CourseHero
            id={courseDetailData.id}
            title={courseConent.title}
            currentPrice={courseDetailData.price * (1 - courseDetailData.discount)}
            originalPrice={courseDetailData.price}
            discount={courseDetailData.discount}
            teacher={teacher.first_name + " " + teacher.last_name}
            bannerImage={courseConent.thumbnail_id}
            onEnrollSuccess={handleEnrollSuccess}
        />
        <div className="container mx-auto px-4 pt-4 pb-12">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2">
                  <div className="mb-4">
                    {courseConent.categories.map(c => c.name).map((category, index) => (
                      <Badge
                        key={index}
                        variant="secondary"
                        className={`
                          bg-${getCategoryColor(category)} text-xs text-white
                          hover:bg-white hover:text-${getCategoryColor(category)}
                        `}
                      >
                        {category}
                      </Badge>
                    ))}
                  </div>
                  <Description title={'Course About'} description={courseConent.description} />
                </div>
                <div className="lg:col-span-1">
                    <LessonCurriculum
                      courseTitle={courseConent.title}
                      chapters={courseConent.chapters}
                      lessonsWithoutChapter={courseConent.lessons_without_chapter}
                      currentLessonId={null}
                      status="notEnrolled"
                      onLessonSelect={() => {}}
                    />
                </div>
            </div>
        </div>
    </main>
  )
}

