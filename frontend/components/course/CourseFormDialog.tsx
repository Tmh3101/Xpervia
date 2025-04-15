"use client"

import { useState, useEffect } from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import Select from "react-select"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { getCategoriesApi } from "@/lib/api/course-api"
import type { CreateCourseRequest } from "@/lib/types/course"
import { Label } from "@/components/ui/label"
import { Trash2 } from "lucide-react"
import Image from "next/image"
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
import { formatDate } from "@/lib/utils"
import { getGoogleDriveImageUrl } from "@/lib/google-drive-url"

const courseFormSchema = z.object({
  thumbnail: z.instanceof(File).refine((file) => file instanceof File, {
    message: "Ảnh bìa là bắt buộc",
  }).nullable(),
  title: z.string().min(3, "Tiêu đề phải có ít nhất 3 ký tự"),
  description: z.string().min(20, "Mô tả phải có ít nhất 20 ký tự"),
  price: z.number().min(0, "Giá phải là số dương"),
  start_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, "Định dạng ngày không hợp lệ (YYYY-MM-DD)")
    .nullable(),
  regis_start_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, "Định dạng ngày không hợp lệ (YYYY-MM-DD)")
    .nullable(),
  regis_end_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, "Định dạng ngày không hợp lệ (YYYY-MM-DD)")
    .nullable(),
  max_students: z.number().min(1, "Số lượng học viên tối đa phải ít nhất là 1"),
  is_visible: z.boolean().default(true),
  categories: z.array(z.number()).min(1, "Phải chọn ít nhất một danh mục"),
  discount: z.number().min(0).max(100, "Giảm giá phải từ 0 đến 100").nullable(),
})

type CourseFormProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: CreateCourseRequest) => void
  onDelete?: () => void
  mode: "create" | "edit"
  initialData?: any
}

const getInitalData = (initialData: any) => {
  return {
    thumbnail: null,
    title: initialData.course_content.title || "",
    description: initialData.course_content.description || "",
    price: initialData.price || 0,
    start_date: formatDate(initialData.start_date) || null,
    regis_start_date: formatDate(initialData.regis_start_date) || null,
    regis_end_date: formatDate(initialData.regis_end_date) || null,
    max_students: initialData.max_students || 100,
    is_visible: initialData.is_visible !== undefined ? initialData.is_visible : true,
    categories: initialData.course_content.categories?.map((cat: any) => cat.id) || [],
    discount: initialData.discount ? initialData.discount * 100 : null,
  }
}

export const CourseFormDialog = ({ open, onOpenChange, onSubmit, onDelete, mode, initialData }: CourseFormProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [categoryOptions, setCategoryOptions] = useState<{ label: string; value: number }[]>([])
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isDeletting, setIsDeletting] = useState(false)

  const form = useForm<CreateCourseRequest>({
    resolver: zodResolver(courseFormSchema),
    defaultValues:
      mode === "edit" && initialData
        ? getInitalData(initialData)
        : {
            thumbnail: null,
            title: "",
            description: "",
            price: 0,
            start_date: null,
            regis_start_date: null,
            regis_end_date: null,
            max_students: 100,
            is_visible: true,
            categories: [],
            discount: null,
          },
  })

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const categories = await getCategoriesApi()
        const options = categories.map((category) => ({
          label: category.name,
          value: category.id,
        }))
        setCategoryOptions(options)
      } catch (error) {
        console.error("Không thể lấy danh mục", error)
      }
    }

    fetchCategories()
  }, [])

  // Reset form when initialData changes
  useEffect(() => {
    if (mode === "edit" && initialData && open) {
      form.reset(getInitalData(initialData))
    }
  }, [initialData, mode, open, form])

  const handleSubmit = async (data: CreateCourseRequest) => {
    setIsSubmitting(true)
    if (data.discount != null) {
      data.discount = data.discount / 100
    }
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
    setIsDeletting(true)
    if (onDelete) {
      onDelete()
    }
    setIsDeletting(false)
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[800px]">
          <DialogHeader>
            <DialogTitle className="text-center">
              {mode === "create" ? "Tạo khóa học mới" : "Chỉnh sửa khóa học"}
            </DialogTitle>
          </DialogHeader>

          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            {form.formState.errors && Object.values(form.formState.errors).length > 0 && (
              <div className="text-red-500 text-center italic text-sm">
                {Object.values(form.formState.errors)[0]?.message}
              </div>
            )}

            <div className="flex flex-col md:flex-row gap-6">
              {/* Left Section: Course Content Fields */}
              <div className="flex-1 space-y-4">
                <div>
                  <Label htmlFor="title">Tiêu đề khóa học</Label>
                  <Controller
                    name="title"
                    control={form.control}
                    render={({ field }: any) => <Input id="title" placeholder="Nhập tiêu đề khóa học" {...field} />}
                  />
                </div>

                <div>
                  <Label htmlFor="description">Mô tả khóa học</Label>
                  <Controller
                    name="description"
                    control={form.control}
                    render={({ field }: any) => (
                      <Textarea id="description" placeholder="Nhập mô tả khóa học" className="min-h-[100px]" {...field} />
                    )}
                  />
                </div>

                <div>
                  <Label htmlFor="thumbnail">Ảnh bìa khóa học</Label>
                  <div className="flex items-center space-x-2">
                    {initialData?.course_content?.thumbnail_id && (
                      <div className="relative">
                        <Image
                          src={getGoogleDriveImageUrl(initialData?.course_content?.thumbnail_id || "")}
                          alt={initialData?.course_content?.title}
                          width={100}
                          height={100}
                          className="rounded-md object-cover"
                        />
                      </div>
                    )}
                    <Controller
                      name="thumbnail"
                      control={form.control}
                      render={({ field: { onChange } }: any) => (
                        <input
                          id="thumbnail"
                          type="file"
                          accept="image/png, image/jpeg, image/jpg"
                          onChange={(event) => {
                            const file = event.target.files?.[0];
                            if (file) {
                              onChange(file);
                            }
                          }}
                          className={cn(
                            "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
                          )}
                        />
                      )}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="categories">Danh mục khóa học</Label>
                  <Controller
                    name="categories"
                    control={form.control}
                    render={({ field }: any) => (
                      <Select
                        id="categories"
                        isMulti
                        options={categoryOptions}
                        value={categoryOptions.filter((option) => field.value.includes(option.value))}
                        onChange={(selectedOptions) => field.onChange(selectedOptions.map((option) => option.value))}
                        placeholder="Chọn danh mục"
                        className="basic-multi-select"
                        classNamePrefix="select"
                      />
                    )}
                  />
                </div>
              </div>

              {/* Right Section: Course Fields */}
              <div className="flex-1 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="price">Giá (VND)</Label>
                    <Controller
                      name="price"
                      control={form.control}
                      render={({ field }: any) => (
                        <Input
                          id="price"
                          type="number"
                          step="1000"
                          min="0"
                          placeholder="Nhập giá"
                          {...field}
                          onChange={(e) => field.onChange(Number(e.target.value))}
                        />
                      )}
                    />
                  </div>

                  <div>
                    <Label htmlFor="discount">Giảm giá (%)</Label>
                    <Controller
                      name="discount"
                      control={form.control}
                      render={({ field }: any) => (
                        <Input
                          id="discount"
                          type="number"
                          step="1"
                          min="0"
                          max="100"
                          placeholder="Nhập giảm giá"
                          {...field}
                          onChange={(e) => field.onChange(Number(e.target.value))}
                        />
                      )}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="start_date">Ngày bắt đầu khóa học</Label>
                  <Controller
                    name="start_date"
                    control={form.control}
                    render={({ field }: any) => (
                      <div className="flex flex-col">
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              id="start_date"
                              variant={"outline"}
                              className={cn("w-full pl-3 text-left font-normal", !field.value && "text-muted-foreground")}
                            >
                              {field.value ? field.value : <span>Chọn ngày</span>}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                              mode="single"
                              selected={field.value ? new Date(field.value) : undefined}
                              onSelect={(date) => field.onChange(date ? date.toISOString().split("T")[0] : "")}
                              disabled={(date) => date < new Date()}
                              initialFocus
                            />
                          </PopoverContent>
                        </Popover>
                      </div>
                    )}
                  />
                </div>

                <div>
                  <Label htmlFor="regis_start_date">Ngày mở đăng ký</Label>
                  <Controller
                    name="regis_start_date"
                    control={form.control}
                    render={({ field }: any) => (
                      <div className="flex flex-col">
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              id="regis_start_date"
                              variant={"outline"}
                              className={cn("w-full pl-3 text-left font-normal", !field.value && "text-muted-foreground")}
                            >
                              {field.value ? field.value : <span>Chọn ngày</span>}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                              mode="single"
                              selected={field.value ? new Date(field.value) : undefined}
                              onSelect={(date) => field.onChange(date ? date.toISOString().split("T")[0] : "")}
                              initialFocus
                            />
                          </PopoverContent>
                        </Popover>
                      </div>
                    )}
                  />
                </div>

                <div>
                  <Label htmlFor="regis_end_date">Ngày đóng đăng ký</Label>
                  <Controller
                    name="regis_end_date"
                    control={form.control}
                    render={({ field }: any) => (
                      <div className="flex flex-col">
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              id="regis_end_date"
                              variant={"outline"}
                              className={cn("w-full pl-3 text-left font-normal", !field.value && "text-muted-foreground")}
                            >
                              {field.value ? field.value : <span>Chọn ngày</span>}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0" align="start">
                            <Calendar
                              mode="single"
                              selected={field.value ? new Date(field.value) : undefined}
                              onSelect={(date) => field.onChange(date ? date.toISOString().split("T")[0] : "")}
                              disabled={(date) => date < new Date(form.getValues().regis_start_date)}
                              initialFocus
                            />
                          </PopoverContent>
                        </Popover>
                      </div>
                    )}
                  />
                </div>

                <div>
                  <Label htmlFor="max_students">Số lượng học viên tối đa</Label>
                  <Controller
                    name="max_students"
                    control={form.control}
                    render={({ field }: any) => (
                      <Input
                        id="max_students"
                        type="number"
                        min="1"
                        placeholder="Nhập số lượng học viên tối đa"
                        {...field}
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    )}
                  />
                </div>

                <div>
                  <Label htmlFor="is_visible">Hiển thị khóa học</Label>
                  <Controller
                    name="is_visible"
                    control={form.control}
                    render={({ field }: any) => (
                      <div className="flex flex-row items-center space-x-3 rounded-md border p-3 h-10">
                        <Checkbox id="is_visible" checked={field.value} onCheckedChange={field.onChange} />
                        <label
                          htmlFor="is_visible"
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                          Hiển thị khóa học cho học viên
                        </label>
                      </div>
                    )}
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-4 pt-4">
              {mode === "edit" && onDelete && (
                <Button
                  type="button"
                  variant="destructive"
                  onClick={() => setIsDeleteDialogOpen(true)}
                  className="mr-auto bg-red-500 hover:bg-red-600"
                >
                  {isDeletting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                      Đang xóa...
                    </>
                  ) : (
                    <>
                      <Trash2 className="mr-2 h-4 w-4" />
                      Xóa
                    </>
                  )}
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
                  "Tạo khóa học"
                ) : (
                  "Cập nhật khóa học"
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Bạn có chắc chắn muốn xóa?</AlertDialogTitle>
            <AlertDialogDescription>
              Hành động này không thể hoàn tác. Điều này sẽ xóa vĩnh viễn khóa học này và tất cả dữ liệu liên quan.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Hủy</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-red-500 text-red-500-foreground hover:bg-red-600">
              Xóa
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}

