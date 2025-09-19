"use client";

import { useState } from "react";
import { requestResetPasswordApi } from "@/lib/api/auth-api";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export default function RequestResetPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const res = await requestResetPasswordApi(email);
    if (res.error) {
      setError(res.error);
    } else {
      setSuccess(true);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg px-8 pt-8 pb-4 flex flex-col items-center">
        {success ? (
          <>
            <h2 className="text-xl font-bold text-destructive text-center uppercase mb-2">
              Hãy kiểm tra email của bạn
            </h2>
            <p className="text-gray-600 text-sm text-center mb-4">
              Chúng tôi đã gửi thông tin xác nhận đặt lại mật khẩu tới email của
              bạn.
            </p>
            <button
              className="w-full py-3 rounded-xl bg-primary text-white font-semibold hover:bg-primary/90 transition"
              onClick={() => router.push("/")}
            >
              Về trang chủ
            </button>
          </>
        ) : (
          <>
            <form
              className="w-full flex flex-col gap-4"
              onSubmit={handleSubmit}
            >
              <h2 className="text-xl font-bold text-destructive text-center uppercase">
                Đặt lại mật khẩu
              </h2>
              <p className="text-gray-600 text-sm text-center">
                Nhập email đã đăng ký để xác nhận đặt lại mật khẩu.
              </p>
              {error && (
                <div className="text-red-500 text-sm text-center">{error}</div>
              )}
              <input
                type="email"
                placeholder="Nhập email của bạn"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              />
              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-primary text-sm text-white font-semibold hover:bg-primary/90 transition mb-2"
              >
                Đặt lại mật khẩu
              </button>
            </form>
            <Button
              variant="link"
              className="text-primary p-0"
              onClick={() => router.push("/")}
            >
              Về trang chủ
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
