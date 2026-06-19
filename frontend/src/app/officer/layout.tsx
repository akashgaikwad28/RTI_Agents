"use client";

import { PortalShell, officerNav } from "@/components/app-shell/portal-shell";
import { useAuthGuard } from "@/hooks/use-auth-guard";
import { useTranslations } from "@/hooks/use-translations";

export default function OfficerLayout({ children }: { children: React.ReactNode }) {
  const { hydrated, user } = useAuthGuard(["officer", "admin"]);
  const t = useTranslations();

  if (!hydrated || !user) {
    return <div className="min-h-screen bg-[hsl(var(--bg))]" />;
  }

  return <PortalShell title={t("officerPortal")} nav={officerNav}>{children}</PortalShell>;
}

