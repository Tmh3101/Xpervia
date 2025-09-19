import authAxios from "./axios-auth";
import type { User, UserWithPassword } from "@/lib/types/user";

export const getUsersApi = async (): Promise<User[]> => {
  const response = await authAxios.get(`admin/users/`);
  return response.data.users;
};

export const createUserApi = async (
  userData: UserWithPassword
): Promise<UserWithPassword> => {
  const response = await authAxios.post(`admin/users/create/`, userData);
  return response.data.user;
};

export const updateUserApi = async (
  userId: string,
  userData: any
): Promise<User> => {
  const response = await authAxios.put(
    `admin/users/${userId}/update/`,
    userData
  );
  return response.data.user;
};

export const deleteUserApi = async (userId: string): Promise<boolean> => {
  const response = await authAxios.delete(`admin/users/${userId}/delete/`);
  return response.data.success;
};

// đang fix
export const changePasswordApi = async (
  userId: string,
  data: any
): Promise<boolean> => {
  const response = await authAxios.put(
    `users/${userId}/change-password/`,
    data
  );
  return response.data.success;
};

export const disableUserApi = async (userId: string): Promise<User> => {
  const response = await authAxios.put(`admin/users/${userId}/disable/`, {});
  return response.data.user;
};

export const enableUserApi = async (userId: string): Promise<User> => {
  const response = await authAxios.put(`admin/users/${userId}/enable/`, {});
  return response.data.user;
};
