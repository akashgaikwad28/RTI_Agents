"use client";

import { PortalShell, adminNav } from "@/components/app-shell/portal-shell";
import { useAuthGuard } from "@/hooks/use-auth-guard";
import { useTranslations } from "@/hooks/use-translations";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { hydrated, user } = useAuthGuard(["admin"]);
  const t = useTranslations();

  if (!hydrated || !user) {
    return <div className="min-h-screen bg-[hsl(var(--bg))]" />;
  }

  return <PortalShell title={t("adminConsole")} nav={adminNav}>{children}</PortalShell>;
}
