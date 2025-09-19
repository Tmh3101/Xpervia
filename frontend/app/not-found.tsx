import Image from "next/image";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import notFoundImage from "@/public/404_notfound.png";

export default function NotFound() {
  return (
    <main className="mt-[80px] flex-grow flex flex-col items-center justify-center px-4 py-16">
      <div className="max-w-md w-full text-center">
        <Image
          src={notFoundImage}
          alt="404 Not Found"
          width={400}
          height={400}
          className="mx-auto mb-6"
        />
        <h1 className="text-3xl font-bold mb-2">Không tìm thấy trang</h1>
        <p className="text-gray-600 mb-8">
          Trang này có thể đã bị ẩn hoặc không tồn tại.
        </p>
        <Link href="/">
          <Button className="px-6 py-2 rounded-lg">Trờ về trang chủ</Button>
        </Link>
      </div>
    </main>
  );
}
