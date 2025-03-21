"use client"

import { createContext, useContext, useState, type ReactNode } from "react"
import { useRouter, usePathname } from "next/navigation"
import { useEffect } from "react"
import { loginApi, logoutApi } from "@/lib/api/auth-api"
import { getEnrollmentsApi, enrollCourseApi } from "@/lib/api/enrollment-api"
import { User } from "@/lib/types/user"
import { Enrollment } from "@/lib/types/enrollment"

interface AuthContextType {
  token: string | null
  user: User | null
  login: (email: string, password: string) => Promise<{ error?: string }>
  logout: () => void
  enrollments: Enrollment[]
  enrollInCourse: (courseId: number) => void
  fetchEnrollments: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [enrollments, setEnrollments] = useState<Enrollment[]>([])
  const router = useRouter()
  const pathname = usePathname();

  useEffect(() => {
    // Kiểm tra và khởi tạo lại state của user khi component được mount
    const storedUser = sessionStorage.getItem("user")
    const storedToken = sessionStorage.getItem("token")
    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser))
      setToken(storedToken)
    }
  }, [])

  useEffect(() => {
    // Cập nhật sessionStorage khi state của user thay đổi
    if (user && token) {
      sessionStorage.setItem("user", JSON.stringify(user))
      sessionStorage.setItem("token", token || "")
    } else {
      sessionStorage.removeItem("user")
      sessionStorage.removeItem("token")
    }
  }, [token, user])

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
    sessionStorage.setItem("token", token)
    setToken(token)

    // Remove password from user object before setting in state
    const { password: _, ...userWithoutPassword } = user
    sessionStorage.setItem("user", user)
    setUser(userWithoutPassword)
    handleRoleBasedRedirect(userWithoutPassword.role)

    await fetchEnrollments()
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
    setEnrollments([])
    router.push("/")
  }

  const enrollInCourse = (courseId: number) => {
    if (!user || user.role !== "student") return
    enrollCourseApi(courseId).then(() => fetchEnrollments())
  }

  const fetchEnrollments = () => {
    if (token) {
      getEnrollmentsApi().then(enrollments => setEnrollments(enrollments))
    }
  }

  return (
    <AuthContext.Provider value={{ token, user, login, logout, enrollments, enrollInCourse, fetchEnrollments }}>
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

