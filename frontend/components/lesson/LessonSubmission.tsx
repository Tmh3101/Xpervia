"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Upload, X, FileText, Download } from "lucide-react"
import { cn } from "@/lib/utils"
import { format, set } from "date-fns"
import { getGoogleDriveDownloadFileUrl } from "@/lib/google-drive-url"
import { submitAssignmentApi, deleteSubmissionApi } from "@/lib/api/submission-api"
import { Submission } from "@/lib/types/submission"

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
    if (submissionData) {
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
              <Button
                variant="ghost"
                size="sm"
                className="bg-[#FF4545] text-white hover:bg-[#C62E2E] hover:text-white"
                onClick={handleDelete}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <div className="mt-2 flex items-center gap-2">
          <Button
            variant="outline"
            className="w-full justify-center bg-primary text-white hover:bg-secondary hover:text-white"
            onClick={() => document.getElementById("file-upload")?.click()}
          >
          <Upload className="mr-2 h-4 w-4" />
            Upload Submison File
          </Button>
        </div>
      )}
      <input id="file-upload" type="file" className="hidden" accept=".pdf,.doc,.docx" onChange={handleSubmit} />
    </div>
  )

  // if (submission?.status === "graded") {
  //   return (
  //     <div className="mt-2 bg-white rounded-xl p-6 border">
  //       <div className="space-y-4">
  //         <div className="flex items-center justify-between">
  //           <h3 className="text-lg font-semibold">Assignment Submission</h3>
  //           <span className="text-sm text-muted-foreground">
  //             Graded on {format(new Date(submission.submittedAt!), "MMM d, yyyy")}
  //           </span>
  //         </div>

  //         <div className="flex items-center gap-4">
  //           <div className="flex-1">
  //             <Progress value={submission.score} className="h-2" />
  //           </div>
  //           <div className="min-w-[80px] text-right">
  //             <span className="text-lg font-semibold">{submission.score}/100</span>
  //           </div>
  //         </div>

  //         {submission.file && (
  //           <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
  //             <FileText className="w-4 h-4 text-primary" />
  //             <div className="flex-1">
  //               <p className="text-sm font-medium">{submission.file.name}</p>
  //               <p className="text-xs text-muted-foreground">{formatFileSize(submission.file.size)}</p>
  //             </div>
  //             <Button variant="ghost" size="sm" className="text-primary" asChild>
  //               <a href="#" download>
  //                 Download
  //               </a>
  //             </Button>
  //           </div>
  //         )}

  //         {submission.feedback && (
  //           <div className="mt-4">
  //             <h4 className="text-sm font-semibold mb-2">Feedback</h4>
  //             <p className="text-sm text-muted-foreground bg-muted p-3 rounded-lg">{submission.feedback}</p>
  //           </div>
  //         )}
  //       </div>
  //     </div>
  //   )
  // }
}

