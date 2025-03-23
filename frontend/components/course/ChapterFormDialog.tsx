"use client"

import { useState, useEffect } from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import type { CreateChapterRequest } from "@/lib/types/chapter"
import { Trash2 } from "lucide-react"
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

const chapterFormSchema = z.object({
  title: z.string().min(3, "Tiêu đề phải có ít nhất 3 ký tự"),
})

type ChapterFormProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: CreateChapterRequest) => void
  onDelete?: () => void
  mode: "create" | "edit"
  initialData?: { id?: number; title?: string } | null
}

export const ChapterFormDialog = ({ open, onOpenChange, onSubmit, onDelete, mode, initialData }: ChapterFormProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)

  const form = useForm({
    resolver: zodResolver(chapterFormSchema),
    defaultValues: {
      title: initialData?.title || "",
    },
  })

  // Update form values when initialData changes
  useEffect(() => {
    if (initialData && initialData.title) {
      form.reset({
        title: initialData.title,
      })
    }
  }, [initialData, form])

  const handleSubmit = async (data: CreateChapterRequest) => {
    setIsSubmitting(true)
    try {
      await onSubmit(data)
      form.reset()
    } catch (error) {
      console.error("Lỗi khi gửi biểu mẫu:", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = () => {
    setIsDeleteDialogOpen(false)
    if (onDelete) {
      onDelete()
    }
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>{mode === "create" ? "Tạo chương mới" : "Chỉnh sửa chương"}</DialogTitle>
          </DialogHeader>

          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            {form.formState.errors && Object.values(form.formState.errors).length > 0 && (
              <div className="text-red-500 text-center italic text-sm">
                {Object.values(form.formState.errors)[0]?.message as string}
              </div>
            )}

            <div className="space-y-1">
              <Label htmlFor="title">Tiêu đề chương</Label>
              <Controller
                name="title"
                control={form.control}
                render={({ field }: any) => <Input id="title" placeholder="Nhập tiêu đề chương" {...field} />}
              />
            </div>

            <DialogFooter className="pt-4">
              {mode === "edit" && onDelete && (
                <Button
                  type="button"
                  variant="destructive"
                  onClick={() => setIsDeleteDialogOpen(true)}
                  className="mr-auto bg-red-500 hover:bg-red-600"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Xóa
                </Button>
              )}
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Hủy
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                    {mode === "create" ? "Đang tạo..." : "Đang cập nhật..."}
                  </>
                ) : mode === "create" ? (
                  "Tạo chương"
                ) : (
                  "Cập nhật chương"
                )}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Bạn có chắc chắn muốn xóa?</AlertDialogTitle>
            <AlertDialogDescription>
              Hành động này không thể hoàn tác. Điều này sẽ xóa vĩnh viễn chương này và tất cả các bài học trong đó.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Hủy</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-red-500 hover:bg-red-600">
              Xóa
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}

