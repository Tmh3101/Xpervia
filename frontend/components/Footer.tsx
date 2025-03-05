import Link from "next/link"
import Image from "next/image"
import logo from "@/public/logo-ngang.png"

export function Footer() {
  return (
    <footer className="bg-destructive text-white pt-8 pb-4">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-6 gap-12">
          <div className="col-span-1">
            <Link href="/" className="flex items-center">
              <Image src={logo} alt="Xpervia Logo" width={100} className="rounded-[14px]"/>
            </Link>
          </div>
          <div className="col-span-2">
            <h3 className="text-lg font-semibold mb-4">Thông tin chung</h3>
            <p className="text-gray-300 text-justify">
              Xpervia – Không chỉ là học tập, mà còn là hành trình trải nghiệm và chinh phục tri thức theo cách thông minh nhất.
            </p>
          </div>
          <div className="col-span-1">
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/courses" className="text-gray-300 hover:text-[#1E88E5]">
                  Courses
                </Link>
              </li>
              <li>
                <Link href="/instructors" className="text-gray-300 hover:text-[#1E88E5]">
                  Instructors
                </Link>
              </li>
              <li>
                <Link href="/about" className="text-gray-300 hover:text-[#1E88E5]">
                  About Us
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-gray-300 hover:text-[#1E88E5]">
                  Contact
                </Link>
              </li>
            </ul>
          </div>
          <div className="col-span-2">
            <h3 className="text-lg font-semibold mb-4">Liên hệ</h3>
            <p className="text-gray-300">Email: info@xpervia.com</p>
            <p className="text-gray-300">SĐT: +1 (123) 456-7890</p>
          </div>
        </div>
        <div className="mt-8 py-4 border-t border-gray-700 text-center">
          <p className="text-gray-300">&copy; 2023 Xpervia. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

