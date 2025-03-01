import Link from "next/link"
import Image from "next/image"
import logo from "@/public/logo-ngang.png"

export function Footer() {
  return (
    <footer className="bg-destructive text-white pt-8 pb-4">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <Link href="/" className="flex items-center">
              <Image src={logo} alt="Xpervia Logo" width={100} className="rounded-[14px]"/>
            </Link>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">About Xpervia</h3>
            <p className="text-gray-300">
              Xpervia is a modern e-learning platform designed to enhance online education through an engaging and
              interactive learning experience.
            </p>
          </div>
          <div>
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
          <div>
            <h3 className="text-lg font-semibold mb-4">Contact Us</h3>
            <p className="text-gray-300">Email: info@xpervia.com</p>
            <p className="text-gray-300">Phone: +1 (123) 456-7890</p>
          </div>
        </div>
        <div className="mt-8 py-4 border-t border-gray-700 text-center">
          <p className="text-gray-300">&copy; 2023 Xpervia. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

