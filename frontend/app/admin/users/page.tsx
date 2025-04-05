"use client"

import { useState, useEffect, use } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { getUsersApi } from "@/lib/api/user-api"
import type { User } from "@/lib/types/user"
import { Loading } from "@/components/Loading"
import { UserTable } from "@/components/admin/UserTable"

export default function UsersManagement() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState("students")

  useEffect(() => {
    setLoading(true)
    getUsersApi()
      .then((users) => {
        setUsers(users)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <Loading />
  }

  const students = users.filter((user) => user.role === "student")
  const teachers = users.filter((user) => user.role === "teacher")

  const handleDisableUser = (userId: string) => {
    console.log(`Disable user with ID: ${userId}`)
  }

  const handleEditUser = (userId: string) => {
    console.log(`Edit user with ID: ${userId}`)
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Quản lý tài khoản</h1>

      <Tabs defaultValue="students" onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="students">Học viên</TabsTrigger>
          <TabsTrigger value="teachers">Giảng viên</TabsTrigger>
        </TabsList>

        <TabsContent value="students">
          <Card>
            <CardHeader>
              <CardTitle>Danh sách học viên</CardTitle>
            </CardHeader>
            <CardContent>
              <UserTable users={students} onDisable={handleDisableUser} onEdit={handleEditUser} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="teachers">
          <Card>
            <CardHeader>
              <CardTitle>Danh sách giảng viên</CardTitle>
            </CardHeader>
            <CardContent>
              <UserTable users={teachers} onDisable={handleDisableUser} onEdit={handleEditUser} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

