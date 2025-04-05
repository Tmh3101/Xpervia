"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Users, BookOpen, DollarSign, ChevronDown, ChevronRight, Home } from "lucide-react"
import { cn } from "@/lib/utils"
import Image from "next/image"

interface SidebarItem {
  title: string
  href?: string
  icon: React.ReactNode
  submenu?: { title: string; href: string }[]
}

export function AdminSidebar() {
  const pathname = usePathname()
  const [openSection, setOpenSection] = useState<string | null>("management")

  const managementItems: SidebarItem[] = [
    {
      title: "Quản lý tài khoản",
      href: "/admin/users",
      icon: <Users className="h-5 w-5" />,
    },
    {
      title: "Quản lý khóa học",
      href: "/admin/courses",
      icon: <BookOpen className="h-5 w-5" />,
    },
  ]

  const statisticsItems: SidebarItem[] = [
    {
      title: "Thống kê người dùng",
      href: "/admin/statistics/users",
      icon: <Users className="h-5 w-5" />,
    },
    {
      title: "Thống kê khóa học & doanh thu",
      href: "/admin/statistics/revenue",
      icon: <DollarSign className="h-5 w-5" />,
    },
  ]

  const sections = [
    {
      id: "management",
      title: "Quản Lý",
      items: managementItems,
    },
    {
      id: "statistics",
      title: "Thống Kê",
      items: statisticsItems,
    },
  ]

  const toggleSection = (sectionId: string) => {
    setOpenSection(openSection === sectionId ? null : sectionId)
  }

  return (
    <div className="w-64 bg-white border-r border-gray-200 h-full flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <Link href="/admin" className="flex items-center">
          <Image src="/logo-ngang.png" alt="Xpervia Logo" width={150} height={40} className="mx-auto" />
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto py-4">
        <Link
          href="/admin"
          className={cn(
            "flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100",
            pathname === "/admin" && "bg-primary/10 text-primary font-medium",
          )}
        >
          <Home className="h-5 w-5 mr-3" />
          <span>Dashboard</span>
        </Link>

        {sections.map((section) => (
          <div key={section.id} className="mt-4">
            <button
              onClick={() => toggleSection(section.id)}
              className="flex items-center justify-between w-full px-4 py-2 text-gray-700 hover:bg-gray-100"
            >
              <span className="font-medium">{section.title}</span>
              {openSection === section.id ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </button>

            {openSection === section.id && (
              <div className="mt-1 pl-4">
                {section.items.map((item) => (
                  <Link
                    key={item.title}
                    href={item.href || "#"}
                    className={cn(
                      "flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md",
                      pathname === item.href && "bg-primary/10 text-primary font-medium",
                    )}
                  >
                    {item.icon}
                    <span className="ml-3">{item.title}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">Admin Dashboard v1.0</div>
      </div>
    </div>
  )
}

