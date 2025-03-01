"use client"

import { useState, useEffect } from "react"
import { X } from "lucide-react"
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog"
import { LoginForm } from "./LoginForm"
import { SignUpForm } from "./SignUpForm"
import { Button } from "@/components/ui/button"
import Image from "next/image"

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  defaultView?: "login" | "signup"
}

export function AuthModal({ isOpen, onClose, defaultView = "login" }: AuthModalProps) {
  const [view, setView] = useState<"login" | "signup">(defaultView)

  useEffect(() => {
    setView(defaultView)
  }, [defaultView])

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[800px] p-0 overflow-hidden">
        <DialogTitle className="hidden"></DialogTitle>
        <Button
          variant="ghost"
          size="icon"
          className="absolute bg-white rounded-full z-30 right-2 top-2 text-gray-500"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
        </Button>

        <div className="flex h-[500px] transition-transform duration-500 ease-in-out">
          <div
            className={`w-1/2 z-20 transition-transform duration-500 ${view === "signup" ? "translate-x-full" : ""}`}
          >
            <Image
              src="https://westcoastuniversity.edu/wp-content/uploads/2023/03/Study-Buddy-Efficiency-Expert-blog.jpg"
              alt="Learning"
              width={400}
              height={500}
              className="w-full h-full object-cover"
            />
          </div>

          <div
            className={`absolute w-1/2 transition-transform duration-500 z-10 ${
              view === "signup"
                ? "translate-x-0 opacity-100 pointer-events-auto"
                : "translate-x-full opacity-0 pointer-events-none"
            }`}
          >
            <SignUpForm onLoginClick={() => setView("login")} />
          </div>

          <div
            className={`absolute right-0 w-1/2 transition-transform duration-500 z-10 ${
              view === "login"
                ? "translate-x-0 opacity-100 pointer-events-auto"
                : "-translate-x-full opacity-0 pointer-events-none"
            }`}
          >
            <LoginForm onSignUpClick={() => setView("signup")} onClose={onClose} />
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

