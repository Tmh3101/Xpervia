import { User } from "@/lib/types/user"
import axios from "axios"
import { headers } from "next/headers"

const baseUrl = 'http://localhost:8000/api/'

export const getUserInforApi = (): User => {
    const user = localStorage.getItem("user")
    if (!user) {
        throw new Error("User is not logged in")
    }
    return JSON.parse(user)
}

interface UpdateUser {
    first_name?: string;
    last_name?: string;
    date_of_birth?: string;
}

export const updateUserApi = async (userId: string , userData: UpdateUser): Promise<User> => {
    const headers = {
        'Authorization': `Token ${localStorage.getItem('token')}`
    }
    console.log('token', localStorage.getItem('token'))
    const response = await axios.put(
        `${baseUrl}users/${userId}/update/`,
        userData,
        { headers }
    )
    return response.data.user
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