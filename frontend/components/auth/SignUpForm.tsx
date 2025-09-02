"use client";

import { useState, useRef } from "react";
import Image from "next/image";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { registerApi } from "@/lib/api/auth-api";
import { useForm } from "react-hook-form";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import logo from "@/public/logo-ngang.png";

interface SignUpFormProps {
  onLoginClick: () => void;
  onClose: () => void;
}

export const SignUpForm = ({ onLoginClick, onClose }: SignUpFormProps) => {
  interface SignUpFormData {
    email: string;
    firstName: string;
    lastName: string;
    dateOfBirth: string;
    password: string;
    confirmPassword: string;
    role: string;
  }

  const [serverError, setServerError] = useState<string>("");
  const [isTeacher, setIsTeacher] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignUpFormData>();

  const onSubmit = async (data: SignUpFormData) => {
    setServerError("");
    if (!data.email) {
      setServerError("Email là bắt buộc");
      return;
    }
    if (!data.firstName) {
      setServerError("Tên là bắt buộc");
      return;
    }
    if (!data.lastName) {
      setServerError("Họ là bắt buộc");
      return;
    }
    if (!data.dateOfBirth) {
      setServerError("Ngày sinh là bắt buộc");
      return;
    }
    if (!data.password) {
      setServerError("Mật khẩu là bắt buộc");
      return;
    }
    if (data.password.length < 8) {
      setServerError("Mật khẩu phải chứa ít nhất 8 ký tự");
      return;
    }
    // Password should contain at least one character of each: abcdefghijklmnopqrstuvwxyz, ABCDEFGHIJKLMNOPQRSTUVWXYZ, 0123456789, !@#$%^&*()_+-=[]{};':"|<>?,./`~.
    const passwordPattern =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"|<>?,.\/`~]).{8,}$/;
    if (!passwordPattern.test(data.password)) {
      setServerError(
        "Mật khẩu phải bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt."
      );
      return;
    }
    if (data.password !== data.confirmPassword) {
      setServerError("Mật khẩu không khớp");
      return;
    }
    const role = isTeacher ? "teacher" : "student";
    const result = await registerApi(
      data.email,
      data.firstName,
      data.lastName,
      data.dateOfBirth,
      data.password,
      role
    );
    if (result.error) {
      setServerError(result.error);
    } else {
      setShowSuccess(true);
      // Tự động tắt popup sau 5 giây và tắt AuthModal
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => {
        setShowSuccess(false);
        onClose();
      }, 5000);
    }
  };

  return (
    <div className="p-8 pt-4 h-full flex flex-col justify-center relative">
      {/* Popup thông báo đăng ký thành công */}
      {showSuccess && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl px-8 py-10 flex flex-col items-center animate-fade-in">
            <div className="mb-4">
              <svg
                className="h-16 w-16 text-green-500 animate-bounce"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle cx="12" cy="12" r="12" fill="#22c55e" />
                <path
                  d="M7 13l3 3 7-7"
                  stroke="#fff"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-green-600 mb-2">
              Đăng ký thành công!
            </h2>
            <p className="text-gray-700 text-center mb-2">
              Bạn đã đăng ký thành công, hãy kiểm tra email để xác nhận.
            </p>
            <span className="text-xs text-gray-400">
              Bạn sẽ được chuyển hướng về trang chủ sau vài giây...
            </span>
          </div>
        </div>
      )}
      <div className="text-center my-2">
        <Image src={logo} alt="Xpervia Logo" width={100} className="mx-auto" />
      </div>
      <form className="space-y-2" onSubmit={handleSubmit(onSubmit)}>
        <p className="min-h-[20px] text-center text-sm text-red-500 italic">
          {serverError}
        </p>
        <div>
          <Input
            type="email"
            placeholder="Địa chỉ email"
            className={`rounded-xl py-5`}
            {...register("email")}
          />
        </div>
        <div className="flex gap-4">
          <div className="w-1/2">
            <Input
              type="text"
              placeholder="Tên"
              className={`rounded-xl py-5`}
              {...register("firstName")}
            />
          </div>
          <div className="w-1/2">
            <Input
              type="text"
              placeholder="Họ"
              className={`rounded-xl py-5`}
              {...register("lastName")}
            />
          </div>
        </div>
        <div>
          <Input
            type="date"
            placeholder="Ngày sinh"
            className="rounded-xl py-5 text-gray-500"
            {...register("dateOfBirth")}
          />
        </div>
        <div>
          <Input
            type="password"
            placeholder="Mật khẩu"
            className={`rounded-xl py-5`}
            {...register("password")}
          />
        </div>
        <div>
          <Input
            type="password"
            placeholder="Nhập lại mật khẩu"
            className={`rounded-xl py-4`}
            {...register("confirmPassword")}
          />
        </div>
        <div className="flex items-center space-x-2">
          <Switch
            id="teacher-account"
            className="h-6 w-11"
            checked={isTeacher}
            onCheckedChange={(checked) => setIsTeacher(checked)}
          />
          <Label
            htmlFor="teacher-account"
            className={isTeacher ? "text-black font-medium" : "text-gray-400"}
          >
            Đăng ký tài khoản giảng viên
          </Label>
        </div>
        <Button
          type="submit"
          className="w-full bg-primary hover:bg-primary/90 rounded-xl py-4 text-base"
        >
          Đăng ký
        </Button>
      </form>
      <div className="text-center mt-2">
        <p className="text-sm text-gray-600">
          Bạn đã có tài khoản?{" "}
          <Button
            variant="link"
            className="text-primary p-0"
            onClick={onLoginClick}
          >
            Đăng nhập ngay
          </Button>
        </p>
      </div>
      {/* Hiệu ứng fade-in cho popup */}
      <style jsx>{`
        .animate-fade-in {
          animation: fadeIn 0.5s ease;
        }
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
      `}</style>
    </div>
  );
};
