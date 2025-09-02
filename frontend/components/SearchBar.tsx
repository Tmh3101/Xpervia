"use client";

import type React from "react";
import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getCategoriesApi } from "@/lib/api/category-api";
import type { Category } from "@/lib/types/course-content";
import { getCategoryColor } from "@/lib/utils";

interface SearchBarProps {
  onSearch: (query: string) => void;
  onCategorySelect: (categoryId: number | null) => void;
}

export function SearchBar({ onSearch, onCategorySelect }: SearchBarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    const fetchCategories = async () => {
      // if (user && user.role === "teacher") return;

      try {
        const categoriesData = await getCategoriesApi();
        setCategories(categoriesData);
      } catch (error) {
        console.error("Failed to fetch categories:", error);
      }
    };

    fetchCategories();
  }, []);

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      onSearch(searchQuery);
    }
  };

  const handleSearchInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  const handleSearch = () => {
    onSearch(searchQuery);
  };

  const handleCategorySelect = (categoryId: number | null) => {
    setSelectedCategory(categoryId);
    onCategorySelect(categoryId);
  };

  return (
    <div className="container mx-auto -mt-20 mb-8 relative z-10 w-full">
      <div className="bg-white rounded-2xl shadow-lg p-6 max-w-3xl mx-auto">
        <h2 className="text-xl font-bold mb-4 text-destructive">
          Bạn muốn học gì hôm nay?
        </h2>
        <div className="flex gap-4">
          <div className="relative flex-grow">
            <Input
              type="text"
              placeholder="Tên khóa học..."
              className="pl-10 pr-4 py-2 w-full rounded-xl"
              value={searchQuery}
              onKeyDown={handleKeyDown}
              onChange={handleSearchInput}
            />
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          </div>
          <Button
            className="bg-primary hover:bg-secondary rounded-xl px-6 py-2 text-sm"
            onClick={handleSearch}
          >
            Tìm kiếm
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mt-4 justify-center">
        <button
          onClick={() => handleCategorySelect(null)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            selectedCategory === null
              ? "bg-gray-500 text-white"
              : "bg-gray-100 text-gray-500"
          }`}
        >
          Tất cả
        </button>
        {categories.map((category, index) => (
          <button
            key={category.id}
            onClick={() => handleCategorySelect(category.id)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              selectedCategory === category.id
                ? `bg-${getCategoryColor(index)}-500 text-white`
                : `bg-${getCategoryColor(index)}-100 text-${getCategoryColor(
                    index
                  )}-500`
            }`}
          >
            {category.name}
          </button>
        ))}
      </div>
    </div>
  );
}
