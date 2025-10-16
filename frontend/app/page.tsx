"use client";

import { useAuth } from "@/lib/auth-context";
import { useEffect, useState } from "react";
import { HeroSection } from "@/components/HeroSection";
import { SearchBar } from "@/components/SearchBar";
import { CourseList } from "@/components/course/CourseList";
import { getHomepageRecommendedCoursesApi } from "@/lib/api/course-api";
import { CoursePagination } from "@/components/CoursePagination";
import type { Course } from "@/lib/types/course";

export default function Home() {
  const [filteredCourses, setFilteredCourses] = useState<Course[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (user && user.role === "teacher") return;
    setIsLoading(true);
    getHomepageRecommendedCoursesApi(
      page,
      searchQuery,
      selectedCategory || undefined
    ).then((data) => {
      setCount(data.count);
      setFilteredCourses(data.results);
      setIsLoading(false);
    });
  }, [user, page, searchQuery, selectedCategory]);

  const handleCategorySelect = (categoryId: number | null) => {
    setPage(1);
    setSelectedCategory(categoryId);
  };

  const handleSearch = (query: string) => {
    setPage(1);
    setSearchQuery(query);
  };

  return (
    <main>
      <HeroSection />
      <SearchBar
        onSearch={handleSearch}
        onCategorySelect={handleCategorySelect}
      />
      <section className="container mx-auto pb-12 min-h-[400px]">
        <h2 className="text-3xl text-destructive font-bold mb-8 text-center">
          Khóa học hàng đầu
        </h2>
        {filteredCourses.length > 0 ? (
          <div>
            <CourseList courses={filteredCourses} isLoading={isLoading} />
            {count > 12 && (
              <CoursePagination
                currentPage={page}
                totalPages={Math.ceil(count / 12)}
                onPageChange={setPage}
              />
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-lg text-gray-500">
              Không tìm thấy khóa học phù hợp.
            </p>
          </div>
        )}
      </section>
    </main>
  );
}
