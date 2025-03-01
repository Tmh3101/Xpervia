interface CategoryColor {
    category: string
    color: string
}

const categoryColors: CategoryColor[] = [
    { category: "Technology", color: "blue-500" },
    { category: "Mobile Development", color: "green-500" },
    { category: "Programming", color: "yellow-500" },
    { category: "Web Development", color: "red-500" },
    { category: "UI/UX", color: "purple-500" },
    { category: "Data Science", color: "green-500" },
    { category: "Design", color: "pink-500" },
    { category: "Marketing", color: "orange-500" },
    { category: "Business", color: "cyan-500" },
    { category: "Photography", color: "purple-500" },
    { category: "Art", color: "pink-500" },
    { category: "Security", color: "red-500" },
    { category: "AI/ML", color: "blue-500" },
    { category: "Video Editing", color: "indigo-500" }
]

export const getCategoryColor = (category: string) => {
    const color = categoryColors.find(c => c.category === category)
    return color?.color || "gray-500"
}