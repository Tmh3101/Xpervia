"use client";

import type React from "react";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { changePasswordApi } from "@/lib/api/user-api";

const changePasswordFormSchema = z.object({
  old_password: z.string().nonempty("Mật khẩu cũ không được để trống"),
  new_password: z.string().nonempty("Mật khẩu mới không được để trống"),
  confirm_password: z
    .string()
    .nonempty("Xác nhận mật khẩu không được để trống"),
});

interface ChangePasswordProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ChangePasswordDialog({ isOpen, onClose }: ChangePasswordProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { user } = useAuth();

  const form = useForm({
    resolver: zodResolver(changePasswordFormSchema),
    defaultValues: {
      old_password: "",
      new_password: "",
      confirm_password: "",
    },
  });

  const handlChangePasswordSubmit = async (data: any) => {
    if (!user) return;

    if (data.new_password !== data.confirm_password) {
      form.setError("confirm_password", {
        type: "manual",
        message: "Xác nhận mật khẩu không khớp",
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await changePasswordApi(user.id, data);
      form.reset();
      onClose();
    } catch (error) {
      console.error("Lỗi khi gửi biểu mẫu:", error);
      form.setError("old_password", {
        type: "manual",
        message: "Mật khẩu cũ không đúng",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Đổi mật khẩu</DialogTitle>
        </DialogHeader>
        <form
          onSubmit={form.handleSubmit(handlChangePasswordSubmit)}
          className="space-y-4"
        >
          {form.formState.errors &&
            Object.values(form.formState.errors).length > 0 && (
              <div className="text-red-500 text-center italic text-sm">
                {Object.values(form.formState.errors)[0]?.message as string}
              </div>
            )}

          <div className="space-y-1">
            <Label htmlFor="old_password">Mật khẩu cũ</Label>
            <Controller
              name="old_password"
              control={form.control}
              render={({ field }: any) => (
                <Input
                  type="password"
                  id="old_password"
                  placeholder="Nhập mật khẫu cũ..."
                  {...field}
                />
              )}
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="new_password">Mật khẩu mới</Label>
            <Controller
              name="new_password"
              control={form.control}
              render={({ field }: any) => (
                <Input
                  type="password"
                  id="last_new_passwordname"
                  placeholder="Nhập mật khẩu mới..."
                  {...field}
                />
              )}
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="confirm_password">Xác nhận mật khẩu</Label>
            <Controller
              name="confirm_password"
              control={form.control}
              render={({ field }: any) => (
                <Input
                  type="password"
                  id="confirm_password"
                  placeholder="Xác nhận mật khẩu..."
                  {...field}
                />
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
  );
}
