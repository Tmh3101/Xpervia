"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { getUsersApi, createUserApi, updateUserApi, deleteUserApi, disableUserApi, enableUserApi } from "@/lib/api/user-api"
import type { UserWithPassword, User } from "@/lib/types/user"
import { Loading } from "@/components/Loading"
import { UserTable } from "@/components/admin/UserTable"
import { UserDialog } from "@/components/admin/UserDialog"
import { Plus, Search } from "lucide-react"

export default function UsersManagement() {
  const [users, setUsers] = useState<User[]>([])
  const [activeTab, setActiveTab] = useState("students")
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editUser, setEditUser] = useState<User | null>(null)

  useEffect(() => {
    getUsersApi().then((users) => {
      setUsers(users)
    })
  }, [])

  if (users.length === 0) {
    return <Loading />
  }

  const students = users.filter((user) => user.role === "student")
  const teachers = users.filter((user) => user.role === "teacher")
  const admins = users.filter((user) => user.role === "admin")

  const handleToggleDisableUser = (userId: string) => {
    const user = users.find((u) => u.id === userId)
    if (user) {
      if (user.is_active) {
        disableUserApi(userId).then(() => {
          setUsers((prev) => prev.map((u) => (u.id === userId ? { ...u, is_active: false } : u)))
        })
      } else {
        enableUserApi(userId).then(() => {
          setUsers((prev) => prev.map((u) => (u.id === userId ? { ...u, is_active: true } : u)))
        })
      }
    }
  }

  const handleEditUser = (userId: string) => {
    const user = users.find((u) => u.id === userId)
    if (user) {
      setEditUser(user)
      setIsDialogOpen(true)
    }
  }

  const handleCreateUser = () => {
    setEditUser(null)
    setIsDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setIsDialogOpen(false)
    setEditUser(null)
  }

  const handleSaveUser = (userData: Partial<UserWithPassword>) => {    
    if (editUser) {
      // Update existing user
      updateUserApi(editUser.id, userData).then((updatedUser) => {
        setUsers((prev) =>
          prev.map((user) => (user.id === updatedUser.id ? { ...user, ...updatedUser } : user)),
        )
      })
    } else {
      // Create new user
      createUserApi(userData as UserWithPassword).then((newUser) => {
        setUsers((prev) => [...prev, newUser])
      })
    }
    // Close the dialog after saving
    setIsDialogOpen(false)
    setEditUser(null)
  }

  const handleDeleteUser = (userId: string) => {
    deleteUserApi(userId).then(() => {
      setUsers((prev) => prev.filter((user) => user.id !== userId))
    })
    setIsDialogOpen(false)
    setEditUser(null)
  }

  const filterUsersBySearch = (users: User[]) => {
    if (!searchQuery) return users
    return users.filter((user) => user.email.toLowerCase().includes(searchQuery.toLowerCase()))
  }

  const filterUsersByStatus = (users: User[]) => {
    if (statusFilter === "all") return users
    const isActive = statusFilter === "active"
    return users.filter((user) => user.is_active == isActive)
  }

  const getFilteredUsers = (users: User[]) => {
    return filterUsersByStatus(filterUsersBySearch(users))
  }

  return (
    <div className="py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold uppercase">Quản lý tài khoản</h1>
        <Button onClick={handleCreateUser}>
          <Plus className="h-4 w-4 mr-2" />
          Tạo tài khoản
        </Button>
      </div>

      <Tabs defaultValue="students" onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="students">Học viên</TabsTrigger>
          <TabsTrigger value="teachers">Giảng viên</TabsTrigger>
          <TabsTrigger value="admins">Quản trị viên</TabsTrigger>
        </TabsList>

        {["students", "teachers", "admins"].map((tab) => {
          const tabUsers = tab === "students" ? students : tab === "teachers" ? teachers : admins
          return (
            <TabsContent key={tab} value={tab}>
              <Card>
                <CardHeader className="pb-0">
                  <CardTitle className="mb-4">
                    {tab === "students"
                      ? "Danh sách học viên"
                      : tab === "teachers"
                        ? "Danh sách giảng viên"
                        : "Danh sách quản trị viên"}
                  </CardTitle>
                  <div className="flex flex-col sm:flex-row gap-4 mt-4">
                    <div className="relative flex-1">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Tìm kiếm theo email..."
                        className="pl-8"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                      <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Trạng thái" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Tất cả</SelectItem>
                        <SelectItem value="active">Hoạt động</SelectItem>
                        <SelectItem value="disabled">Đã vô hiệu</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardHeader>
                <CardContent>
                  <UserTable users={getFilteredUsers(tabUsers)} onToggleDisable={handleToggleDisableUser} onEdit={handleEditUser} />
                </CardContent>
              </Card>
            </TabsContent>
          )
        })}
      </Tabs>

      <UserDialog
        open={isDialogOpen}
        onClose={handleCloseDialog}
        onSave={handleSaveUser}
        onDelete={handleDeleteUser}
        initialData={editUser}
        mode={editUser ? "edit" : "create"}
      />
    </div>
  )
}

