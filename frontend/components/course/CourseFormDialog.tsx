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
import { CreateCourseRequest } from "@/lib/types/course"


const courseFormSchema = z.object({
  thumbnail: z.instanceof(File).refine((file) => file instanceof File, {
    message: "Ảnh bìa là bắt buộc",
  }),
  title: z.string().min(3, "Tiêu đề phải có ít nhất 3 ký tự"),
  description: z.string().min(20, "Mô tả phải có ít nhất 20 ký tự"),
  price: z.number().min(0, "Giá phải là số dương"),
  start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Định dạng ngày không hợp lệ (YYYY-MM-DD)"),
  regis_start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Định dạng ngày không hợp lệ (YYYY-MM-DD)"),
  regis_end_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Định dạng ngày không hợp lệ (YYYY-MM-DD)").nullable(),
  max_students: z.number().min(1, "Số lượng học viên tối đa phải ít nhất là 1"),
  is_visible: z.boolean().default(true),
  categories: z.array(z.number()).min(1, "Phải chọn ít nhất một danh mục"),
  discount: z.number().min(0).max(100, "Giảm giá phải từ 0 đến 100").nullable(),
});

type CourseFormProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: CreateCourseRequest) => void;
  mode: "create" | "edit";
};

export const CourseFormDialog = ({ open, onOpenChange, onSubmit, mode }: CourseFormProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [categoryOptions, setCategoryOptions] = useState<{ label: string; value: number }[]>([]);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const categories = await getCategoriesApi();
        const options = categories.map((category) => ({
          label: category.name,
          value: category.id,
        }));
        setCategoryOptions(options);
      } catch (error) {
        console.error("Failed to fetch categories", error);
      }
    };

    fetchCategories();
  }, []);

  const form = useForm<CreateCourseRequest>({
    resolver: zodResolver(courseFormSchema),
    defaultValues: {
      thumbnail: null,
      title: "",
      description: "",
      price: 0,
      start_date: "",
      regis_start_date: "",
      regis_end_date: null,
      max_students: 100,
      is_visible: true,
      categories: [],
      discount: null,
    },
  });

  const handleSubmit = async (data: CreateCourseRequest) => {
    if (data.discount != null) {
      data.discount = data.discount / 100;
    }
    
    console.log("Submitting form with data:", data);
    setIsSubmitting(true);
    try {
      onSubmit(data);
      form.reset();
    } catch (error) {
      console.error("Error submitting form:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{mode === "create" ? "Tạo khóa học" : "Chỉnh sửa khóa học"}</DialogTitle>
        </DialogHeader>

        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
          {form.formState.errors && Object.values(form.formState.errors).length > 0 && (
            <div className="text-red-500 text-center italic text-sm">{Object.values(form.formState.errors)[0]?.message}</div>
          )}
          <Controller
            name="title"
            control={form.control}
            render={({ field }: any) => (
              <Input placeholder="Nhập tiêu đề khóa học" {...field} />
            )}
          />

          <Controller
            name="description"
            control={form.control}
            render={({ field }: any) => (
              <Textarea placeholder="Nhập mô tả khóa học" className="min-h-[100px]" {...field} />
            )}
          />

          <div className="grid grid-cols-2 gap-4">
            <Controller
              name="price"
              control={form.control}
              render={({ field }: any) => (
                  <Input
                    type="number"
                    step="1000"
                    min="0"
                    placeholder="Nhập giá (VND)"
                    {...field}
                    onChange={(e) => field.onChange(Number(e.target.value))}
                  />
              )}
            />

            <Controller
              name="discount"
              control={form.control}
              render={({ field }: any) => (
                  <Input
                    type="number"
                    step="1"
                    min="0"
                    max="100"
                    placeholder="Nhập giảm giá (%)"
                    {...field}
                    onChange={(e) => field.onChange(Number(e.target.value))}
                  />
              )}
            />
          </div>

          <Controller
            name="thumbnail"
            control={form.control}
            render={({ field: { onChange } }: any) => (
              <input
                type="file"
                accept="image/png, image/jpeg, image/jpg"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) {
                    setSelectedFileName(file.name);
                    onChange(file);
                  }
                }}
                className={cn(
                  "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
                )}
              />
            )}
          />

          <Controller
            name="categories"
            control={form.control}
            render={({ field }: any) => (
              <Select
                isMulti
                options={categoryOptions}
                value={categoryOptions.filter((option) => field.value.includes(option.value))}
                onChange={(selectedOptions) => field.onChange(selectedOptions.map((option) => option.value))}
                placeholder="Chọn danh mục"
              />
            )}
          />

          <div className="grid grid-cols-3 gap-2">

            <Controller
              name="start_date"
              control={form.control}
              render={({ field }: any) => (
                <div className="flex flex-col">
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant={"outline"}
                        className={cn("w-full pl-3 text-left font-normal", !field.value && "text-muted-foreground")}
                      >
                        {field.value ? field.value : <span>Ngày bắt đầu</span>}
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


            <Controller
              name="regis_start_date"
              control={form.control}
              render={({ field }: any) => (
                <div className="flex flex-col">
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant={"outline"}
                        className={cn("w-full pl-3 text-left font-normal", !field.value && "text-muted-foreground")}
                      >
                        {field.value ? field.value : <span>Ngày mở đăng ký</span>}
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

            <Controller
              name="regis_end_date"
              control={form.control}
              render={({ field }: any) => (
                <div className="flex flex-col">
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant={"outline"}
                        className={cn("w-full pl-3 text-left font-normal", !field.value && "text-muted-foreground")}
                      >
                        {field.value ? field.value : <span>Ngày đóng đăng ký</span>}
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

          <div className="grid grid-cols-2 gap-2">
            <Controller
              name="max_students"
              control={form.control}
              render={({ field }: any) => (
                <Input
                  type="number"
                  min="1"
                  placeholder="Nhập số lượng học viên tối đa"
                  {...field}
                  onChange={(e) => field.onChange(Number(e.target.value))}
                  className="h-full"
                />
              )}
            />

            <Controller
              name="is_visible"
              control={form.control}
              render={({ field }: any) => (
                <div className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                  <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                  <div className="space-y-1 leading-none">
                    <label>Hiển thị khóa học</label>
                  </div>
                </div>
              )}
            />
          </div>

          <div className="flex justify-end gap-4">
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
  )
}

