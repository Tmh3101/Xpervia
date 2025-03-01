import { FileText, Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { useState } from "react"
import { getGoogleDriveDownloadFileUrl, getGoogleDriveFileUrl } from "@/lib/google-drive-url"


interface LessonAttachmentsProps {
  attachments: string[]
}

export function LessonAttachments({ attachments }: LessonAttachmentsProps) {
  const [selectedAttachment, setSelectedAttachment] = useState<string | null>(null)

  const handleDownload = () => {
    if (selectedAttachment) {
      window.open(getGoogleDriveDownloadFileUrl(selectedAttachment), "_blank")
    }
  }

  if (!attachments?.length) return null

  return (
    <div className="mt-4 bg-white rounded-xl px-6 py-4 border">
      <h3 className="text-lg text-destructive font-semibold mb-3">Lesson Resources</h3>
      <div className="flex flex-wrap gap-3">
        {attachments.map((attachment, index) => (
          <Button
            key={index}
            variant="outline"
            className="flex items-center gap-2 bg-primary text-white hover:bg-secondary hover:text-white"
            onClick={() => setSelectedAttachment(attachment)}
          >
            <FileText className="w-4 h-4" />
          </Button>
        ))}
      </div>

      <Dialog open={!!selectedAttachment} onOpenChange={() => setSelectedAttachment(null)}>
        <DialogContent className="max-w-4xl h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center justify-between mt-3">
              {selectedAttachment && (
                <Button
                  variant="outline"
                  size="sm"
                  className="bg-primary text-white flex items-center gap-2"
                  onClick={handleDownload}
                >
                  <Download className="w-4 h-4" />
                  Download
                </Button>
              )}
            </DialogTitle>
          </DialogHeader>
          <div className="flex-1 w-full min-h-0 -mt-[220px] h-auto">
            {selectedAttachment && (
              <iframe
                src={getGoogleDriveFileUrl(selectedAttachment)}
                className="w-full h-full rounded-md"
                allow="autoplay"
              />
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

