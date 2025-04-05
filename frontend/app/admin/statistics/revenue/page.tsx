"use client"

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
  PieChart,
  Pie,
  Cell,
} from "recharts"
import { formatCurrency } from "@/lib/utils"

// Mock data for charts
const monthlyData = [
  { name: "Jan", courses: 2, revenue: 1200 },
  { name: "Feb", courses: 3, revenue: 1800 },
  { name: "Mar", courses: 1, revenue: 900 },
  { name: "Apr", courses: 4, revenue: 2400 },
  { name: "May", courses: 2, revenue: 1500 },
  { name: "Jun", courses: 3, revenue: 2100 },
  { name: "Jul", courses: 5, revenue: 3000 },
  { name: "Aug", courses: 2, revenue: 1700 },
  { name: "Sep", courses: 4, revenue: 2800 },
  { name: "Oct", courses: 3, revenue: 2200 },
  { name: "Nov", courses: 6, revenue: 4000 },
  { name: "Dec", courses: 5, revenue: 3500 },
]

const yearlyData = [
  { name: "2020", courses: 15, revenue: 12000 },
  { name: "2021", courses: 25, revenue: 20000 },
  { name: "2022", courses: 35, revenue: 30000 },
  { name: "2023", courses: 45, revenue: 45000 },
  { name: "2024", courses: 30, revenue: 35000 },
]

const categoryData = [
  { name: "Programming", value: 40 },
  { name: "Design", value: 25 },
  { name: "Business", value: 15 },
  { name: "Marketing", value: 10 },
  { name: "Other", value: 10 },
]

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"]

export default function RevenueStatistics() {
  const totalCourses = 45
  const totalRevenue = 120000
  const averageRevenuePerCourse = totalRevenue / totalCourses

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Thống kê khóa học & doanh thu</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardContent className="pt-6">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Tổng khóa học</p>
              <h3 className="text-3xl font-bold">{totalCourses}</h3>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Tổng doanh thu</p>
              <h3 className="text-3xl font-bold">{formatCurrency(totalRevenue)}</h3>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Doanh thu trung bình/khóa học</p>
              <h3 className="text-3xl font-bold">{formatCurrency(averageRevenuePerCourse)}</h3>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card className="lg:col-span-2">
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
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
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
                  <XAxis type="number" />
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
        <TabsList className="mb-6">
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
                  <BarChart data={monthlyData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
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
                  <LineChart data={yearlyData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Legend />
                    <Line type="monotone" dataKey="revenue" name="Doanh thu" stroke="#10b981" activeDot={{ r: 8 }} />
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

