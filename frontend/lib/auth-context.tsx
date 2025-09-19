"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";
import { loginApi, getMe } from "@/lib/api/auth-api";
import { enrollCourseApi } from "@/lib/api/enrollment-api";
import { favoriteCourseApi, unfavoriteCourseApi } from "@/lib/api/favorite-api";
import type { User } from "@/lib/types/user";

interface AuthContextType {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  enrolledCourseIds: number[];
  favoritedCourseIds: number[];
  setAccessToken: (token: string | null) => void;
  setRefreshToken: (token: string | null) => void;
  setNewUser: (user: User | null) => void;
  login: (email: string, password: string) => Promise<{ error?: string }>;
  logout: () => void;
  enrollInCourse: (courseId: number) => boolean;
  toggleFavorite: (courseId: number) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [enrolledCourseIds, setEnrolledCourseIds] = useState<number[]>([]);
  const [favoritedCourseIds, setFavoritedCourseIds] = useState<number[]>([]);
  const router = useRouter();
  const pathname = usePathname();

  // Load user data from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const storedAccessToken = localStorage.getItem("accessToken");
    const storedRefreshToken = localStorage.getItem("refreshToken");

    if (storedUser && storedAccessToken && storedRefreshToken) {
      let isReload = false;

      if (JSON.parse(storedUser) !== user) {
        setUser(JSON.parse(storedUser));
        isReload = true;
      }

      if (storedAccessToken !== accessToken) {
        setAccessToken(storedAccessToken);
        isReload = true;
      }

      if (storedRefreshToken !== refreshToken) {
        setRefreshToken(storedRefreshToken);
        isReload = true;
      }

      if (isReload && JSON.parse(storedUser).role === "student") {
        getMe().then((data) => {
          setEnrolledCourseIds(data.enrollment_ids);
          setFavoritedCourseIds(data.favorite_ids);
        });
      }
    }
  }, []);

  // Update user data to localStorage when it changes
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

    setAccessToken(res.access_token);
    setRefreshToken(res.refresh_token);
    setUser(res.user);

    handleRoleBasedRedirect(res.user.role);

    if (res.user.role === "student") {
      setEnrolledCourseIds(res.enrollment_ids);
      setFavoritedCourseIds(res.favorite_ids);
    }

    return { error: undefined };
  };

  const logout = () => {
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    setEnrolledCourseIds([]);
    setFavoritedCourseIds([]);
    localStorage.removeItem("user");
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    router.push("/");
  };

  const enrollInCourse = (courseId: number): boolean => {
    if (!user || user.role !== "student") return false;
    enrollCourseApi(courseId);
    setEnrolledCourseIds([...enrolledCourseIds, courseId]);
    return true;
  };

  const toggleFavorite = (courseId: number): boolean => {
    if (!user || user.role !== "student") return false;

    const favoritedCourseIdToRemove = favoritedCourseIds.find(
      (id) => id === courseId
    );

    if (favoritedCourseIdToRemove) {
      unfavoriteCourseApi(favoritedCourseIdToRemove);
      const updatedFavorites = favoritedCourseIds.filter(
        (id) => id !== favoritedCourseIdToRemove
      );
      setFavoritedCourseIds(updatedFavorites);
    } else {
      favoriteCourseApi(courseId);
      setFavoritedCourseIds([...favoritedCourseIds, courseId]);
    }
    return true;
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
        enrolledCourseIds,
        favoritedCourseIds,
        setNewUser,
        setAccessToken,
        setRefreshToken,
        login,
        logout,
        enrollInCourse,
        toggleFavorite,
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
