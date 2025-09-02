import authAxios from "./axios-auth";

export interface LoginPayload {
  email: string;
  password: string;
}

// Đăng nhập, nhận access và refresh token
export const loginApi = async (payload: LoginPayload) => {
  try {
    const response = await authAxios.post(`auth/login/`, payload);
    return response.data;
  } catch (error) {
    console.error("Error during login:", error);
    if (error.response && error.response.data) {
      return { error: error.response.data.error || "An error occurred" };
    }
  }
};

// Làm mới access token bằng refresh token
export const refreshTokenApi = async (refreshToken: string) => {
  const response = await authAxios.post(`auth/refresh-session/`, {
    refresh_token: refreshToken,
  });
  return response.data;
};

// Kiểm tra token hợp lệ
export const verifyTokenApi = async (token: string): Promise<boolean> => {
  try {
    await authAxios.post(`auth/verify/`, {
      token,
    });
    return true;
  } catch {
    return false;
  }
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
    const response = await authAxios.post(`auth/register/`, {
      email: email_value,
      first_name: first_name_value,
      last_name: last_name_value,
      date_of_birth: date_of_birth_value,
      password: password_value,
      role: role_value,
    });
    return response.data.user;
  } catch (error) {
    console.error("Error during registration:", error);
    if (error.response && error.response.data) {
      return { error: error.response.data.error || "An error occurred" };
    }
  }
};

export const requestResetPasswordApi = async (email: string) => {
  try {
    const response = await authAxios.post(`auth/request-reset-password/`, {
      email,
      redirect_url: "http://localhost:3000/auth/reset-password",
    });
    return response.data;
  } catch (error) {
    if (error.response && error.response.data) {
      return { error: error.response.data.error || "An error occurred" };
    }
  }
};

export const resetPasswordApi = async (
  newPassword: string,
  accessToken: string
) => {
  const headers = {
    Authorization: `Bearer ${accessToken}`,
  };

  try {
    const response = await authAxios.post(
      `auth/reset-password/`,
      {
        new_password: newPassword,
      },
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error("Error during password reset:", error);

    if (error.response && error.response.data) {
      return { error: error.response.data.error || "An error occurred" };
    }
  }
};

export const getMe = async (accessToken: string) => {
  try {
    const response = await authAxios.get(`auth/current-user/`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data.user;
  } catch (error) {
    console.error("Error fetching user data:", error);
    return { error: "An error occurred" };
  }
};
