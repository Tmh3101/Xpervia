"use client"

import { Loading } from "@/components/Loading"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
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
} from "recharts"
import { getUsersApi } from "@/lib/api/user-api"
import { Users, BookUser, UserPen, UserCog } from "lucide-react"
import type { User } from "@/lib/types/user"

export default function UserStatistics() {
  const [users, setUsers] = useState<User[]>([])

  useEffect(() => {
    getUsersApi().then((data) => setUsers(data))
  }, [])

  if (!users) {
    return <Loading />
  }

  const totalUsers = users.length
  const totalStudents = users.filter((user) => user.role === "student").length
  const totalTeachers = users.filter((user) => user.role === "teacher").length
  const totalAdmins = users.filter((user) => user.role === "admin").length

  // Mock data for charts
  const monthlyData = [
    { name: "T1", users: 0 },
    { name: "T2", users: 0 },
    { name: "T3", users: 0 },
    { name: "T4", users: 0 },
    { name: "T5", users: 0 },
    { name: "T6", users: 0 },
    { name: "T7", users: 0 },
    { name: "T8", users: 0 },
    { name: "T9", users: 0 },
    { name: "T10", users: 0 },
    { name: "T11", users: 0 },
    { name: "T12", users: 0 },
  ]

  const yearlyData = [
    { name: 2023, users: 0 },
    { name: 2024, users: 0 },
    { name: 2025, users: 0 },
  ]

  users.forEach((user) => {
    const date = new Date(user.date_joined)
    const month = date.getMonth()
    const year = date.getFullYear()
    monthlyData[month].users++
    yearlyData[year - 2023].users++
  })

  return (
    <div className="p-6">
      <h1 className="text-3xl uppercase font-bold mb-6">Thống kê người dùng</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Tổng số người dùng</p>
                <h3 className="text-2xl font-bold">{totalUsers}</h3>
              </div>
              <div className="p-2 bg-yellow-100 rounded-full">
                <Users className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Tổng số học viên</p>
                <h3 className="text-2xl font-bold">{totalStudents}</h3>
              </div>
              <div className="p-2 bg-primary/10 rounded-full">
                <BookUser className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Tổng số giảng viên</p>
                <h3 className="text-2xl font-bold">{totalTeachers}</h3>
              </div>
              <div className="p-2 bg-success/10 rounded-full">
                <UserPen className="h-6 w-6 text-success" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Tổng số quản trị viên</p>
                <h3 className="text-2xl font-bold">{totalAdmins}</h3>
              </div>
              <div className="p-2 bg-gray-100 rounded-full">
                <UserCog className="h-6 w-6 text-gray-600" />
              </div>
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
              <CardTitle>Đăng ký người dùng theo tháng (2024)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis 
                      tickFormatter={(value) => Math.floor(value)} // Làm tròn về số nguyên
                      domain={[0, 'dataMax']} // Đảm bảo hiển thị đúng khoảng dữ liệu
                      allowDecimals={false} // Chặn số lẻ
                    />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="users" name="Học viên" fill="#4f46e5" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="yearly">
          <Card>
            <CardHeader>
              <CardTitle>Đăng ký người dùng theo năm</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={yearlyData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="users" name="Học viên" stroke="#4f46e5" activeDot={{ r: 8 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

