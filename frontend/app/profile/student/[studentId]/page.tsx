"use client"

import { Loading } from "@/components/Loading"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import Image from "next/image"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ProfileEditDialog } from "@/components/profile/ProfileEditDialog"
import { ChangePasswordDialog } from "@/components/profile/ChangePasswordDialog"
import type { User } from "@/lib/types/user"
import type { Enrollment } from "@/lib/types/enrollment"
import type { Course } from "@/lib/types/course"
import { useAuth } from "@/lib/auth-context"
import { BookOpen, GraduationCap, Clock } from "lucide-react"
import { getCoursesApi } from '@/lib/api/course-api'
import { Progress } from "@/components/course/Progress"
import { getGoogleDriveImageUrl } from "@/lib/google-drive-url"
import { UserProfile } from "@/components/profile/UserProfile"

export default function StudentProfilePage() {
  const { studentId } = useParams()
  const { user: currentUser, enrollments: currentEnrollments } = useAuth()
  const [user, setUser] = useState<User | null>(null)
  const [enrollments, setEnrollments] = useState<Enrollment[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [showChangePasswordDialog, setShowChangePasswordDialog] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setUser(currentUser)
        setEnrollments(currentEnrollments)
        getCoursesApi().then((data) => setCourses(data))
      } catch (error) {
        console.error("Failed to fetch user data:", error)
      }
    }

    fetchData()
  }, [studentId])

  if (!user) {
    return <Loading />
  }

  const getCourseById = (courseId: number) => {
    return courses.find((c) => c.id === courseId)
  }

  // Calculate statistics
  const totalCourses = enrollments.length
  const ongoingCourses = enrollments.filter((e) => e.progress < 100).length
  const completedCourses = enrollments.filter((e) => e.progress === 100).length

  return (
    <div className="container mx-auto py-20 pt-[120px] min-h-[500px]">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Left Column - Personal Information */}
        <div className="md:col-span-1">
          <UserProfile
            user={user}
            handleShowEditDialog={() => setShowEditDialog(true)}
            handleShowChangePasswordDialog={() => setShowChangePasswordDialog(true)}
          />
        </div>

        {/* Right Column - Learning Progress */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Tiến độ học tập</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Tổng khóa học</p>
                        <p className="text-2xl font-bold">{totalCourses}</p>
                      </div>
                      <BookOpen className="h-8 w-8 text-primary" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Đang học</p>
                        <p className="text-2xl font-bold">{ongoingCourses}</p>
                      </div>
                      <Clock className="h-8 w-8 text-yellow-500" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Đã hoàn thành</p>
                        <p className="text-2xl font-bold">{completedCourses}</p>
                      </div>
                      <GraduationCap className="h-8 w-8 text-green-500" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Tabs defaultValue="enrolled">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="enrolled">Khóa học đã tham gia</TabsTrigger>
                  <TabsTrigger value="completed">Khóa học đã hoàn thành</TabsTrigger>
                </TabsList>

                <TabsContent value="enrolled" className="space-y-4 mt-4">
                  {enrollments.length > 0 ? (
                    enrollments.map((enrollment) => (
                      <Card key={enrollment.id}>
                        <CardContent className="p-4 pb-2">
                          <div className="flex justify-between items-center">
                            <div>
                              <h3 className="font-bold">{enrollment.course.course_content.title}</h3>
                              <div className="flex items-center space-x-2 mt-2">
                                <p className="text-sm text-muted-foreground">Tiến độ:</p>
                                <Progress progress={enrollment.progress} />
                              </div>
                            </div>
                            <div className="w-16 h-16 relative">
                              <Image
                                src={
                                  getGoogleDriveImageUrl(
                                    getCourseById(enrollment.course.id)?.course_content.thumbnail_id || ""
                                  )}
                                alt={enrollment.course.course_content.title}
                                width={64}
                                height={64}
                                className="rounded-md object-cover"
                              />
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    <p className="text-center py-4 text-muted-foreground">Chưa đăng ký khóa học nào.</p>
                  )}
                </TabsContent>

                <TabsContent value="completed" className="space-y-4 mt-4">
                  {enrollments.filter((e) => e.progress === 100).length > 0 ? (
                    enrollments
                      .filter((e) => e.progress === 100)
                      .map((enrollment) => (
                        <Card key={enrollment.id}>
                          <CardContent className="p-4">
                            <div className="flex justify-between items-center">
                              <div>
                                <h3 className="font-medium">{enrollment.course.course_content.title}</h3>
                                <p className="text-sm text-muted-foreground">Hoàn thành: 100%</p>
                              </div>
                              {/* <div className="w-16 h-16 relative">
                                <Image
                                  src={enrollment.course.thumbnail || "/placeholder.svg?height=64&width=64"}
                                  alt={enrollment.course.title}
                                  width={64}
                                  height={64}
                                  className="rounded-md object-cover"
                                />
                              </div> */}
                            </div>
                          </CardContent>
                        </Card>
                      ))
                  ) : (
                    <p className="text-center py-4 text-muted-foreground">Chưa hoàn thành khóa học nào.</p>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>

      {showEditDialog && user && (
        <ProfileEditDialog
          isOpen={showEditDialog}
          onClose={() => setShowEditDialog(false)}
          onUserInforUpdate={(updatedUser) => setUser(updatedUser)}
        />
      )}

      {showChangePasswordDialog && (
        <ChangePasswordDialog
          isOpen={showChangePasswordDialog}
          onClose={() => setShowChangePasswordDialog(false)}
        />
      )}
    </div>
  )
}

