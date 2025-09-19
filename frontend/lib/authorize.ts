import { routePermissions } from "./role-access-rules";

// Check if user is authorized to access a route
export function authorizeWith(
  pathname: string,
  role: string
): "allowed" | "not-allowed" | "not-found" {
  // Get all patterns for the current role
  const patterns =
    routePermissions[role as keyof typeof routePermissions] || [];

  // Check if the route exists in any role
  const isValidRoute = Object.values(routePermissions).some((patterns) =>
    patterns.some((pattern) => pattern.test(pathname))
  );

  if (!isValidRoute) {
    return "not-found"; // Route does not exist
  }

  // Check access rights
  const isAllowed = patterns.some((pattern) => pattern.test(pathname));
  return isAllowed ? "allowed" : "not-allowed";
}
