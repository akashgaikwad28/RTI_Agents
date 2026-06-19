"use client";

import { PortalShell, citizenNav } from "@/components/app-shell/portal-shell";
import { useAuthGuard } from "@/hooks/use-auth-guard";
import { useTranslations } from "@/hooks/use-translations";

export default function CitizenLayout({ children }: { children: React.ReactNode }) {
  const { hydrated, user } = useAuthGuard(["citizen"]);
  const t = useTranslations();

  if (!hydrated || !user) {
    return <div className="min-h-screen bg-[hsl(var(--bg))]" />;
  }

  return <PortalShell title={t("citizenDashboard")} nav={citizenNav}>{children}</PortalShell>;
}
