import authAxios from "./axios-auth";
import { Submission, SubmissionScore } from "../types/submission";

export const submitAssignmentApi = async (
  assignmentId: number,
  fileData: File
): Promise<Submission> => {
  const response = await authAxios.post(
    `courses/assignments/${assignmentId}/submissions/create/`,
    { file: fileData },
    {
      headers: { "Content-Type": "multipart/form-data" },
    }
  );
  return response.data.submission;
};

export const deleteSubmissionApi = async (
  submissionId: number
): Promise<boolean> => {
  const response = await authAxios.delete(
    `courses/assignments/submissions/${submissionId}/delete/`
  );
  return response.data.success;
};

export const createSubmissionScoreApi = async (
  submissionId: number,
  submissionScore: SubmissionScore
): Promise<SubmissionScore> => {
  const response = await authAxios.post(
    `courses/assignments/submissions/${submissionId}/score/create/`,
    {
      score: submissionScore.score,
      feedback: submissionScore.feedback,
    }
  );
  return response.data.submission_score;
};

export const updateSubmissionScoreApi = async (
  submissionScoreId: number,
  submissionScore: SubmissionScore
): Promise<SubmissionScore> => {
  const response = await authAxios.put(
    `courses/assignments/submissions/score/${submissionScoreId}/update/`,
    {
      score: submissionScore.score,
      feedback: submissionScore.feedback,
    }
  );
  return response.data.submission_score;
};
