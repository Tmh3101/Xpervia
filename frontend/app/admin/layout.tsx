import type React from "react"
import { AdminSidebar } from "@/components/admin/AdminSidebar"
import { Toaster } from "@/components/ui/toaster"

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen bg-gray-100">
      <AdminSidebar />
      <div className="flex-1 overflow-auto">
        <main className="py-6 px-12">{children}</main>
      </div>
      <Toaster />
    </div>
  )
}