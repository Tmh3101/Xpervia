"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";
import { loginApi } from "@/lib/api/auth-api";
import {
  getEnrollmentsByStudentApi,
  enrollCourseApi,
} from "@/lib/api/enrollment-api";
import type { User } from "@/lib/types/user";
import type { Enrollment } from "@/lib/types/enrollment";

interface AuthContextType {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  setNewUser: (user: User | null) => void;
  setAccessToken: (token: string | null) => void;
  setRefreshToken: (token: string | null) => void;
  login: (email: string, password: string) => Promise<{ error?: string }>;
  logout: () => void;
  enrollments: Enrollment[];
  enrollInCourse: (courseId: number) => boolean;
  fetchEnrollments: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const storedAccessToken = localStorage.getItem("accessToken");
    const storedRefreshToken = localStorage.getItem("refreshToken");

    if (storedUser && storedAccessToken && storedRefreshToken) {
      setUser(JSON.parse(storedUser));
      setAccessToken(storedAccessToken);
      setRefreshToken(storedRefreshToken);
    }
  }, []);

  useEffect(() => {
    if (user && accessToken && refreshToken) {
      localStorage.setItem("user", JSON.stringify(user));
      localStorage.setItem("accessToken", accessToken);
      localStorage.setItem("refreshToken", refreshToken);
    } else {
      localStorage.removeItem("user");
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
    }
  }, [user, accessToken, refreshToken]);

  // Handle role-based routing after login
  const handleRoleBasedRedirect = (role: User["role"]) => {
    switch (role) {
      case "admin":
        router.push("/admin");
        break;
      case "teacher":
        router.push("/teacher");
        break;
      case "student":
        router.push(pathname);
        break;
      default:
        router.push("/");
    }
  };

  const login = async (email: string, password: string) => {
    const res = await loginApi({ email, password });
    if (res.error) {
      return { error: res.error };
    }

    const { access_token, refresh_token, user } = res;

    setAccessToken(access_token);
    setRefreshToken(refresh_token);
    setUser(user);

    localStorage.setItem("accessToken", access_token);
    localStorage.setItem("refreshToken", refresh_token);
    localStorage.setItem("user", JSON.stringify(user));

    handleRoleBasedRedirect(user.role);

    if (user.role === "student") {
      await fetchEnrollments();
    }

    return { error: undefined };
  };

  const logout = async () => {
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    setEnrollments([]);
    router.push("/");
  };

  const enrollInCourse = (courseId: number): boolean => {
    if (!user || user.role !== "student") return false;
    enrollCourseApi(courseId)
      .then(() => fetchEnrollments())
      .catch(() => false);
    return true;
  };

  const fetchEnrollments = async () => {
    if (accessToken) {
      try {
        const enrollments = await getEnrollmentsByStudentApi();
        setEnrollments(enrollments);
      } catch (error) {
        console.error("Lỗi khi gọi API enrollments:", error);
      }
    }
  };

  const setNewUser = (user: User | null) => {
    setUser(user);
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      localStorage.removeItem("user");
    }
  };

  return (
    <AuthContext.Provider
      value={{
        accessToken,
        refreshToken,
        user,
        setNewUser,
        setAccessToken,
        setRefreshToken,
        login,
        logout,
        enrollments,
        enrollInCourse,
        fetchEnrollments,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
