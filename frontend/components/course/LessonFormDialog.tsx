"use client"

import { useState } from "react"
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

const lessonFormSchema = z.object({
  title: z.string().min(3, "Tiêu đề phải có ít nhất 3 ký tự"),
  content: z.string().min(20, "Nội dung phải có ít nhất 20 ký tự"),
  video: z.instanceof(File).refine((file) => file !== null, { 
    message: "Video là bắt buộc, vui lòng tải lên một tệp."
  }),
  subtitle_vi: z.instanceof(File).nullable().optional(),
  attachment: z.instanceof(File).nullable().optional(),
  is_visible: z.boolean().default(true),
  order: z.number().default(0),
})

type LessonFormProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: any) => void
  chapterTitle?: string | null
  mode: "create" | "edit"
  initialData?: Partial<LessonDetail>
}

export const LessonFormDialog = ({
  open,
  onOpenChange,
  onSubmit,
  chapterTitle,
  mode,
  initialData,
}: LessonFormProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm({
    resolver: zodResolver(lessonFormSchema),
    defaultValues:
      mode === "edit" && initialData
        ? {
            title: initialData.title,
            content: initialData.content,
            video: null,
            subtitle_vi: null,
            attachment: null,
            is_visible: initialData.is_visible !== null ? initialData.is_visible : true,
            order: initialData.order || 0,
          }
        : {
            title: "",
            content: "",
            video: null,
            subtitle_vi: null,
            attachment: null,
            is_visible: true,
            order: 0,
          },
  })

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

  return (
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
              {Object.values(form.formState.errors)[0]?.message}
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
            <Label htmlFor="video">Upload Video</Label>
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
            <Label htmlFor="subtitle_vi">Upload File Phụ đề</Label>
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
            <Label htmlFor="attachment">Tệp đính kèm</Label>
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
  )
}

