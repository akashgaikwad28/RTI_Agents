"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuthStore } from "@/store";
import { canAccess, roleHome } from "@/lib/rbac";
import type { UserRole } from "@/types/governance";

export function useAuthGuard(allowedRoles: UserRole[]) {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const hydrated = useAuthStore((state) => state.hydrated);

  useEffect(() => {
    if (!hydrated) {
      return;
    }
    if (!user) {
      router.replace("/login");
      return;
    }
    if (!allowedRoles.includes(user.role)) {
      router.replace(roleHome[user.role]);
    }
  }, [allowedRoles, hydrated, router, user]);

  return {
    hydrated,
    user,
    allowed: Boolean(user && canAccess(user.role, roleHome[allowedRoles[0] ?? "citizen"])),
  };
}

