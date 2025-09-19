import type { Submission, SubmissionDetail } from "./submission";

export interface Assignment {
  id: number;
  title: string;
  due_at: string;
  start_at: string;
}

export interface AssignmentDetail extends Assignment {
  content: string;
  submission: Submission | null;
}

export interface AssignmentSubmissions extends Assignment {
  content: string;
  submissions: SubmissionDetail[];
}

export interface CreateAssignmentRequest {
  title: string;
  content: string;
  start_at: string;
  due_at?: string;
}
