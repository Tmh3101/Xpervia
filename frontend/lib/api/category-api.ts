import authAxios from "./axios-auth";
import { Category } from "@/lib/types/course-content";

export const getCategoriesApi = async (): Promise<Category[]> => {
  const response = await authAxios.get(`categories/`);
  return response.data.categories;
};
