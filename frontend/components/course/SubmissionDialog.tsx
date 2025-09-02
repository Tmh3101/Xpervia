"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useForm, Controller } from "react-hook-form";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Download, File, User } from "lucide-react";
import { downloadViaFetch } from "@/lib/utils";
import {
  createSubmissionScoreApi,
  updateSubmissionScoreApi,
} from "@/lib/api/submission-api";
import type { AssignmentSubmissions } from "@/lib/types/assignment";
import type { SubmissionDetail } from "@/lib/types/submission";
import type { SubmissionScore } from "@/lib/types/submission";

const submissionScoreFormSchema = z.object({
  score: z
    .number()
    .int()
    .min(0, "Điểm số phải lớn hơn hoặc bằng 0")
    .max(100, "Điểm số phải nhỏ hơn hoặc bằng 100"),
  feedback: z.string().optional(),
});

interface SubmissionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  assignment: AssignmentSubmissions;
  initialData?: SubmissionScore;
}

export function SubmissionDialog({
  open,
  onOpenChange,
  assignment,
  initialData,
}: SubmissionDialogProps) {
  const [selectedSubmission, setSelectedSubmission] =
    useState<SubmissionDetail | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm({
    resolver: zodResolver(submissionScoreFormSchema),
    defaultValues: {
      score: initialData?.score || undefined,
      feedback: initialData?.feedback || "",
    },
  });

  // Update form values when initialData changes
  useEffect(() => {
    if (initialData && initialData.score) {
      form.reset({
        score: initialData.score,
        feedback: initialData.feedback || "",
      });
    }
  }, [initialData, form]);

  const handleSelectSubmission = (submission: SubmissionDetail) => {
    setSelectedSubmission(submission);
  };

  const handleSaveSubmissionScore = async (data: SubmissionScore) => {
    if (!selectedSubmission || !data) return;

    setIsSubmitting(true);
    try {
      let newSubmissionScore = null;
      if (!selectedSubmission.submission_score) {
        newSubmissionScore = await createSubmissionScoreApi(
          selectedSubmission.id,
          data
        );
      } else {
        if (selectedSubmission.submission_score.id) {
          newSubmissionScore = await updateSubmissionScoreApi(
            selectedSubmission.submission_score.id,
            data
          );
        }
      }

      if (!newSubmissionScore) return;

      const updatedSubmission = {
        ...selectedSubmission,
        submission_score: newSubmissionScore,
      };

      setSelectedSubmission(updatedSubmission);

      assignment.submissions = assignment.submissions?.map((sub) =>
        sub.id === selectedSubmission.id ? updatedSubmission : sub
      );

      form.reset({
        score: newSubmissionScore.score || 0,
        feedback: newSubmissionScore.feedback || "",
      });
    } catch (error) {
      console.error("Error saving submission score:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDownload = () => {
    if (selectedSubmission) {
      downloadViaFetch(
        selectedSubmission.file.file_url,
        selectedSubmission.file.file_name
      );
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[900px] max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Bài nộp cho: {assignment.title}</DialogTitle>
        </DialogHeader>
        <div className="flex-1 overflow-hidden">
          {!assignment.submissions ? (
            <div className="text-center py-8 text-gray-500">
              Chưa có bài nộp nào cho bài tập này
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-4 h-full">
              {/* Left side - List of submissions */}
              <div className="col-span-1 border rounded-md overflow-hidden">
                <div className="p-3 bg-muted font-medium">
                  Danh sách bài nộp
                </div>
                <ScrollArea className="h-[500px]">
                  <div className="p-2 space-y-2">
                    {assignment.submissions.map((submission) => (
                      <Card
                        key={submission.id}
                        className={`cursor-pointer transition-colors ${
                          selectedSubmission?.id === submission.id
                            ? "border-primary"
                            : ""
                        }`}
                        onClick={() => handleSelectSubmission(submission)}
                      >
                        <CardContent className="p-3">
                          <div className="flex items-center">
                            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center mr-2">
                              <User className="w-4 h-4 text-primary" />
                            </div>
                            <div className="flex-1">
                              <div className="font-medium">{`${submission.student.first_name} ${submission.student.last_name}`}</div>
                              <div className="text-xs text-muted-foreground">
                                Nộp vào:{" "}
                                {new Date(
                                  submission.created_at
                                ).toLocaleString()}
                              </div>
                            </div>
                            {submission.submission_score && (
                              <div className="bg-primary/10 text-primary font-medium px-2 py-1 rounded text-sm">
                                {submission.submission_score.score}/100
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </ScrollArea>
              </div>

              {/* Right side - Submission details and grading */}
              <div className="col-span-2 border rounded-md overflow-hidden flex flex-col">
                <div className="p-3 bg-muted font-medium">Chi tiết bài nộp</div>
                {!selectedSubmission ? (
                  <div className="flex-1 flex items-center justify-center text-muted-foreground">
                    Chọn một bài nộp để xem chi tiết
                  </div>
                ) : (
                  <ScrollArea className="flex-1">
                    <div className="p-4 space-y-4">
                      {/* Submission file */}
                      {selectedSubmission.file && (
                        <div className="border rounded-md p-3">
                          <div className="flex items-center">
                            <File className="w-8 h-8 text-primary mr-2" />
                            <div className="flex-1">
                              <div className="font-medium">
                                {selectedSubmission.file.file_name}
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {new Date(
                                  selectedSubmission.file.created_at
                                ).toLocaleString()}
                              </div>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              className="bg-primary text-white flex items-center gap-2"
                              onClick={handleDownload}
                            >
                              <Download className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      )}

                      {/* Submission score form */}
                      <form
                        onSubmit={form.handleSubmit(handleSaveSubmissionScore)}
                        className="space-y-4"
                      >
                        {form.formState.errors &&
                          Object.values(form.formState.errors).length > 0 && (
                            <div className="text-red-500 text-center italic text-sm">
                              {
                                Object.values(form.formState.errors)[0]
                                  ?.message as string
                              }
                            </div>
                          )}

                        <div className="space-y-1">
                          <Label htmlFor="score">Điểm số (0 - 100)</Label>
                          <Controller
                            name="score"
                            control={form.control}
                            render={({ field }: any) => (
                              <Input
                                type="number"
                                min={0}
                                max={100}
                                id="score"
                                placeholder="Nhập điểm số"
                                {...field}
                                onChange={(e) =>
                                  field.onChange(
                                    e.target.value === ""
                                      ? undefined
                                      : Number(e.target.value)
                                  )
                                }
                              />
                            )}
                          />
                        </div>

                        <div className="space-y-1">
                          <Label htmlFor="feedback">Nhận xét</Label>
                          <Controller
                            name="feedback"
                            control={form.control}
                            render={({ field }: any) => (
                              <Textarea
                                id="feedback"
                                placeholder="Nhập nhận xét"
                                {...field}
                              />
                            )}
                          />
                        </div>

                        <DialogFooter className="pt-4">
                          <Button type="submit" disabled={isSubmitting}>
                            {isSubmitting ? (
                              <>
                                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                                {"Đang lưu..."}
                              </>
                            ) : (
                              "Lưu đánh giá"
                            )}
                          </Button>
                        </DialogFooter>
                      </form>
                    </div>
                  </ScrollArea>
                )}
              </div>
            </div>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Đóng
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
