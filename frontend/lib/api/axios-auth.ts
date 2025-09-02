// lib/api/axios-auth.ts
import axios from "axios";

const baseUrl = process.env.NEXT_PUBLIC_API_URL;

const authAxios = axios.create({
  baseURL: baseUrl,
});

authAxios.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem("accessToken");
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

authAxios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem("refreshToken");
      if (!refreshToken) {
        console.warn("Refresh token not found.");
        return Promise.reject(error);
      }

      try {
        const response = await axios.post(`${baseUrl}auth/refresh-session/`, {
          refresh_token: refreshToken,
        });

        const newAccessToken = response.data.access_token;
        const newRefreshToken = response.data.refresh_token;

        localStorage.setItem("accessToken", newAccessToken);
        localStorage.setItem("refreshToken", newRefreshToken);

        // Cập nhật lại header Authorization
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return authAxios(originalRequest);
      } catch (refreshError) {
        console.error("Refresh token expired or invalid");
        // Optional: logout user here
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default authAxios;
