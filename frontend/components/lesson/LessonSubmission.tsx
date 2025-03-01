"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Upload, X, FileText } from "lucide-react"
import { cn } from "@/lib/utils"
import { format, set } from "date-fns"
import { Submission } from "@/lib/types/assignment"
import { getGoogleDriveDownloadFileUrl } from "@/lib/google-drive-url"

interface SubmissionData {
  submission: Submission | null
}

export function LessonSubmission({ submission }: SubmissionData) {
  const [fileId, setFileId] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  useEffect(() => {
    if (submission){
      setFileId(submission.file_id)
    } else {
      setFileId(null)
    }
  }, [fileId])

  const handleDelete = () => {
    console.log("Delete file", fileId)
    setFileId(null)
  }

  const handleDownload = () => {
    if (fileId) {
      window.open(getGoogleDriveDownloadFileUrl(fileId), "_blank")
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // const selectedFile = e.target.files?.[0]
    // if (selectedFile) {
    //   setFileId(selectedFile)
    //   //onSubmit?.(selectedFile)
    // }
  }

  const handleDrop = (e: React.DragEvent) => {
    // e.preventDefault()
    // setIsDragging(false)
    // const droppedFile = e.dataTransfer.files[0]
    // if (droppedFile) {
    //   setFileId(droppedFile)
    //   //onSubmit?.(droppedFile)
    // }
  }

  const handleDragOver = (e: React.DragEvent) => {
    // e.preventDefault()
    // setIsDragging(true)
  }

  const handleDragLeave = () => {
    // setIsDragging(false)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  return (
    <div className="mt-2">
      <h3 className="text-lg font-semibold mb-4">Assignment Submission</h3>
      {submission ? (
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
            <FileText className="w-4 h-4 text-primary" />
            <div className="flex-1">
              {/* <p className="text-sm font-medium">{submission.file_id}</p> */}
              <p className="text-xs text-muted-foreground">
                Submitted on {format(new Date(submission.created_at), "MMM d, yyyy 'at' h:mm a")}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="bg-primary text-white hover:bg-secondary hover:text-white"
                onClick={handleDownload}
              >
                Download
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

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              className="w-full justify-center border border-primary text-primary hover:text-destructive hover:border-destructive"
              onClick={() => document.getElementById("file-upload")?.click()}
            >
              <Upload className="mr-2 h-4 w-4" />
              Change Submission
            </Button>
          </div>
        </div>
      ) : (
        <>
          <div
            className={cn(
              "border-2 border-dashed rounded-lg p-8 transition-colors",
              isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25",
            )}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <div className="flex flex-col items-center justify-center gap-2 text-center">
              <Upload className={cn("h-8 w-8", isDragging ? "text-primary" : "text-muted-foreground/50")} />
              <p className="text-sm font-medium">Drag and drop your file here, or click to browse</p>
              <p className="text-xs text-muted-foreground">Supported formats: PDF, DOC, DOCX (Max 10MB)</p>
            </div>
          </div>
          <div className="mt-2 flex items-center gap-2">
            <Button
              variant="outline"
              className="w-full justify-center bg-primary text-white"
              onClick={() => document.getElementById("file-upload")?.click()}
            >
            <Upload className="mr-2 h-4 w-4" />
              Upload Submison File
            </Button>
          </div>
        </>
      )}
      <input id="file-upload" type="file" className="hidden" accept=".pdf,.doc,.docx" onChange={handleFileChange} />
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

