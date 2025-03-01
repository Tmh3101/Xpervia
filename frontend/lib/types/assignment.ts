export interface Submission {
    id: number;
    file_id: string;
    created_at: string;
}

export interface Assignment {
    id: number;
    title: string;
    content: string;
    due_at: string;
    submission: Submission | null;
}