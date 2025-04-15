import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value) // Assuming the input is in thousands
}

// Format date "2025-03-02T09:35:23.388805Z" to "2025-03-02"
export function formatDate(date: string): string {
  const dateObj = new Date(date)
  return dateObj.toISOString().split("T")[0]
}

const categoryColors = ['blue', 'green', 'yellow', 'red', 'purple', 'pink', 'orange', 'cyan', 'indigo']
export const getCategoryColor = (index: number) => categoryColors[index] || 'gray'
