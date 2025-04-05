"use client"

import type { ReactNode } from "react"
import { AuthProvider } from "@/lib/auth-context"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { usePathname, redirect } from "next/navigation"
import { useEffect } from "react"
import { useAuth } from "@/lib/auth-context"
import { Inter } from 'next/font/google';
import logo from '@/public/logo-vuong.png'

const inter = Inter({ subsets: ['latin'] });

// Define protected route patterns
const PROTECTED_ROUTES = {
  student: /^\/student\//,
  admin: /^\/admin\//,
  teacher: /^\/teacher\//,
}

function RoleBasedProtection({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const pathname = usePathname()

  useEffect(() => {
    // Check if the current path matches any protected route pattern
    for (const [role, pattern] of Object.entries(PROTECTED_ROUTES)) {
      if (pattern.test(pathname)) {
        // If user is not logged in or doesn't have the required role, redirect to home
        if (!user || user.role !== role) {
          redirect("/")
        }
        break
      }
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
