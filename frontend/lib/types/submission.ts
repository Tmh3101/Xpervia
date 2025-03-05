import { User } from './user'
import { File } from './file'

export interface Submission {
    id: number;
    file: File;
    created_at: string;
}

export interface SubmissionDetail extends Submission { 
    student: User;
}