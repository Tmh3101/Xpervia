"use client"

import { Badge } from "@/components/ui/badge"
import { getCategoryColor } from "@/lib/utils"

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
                    className={`text-[10px] bg-${getCategoryColor(index)}-500 text-white hover:bg-${getCategoryColor(index)}-600 hover:text-white`}
                >
                    {category}
                </Badge>
            ))}
        </>
    )
}