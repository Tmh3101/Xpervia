import axios from 'axios'

const baseUrl = process.env.NEXT_PUBLIC_API_URL

export const loginApi = async (email: string, password: string) => {
    try {
        const response = await axios.post(`${baseUrl}token/login/`, {
            email,
            password
        })
        return {token: response.data.token, user: response.data.user}
    } catch (error) {
        if (axios.isAxiosError(error) && error.response) {
            return { error: error.response.data.error };
        }
        return { error: 'An error occurred' };
    }
}

export const registerApi = async (
    email_value: string,
    first_name_value: string,
    last_name_value: string,
    date_of_birth_value: string,
    password_value: string,
    role_value: string
) => {
    try {
        const response = await axios.post(`${baseUrl}register/`, {
            email: email_value,
            password: password_value,
            first_name: first_name_value,
            last_name: last_name_value,
            date_of_birth: date_of_birth_value,
            role: role_value
        })
        return response.data.user
    } catch (error) {
        if (axios.isAxiosError(error) && error.response) {
            return { error: error.response.data.error };
        }
        return { error: 'An error occurred' };
    }
}

export const logoutApi = async (token: string) => {
    const headers = {
        'Authorization': `Token ${token}`
    }
    const response = await axios.delete(`${baseUrl}token/logout/`, { headers })
    return response.data.success
}
