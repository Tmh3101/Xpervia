"use client"

import { useState, useEffect } from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import type { LessonDetail } from "@/lib/types/lesson"
import { Trash2 } from "lucide-react"
import { FileText } from "lucide-react"
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

const lessonFormSchema = z.object({
  title: z.string().min(3, "Tiêu đề phải có ít nhất 3 ký tự"),
  content: z.string().min(20, "Nội dung phải có ít nhất 20 ký tự"),
  video: z.any().optional(),
  subtitle_vi: z.any().optional(),
  attachment: z.any().optional(),
  is_visible: z.boolean().default(true),
  order: z.number().default(0),
})

type LessonFormProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: any) => void
  onDelete?: () => void
  chapterTitle?: string | null
  mode: "create" | "edit"
  initialData?: Partial<LessonDetail>
}

export const LessonFormDialog = ({
  open,
  onOpenChange,
  onSubmit,
  onDelete,
  chapterTitle,
  mode,
  initialData,
}: LessonFormProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)

  const form = useForm({
    resolver: zodResolver(lessonFormSchema),
    defaultValues: {
      title: "",
      content: "",
      video: null,
      subtitle_vi: null,
      attachment: null,
      is_visible: true,
      order: 0,
    },
  })

  // Update form values when initialData changes
  useEffect(() => {
    if (initialData) {
      form.reset({
        title: initialData.title || "",
        content: initialData.content || "",
        video: null, // Can't pre-fill file inputs
        subtitle_vi: null,
        attachment: null,
        is_visible: initialData.is_visible !== undefined ? initialData.is_visible : true,
        order: initialData.order || 0,
      })
    }
  }, [initialData, form])

  const handleSubmit = async (data: any) => {
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
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>
              {mode === "create"
                ? chapterTitle
                  ? `Thêm bài học vào chương: ${chapterTitle}`
                  : "Tạo bài học mới"
                : "Chỉnh sửa bài học"}
            </DialogTitle>
          </DialogHeader>

          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            {form.formState.errors && Object.values(form.formState.errors).length > 0 && (
              <div className="text-red-500 text-center italic text-sm">
                {Object.values(form.formState.errors)[0]?.message as string}
              </div>
            )}

            <div className="space-y-1">
              <Label htmlFor="title">Tiêu đề bài học</Label>
              <Controller
                name="title"
                control={form.control}
                render={({ field }: any) => <Input id="title" placeholder="Nhập tiêu đề bài học" {...field} />}
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="content">Nội dung bài học</Label>
              <Controller
                name="content"
                control={form.control}
                render={({ field }: any) => (
                  <Textarea id="content" placeholder="Nhập nội dung bài học" className="min-h-[100px]" {...field} />
                )}
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="video">Upload Video {mode === "edit" && "(Để trống nếu không muốn thay đổi)"}</Label>
              <Controller
                name="video"
                control={form.control}
                render={({ field: { onChange } }: any) => (
                  <Input
                    id="video"
                    type="file"
                    accept="video/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) {
                        onChange(file)
                      }
                    }}
                  />
                )}
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="subtitle_vi">
                Upload File Phụ đề {mode === "edit" && "(Để trống nếu không muốn thay đổi)"}
              </Label>
              <Controller
                name="subtitle_vi"
                control={form.control}
                render={({ field: { onChange } }: any) => (
                  <Input
                    id="subtitle_vi"
                    type="file"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) {
                        onChange(file)
                      }
                    }}
                  />
                )}
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="attachment">Tệp đính kèm {mode === "edit" && "(Để trống nếu không muốn thay đổi)"}</Label>
              <div className="flex items-center space-x-2">
                {initialData?.attachment && (
                  <div className="relative max-w-[160px] flex items-center space-x-2 bg-primary text-white border rounded-md p-2">
                    <FileText className="w-4 h-4" />
                    <p className="text-sm font-medium truncate w-24">{initialData?.attachment.file_name}</p>
                  </div>
                )}
                <Controller
                  name="attachment"
                  control={form.control}
                  render={({ field: { onChange } }: any) => (
                    <Input
                      id="attachment"
                      type="file"
                      onChange={(e) => {
                        const file = e.target.files?.[0]
                        if (file) {
                          onChange(file)
                        }
                      }}
                    />
                  )}
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Controller
                name="is_visible"
                control={form.control}
                render={({ field }: any) => (
                  <Checkbox id="is_visible" checked={field.value} onCheckedChange={field.onChange} />
                )}
              />
              <Label htmlFor="is_visible">Hiển thị bài học cho học viên</Label>
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
                  "Tạo bài học"
                ) : (
                  "Cập nhật bài học"
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
              Hành động này không thể hoàn tác. Điều này sẽ xóa vĩnh viễn bài học này và tất cả dữ liệu liên quan.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Hủy</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground">
              Xóa
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}

