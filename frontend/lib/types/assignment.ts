import { Submission } from './submission';

export interface Assignment {
    id: number;
    title: string;
    due_at: string;
}

export interface AssignmentDetail {
    id: number;
    title: string;
    content: string;
    due_at: string;
    submission: Submission | null;
}