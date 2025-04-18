import axios from 'axios';
import { User, UserWithPassword } from "@/lib/types/user"
import authAxios from './axios-auth'

const baseUrl = process.env.NEXT_PUBLIC_API_URL

export const getUserInforApi = async (accessToken: string): Promise<User> => {
    const headers = {
        Authorization: `Bearer ${accessToken}`,
    }
    const response = await axios.get(
        `${baseUrl}users/me/`,
        { headers }
)
    return response.data.user
}

export const getUsersApi = async (): Promise<User[]> => {
    const response = await authAxios.get(`users/`)
    return response.data.users
}

export const createUserApi = async (userData: UserWithPassword): Promise<UserWithPassword> => {
    const response = await authAxios.post(`users/create/`, userData)
    return response.data.user
}

export const updateUserApi = async (userId: string, userData: any): Promise<User> => {
    const response = await authAxios.put(`users/${userId}/update/`, userData)
    return response.data.user
}

export const deleteUserApi = async (userId: string): Promise<boolean> => {
    const response = await authAxios.delete(`users/${userId}/delete/`)
    return response.data.success
}

export const changePasswordApi = async (userId: string, data: any): Promise<boolean> => {
    const response = await authAxios.put(`users/${userId}/update-password/`, data)
    return response.data.success
}

export const disableUserApi = async (userId: string): Promise<User> => {
    const response = await authAxios.put(`users/${userId}/disable/`, {})
    return response.data.user
}

export const enableUserApi = async (userId: string): Promise<User> => {
    const response = await authAxios.put(`users/${userId}/enable/`, {})
    return response.data.user
}