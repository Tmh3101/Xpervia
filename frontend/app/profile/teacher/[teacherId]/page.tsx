"use client";

import { Loading } from "@/components/Loading";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Image from "next/image";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { UserProfile } from "@/components/profile/UserProfile";
import { ProfileEditDialog } from "@/components/profile/ProfileEditDialog";
import { ChangePasswordDialog } from "@/components/profile/ChangePasswordDialog";
import { getCourseByTeacherApi } from "@/lib/api/course-api";
import type { User } from "@/lib/types/user";
import type { Course } from "@/lib/types/course";
import { useAuth } from "@/lib/auth-context";
import { BookOpen, Users } from "lucide-react";

export default function TeacherProfilePage() {
  const { teacherId } = useParams();
  const { user: currentUser } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showChangePasswordDialog, setShowChangePasswordDialog] =
    useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setUser(currentUser);
        await getCourseByTeacherApi().then((data) => setCourses(data));
      } catch (error) {
        console.error("Failed to fetch user data:", error);
      }
    };

    fetchData();
  }, [teacherId]);

  if (!user) {
    return <Loading />;
  }

  // Calculate statistics
  const totalCourses = courses.length;
  const totalStudents = courses.reduce(
    (acc, course) => acc + (course.num_students || 0),
    0
  );

  return (
    <div className="container mx-auto py-20 pt-[120px] min-h-[500px]">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Left Column - Personal Information */}
        <div className="md:col-span-1">
          <UserProfile
            user={user}
            handleShowEditDialog={() => setShowEditDialog(true)}
            handleShowChangePasswordDialog={() =>
              setShowChangePasswordDialog(true)
            }
          />
        </div>

        {/* Right Column - Teaching Activity */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Hoạt động giảng dạy</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">
                          Tổng khóa học
                        </p>
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
                        <p className="text-sm font-medium text-muted-foreground">
                          Tổng học viên
                        </p>
                        <p className="text-2xl font-bold">{totalStudents}</p>
                      </div>
                      <Users className="h-8 w-8 text-blue-500" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Tabs defaultValue="all">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="all">Tất cả khóa học</TabsTrigger>
                  <TabsTrigger value="active">Khóa học đang ẩn</TabsTrigger>
                </TabsList>

                <TabsContent value="all" className="space-y-4 mt-4">
                  {courses.length > 0 ? (
                    courses.map((course) => (
                      <Card key={course.id}>
                        <CardContent className="p-4">
                          <div className="flex justify-between items-center">
                            <div>
                              <h3 className="font-medium">
                                {course.course_content.title}
                              </h3>
                              <p className="text-sm text-muted-foreground">
                                {course.num_students || 0} học viên đã đăng ký
                              </p>
                            </div>
                            <div className="w-16 h-16 relative">
                              <Image
                                src={
                                  course.course_content.thumbnail_url ||
                                  "/placeholder.svg?height=64&width=64"
                                }
                                alt={course.course_content.title}
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
                    <p className="text-center py-4 text-muted-foreground">
                      Chưa có khóa học nào.
                    </p>
                  )}
                </TabsContent>

                <TabsContent value="active" className="space-y-4 mt-4">
                  {courses.filter((c) => !c.is_visible).length > 0 ? (
                    courses
                      .filter((c) => !c.is_visible)
                      .map((course) => (
                        <Card key={course.id}>
                          <CardContent className="p-4">
                            <div className="flex justify-between items-center">
                              <div>
                                <h3 className="font-medium">
                                  {course.course_content.title}
                                </h3>
                                <p className="text-sm text-muted-foreground">
                                  {course.num_students || 0} học viên đã đăng ký
                                </p>
                              </div>
                              <div className="w-16 h-16 relative">
                                <Image
                                  src={
                                    course.course_content.thumbnail_url ||
                                    "/placeholder.svg?height=64&width=64"
                                  }
                                  alt={course.course_content.title}
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
                    <p className="text-center py-4 text-muted-foreground">
                      Không có khóa học đang hoạt động.
                    </p>
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
  );
}
