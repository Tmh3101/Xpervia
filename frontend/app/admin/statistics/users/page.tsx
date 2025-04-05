"use client"

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
import { Loading } from "@/components/Loading"
import { getUsersApi } from "@/lib/api/user-api"
import type { User } from "@/lib/types/user"

export default function UserStatistics() {
  const [users, setUsers] = useState<User[]>([])

  useEffect(() => {
    getUsersApi().then((data) => setUsers(data))
  }, [])

  if (!users) {
    return <Loading />
  }

  const totalUsers = users.filter((user) => user.role !== "admin").length
  const totalStudents = users.filter((user) => user.role === "student").length
  const totalTeachers = users.filter((user) => user.role === "teacher").length

  // Mock data for charts
  const monthlyData = [
    { name: "Jan", users: 0 },
    { name: "Feb", users: 0 },
    { name: "Mar", users: 0 },
    { name: "Apr", users: 0 },
    { name: "May", users: 0 },
    { name: "Jun", users: 0 },
    { name: "Jul", users: 0 },
    { name: "Aug", users: 0 },
    { name: "Sep", users: 0 },
    { name: "Oct", users: 0 },
    { name: "Nov", users: 0 },
    { name: "Dec", users: 0 },
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
    <div>
      <h1 className="text-2xl font-bold mb-6">Thống kê người dùng</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardContent className="pt-6">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Tổng người dùng</p>
              <h3 className="text-3xl font-bold">{totalUsers}</h3>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Học viên</p>
              <h3 className="text-3xl font-bold">{totalStudents}</h3>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Giảng viên</p>
              <h3 className="text-3xl font-bold">{totalTeachers}</h3>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="monthly">
        <TabsList className="mb-6">
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

