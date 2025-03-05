"use client"

import { Badge } from "@/components/ui/badge"

const categoryColors: { [key: string]: string } = {
    "Technology": "bg-blue-500",
    "Mobile Development": "bg-green-500",
    "Programming": "bg-yellow-500",
    "Web Development": "bg-red-500",
    "Ui/ux": "bg-purple-500",
    "Data Science": "bg-pink-500",
    "Design": "bg-pink-500",
    "Marketing": "bg-orange-500",
    "Business": "bg-cyan-500",
    "Photography": "bg-purple-500",
    "Art": "bg-pink-500",
    "Security": "bg-red-500",
    "AI/ML": "bg-blue-500",
    "Video Editing": "bg-indigo-500"
}

interface CourseCategoriesProps {
    categories: string[]
}

export const CourseCategories = ({ categories }: CourseCategoriesProps) => {
    return (
        <>
            {categories.map((category, index) => (
                <Badge
                    key={index}
                    variant="secondary"
                    className={`text-[10px] ${categoryColors[category] || "bg-gray-500"} text-white`}
                >
                    {category}
                </Badge>
            ))}
        </>
    )
}