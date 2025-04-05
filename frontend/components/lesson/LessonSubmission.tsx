"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { submitAssignmentApi, deleteSubmissionApi } from "@/lib/api/submission-api"
import { Loader2, Upload, X, Download } from "lucide-react"
import { getGoogleDriveDownloadFileUrl } from "@/lib/google-drive-url"
import { getGoogleDriveFileUrl } from "@/lib/google-drive-url"
import { Submission } from "@/lib/types/submission"

interface LessonSubmissionProps {
  assignmentId: number
  submission: Submission | null
}

export function LessonSubmission({ assignmentId, submission }: LessonSubmissionProps) {
  const [file, setFile] = useState<File | null>(null)
  const [content, setContent] = useState("")
  const [isUploading, setIsUploading] = useState(false)
  const [currentSubmission, setCurrentSubmission] = useState<Submission | null>(submission)
  const [isOpenSubmissionDialog, setIsOpenSubmissionDialog] = useState(false)
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

    try {
      if (!file) {
        return
      }
      const response = await submitAssignmentApi(assignmentId, file)
      setCurrentSubmission(response)
      setFile(null)
      setContent("")
    } catch (error) {
      console.error("Error submitting assignment:", error)
    } finally {
      setIsUploading(false)
    }
  }

  const handleDelete = async () => {

    if (!currentSubmission) return

    setIsDeleting(true)

    try {
      await deleteSubmissionApi(currentSubmission.id)
      setCurrentSubmission(null)
    } catch (error) {
      console.error("Error deleting submission:", error)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleDownload = () => {
    if (currentSubmission) {
      window.open(getGoogleDriveDownloadFileUrl(currentSubmission.file.file_id), "_blank")
    }
  }

  if (currentSubmission) {
    return (
      <>
        <div className="mt-4 p-4 border rounded-lg bg-gray-50">
          <div className="flex justify-between items-start">
            <div>
              <h3
                className="font-medium text-gray-800 hover:text-primary hover:underline cursor-pointer"
                onClick={() => setIsOpenSubmissionDialog(true)}
              >
                {currentSubmission.file.file_name}
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                Đã nộp vào {new Date(currentSubmission.created_at).toLocaleString()}
              </p>
            </div>
            {currentSubmission.submission_score ? (
              <div className="items-center">
                <div className="min-w-[80px] text-center">
                  <span className="text-lg font-semibold text-success">{currentSubmission.submission_score.score}/100</span>
                </div>
                <span className="text-sm text-muted-foreground">
                  {new Date(currentSubmission.submission_score.created_at).toLocaleString()}
                </span>
              </div>
            ) : (
              <div className="flex items-center">
                <Button
                  size="sm"
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="bg-red-500 text-white mr-2 hover:bg-red-600"
                >
                  {isDeleting ? 
                    <Loader2 className="w-4 h-4 animate-spin" />
                    :
                    <X className="w-4 h-4" />
                  }
                </Button>
                {currentSubmission && (
                  <Button
                    size="sm"
                    className="bg-primary text-white flex items-center gap-2 hover:bg-secondary"
                    onClick={handleDownload}
                  >
                    <Download className="w-4 h-4" />
                  </Button>
                )}
              </div>
            )}
          </div>
          {currentSubmission.submission_score && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold italic">Nhận xét từ giảng viên:</h4>
              <p className="text-sm text-muted-foreground bg-muted p-3 rounded-lg">
                {currentSubmission.submission_score.feedback}
              </p>
            </div>
          )}
        </div>

        <Dialog open={!!isOpenSubmissionDialog} onOpenChange={() => setIsOpenSubmissionDialog(false)}>
        <DialogContent className="max-w-4xl h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center justify-between mt-3">
              <span className="text-lg font-semibold">{currentSubmission.file.file_name}</span>
              <Button
                variant="outline"
                size="sm"
                className="bg-primary text-white flex items-center gap-2"
                onClick={handleDownload}
              >
                <Download className="w-4 h-4" />
                Download
              </Button>
            </DialogTitle>
          </DialogHeader>
          <div className="flex-1 w-full min-h-0 -mt-[220px] h-auto">
            <iframe
              src={getGoogleDriveFileUrl(currentSubmission.file.file_id)}
              className="w-full h-full rounded-md"
              allow="autoplay"
            />
          </div>
        </DialogContent>
      </Dialog>

      </>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4">
      <div className="space-y-4">
        <div>
          <label htmlFor="file" className="block text-sm font-medium mb-1">
            Upload bài nộp
          </label>
          <div className="flex items-center space-x-2">
            <Button type="submit" disabled={isUploading || (!file && !content)}>
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Đang tải...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Nộp bài
                </>
              )}
            </Button>
            <input
              id="file"
              type="file"
              onChange={handleFileChange}
              disabled={isUploading}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border file:border-primary file:text-sm file:font-semibold file:bg-white file:text-primary hover:file:bg-primary/10"
            />
          </div>
        </div>
      </div>
    </form>
  )
}

