"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { resetPasswordApi, getMe } from "@/lib/api/auth-api";

function getAccessTokenFromHash() {
  if (typeof window === "undefined") return null;
  const hash = window.location.hash.substring(1);
  const params = new URLSearchParams(hash.replace(/&/g, "&"));
  return params.get("access_token");
}

export default function ResetPasswordPage() {
  const router = useRouter();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    setAccessToken(getAccessTokenFromHash());

    const fetchUser = async () => {
      if (accessToken) {
        const { user } = await getMe();
        setEmail(user.email);

        console.log("User fetched:", user);
      }
    };

    fetchUser();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!newPassword || !confirmPassword) {
      setError("Vui lòng nhập đầy đủ thông tin.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Mật khẩu nhập lại không khớp.");
      return;
    }
    if (!accessToken) {
      setError("Phiên đã hết hạn.");
      return;
    }
    setLoading(true);
    const res = await resetPasswordApi(newPassword, accessToken);
    setLoading(false);
    if (res.error) {
      setError(res.error);
    } else {
      setSuccess(true);
      setTimeout(() => {
        router.push("/");
      }, 3000);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8 flex flex-col items-center">
        {success ? (
          <>
            <h2 className="text-xl font-bold text-destructive text-center uppercase mb-2">
              Đặt lại mật khẩu cho tài khoản <strong>{email}</strong> thành
              công!
            </h2>
            <p className="text-gray-600 mb-6">
              Bạn sẽ được chuyển về trang chủ và cần đăng nhập lại.
            </p>
            <button
              className="w-full py-3 rounded-xl bg-primary text-white font-semibold hover:bg-primary/90 transition"
              onClick={() => router.push("/")}
            >
              Về trang chủ
            </button>
          </>
        ) : (
          <form className="w-full flex flex-col gap-4" onSubmit={handleSubmit}>
            <h2 className="text-xl font-bold text-destructive text-center uppercase">
              Đặt lại mật khẩu mới
            </h2>
            <p className="text-gray-600 mb-2 text-sm text-center">
              Đặt lại mật khẩu mới cho tài khoản cho tài khoản{" "}
              <strong>{email}</strong>.
            </p>
            <input
              type="password"
              placeholder="Mật khẩu mới"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
            <input
              type="password"
              placeholder="Nhập lại mật khẩu mới"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
            {error && (
              <div className="text-red-500 text-sm text-center mb-2">
                {error}
              </div>
            )}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-primary text-sm text-white font-semibold hover:bg-primary/90 transition mb-2"
            >
              {loading ? "Đang xử lý..." : "Đặt lại mật khẩu"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
