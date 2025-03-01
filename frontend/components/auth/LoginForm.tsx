"use client"

import { useState } from "react"
import Image from "next/image"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useForm } from "react-hook-form"
import { useAuth } from "@/lib/auth-context"
import logo from "@/public/logo-ngang.png"

interface LoginFormProps {
  onSignUpClick: () => void
  onClose: () => void
}

interface LoginFormData {
  email: string
  password: string
}

export function LoginForm({ onSignUpClick, onClose }: LoginFormProps) {
  const { login } = useAuth()
  const [serverError, setServerError] = useState<string>("")
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>()

  const onSubmit = async (data: LoginFormData) => {
    setServerError("")

    if (!data.email) {
      setServerError("Email is required")
      return
    }

    if (!data.password) {
      setServerError("Password is required")
      return
    }

    const result = await login(data.email, data.password)
    if (result.error) {
      setServerError(result.error)
    } else {
      onClose()
    }
  }

  return (
    <div className="p-8 h-full flex flex-col justify-center">
      <div className="text-center mb-4">
        <Image src={logo} alt="Xpervia Logo" width={100} className="mx-auto" />
      </div>

      <form className="space-y-2 pt-[72px]" onSubmit={handleSubmit(onSubmit)}>
        {serverError && <p className="text-sm text-red-500 text-center italic">{serverError}</p>}
        <div>
          <Input
            type="email"
            placeholder="Email Address"
            className={`rounded-xl py-5`}
            {...register("email")}
          />
        </div>
        <div>
          <Input
            type="password"
            placeholder="Password"
            className={`rounded-xl py-5`}
            {...register("password")}
          />
        </div>
        <Button type="submit" className="w-full bg-primary hover:bg-primary/90 rounded-xl py-4 text-base">
          Login
        </Button>
      </form>

      <div className="text-center mt-2">
        <p className="text-sm text-gray-600">
          Need an Account?{" "}
          <Button variant="link" className="text-primary p-0" onClick={onSignUpClick}>
            Sign Up
          </Button>
        </p>
      </div>
    </div>
  )
}

