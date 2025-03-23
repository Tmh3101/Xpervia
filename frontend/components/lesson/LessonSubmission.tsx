"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Progress } from "@/components/ui/progress"
import { createSubmissionApi, deleteSubmissionApi } from "@/lib/api/submission-api"
import { Loader2, Upload, X, Download } from "lucide-react"

interface LessonSubmissionProps {
  assignmentId: number
  submission?: any
  onLoadingChange?: (isLoading: boolean) => void
}

export function LessonSubmission({ assignmentId, submission, onLoadingChange }: LessonSubmissionProps) {
  const [file, setFile] = useState<File | null>(null)
  const [content, setContent] = useState("")
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [currentSubmission, setCurrentSubmission] = useState(submission)
  const [isDeleting, setIsDeleting] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file && !content) return

    setIsUploading(true)
    if (onLoadingChange) onLoadingChange(true)

    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 95) {
          clearInterval(progressInterval)
          return 95
        }
        return prev + 5
      })
    }, 200)

    try {
      const formData = new FormData()
      if (file) formData.append("file", file)
      formData.append("content", content)

      const response = await createSubmissionApi(assignmentId, formData)
      setCurrentSubmission(response)
      setFile(null)
      setContent("")
    } catch (error) {
      console.error("Error submitting assignment:", error)
    } finally {
      clearInterval(progressInterval)
      setUploadProgress(100)
      setTimeout(() => {
        setUploadProgress(0)
        setIsUploading(false)
        if (onLoadingChange) onLoadingChange(false)
      }, 500)
    }
  }

  const handleDelete = async () => {
    if (!currentSubmission) return

    setIsDeleting(true)
    if (onLoadingChange) onLoadingChange(true)

    try {
      await deleteSubmissionApi(currentSubmission.id)
      setCurrentSubmission(null)
    } catch (error) {
      console.error("Error deleting submission:", error)
    } finally {
      setIsDeleting(false)
      if (onLoadingChange) onLoadingChange(false)
    }
  }

  if (currentSubmission) {
    return (
      <div className="mt-4 p-4 border rounded-lg bg-gray-50">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-medium">Bài nộp của bạn</h3>
            <p className="text-sm text-gray-500 mt-1">
              Đã nộp vào {new Date(currentSubmission.created_at).toLocaleString()}
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={handleDelete} disabled={isDeleting}>
            {isDeleting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <X className="w-4 h-4 mr-2" />}
            Xóa bài nộp
          </Button>
        </div>
        {currentSubmission.content && (
          <div className="mt-2">
            <p className="text-sm">{currentSubmission.content}</p>
          </div>
        )}
        {currentSubmission.file && (
          <div className="mt-2">
            <a
              href={currentSubmission.file.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center text-sm text-blue-600 hover:underline"
            >
              <Download className="w-4 h-4 mr-1" />
              {currentSubmission.file.name}
            </a>
          </div>
        )}
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4">
      <div className="space-y-4">
        <div>
          <label htmlFor="content" className="block text-sm font-medium mb-1">
            Nội dung bài nộp
          </label>
          <Textarea
            id="content"
            placeholder="Nhập nội dung bài nộp của bạn"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            disabled={isUploading}
          />
        </div>
        <div>
          <label htmlFor="file" className="block text-sm font-medium mb-1">
            Tệp đính kèm
          </label>
          <input
            id="file"
            type="file"
            onChange={handleFileChange}
            disabled={isUploading}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-primary/90"
          />
          {file && <p className="mt-1 text-sm text-gray-500">{file.name}</p>}
        </div>
        {uploadProgress > 0 && (
          <div className="space-y-1">
            <div className="flex justify-between text-sm">
              <span>Đang tải lên...</span>
              <span>{uploadProgress}%</span>
            </div>
            <Progress value={uploadProgress} className="h-2" />
          </div>
        )}
        <Button type="submit" disabled={isUploading || (!file && !content)}>
          {isUploading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              Đang tải lên...
            </>
          ) : (
            <>
              <Upload className="w-4 h-4 mr-2" />
              Nộp bài
            </>
          )}
        </Button>
      </div>
    </form>
  )
}

