"use client"

import React from "react"
import { getGoogleDriveVideoUrl } from "@/lib/google-drive-url"

interface VideoPlayerProps {
  videoId: string
}

export function VideoPlayer({ videoId }: VideoPlayerProps) {
  return (
    <div className="relative w-full pt-[56.25%] bg-black rounded-lg overflow-hidden">
      <iframe
        src={getGoogleDriveVideoUrl(videoId) || "/placeholder.svg"}
        allow="autoplay; fullscreen"
        className="absolute top-0 left-0 w-full h-full"
      />
    </div>
  )
}

