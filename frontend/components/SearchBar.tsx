import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export function SearchBar() {
  return (
    <div className="container mx-auto -mt-20 mb-12 relative z-10 max-w-3xl">
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4 text-destructive">Bạn muốn học gì hôm nay?</h2>
        <div className="flex gap-4">
          <div className="relative flex-grow">
            <Input
              type="text"
              placeholder="Khóa học, kỹ năng, thể loại..."
              className="pl-10 pr-4 py-2 w-full rounded-xl"
            />
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          </div>
          <Button className="bg-primary hover:bg-secondary rounded-xl px-6 py-2 text-sm">Tìm kiếm</Button>
        </div>
      </div>
    </div>
  )
}

