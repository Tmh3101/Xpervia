import { User, UserWithPassword } from "@/lib/types/user"
import axios from "axios"

const baseUrl = process.env.NEXT_PUBLIC_API_URL

export const getUserInforApi = (): User => {
    const user = localStorage.getItem("user")
    if (!user) {
        throw new Error("User is not logged in")
    }
    return JSON.parse(user)
}

export const getUsersApi = async (): Promise<User[]> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem('token')}`
    }
    const response = await axios.get(
        `${baseUrl}users/`,
        { headers }
    )
    return response.data.users
}

export const createUserApi = async (userData: UserWithPassword): Promise<UserWithPassword> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem('token')}`
    }
    const response = await axios.post(
        `${baseUrl}users/create/`,
        userData,
        { headers }
    )
    return response.data.user
}

export const updateUserApi = async (userId: string , userData: any): Promise<User> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem('token')}`
    }
    const response = await axios.put(
        `${baseUrl}users/${userId}/update/`,
        userData,
        { headers }
    )
    return response.data.user
}

export const deleteUserApi = async (userId: string): Promise<boolean> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem('token')}`
    }
    const response = await axios.delete(
        `${baseUrl}users/${userId}/delete/`,
        { headers }
    )
    return response.data.success
}

export const changePasswordApi = async (userId: string, data: any): Promise<boolean> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem('token')}`
    }
    const response = await axios.put(
        `${baseUrl}users/${userId}/update-password/`,
        data,
        { headers }
    )
    return response.data.success
}

export const disableUserApi = async (userId: string): Promise<User> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem('token')}`
    }
    const response = await axios.put(
        `${baseUrl}users/${userId}/disable/`,
        {},
        { headers }
    )
    return response.data.user
}

export const enableUserApi = async (userId: string): Promise<User> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem('token')}`
    }
    const response = await axios.put(
        `${baseUrl}users/${userId}/enable/`,
        {},
        { headers }
    )
    return response.data.user
}