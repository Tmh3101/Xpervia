"use client"

import { useState } from "react"
import Image from "next/image"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { registerApi } from "@/lib/api/auth-api"
import { useForm } from "react-hook-form"
import logo from "@/public/logo-ngang.png"

interface SignUpFormProps {
  onLoginClick: () => void
}

interface SignUpFormData {
  email: string
  firstName: string
  lastName: string
  dateOfBirth: string
  password: string
  confirmPassword: string
}

export const SignUpForm = ({ onLoginClick }: SignUpFormProps) => {
  const [serverError, setServerError] = useState<string>("")
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SignUpFormData>()

  const password = watch("password")

  const onSubmit = async (data: SignUpFormData) => {

    console.log(data)

    setServerError("")

    if (!data.email) {
      setServerError("Email là bắt buộc")
      return
    }

    if (!data.firstName) {
      setServerError("Tên là bắt buộc")
      return
    }

    if (!data.lastName) {
      setServerError("Họ là bắt buộc")
      return
    }

    if (!data.dateOfBirth) {
      setServerError("Ngày sinh là bắt buộc")
      return
    }

    if (!data.password) {
      setServerError("Mật khẩu là bắt buộc")
      return
    }

    if (data.password.length < 8) {
      setServerError("Mật khẩu phải chứa ít nhất 8 ký tự")
      return
    }

    if (data.password !== data.confirmPassword) {
      setServerError("Mật khẩu không khớp")
      return
    }

    const result = await registerApi(
      data.email,
      data.firstName,
      data.lastName,
      data.dateOfBirth,
      data.password
    )

    if (result.error) {
      setServerError(result.error)
    } else {
      onLoginClick()
    }
  }

  return (
    <div className="p-8 h-full flex flex-col justify-center">
      <div className="text-center mb-4">
        <Image src={logo} alt="Xpervia Logo" width={100} className="mx-auto" />
      </div>

      <form className="space-y-2" onSubmit={handleSubmit(onSubmit)}>
        {serverError && <p className="text-center text-sm text-red-500 italic">{serverError}</p>}
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

        <Button type="submit" className="w-full bg-primary hover:bg-primary/90 rounded-xl py-4 text-base">
          Đăng ký
        </Button>
      </form>

      <div className="text-center mt-2">
        <p className="text-sm text-gray-600">
          Bạn đã có tài khoản?{" "}
          <Button variant="link" className="text-primary p-0" onClick={onLoginClick}>
            Đăng nhập ngay
          </Button>
        </p>
      </div>
    </div>
  )
}

