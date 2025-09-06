import authAxios from "./axios-auth";
import type { Favorite } from "../types/favorite";

export const getFavoritesApi = async (): Promise<Favorite[]> => {
  const response = await authAxios.get(`favorites/`);
  return response.data.favorites;
};

export const getFavoritesByStudentApi = async (): Promise<Favorite[]> => {
  const response = await authAxios.get(`favorites/student/`);
  return response.data.favorites;
};

export const getFavoritesByCourseApi = async (
  courseId: number
): Promise<Favorite[]> => {
  const response = await authAxios.get(`favorites/courses/${courseId}/`);
  return response.data.favorites;
};

export const favoriteCourseApi = async (
  courseId: number
): Promise<Favorite> => {
  const response = await authAxios.post(`favorites/create/${courseId}/`, {});
  return response.data.favorite;
};

export const unfavoriteCourseApi = async (
  courseId: number
): Promise<boolean> => {
  const response = await authAxios.delete(`favorites/${courseId}/delete/`);
  return response.data.success;
};
