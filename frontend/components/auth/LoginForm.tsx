"use client";

import { useState } from "react";
import Image from "next/image";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useForm } from "react-hook-form";
import { useAuth } from "@/lib/auth-context";
import logo from "@/public/logo-ngang.png";

interface LoginFormProps {
  onSignUpClick: () => void;
  onHandleResetPassword: () => void;
  onClose: () => void;
}

interface LoginFormData {
  email: string;
  password: string;
}

export function LoginForm({
  onSignUpClick,
  onHandleResetPassword,
  onClose,
}: LoginFormProps) {
  const { login } = useAuth();
  const [serverError, setServerError] = useState<string>("");
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  const onSubmit = async (data: LoginFormData) => {
    setServerError("");

    if (!data.email) {
      setServerError("Email là bắt buộc");
      return;
    }

    if (!data.password) {
      setServerError("Mật khẩu là bắt buộc");
      return;
    }

    const result = await login(data.email, data.password);
    if (result.error) {
      setServerError(result.error);
    } else {
      onClose();
    }
  };

  return (
    <div className="p-8 h-full flex flex-col justify-center">
      <div className="text-center mb-4">
        <Image src={logo} alt="Xpervia Logo" width={100} className="mx-auto" />
      </div>

      <form className="space-y-2 pt-[80px]" onSubmit={handleSubmit(onSubmit)}>
        {serverError && (
          <p className="text-sm text-red-500 text-center italic">
            {serverError}
          </p>
        )}
        <div>
          <Input
            type="email"
            placeholder="Địa chỉ email"
            className={`rounded-xl py-5`}
            {...register("email")}
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
        <Button
          type="submit"
          className="w-full bg-primary hover:bg-primary/90 rounded-xl py-4 text-base"
        >
          Đăng nhập
        </Button>
      </form>

      <div className="text-center mt-2">
        <p className="text-sm text-gray-600">
          Bạn chưa có tài khoản?{" "}
          <Button
            variant="link"
            className="text-primary p-0"
            onClick={onSignUpClick}
          >
            Đăng ký ngay
          </Button>
        </p>
        <p className="text-sm text-gray-600">
          Bạn đã không nhớ mật khẩu?{" "}
          <Button
            variant="link"
            className="text-primary p-0"
            onClick={onHandleResetPassword}
          >
            Đặt lại mật khẩu
          </Button>
        </p>
      </div>
    </div>
  );
}
