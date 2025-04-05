"use client"

import type React from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { CalendarIcon } from "lucide-react"
import { Calendar } from "@/components/ui/calendar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { User } from "@/lib/types/user"
import { updateUserApi } from "@/lib/api/user-api"
import { useAuth } from "@/lib/auth-context"
import { format } from "date-fns"
import { cn } from "@/lib/utils"

const profileEditFormSchema = z.object({
  first_name: z.string().nonempty("Tên không được để trống"),
  last_name: z.string().nonempty("Họ không được để trống"),
  email: z.string().email("Email không hợp lệ"),
  date_of_birth: z.string().optional(),
})

interface ProfileEditDialogProps {
  isOpen: boolean
  onClose: () => void
  onUserInforUpdate: (updatedUser: User) => void
}

export function ProfileEditDialog({ isOpen, onClose, onUserInforUpdate }: ProfileEditDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { user, setNewUser } = useAuth()

  const form = useForm({
    resolver: zodResolver(profileEditFormSchema),
    defaultValues: {
      first_name: user?.first_name || "",
      last_name: user?.last_name || "",
      email: user?.email || "",
      date_of_birth: user?.date_of_birth || "",
    },
  })

  // Update form values when user changes
  useEffect(() => {
    if (user) {
      form.reset({
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email,
        date_of_birth: user.date_of_birth,
      })
    }
  }, [user, form])

  const handlePersonalInfoSubmit = async (data: any) => {
    if (!user) return

    setIsSubmitting(true)
    try {
      const newUser = await updateUserApi(user.id, data)
      if (newUser) {
        onUserInforUpdate(newUser)
        setNewUser(newUser)
        onClose()
        form.reset()
      }
    } catch (error) {
      console.error("Lỗi khi gửi biểu mẫu:", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Chỉnh sửa hồ sơ</DialogTitle>
        </DialogHeader>
          <form onSubmit={form.handleSubmit(handlePersonalInfoSubmit)} className="space-y-4">
            {form.formState.errors && Object.values(form.formState.errors).length > 0 && (
              <div className="text-red-500 text-center italic text-sm">
                {Object.values(form.formState.errors)[0]?.message as string}
              </div>
            )}

            <div className="space-y-1">
              <Label htmlFor="first_name">Tên</Label>
              <Controller
                name="first_name"
                control={form.control}
                render={({ field }: any) => <Input id="first_name" placeholder="Nhập tên" {...field} />}
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="last_name">Họ</Label>
              <Controller
                name="last_name"
                control={form.control}
                render={({ field }: any) => <Input id="last_name" placeholder="Nhập họ" {...field} />}
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="email">Email</Label>
              <Controller
                name="email"
                control={form.control}
                render={({ field }: any) => <Input id="email" placeholder="Nhập email" {...field} />}
              />
            </div>

            <div className="space-y-2">
              <Label>Ngày sinh</Label>
              <Controller
                name="date_of_birth"
                control={form.control}
                render={({ field }: any) => (
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        id="date_of_birth"
                        variant="outline"
                        className={cn(
                          "w-full justify-start text-left font-normal",
                          !field.value && "text-muted-foreground"
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {field.value ? format(new Date(field.value), "dd/MM/yyyy") : "Chọn ngày"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={field.value ? new Date(field.value) : undefined}
                      onSelect={(date) => field.onChange(date ? date.toISOString().split("T")[0] : "")} // Cập nhật giá trị vào form
                      initialFocus
                    />
                    </PopoverContent>
                  </Popover>
                )}
              />
            </div>

            <DialogFooter className="pt-4">
              <Button type="button" variant="outline" onClick={() => onClose()}>
                Hủy
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                    Đang cập nhật...
                  </>
                ) : (
                  "Lưu"
                )}
              </Button>
            </DialogFooter>
          </form>
      </DialogContent>
    </Dialog>
  )
}

