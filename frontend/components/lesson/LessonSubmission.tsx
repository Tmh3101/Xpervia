"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Upload, X, FileText, Download } from "lucide-react"
import { format } from "date-fns"
import { getGoogleDriveDownloadFileUrl } from "@/lib/google-drive-url"
import { submitAssignmentApi, deleteSubmissionApi } from "@/lib/api/submission-api"
import type { Submission } from "@/lib/types/submission"

interface SubmissionData {
  assignmentId: number
  submission: Submission | null
}

export function LessonSubmission({ assignmentId, submission }: SubmissionData) {
  const [file, setFile] = useState<File | null>(null)
  const [submissionData, setSubmissionData] = useState<Submission | null>(submission || null)

  useEffect(() => {
    setSubmissionData(submission)
  }, [submission, file])

  const handleSubmit = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)

      if (!submissionData) {
        try {
          const response = await submitAssignmentApi(assignmentId, selectedFile)
          setSubmissionData(response)
        } catch (error) {
          console.error("Failed to submit assignment", error)
        }
      }
    }
  }

  const handleDelete = () => {
    if (submissionData && !submissionData.submission_score) {
      deleteSubmissionApi(submissionData.id)
      setSubmissionData(null)
      setFile(null)
    }
  }

  const handleDownload = () => {
    if (submissionData) {
      window.open(getGoogleDriveDownloadFileUrl(submissionData.file.file_id), "_blank")
    }
  }

  return (
    <div className="mt-2">
      <h3 className="text-lg font-semibold mb-4">Bài nộp của học viên</h3>
      {submissionData ? (
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
            <FileText className="w-4 h-4 text-primary" />
            <div className="flex-1">
              <p className="text-sm font-medium">{submissionData.file.file_name}</p>
              <p className="text-xs text-muted-foreground">
                Submitted on {format(new Date(submissionData.created_at), "MMM d, yyyy 'at' h:mm a")}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="bg-primary text-white hover:bg-secondary hover:text-white"
                onClick={handleDownload}
              >
                <Download className="w-4 h-4" />
              </Button>
              {!submissionData.submission_score && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="bg-[#FF4545] text-white hover:bg-[#C62E2E] hover:text-white"
                  onClick={handleDelete}
                >
                  <X className="w-4 h-4" />
                </Button>
              )}
            </div>
          </div>

          {submissionData.submission_score && (
            <>
              <div className="flex items-center justify-between p-3 rounded-lg bg-success/10 border border-success">
                <span className="text-sm text-muted-foreground italic text-success">
                  Chấm điểm vào {format(new Date(submissionData.submission_score.created_at), "MMM d, yyyy")}
                </span>
                <div className="min-w-[80px] text-right">
                  <span className="text-lg font-semibold text-success">{submissionData.submission_score.score}/100</span>
                </div>
              </div>
              <div className="mt-4">
                <h4 className="text-sm font-semibold mb-2">Nhận xét</h4>
                <p className="text-sm text-muted-foreground bg-muted p-3 rounded-lg">
                  {submissionData.submission_score.feedback}
                </p>
              </div>
            </>
          )}

        </div>
      ) : (
        <div className="mt-2 flex items-center gap-2">
          <Button
            variant="outline"
            className="w-full justify-center bg-primary text-white hover:bg-secondary hover:text-white"
            onClick={() => document.getElementById("file-upload")?.click()}
          >
            <Upload className="mr-2 h-4 w-4" />
            Upload Submission File
          </Button>
        </div>
      )}
      <input id="file-upload" type="file" className="hidden" accept=".pdf,.doc,.docx" onChange={handleSubmit} />
    </div>
  )
}

