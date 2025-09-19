"use client";

import React from "react";

interface VideoPlayerProps {
  videoUrl: string;
}

export function VideoPlayer({ videoUrl }: VideoPlayerProps) {
  return (
    <div className="relative w-full pt-[56.25%] bg-black rounded-lg overflow-hidden">
      <iframe
        src={videoUrl}
        allow="autoplay; fullscreen"
        className="absolute top-0 left-0 w-full h-full"
      />
    </div>
  );
}
