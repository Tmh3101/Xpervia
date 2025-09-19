import authAxios from "./axios-auth";
import type {
  AssignmentDetail,
  AssignmentSubmissions,
  CreateAssignmentRequest,
} from "../types/assignment";

export const getLessonAssignmentsApi = async (
  lessonId: string
): Promise<AssignmentDetail[]> => {
  const response = await authAxios.get(
    `courses/lessons/${lessonId}/assignments/student/`
  );
  return response.data.assignments;
};

export const getAssignmentSubmissionsApi = async (
  lessonId: string
): Promise<AssignmentSubmissions[]> => {
  const response = await authAxios.get(
    `courses/lessons/${lessonId}/assignments/`
  );
  return response.data.assignments;
};

export const createAssignmentApi = async (
  lessonId: string,
  data: CreateAssignmentRequest
): Promise<void> => {
  if (data.due_at === "") {
    delete data.due_at;
  }
  await authAxios.post(`courses/lessons/${lessonId}/assignments/create/`, data);
};

export const deleteAssignmentApi = async (
  assignmentId: number
): Promise<void> => {
  await authAxios.delete(`courses/lessons/assignments/${assignmentId}/delete/`);
};

export const updateAssignmentApi = async (
  assignmentId: number,
  data: CreateAssignmentRequest
): Promise<AssignmentDetail> => {
  if (data.due_at === "") {
    delete data.due_at;
  }
  const response = await authAxios.put(
    `courses/lessons/assignments/${assignmentId}/update/`,
    data
  );
  return response.data.assignment;
};
