"use client"

import type React from "react"

interface AssignmentData {
  title: string
  content: string
}

export function LessonAssignment({ title, content }: AssignmentData) {

  return (
    <div className="mt-2">
      <h3 className="text-lg text-destructive font-semibold mb-2">{title}</h3>
        <div className="space-y-4">
          <p className="text-sm text-gray-600">{content}</p>
        </div>
    </div>
  )
}

