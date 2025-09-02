"use client";

import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { CalendarIcon, Trash2 } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import type { CreateAssignmentRequest } from "@/lib/types/assignment";

const assignmentFormSchema = z.object({
  title: z.string().min(3, "Tiêu đề phải có ít nhất 3 ký tự"),
  content: z.string().min(3, "Nội dung phải có ít nhất 3 ký tự"),
  start_at: z.string(),
  due_at: z.string().optional(),
});

interface AssignmentFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: any) => void;
  onDelete?: () => void;
  mode: "create" | "edit";
  initialData?: {
    id?: number;
    title?: string;
    content?: string;
    start_at?: string;
    due_at?: string;
  };
}

export function AssignmentFormDialog({
  open,
  onOpenChange,
  onSubmit,
  onDelete,
  mode = "create",
  initialData,
}: AssignmentFormDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDeleteAlert, setShowDeleteAlert] = useState(false);

  const form = useForm({
    resolver: zodResolver(assignmentFormSchema),
    defaultValues: {
      title: initialData?.title || "",
      content: initialData?.content || "",
      start_at: initialData?.start_at
        ? new Date(initialData.start_at).toISOString()
        : new Date().toISOString(),
      due_at: initialData?.due_at || "",
    },
  });

  // Update form values when initialData changes
  useEffect(() => {
    if (initialData) {
      form.reset({
        title: initialData.title,
        content: initialData.content,
        start_at: initialData.start_at,
        due_at: initialData.due_at,
      });
    } else {
      form.reset({
        title: "",
        content: "",
        start_at: new Date().toISOString(),
        due_at: "",
      });
    }
  }, [initialData, form]);

  const handleSubmit = async (data: CreateAssignmentRequest) => {
    if (!data) return;
    setIsSubmitting(true);

    // Check start_at and due_at values
    if (data.start_at && data.due_at) {
      const startDate = new Date(data.start_at);
      const dueDate = new Date(data.due_at);

      if (startDate > dueDate) {
        form.setError("due_at", {
          message: "Hạn nộp phải lớn hơn ngày bắt đầu",
        });
        setIsSubmitting(false);
        return;
      }
    }

    try {
      await onSubmit(data);
    } catch (error) {
      console.error("Error submitting assignment:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = () => {
    setShowDeleteAlert(true);
  };

  const confirmDelete = async () => {
    if (onDelete) {
      await onDelete();
    }
    setShowDeleteAlert(false);
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[500px] gap-0">
          <DialogHeader>
            <DialogTitle>
              {mode === "create" ? "Thêm bài tập mới" : "Chỉnh sửa bài tập"}
            </DialogTitle>
            <DialogDescription>
              {mode === "create"
                ? "Tạo bài tập mới cho học viên"
                : "Chỉnh sửa thông tin bài tập"}
            </DialogDescription>
          </DialogHeader>

          <form
            onSubmit={form.handleSubmit(handleSubmit)}
            className="space-y-4 pt-4"
          >
            {form.formState.errors &&
              Object.values(form.formState.errors).length > 0 && (
                <div className="text-red-500 text-center italic text-sm">
                  {Object.values(form.formState.errors)[0]?.message as string}
                </div>
              )}

            <div className="space-y-1">
              <Label htmlFor="title">Tiêu đề bài tập</Label>
              <Controller
                name="title"
                control={form.control}
                render={({ field }: any) => (
                  <Input
                    id="title"
                    placeholder="Nhập tiêu đề bài tập"
                    {...field}
                  />
                )}
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="content">Nội dung bài tập</Label>
              <Controller
                name="content"
                control={form.control}
                render={({ field }: any) => (
                  <Textarea
                    id="content"
                    placeholder="Nhập nội dung bài tập"
                    className="min-h-[150px]"
                    {...field}
                  />
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label>Ngày bắt đầu</Label>
                <Controller
                  name="start_at"
                  control={form.control}
                  render={({ field }: any) => (
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          id="start_at"
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !field.value && "text-muted-foreground"
                          )}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {field.value
                            ? format(new Date(field.value), "dd/MM/yyyy")
                            : "Chọn ngày"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={
                            field.value ? new Date(field.value) : undefined
                          }
                          onSelect={(date) =>
                            field.onChange(date ? date.toISOString() : "")
                          } // Cập nhật giá trị vào form
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  )}
                />
              </div>

              <div className="space-y-1">
                <Label>Hạn nộp</Label>
                <Controller
                  name="due_at"
                  control={form.control}
                  render={({ field }: any) => (
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          id="due_at"
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !field.value && "text-muted-foreground"
                          )}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {field.value
                            ? format(new Date(field.value), "dd/MM/yyyy")
                            : "Chọn ngày"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={
                            field.value ? new Date(field.value) : undefined
                          }
                          onSelect={(date) =>
                            field.onChange(date ? date.toISOString() : "")
                          } // Cập nhật giá trị vào form
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  )}
                />
              </div>
            </div>

            <DialogFooter className="pt-4">
              {mode === "edit" && onDelete && (
                <Button
                  type="button"
                  variant="destructive"
                  onClick={() => handleDelete()}
                  className="mr-auto bg-red-500 hover:bg-red-600"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Xóa
                </Button>
              )}
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
              >
                Hủy
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                    {mode === "create" ? "Đang tạo..." : "Đang cập nhật..."}
                  </>
                ) : mode === "create" ? (
                  "Tạo bài tập"
                ) : (
                  "Cập nhật bài tập"
                )}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={showDeleteAlert} onOpenChange={setShowDeleteAlert}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              Bạn có chắc chắn muốn xóa bài tập này?
            </AlertDialogTitle>
            <AlertDialogDescription>
              Hành động này không thể hoàn tác. Tất cả bài nộp của học viên cho
              bài tập này cũng sẽ bị xóa.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Hủy</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-red-500 text-red-500-foreground hover:bg-red-600 text-white"
            >
              Xóa bài tập
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
