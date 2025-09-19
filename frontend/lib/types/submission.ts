import type { User } from "./user";
import type { File } from "./file";

export interface SubmissionScore {
  id?: number;
  score: number;
  feedback?: string | null;
  created_at?: string;
}

export interface Submission {
  id: number;
  file: File;
  created_at: string;
  submission_score?: SubmissionScore | null;
}

export interface SubmissionDetail extends Submission {
  student: User;
}
