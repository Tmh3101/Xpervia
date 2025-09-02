"use client";

import { Button } from "@/components/ui/button";
import { User } from "lucide-react";
import Image from "next/image";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { AuthModal } from "@/components/auth/AuthModal";
import { PaymentModal } from "./PaymentModal";
import { useRouter } from "next/navigation";
import { CourseCategories } from "@/components/course/CourseCategories";

interface CourseHeroProps {
  id: number;
  title: string;
  currentPrice: number;
  originalPrice: number;
  discount: number;
  teacher: string;
  bannerImageUrl: string;
  categories: string[];
  onEnrollSuccess: () => void;
}

export function CourseHero({
  id,
  title,
  currentPrice,
  originalPrice,
  discount,
  teacher,
  bannerImageUrl,
  categories,
  onEnrollSuccess,
}: CourseHeroProps) {
  const { user, enrollInCourse } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const router = useRouter();
  const isFree = originalPrice === 0 || currentPrice === 0;

  const handleBuyClick = () => {
    if (!user) {
      setShowAuthModal(true);
    } else {
      if (isFree) {
        handlePaymentSuccess();
      } else {
        setShowPaymentModal(true);
      }
    }
  };

  const handlePaymentSuccess = () => {
    try {
      const success = enrollInCourse(id);
      console.log("Enroll success", success);
      if (success) {
        onEnrollSuccess();
      } else {
        console.error("Failed to enroll in course");
      }
    } catch (error) {
      console.error("Error during enrollment", error);
    }
  };

  return (
    <>
      <div className="relative">
        <Image
          src={bannerImageUrl || "/placeholder.svg"}
          alt={title}
          width={1920}
          height={500}
          className="w-full h-[500px] object-cover"
        />
        <div className="absolute inset-0 bg-black/50" />
        <div className="container mx-auto px-4">
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 w-full max-w-4xl">
            <div className="bg-white rounded-xl p-6 shadow-lg">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                  <div className="mb-2 flex flex-wrap gap-1">
                    <CourseCategories categories={categories} />
                  </div>
                  <h1 className="text-2xl text-destructive font-bold mb-2">
                    {title}
                  </h1>
                  <div className="flex items-center mb-2 mt-2">
                    <User className="w-4 h-4 mr-2 text-primary" />
                    <div className="text-primary font-medium">{teacher}</div>
                  </div>
                </div>
                <div className="flex flex-col items-end">
                  <div className="flex items-center gap-2 mb-2 w-full">
                    {isFree ? (
                      <span className="text-2xl text-primary font-bold w-full text-center">
                        Miễn phí
                      </span>
                    ) : (
                      <>
                        <span className="text-3xl text-destructive font-bold">
                          {currentPrice.toLocaleString("vi-VN")} ₫
                        </span>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-sm text-gray-500 line-through">
                            {originalPrice.toLocaleString("vi-VN")} ₫
                          </span>
                          <span className="text-[10px] font-semibold text-white bg-red-500 px-1 rounded-full">
                            -{discount * 100}%
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                  <Button
                    className="w-[200px] bg-[#1ABC9C] hover:bg-[#1ABC9C]/90 rounded-full"
                    onClick={handleBuyClick}
                  >
                    Tham gia ngay
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        defaultView="login"
      />

      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        onSuccess={handlePaymentSuccess}
        courseTitle={title}
        price={currentPrice}
      />
    </>
  );
}
