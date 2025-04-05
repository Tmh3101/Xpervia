"use client"

import { useToast } from "@/components/ui/use-toast"
import { CheckCircle, AlertCircle, Info } from "lucide-react"
import { ToastProvider, ToastViewport } from "@/components/ui/toast"

export type NotificationType = "success" | "error" | "info"

interface ToastNotificationProps {
  type: NotificationType
  title: string
  description?: string
}

export function showNotification({ type, title, description }: ToastNotificationProps) {
  const { toast } = useToast()

  const icons = {
    success: <CheckCircle className="h-5 w-5 text-green-500" />,
    error: <AlertCircle className="h-5 w-5 text-red-500" />,
    info: <Info className="h-5 w-5 text-blue-500" />,
  }

  toast({
    variant: type === "success" ? "default" : type === "error" ? "destructive" : "default",
    title: (
      <div className="flex items-center gap-2">
        {icons[type]}
        <span>{title}</span>
      </div>
    ),
    description: description,
  })
}

export function Toaster() {
  return (
    <ToastProvider>
      <ToastViewport />
    </ToastProvider>
  )
}

