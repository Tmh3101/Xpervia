"use client";

import Image from "next/image";
import { User, Edit2, Eye, Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardFooter,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import type { Course } from "@/lib/types/course";
import type { Favorite } from "@/lib/types/favorite";
import { CourseCategories } from "@/components/course/CourseCategories";

interface CourseCardProps extends Course {
  mode?: "enrolled" | "teacher" | "student";
  progress?: number | 0;
  studentsEnrolled?: number;
  onEditClick?: () => void;
}

export function CourseCard({
  id,
  course_content,
  price,
  discount,
  is_visible,
  created_at,
  start_date,
  regis_start_date,
  regis_end_date,
  max_students,
  mode = "student",
  progress = 0,
  studentsEnrolled = 0,
  onEditClick,
}: CourseCardProps) {
  const router = useRouter();
  const currentPrice = price * (1 - discount);
  const isFree = price === 0 || currentPrice === 0;
  const hasStarted = new Date() >= new Date(regis_start_date);
  const { favorites, toggleFavorite, user } = useAuth();

  const handleClick = () => {
    if (mode === "teacher") {
      router.push(`/teacher/courses/${id}`);
    } else if (mode === "enrolled") {
      router.push(`/student/lessons/${id}`);
    } else {
      router.push(`/courses/${id}`);
    }
  };

  const isFavorite = (favorites as Favorite[] | undefined)?.some(
    (f: Favorite) => f.course.id === id
  );
  return (
    <Card className="overflow-hidden rounded-2xl border-0 shadow-lg flex flex-col">
      <CardHeader className="p-0 relative">
        <div className="w-full aspect-video overflow-hidden">
          <Image
            src={course_content.thumbnail_url || "/placeholder.svg"}
            alt="thumbnail"
            fill
            className="object-cover"
            priority
          />
        </div>
        <div className="absolute top-0 left-2 flex flex-wrap gap-1">
          <CourseCategories
            categories={course_content.categories.map((c) => c.name)}
          />
        </div>
        {/* Nút yêu thích cho student */}
        {(mode === "student" || mode === "enrolled") && user && (
          <button
            className="absolute top-[2px] right-2 z-10 p-2 rounded-full bg-white/25 shadow-md hover:scale-110 transition-all"
            onClick={(e) => {
              e.stopPropagation();
              toggleFavorite?.(id);
            }}
            aria-label={isFavorite ? "Bỏ yêu thích" : "Yêu thích"}
          >
            <Heart
              className={`w-5 h-5 transition-all duration-200 ${
                isFavorite && "scale-110"
              }`}
              color={isFavorite ? "#FFD600" : "#17A0F0"}
            />
          </button>
        )}
      </CardHeader>
      <CardContent className="px-4 pt-2 pb-0 flex-grow">
        <h3 className="font-bold text-lg/[1.5rem] text-destructive mb-1 line-clamp-2">
          {course_content.title}
        </h3>
        {mode !== "teacher" ? (
          <div className="flex items-center mb-1">
            <User className="w-4 h-4 mr-2 text-primary" />
            <span className="text-sm font-medium text-primary">
              {course_content.teacher.first_name +
                " " +
                course_content.teacher.last_name}
            </span>
          </div>
        ) : (
          ""
        )}
        <p className="text-sm text-gray-600 line-clamp-2">
          {course_content.description}
        </p>
      </CardContent>
      <CardFooter
        className={`p-4 pt-2 ${
          mode === "student"
            ? "items-center justify-between"
            : "flex flex-col gap-2"
        }`}
      >
        {mode === "teacher" ? (
          <div className="flex gap-2 w-full mt-2">
            <Button
              className="flex-1 bg-primary hover:bg-primary/90 rounded-full text-sm"
              onClick={() => router.push(`/teacher/courses/${id}/detail`)}
            >
              <Eye className="w-4 h-4 mr-2" />
              Chi tiết
            </Button>
            <Button
              variant="outline"
              className="flex-1 hover:bg-primary/10 rounded-full text-sm"
              onClick={onEditClick}
            >
              <Edit2 className="w-4 h-4 mr-2" />
              Sửa
            </Button>
          </div>
        ) : mode === "enrolled" ? (
          <>
            <div className="w-full flex flex-row gap-2 justify-between items-center mr-2">
              <span className="ml-2 text-sm text-success">{progress}%</span>
              <Progress value={progress} />
            </div>
            <Button
              className="w-full bg-success hover:bg-success/90 rounded-full text-sm"
              onClick={handleClick}
            >
              Tiếp tục
            </Button>
          </>
        ) : (
          <>
            {hasStarted ? (
              <>
                <div className="flex flex-col items-start">
                  {isFree ? (
                    <span className="text-xl text-primary font-bold">
                      Miễn phí
                    </span>
                  ) : (
                    <>
                      {discount > 0 && (
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-sm text-gray-500 line-through">
                            {price.toLocaleString("vi-VN")} ₫
                          </span>
                          <span className="text-[10px] font-semibold text-white bg-red-500 px-1 rounded-full">
                            -{discount * 100}%
                          </span>
                        </div>
                      )}
                      <span className="text-2xl text-destructive font-bold">
                        {currentPrice.toLocaleString("vi-VN")} ₫
                      </span>
                    </>
                  )}
                </div>
                <Button
                  className="bg-primary hover:bg-secondary rounded-full text-sm mt-auto"
                  onClick={handleClick}
                >
                  Tham gia
                </Button>
              </>
            ) : (
              <div className="flex flex-row gap-2 items-center">
                <span className="text-lg text-gray-500 font-bold">
                  Mở đăng ký vào:
                </span>
                <span className="text-xl text-primary font-bold">
                  {new Date(regis_start_date).toLocaleDateString("vi-VN", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric",
                  })}
                </span>
              </div>
            )}
          </>
        )}
      </CardFooter>
    </Card>
  );
}
