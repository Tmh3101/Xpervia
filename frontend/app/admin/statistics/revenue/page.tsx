"use client";

import { Loading } from "@/components/Loading";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BookCopy, HandCoins, CircleDollarSign } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { formatCurrency } from "@/lib/utils";
import { getCoursesApi } from "@/lib/api/course-api";
import { getEnrollmentsApi } from "@/lib/api/enrollment-api";
import type { Course } from "@/lib/types/course";
import type { Enrollment } from "@/lib/types/enrollment";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"];

export default function RevenueStatistics() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [totalCourses, setTotalCourses] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      const { count, results } = await getCoursesApi();
      const enrollmentData = await getEnrollmentsApi();
      setCourses(results);
      setTotalCourses(count);
      setEnrollments(enrollmentData);
    };
    fetchData();
  }, []);

  if (courses.length === 0 || enrollments.length === 0) {
    return <Loading />;
  }

  const totalRevenue = enrollments.reduce((res, enrollment) => {
    if (enrollment.payment) {
      return res + enrollment.payment.amount;
    }
    return res;
  }, 0);
  const averageRevenuePerCourse = totalRevenue / totalCourses;

  // Calculate category data
  let categoryData: { name: string; value: number }[] = [];
  courses.forEach((course) => {
    course.course_content.categories.forEach((category) => {
      const existingCategory = categoryData.find(
        (cat) => cat.name === category.name
      );
      if (existingCategory) {
        existingCategory.value += 1;
      } else {
        categoryData.push({ name: category.name, value: 1 });
      }
    });
  });

  // Calculate monthly & yearly data
  let monthlyData = [
    { name: "T1", courses: 0, revenue: 0 },
    { name: "T2", courses: 0, revenue: 0 },
    { name: "T3", courses: 0, revenue: 0 },
    { name: "T4", courses: 0, revenue: 0 },
    { name: "T5", courses: 0, revenue: 0 },
    { name: "T6", courses: 0, revenue: 0 },
    { name: "T7", courses: 0, revenue: 0 },
    { name: "T8", courses: 0, revenue: 0 },
    { name: "T9", courses: 0, revenue: 0 },
    { name: "T10", courses: 0, revenue: 0 },
    { name: "T11", courses: 0, revenue: 0 },
    { name: "T12", courses: 0, revenue: 0 },
  ];

  let yearlyData = [
    { name: "2020", courses: 0, revenue: 0 },
    { name: "2021", courses: 0, revenue: 0 },
    { name: "2022", courses: 0, revenue: 0 },
    { name: "2023", courses: 0, revenue: 0 },
    { name: "2024", courses: 0, revenue: 0 },
    { name: "2025", courses: 0, revenue: 0 },
  ];
  courses.forEach((course) => {
    const date = new Date(course.created_at);
    if (date.getFullYear() === new Date().getFullYear()) {
      monthlyData[date.getMonth()].courses += 1;
    }
    yearlyData[date.getFullYear() - 2020].courses += 1;
  });
  enrollments.forEach((enrollment) => {
    if (enrollment.payment) {
      const date = new Date(enrollment.payment.created_at);
      if (date.getFullYear() === new Date().getFullYear()) {
        monthlyData[date.getMonth()].revenue += enrollment.payment.amount;
      }
      yearlyData[date.getFullYear() - 2020].revenue +=
        enrollment.payment.amount;
    }
  });

  return (
    <div className="p-6">
      <h1 className="text-3xl uppercase font-bold mb-6">
        Thống kê khóa học & doanh thu
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Tổng khóa học
                </p>
                <h3 className="text-2xl font-bold">{totalCourses}</h3>
              </div>
              <div className="p-2 bg-primary/10 rounded-full">
                <BookCopy className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Tổng doanh thu
                </p>
                <h3 className="text-2xl font-bold">
                  {formatCurrency(totalRevenue)}
                </h3>
              </div>
              <div className="p-2 bg-yellow-100 rounded-full">
                <CircleDollarSign className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Doanh thu trung bình/khóa học
                </p>
                <h3 className="text-2xl font-bold">
                  {formatCurrency(averageRevenuePerCourse)}
                </h3>
              </div>
              <div className="p-2 bg-success/10 rounded-full">
                <HandCoins className="h-6 w-6 text-success" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Phân bố khóa học theo danh mục</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    label={({ name, percent }) =>
                      `${name}: ${(percent * 100).toFixed(0)}%`
                    }
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value}%`} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Khóa học theo tháng (2024)</CardTitle>
          </CardHeader>
          <CardContent className="pl-0">
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={monthlyData}
                  layout="vertical"
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                  width={500}
                  height={300}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    allowDecimals={false}
                    domain={[0, "dataMax"]}
                  />
                  <YAxis dataKey="name" type="category" />
                  <Tooltip />
                  <Bar dataKey="courses" name="Khóa học" fill="#4f46e5" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="monthly">
        <TabsList>
          <TabsTrigger value="monthly">Theo tháng</TabsTrigger>
          <TabsTrigger value="yearly">Theo năm</TabsTrigger>
        </TabsList>

        <TabsContent value="monthly">
          <Card>
            <CardHeader>
              <CardTitle>Doanh thu theo tháng (2024)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={monthlyData}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip
                      formatter={(value) =>
                        formatCurrency(parseFloat(value + ""))
                      }
                    />
                    <Legend />
                    <Bar dataKey="revenue" name="Doanh thu" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="yearly">
          <Card>
            <CardHeader>
              <CardTitle>Doanh thu theo năm</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={yearlyData}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip
                      formatter={(value) =>
                        formatCurrency(parseFloat(value + ""))
                      }
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="revenue"
                      name="Doanh thu"
                      stroke="#10b981"
                      activeDot={{ r: 8 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
