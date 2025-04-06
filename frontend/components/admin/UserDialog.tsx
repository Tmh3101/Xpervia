"use client"

import type React from "react"
import { useState, useEffect } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import type { UserWithPassword, User } from "@/lib/types/user"
import { Trash2 } from "lucide-react"

interface UserDialogProps {
  open: boolean
  onClose: () => void
  onSave: (userData: Partial<UserWithPassword>) => void
  onDelete: (userId: string) => void
  initialData: User | null
  mode: "create" | "edit"
}

export function UserDialog({ open, onClose, onSave, onDelete, initialData, mode }: UserDialogProps) {
  const [userData, setUserData] = useState<Partial<UserWithPassword>>({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    role: "student",
  })
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [isPasswordEditable, setIsPasswordEditable] = useState(mode === "create") // Default to editable in "create" mode

  useEffect(() => {
    if (initialData) {
      setUserData(initialData)
    }
  }, [initialData])

  const handleChange = (field: keyof UserWithPassword, value: string) => {
    setUserData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(userData)
  }

  const handleDeleteClick = () => {
    setConfirmDelete(true)
  }

  const handleConfirmDelete = () => {
    if (initialData?.id) {
      onDelete(initialData.id)
    }
    setConfirmDelete(false)
  }

  const handleCancelDelete = () => {
    setConfirmDelete(false)
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>{mode === "create" ? "Tạo tài khoản mới" : "Chỉnh sửa tài khoản"}</DialogTitle>
            <DialogDescription>
              {mode === "create" ? "Điền thông tin để tạo tài khoản mới." : "Chỉnh sửa thông tin tài khoản người dùng."}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="first_name" className="text-right">
                  Họ
                </Label>
                <Input
                  id="first_name"
                  value={userData.first_name}
                  placeholder="Nhập họ"
                  onChange={(e) => handleChange("first_name", e.target.value)}
                  className="col-span-3"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="last_name" className="text-right">
                  Tên
                </Label>
                <Input
                  id="last_name"
                  value={userData.last_name}
                  placeholder="Nhập tên"
                  onChange={(e) => handleChange("last_name", e.target.value)}
                  className="col-span-3"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="email" className="text-right">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={userData.email}
                  placeholder="Nhập email"
                  onChange={(e) => handleChange("email", e.target.value)}
                  className="col-span-3"
                  required
                />
              </div>
              {mode === "create" && (
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="role" className="text-right">
                    Vai trò
                  </Label>
                  <Select value={userData.role} onValueChange={(value) => handleChange("role", value)}>
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Chọn vai trò" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="student">Học viên</SelectItem>
                      <SelectItem value="teacher">Giảng viên</SelectItem>
                      <SelectItem value="admin">Quản trị viên</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* Password Field with Switch */}
              {mode === "edit" && (
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="password-editable" className="text-right">
                  </Label>
                  <div className="col-span-3 flex items-center space-x-2">
                    <Switch
                      id="password-editable"
                      checked={isPasswordEditable}
                      onCheckedChange={setIsPasswordEditable}
                    />
                    <Label
                      htmlFor="password-editable"
                      className={isPasswordEditable ? "text-black font-medium" : "text-gray-400"}
                    >
                      Cập nhật mật khẩu
                    </Label>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="password" className="text-right">
                  Mật khẩu
                </Label>
                <Input
                  id="password"
                  type="password"
                  value={""}
                  placeholder="Nhập mật khẩu"
                  onChange={(e) => handleChange("password", e.target.value)}
                  className="col-span-3"
                  disabled={!isPasswordEditable}
                  required={mode === "create"}
                />
              </div>
            </div>
            <DialogFooter className="flex justify-between">
              {mode === "edit" && (
                <Button
                  type="button"
                  variant="destructive"
                  onClick={handleDeleteClick}
                  className="mr-auto bg-red-500 hover:bg-red-600"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Xóa
                </Button>
              )}
              <div className="flex gap-2">
                <Button type="button" variant="outline" onClick={onClose}>
                  Hủy
                </Button>
                <Button type="submit">Lưu</Button>
              </div>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={confirmDelete} onOpenChange={setConfirmDelete}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Bạn có chắc chắn muốn xóa?</AlertDialogTitle>
            <AlertDialogDescription>
              Hành động này không thể hoàn tác. Tài khoản này sẽ bị xóa vĩnh viễn khỏi hệ thống.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={handleCancelDelete}>Hủy</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmDelete} className="bg-red-600 hover:bg-red-700">
              Xóa
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}

