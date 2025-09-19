"use client";

import { Course } from "@/lib/types/course";
import { CourseCard } from "@/components/course/CourseCard";
import { Loading } from "../Loading";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

interface CourseSliderProps {
  courses: Course[];
}

export function CourseSlider({ courses }: CourseSliderProps) {
  if (courses.length === 0) {
    return <Loading />;
  }

  return (
    <div className="w-full bg-white mt-8">
      <h2 className="text-2xl font-bold text-destructive mb-4">
        Khóa học tương tự
      </h2>
      <Carousel>
        <CarouselContent className="px-1">
          {courses.map((course) => (
            <CarouselItem
              key={course.id}
              className="md:basis-1/2 lg:basis-1/5 pb-3"
            >
              <CourseCard {...course} mode="student" />
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselNext className="p-5 right-[-28px] hover:text-primary hover:bg-white shadow-md" />
        <CarouselPrevious className="p-5 left-[-28px] hover:text-primary hover:bg-white shadow-md" />
      </Carousel>
    </div>
  );
}
