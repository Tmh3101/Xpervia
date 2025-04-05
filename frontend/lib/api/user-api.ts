import { User } from "@/lib/types/user"
import axios from "axios"

const baseUrl = 'http://localhost:8000/api/'
// const baseUrl = 'http://192.168.1.4:8000/api/'

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

interface UpdateUser {
    first_name?: string;
    last_name?: string;
    date_of_birth?: string;
}

export const updateUserApi = async (userId: string , userData: UpdateUser): Promise<User> => {
    console.log('userId', userId)
    console.log('userData', userData)
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