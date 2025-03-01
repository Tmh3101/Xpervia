"use client"

import { createContext, useContext, useState, type ReactNode } from "react"
import { useRouter, usePathname } from "next/navigation"
import { useEffect } from "react"
import { loginApi, logoutApi } from "@/lib/api/auth-api"
import { User } from "@/lib/types/user"

interface AuthContextType {
  token: string | null
  user: User | null
  login: (email: string, password: string) => Promise<{ error?: string }>
  logout: () => void
  enrolledCourses: number[]
  enrollInCourse: (courseId: number) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [enrolledCourses, setEnrolledCourses] = useState<number[]>([])
  const router = useRouter()
  const pathname = usePathname();

  useEffect(() => {
    // Kiểm tra và khởi tạo lại state của user khi component được mount
    const storedUser = sessionStorage.getItem("user")
    const storedToken = sessionStorage.getItem("token")
    if (storedUser) {
      setUser(JSON.parse(storedUser))
      setToken(storedToken)
    }
  }, [])

  useEffect(() => {
    // Cập nhật sessionStorage khi state của user thay đổi
    if (user) {
      sessionStorage.setItem("user", JSON.stringify(user))
      sessionStorage.setItem("token", token || "")
    } else {
      sessionStorage.removeItem("user")
      sessionStorage.removeItem("token")
    }
  }, [user])

  // Handle role-based routing after login
  const handleRoleBasedRedirect = (role: User["role"]) => {
    switch (role) {
      case "admin":
        router.push("/admin")
        break
      case "teacher":
        router.push("/teacher")
        break
      case "student":
        router.push(pathname)
        break
      default:
        router.push("/")
    }
  }

  const login = async (email: string, password: string) => {

    const result = await loginApi(email, password)
    
    if (!result.user) {
      return { error: result.error }
    }

    const { token, user } = result

    // Remove password from user object before setting in state
    const { password: _, ...userWithoutPassword } = user
    setUser(userWithoutPassword)
    setToken(token)

    handleRoleBasedRedirect(userWithoutPassword.role)
    return userWithoutPassword
  }

  const logout = async () => {
    if (token) {
      const result = await logoutApi(token)
      if (result) {
        setToken(null)
      }
    }
    setUser(null)
    setEnrolledCourses([])
    router.push("/")
  }

  const enrollInCourse = (courseId: number) => {
    // if (!user || user.role !== "student") return

    // setEnrolledCourses((prev) => {
    //   if (prev.includes(courseId)) return prev
    //   return [...prev, courseId]
    // })

    // In a real app, you would make an API call to update the enrollment in the backend
  }

  return (
    <AuthContext.Provider value={{ token, user, login, logout, enrolledCourses, enrollInCourse }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

