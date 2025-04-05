import { Loader2 } from "lucide-react"

export function Loading() {
  return (
    <div className="flex flex-col items-center justify-center h-[600px]">
      <Loader2 className="h-8 w-8 animate-spin text-primary mb-2" />
      <p className="text-gray-600 font-medium">Đang tải...</p>
    </div>
  )
}