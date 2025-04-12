"use client"

import type { ReactNode } from "react"
import { AuthProvider } from "@/lib/auth-context"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { usePathname, useRouter } from "next/navigation"
import { useEffect } from "react"
import { useAuth } from "@/lib/auth-context"
import { Inter } from 'next/font/google';
import logo from '@/public/logo-vuong.png'
import { authorizeWith } from "@/lib/authorize"

const inter = Inter({ subsets: ['latin'] });

export function RoleBasedProtection({ children }: { children: React.ReactNode }) {
  const { user } = useAuth()
  const pathname = usePathname()
  const router = useRouter()

  useEffect(() => {
    const role = user?.role || "guest"
    const authorization = authorizeWith(pathname, role)

    if (authorization === "not-found") {
      router.push("/404") // Điều hướng đến trang 404
      return
    }

    if (authorization === "not-allowed") {
      const redirectMap: Record<string, string> = {
        student: "/",
        teacher: "/teacher",
        admin: "/admin",
        guest: "/",
      }
      router.push(redirectMap[role] || "/")
    }
  }, [pathname, user])

  return <>{children}</>
}

export default function RootLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <html lang="en">
      <head>
          <title>Xpervia</title>
          <meta charSet="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <link rel="icon" href={logo.src} />
      </head>
      <body className={inter.className}>
          <AuthProvider>
            <RoleBasedProtection>
              <div className="min-h-screen bg-white">
                {
                  pathname.startsWith('/admin') ? (
                    <>{children}</>
                  ) : (
                    <>
                      <Header />
                      {children}
                      <Footer />
                    </>
                  )
                }
              </div>
            </RoleBasedProtection>
          </AuthProvider>
        </body>
    </html>
  )
}



import './globals.css'

// export const metadata = {
//       generator: 'v0.dev'
//     };
