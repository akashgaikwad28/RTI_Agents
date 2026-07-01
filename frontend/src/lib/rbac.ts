import type { UserRole } from "@/types/governance";

export const roleHome: Record<UserRole, string> = {
  citizen: "/dashboard",
  officer: "/officer",
  admin: "/admin",
};

export function canAccess(role: UserRole | undefined, pathname: string) {
  if (!role) {
    return false;
  }
  if (pathname.startsWith("/admin")) {
    return role === "admin";
  }
  if (pathname.startsWith("/officer")) {
    return role === "officer" || role === "admin";
  }
  if (pathname.startsWith("/dashboard")) {
    return role === "citizen" || role === "officer" || role === "admin";
  }
  return true;
}

