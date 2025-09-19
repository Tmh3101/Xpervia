import { useState } from "react";
import { FileText, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { downloadViaFetch } from "@/lib/utils";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { File } from "@/lib/types/file";

interface LessonAttachmentsProps {
  attachment: File;
}

export function LessonAttachment({ attachment }: LessonAttachmentsProps) {
  const [selectedAttachment, setSelectedAttachment] = useState<File | null>(
    null
  );

  // Xử lý tải xuống cho file_url
  const handleDownload = () => {
    if (selectedAttachment) {
      downloadViaFetch(
        selectedAttachment.file_url,
        selectedAttachment.file_name
      );
    }
  };

  if (!attachment) {
    return;
  }

  return (
    <div className="mt-4 bg-white rounded-xl px-6 py-4 border">
      <h3 className="text-lg text-destructive font-semibold mb-3">Đính kèm</h3>
      <div className="flex flex-wrap gap-3">
        <Button
          variant="outline"
          className="flex items-center gap-2 bg-primary text-white hover:bg-secondary hover:text-white"
          onClick={() => setSelectedAttachment(attachment)}
        >
          <FileText className="w-4 h-4" />
          <p className="text-sm font-medium">{attachment.file_name}</p>
        </Button>
      </div>

      <Dialog
        open={!!selectedAttachment}
        onOpenChange={() => setSelectedAttachment(null)}
      >
        <DialogContent className="max-w-4xl h-[90vh]">
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
          <div className="flex-1 w-full min-h-0 -mt-[290px] h-auto">
            {selectedAttachment && (
              <iframe
                src={selectedAttachment.file_url}
                className="w-full h-full rounded-md"
              />
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
