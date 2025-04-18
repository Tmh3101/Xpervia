import authAxios from './axios-auth'

export interface LoginPayload {
    email: string;
    password: string;
}
  
export interface TokenResponse {
    access: string;
    refresh: string;
}

// Đăng nhập, nhận access và refresh token
export const loginApi = async (payload: LoginPayload): Promise<TokenResponse> => {
    const response = await authAxios.post(`token/login/`, payload);
    return response.data;
};

// Làm mới access token bằng refresh token
export const refreshTokenApi = async (refreshToken: string): Promise<{ access: string }> => {
    const response = await authAxios.post(`token/refresh/`, {
        refresh: refreshToken,
    });
    return response.data;
};

// Kiểm tra token hợp lệ
export const verifyTokenApi = async (token: string): Promise<boolean> => {
    try {
        await authAxios.post(`token/verify/`, {
            token,
        });
        return true;
    } catch {
        return false;
    }
};
  
// Đăng xuất (blacklist refresh token)
export const logoutApi = async (refreshToken: string): Promise<void> => {
    await authAxios.post(`token/logout/`, {
        refresh: refreshToken,
    });
};

export const registerApi = async (
    email_value: string,
    first_name_value: string,
    last_name_value: string,
    date_of_birth_value: string,
    password_value: string,
    role_value: string
) => {
    try {
        const response = await authAxios.post(`register/`, {
            email: email_value,
            first_name: first_name_value,
            last_name: last_name_value,
            date_of_birth: date_of_birth_value,
            password: password_value,
            role: role_value
        });
        return response.data.user
    } catch (error) {
        console.error("Error during registration:", error);
        return { error: 'An error occurred' };
    }
}
