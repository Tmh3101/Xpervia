"use client";

import { useEffect, useState } from "react";
import { Loading } from "@/components/Loading";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, BookOpen, UserRoundPen, UserCheck } from "lucide-react";
import Image from "next/image";
import { getUsersApi } from "@/lib/api/user-api";
import { getCoursesByAdminApi } from "@/lib/api/course-api";
import type { User } from "@/lib/types/user";
import type { Course } from "@/lib/types/course";
import userAvatar from "@/public/user-avatar.svg";

export default function AdminDashboard() {
  const [users, setUsers] = useState<User[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [totalCourses, setTotalCourses] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      const users = await getUsersApi();
      setUsers(users);
      const response = await getCoursesByAdminApi();
      setCourses(response.results);
      setTotalCourses(response.count);
    };
    fetchData();
  }, []);

  if (users.length === 0 || courses.length === 0) {
    return <Loading />;
  }

  const totalUsers = users.filter((user) => user.role !== "admin").length;
  const totalStudents = users.filter((user) => user.role === "student").length;
  const totalTeachers = users.filter((user) => user.role === "teacher").length;

  const getRecentUsers = (days: number) => {
    const now = new Date();
    return users.filter((user) => {
      const joinedDate = new Date(user.created_at);
      const diffTime = now.getTime() - joinedDate.getTime();
      const diffDays = diffTime / (1000 * 3600 * 24); // Chuyển đổi ms -> ngày
      return user.role != "admin" && diffDays <= days;
    });
  };

  const getRecentCourses = (days: number) => {
    const now = new Date();
    return courses.filter((course) => {
      const createdDate = new Date(course.created_at);
      const diffTime = now.getTime() - createdDate.getTime();
      const diffDays = diffTime / (1000 * 3600 * 24); // Chuyển đổi ms -> ngày
      return diffDays <= days;
    });
  };

  const recentUsers = getRecentUsers(7);
  const recentCourses = getRecentCourses(7);

  const getNumLessons = (course: Course) => {
    return course.course_content?.num_lessons || 0;
  };

  const truncateDescription = (description: string) => {
    const chars = description.split("");
    if (chars.length > 40) {
      return chars.slice(0, 40).join("") + "...";
    }
    return description;
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Tổng người dùng
                </p>
                <h3 className="text-2xl font-bold">{totalUsers}</h3>
              </div>
              <div className="p-2 bg-primary/10 rounded-full">
                <Users className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Học viên
                </p>
                <h3 className="text-2xl font-bold">{totalStudents}</h3>
              </div>
              <div className="p-2 bg-blue-100 rounded-full">
                <UserCheck className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Giảng viên
                </p>
                <h3 className="text-2xl font-bold">{totalTeachers}</h3>
              </div>
              <div className="p-2 bg-blue-100 rounded-full">
                <UserRoundPen className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Khóa học
                </p>
                <h3 className="text-2xl font-bold">{totalCourses}</h3>
              </div>
              <div className="p-2 bg-green-100 rounded-full">
                <BookOpen className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Người dùng mới gần đây</CardTitle>
          </CardHeader>
          <CardContent>
            {recentUsers.length === 0 ? (
              <p className="text-muted-foreground">
                Không có người dùng đăng ký trong 7 ngày gần nhất
              </p>
            ) : (
              <div className="space-y-3">
                {recentUsers.map((user) => (
                  <div
                    key={user.id}
                    className="flex items-center space-x-3 border-b pb-2 last:border-b-0"
                  >
                    <Image
                      src={userAvatar}
                      alt={`${user.first_name} ${user.last_name}`}
                      className="object-cover w-8 h-8"
                    />
                    <div>
                      <p className="font-medium">
                        {user.first_name} {user.last_name}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {user.email}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Khóa học mới gần đây</CardTitle>
          </CardHeader>
          <CardContent>
            {recentCourses.length === 0 ? (
              <p className="text-muted-foreground">
                Không có khóa học nào được tạo trong 7 ngày gần nhất
              </p>
            ) : (
              <div className="space-y-3">
                {recentCourses.map((course) => (
                  <div
                    key={course.id}
                    className="flex items-center space-x-3 border-b pb-2 last:border-b-0"
                  >
                    {/* Thumbnail */}
                    <div className="w-12 h-12 relative rounded-md overflow-hidden bg-gray-200">
                      <Image
                        src={course.course_content.thumbnail_url}
                        alt={course.course_content.title}
                        layout="fill"
                        objectFit="cover"
                      />
                    </div>

                    {/* Course Info */}
                    <div className="flex-1">
                      <p className="font-medium">
                        {course.course_content.title}
                      </p>
                      <p className="text-sm text-muted-foreground truncate">
                        {truncateDescription(course.course_content.description)}
                      </p>
                    </div>

                    {/* Lesson Count */}
                    <div className="text-sm text-muted-foreground">
                      {getNumLessons(course)} bài học
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
