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

// Format date in the format of "yyyy-MM-dd" to "dd/MM/yyyy" - e.g. "2025-03-02T09:35:23.388805Z" to "02/03/2025"
export function formatDate(date: string): string {
  const d = new Date(date)
  return d.toLocaleDateString("vi-VN")
}

const categoryColors = ['blue', 'green', 'yellow', 'red', 'purple', 'pink', 'orange', 'cyan', 'indigo']
export const getCategoryColor = (index: number) => categoryColors[index] || 'gray'
