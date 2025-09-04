"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";
import { loginApi } from "@/lib/api/auth-api";
import {
  getEnrollmentsByStudentApi,
  enrollCourseApi,
} from "@/lib/api/enrollment-api";
import {
  getFavoritesByStudentApi,
  favoriteCourseApi,
  unfavoriteCourseApi,
} from "@/lib/api/favorite-api";
import type { User } from "@/lib/types/user";
import type { Enrollment } from "@/lib/types/enrollment";
import type { Favorite } from "@/lib/types/favorite";

interface AuthContextType {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  enrollments: Enrollment[];
  favorites: Favorite[];
  setAccessToken: (token: string | null) => void;
  setRefreshToken: (token: string | null) => void;
  setNewUser: (user: User | null) => void;
  fetchEnrollments: () => void;
  fetchFavorites: () => void;
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
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [favorites, setFavorites] = useState<Favorite[]>([]);
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
        fetchFavorites();
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

    const { access_token, refresh_token, user } = res;

    setAccessToken(access_token);
    setRefreshToken(refresh_token);
    setUser(user);

    handleRoleBasedRedirect(user.role);

    if (user.role === "student") {
      await fetchEnrollments();
      await fetchFavorites();
    }

    return { error: undefined };
  };

  const logout = () => {
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

  const fetchFavorites = async () => {
    if (accessToken) {
      try {
        const favorites = await getFavoritesByStudentApi();
        setFavorites(favorites);
      } catch (error) {
        console.error("Lỗi khi gọi API favorites:", error);
      }
    }
  };

  const toggleFavorite = (courseId: number): boolean => {
    if (!user || user.role !== "student") return false;

    const favoriteToRemove = favorites.some(
      (favorite) => favorite.course.id === courseId
    );

    if (favoriteToRemove) {
      const favoriteToRemove = favorites.find(
        (favorite) => favorite.course.id === courseId
      );
      if (favoriteToRemove) {
        unfavoriteCourseApi(favoriteToRemove.id)
          .then(() => {
            const updatedFavorites = favorites.filter(
              (fav) => fav.id !== favoriteToRemove.id
            );
            setFavorites(updatedFavorites);
          })
          .catch(() => false);
      }
    } else {
      favoriteCourseApi(courseId)
        .then((newFavorite) => {
          setFavorites([...favorites, newFavorite]);
        })
        .catch(() => false);
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
        enrollments,
        favorites,
        setNewUser,
        setAccessToken,
        setRefreshToken,
        fetchEnrollments,
        fetchFavorites,
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
