import { routePermissions } from "./role-access-rules"

export function authorizeWith(pathname: string, role: string): "allowed" | "not-allowed" | "not-found" {
  // Lấy tất cả các pattern cho vai trò hiện tại
  const patterns = routePermissions[role as keyof typeof routePermissions] || []

  // Kiểm tra xem route có tồn tại trong bất kỳ vai trò nào không
  const isValidRoute = Object.values(routePermissions).some((patterns) =>
    patterns.some((pattern) => pattern.test(pathname))
  )

  if (!isValidRoute) {
    return "not-found" // Route không tồn tại
  }

  // Kiểm tra quyền truy cập
  const isAllowed = patterns.some((pattern) => pattern.test(pathname))
  return isAllowed ? "allowed" : "not-allowed"
}