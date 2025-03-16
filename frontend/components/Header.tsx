"use client"

import Image from "next/image"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Bell } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState, useEffect } from "react"
import { AuthModal } from "./auth/AuthModal"
import { useAuth } from "@/lib/auth-context"
import { usePathname } from "next/navigation"
import logo from "@/public/logo-ngang.png"
import userAvatar from "@/public/user-avatar.svg"

export function Header() {
  const { user, logout } = useAuth()
  const [isScrolled, setIsScrolled] = useState(false)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authView, setAuthView] = useState<"login" | "signup">("login")
  const pathname = usePathname()
  const router = useRouter()

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0)
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const handleAuthClick = (view: "login" | "signup") => {
    setAuthView(view)
    setShowAuthModal(true)
  }

  const isActive = (path: string) => pathname === path || pathname?.startsWith(path + "/")

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled || pathname !== "/" ? "bg-white shadow-md" : "bg-transparent"
        }`}
      >
        <div className="container mx-auto flex items-center justify-between py-4">
          <Link href="/" className="flex items-center">
            <Image src={logo} alt="Xpervia Logo" width={100} className="rounded-[14px]"/>
          </Link>
          <div className="flex items-center space-x-6">
            {user ? (
              <>
                {user.role === "student" && (
                  <Button
                    variant="ghost"
                    className={`font-medium ${
                      isScrolled || pathname !== "/"
                        ? isActive("/student/my-courses")
                          ? "text-primary"
                          : "text-gray-800 hover:text-primary"
                        : "text-white hover:text-destructive"
                    }`}
                    onClick={() => router.push("/student/my-courses")}
                  >
                    Khóa học của tôi
                  </Button>
                )}
                {/* <Button variant="ghost" className={isScrolled || pathname !== "/" ? "text-gray-800" : "text-white"}>
                  Become Instructor
                </Button> */}
                <Button
                  variant="ghost"
                  size="icon"
                  className={isScrolled || pathname !== "/" ? "text-gray-800" : "text-white"}
                >
                  <Bell className="h-5 w-5" />
                </Button>
                <div className="relative group">
                  <div className="h-8 w-8 rounded-full bg-primary overflow-hidden cursor-pointer">
                    <Image
                      src={userAvatar}
                      alt={`${user.first_name} ${user.last_name}`}
                      width={32}
                      height={32}
                      className="h-full w-full object-cover"
                    />
                  </div>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 invisible group-hover:visible">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <p className="text-sm font-medium">{`${user.first_name} ${user.last_name}`}</p>
                      <p className="text-xs text-gray-500">{user.email}</p>
                    </div>
                    <Button
                      variant="ghost"
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                      onClick={logout}
                    >
                      Đăng xuất
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <>
                <Button
                  variant="ghost"
                  className={`rounded-full hover:text-primary hover:underline ${
                    isScrolled || pathname !== "/" ? "text-primary" : "text-white"
                  }`}
                  onClick={() => handleAuthClick("login")}
                >
                  Đăng nhập
                </Button>
                <Button
                  className="bg-primary hover:bg-primary/90 rounded-full"
                  onClick={() => handleAuthClick("signup")}
                >
                  Đăng ký
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} defaultView={authView} />
    </>
  )
}

