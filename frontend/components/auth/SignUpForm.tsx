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

export function SignUpForm({ onLoginClick }: SignUpFormProps) {
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
      setServerError("Email is required")
      return
    }

    if (!data.firstName) {
      setServerError("First name is required")
      return
    }

    if (!data.lastName) {
      setServerError("Last name is required")
      return
    }

    if (!data.dateOfBirth) {
      setServerError("Date of birth is required")
      return
    }

    if (!data.password) {
      setServerError("Password is required")
      return
    }

    if (data.password.length < 8) {
      setServerError("Password must be at least 8 characters")
      return
    }

    if (data.password !== data.confirmPassword) {
      setServerError("Passwords do not match")
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
            placeholder="Email Address"
            className={`rounded-xl py-5`}
            {...register("email")}
          />
        </div>

        <div className="flex gap-4">
          <div className="w-1/2">
            <Input
              type="text"
              placeholder="First Name"
              className={`rounded-xl py-5`}
              {...register("firstName")}
            />
          </div>
          <div className="w-1/2">
            <Input
              type="text"
              placeholder="Last Name"
              className={`rounded-xl py-5`}
              {...register("lastName")}
            />
          </div>
        </div>

        <div>
          <Input
            type="date"
            placeholder="Select Date"
            className="rounded-xl py-5"
            {...register("dateOfBirth")}
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

        <div>
          <Input
            type="password"
            placeholder="Confirm Password"
            className={`rounded-xl py-4`}
            {...register("confirmPassword")}
          />
        </div>

        <Button type="submit" className="w-full bg-primary hover:bg-primary/90 rounded-xl py-4 text-base">
          Sign Up
        </Button>
      </form>

      <div className="text-center mt-2">
        <p className="text-sm text-gray-600">
          Already have an account?{" "}
          <Button variant="link" className="text-primary p-0" onClick={onLoginClick}>
            Login
          </Button>
        </p>
      </div>
    </div>
  )
}

