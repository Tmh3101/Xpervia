"use client"

import Image from "next/image"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Bell, User, LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState, useEffect } from "react"
import { AuthModal } from "./auth/AuthModal"
import { useAuth } from "@/lib/auth-context"
import { usePathname } from "next/navigation"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
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

  const handleProfileClick = () => {
    if (user) {
      if (user.role === "student") {
        router.push(`/profile/student/${user.id}`)
      } else if (user.role === "teacher") {
        router.push(`/profile/teacher/${user.id}`)
      }
    }
  }

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled || pathname !== "/" ? "bg-white shadow-md" : "bg-transparent"
        }`}
      >
        <div className="container mx-auto flex items-center justify-between py-4">
          <Link href="/" className="flex items-center">
            <Image
              src={logo}
              alt="Xpervia Logo"
              width={100}
              className="rounded-[14px]"
            />
          </Link>
          <div className="flex items-center space-x-6">
            {user ? (
              <>
                {user.role === "student" && (
                  <Button
                    variant="ghost"
                    className={`font-medium rounded-xl ${
                      isScrolled || pathname !== "/"
                        ? isActive("/student/my-courses")
                          ? "text-white bg-primary hover:bg-primary/80 hover:text-white"
                          : "text-gray-800 hover:text-white hover:bg-primary"
                        : "text-white hover:bg-primary hover:text-white"
                    }`}
                    onClick={() => router.push("/student/my-courses")}
                  >
                    Khóa học của tôi
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="icon"
                  className={isScrolled || pathname !== "/" ? "text-gray-800" : "text-white"}
                >
                  <Bell className="h-5 w-5" />
                </Button>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <div className="h-8 w-8 rounded-full bg-primary overflow-hidden cursor-pointer">
                      <Image
                        src={userAvatar}
                        alt={`${user.first_name} ${user.last_name}`}
                        width={32}
                        height={32}
                        className="h-full w-full object-cover"
                      />
                    </div>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56 p-4 mt-6 rounded-xl">
                    <DropdownMenuLabel className="font-normal">
                      <div className="flex flex-col space-y-1">
                        <p className="text-sm font-medium leading-none">{`${user.first_name} ${user.last_name}`}</p>
                        <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                      </div>
                    </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={handleProfileClick} className="cursor-pointer">
                      <User className="mr-2 h-4 w-4" />
                      <span>Hồ sơ</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={logout}
                      className="cursor-pointer text-red-500 focus:text-red-500"
                    >
                      <LogOut className="mr-2 h-4 w-4" />
                      <span>Đăng xuất</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
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

