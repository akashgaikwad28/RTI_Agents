"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bell, Bot, Database, FileSearch, LayoutDashboard, Lock, LogOut, Search, Settings, Shield, UserCircle2, Users2, Workflow, Activity, CheckSquare, Globe } from "lucide-react";
import { cn, getInitials } from "@/lib/utils";
import { useAuthStore, useNotificationStore } from "@/store";
import { LanguageSwitcher } from "./language-switcher";
import { ThemeToggle } from "./theme-toggle";

interface NavItem {
  href: string;
  label: string;
  icon: React.ElementType;
}

interface PortalShellProps {
  title: string;
  nav: NavItem[];
  children: React.ReactNode;
}

export function PortalShell({ title, nav, children }: PortalShellProps) {
  const pathname = usePathname();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const unread = useNotificationStore((state) => state.items.filter((item) => !item.read).length);

  return (
    <div className="min-h-screen bg-[hsl(var(--bg))]">
      <div className="grid min-h-screen lg:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="hidden border-r border-[hsl(var(--border))] bg-[hsl(var(--surface))] lg:flex lg:flex-col">
          <div className="flex h-16 items-center gap-3 border-b border-[hsl(var(--border))] px-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[hsl(var(--accent))] text-white">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-semibold">{title}</p>
              <p className="text-xs text-[hsl(var(--text-muted))]">RTI-Agent v2</p>
            </div>
          </div>
          <nav className="flex-1 space-y-1 px-3 py-4">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm",
                  pathname === item.href ? "bg-[hsl(var(--accent)/0.1)] text-[hsl(var(--accent))]" : "text-[hsl(var(--text-muted))] hover:bg-[hsl(var(--bg))]"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="border-t border-[hsl(var(--border))] p-4">
            <div className="mb-3 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[hsl(var(--accent)/0.15)] text-sm font-semibold text-[hsl(var(--accent))]">
                {getInitials(user?.name ?? "RT")}
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">{user?.name ?? "Guest"}</p>
                <p className="truncate text-xs text-[hsl(var(--text-muted))]">{user?.email ?? ""}</p>
              </div>
            </div>
            <button type="button" className="inline-flex items-center gap-2 text-sm text-[hsl(var(--text-muted))]" onClick={() => logout()}>
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>
        </aside>
        <main className="min-w-0">
          <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-[hsl(var(--border))] bg-[hsl(var(--surface))/0.92] px-4 backdrop-blur">
            <div>
              <p className="text-lg font-semibold">{title}</p>
              <p className="text-xs text-[hsl(var(--text-muted))]">Government-grade AI governance frontend</p>
            </div>
            <div className="flex items-center gap-2">
              <LanguageSwitcher />
              <ThemeToggle />
              <Link href="/dashboard/notifications" aria-label="Notifications" className="relative inline-flex h-10 w-10 items-center justify-center rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))]">
                <Bell className="h-4 w-4" />
                {unread > 0 && <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-[hsl(var(--accent))]" />}
              </Link>
            </div>
          </header>
          <div className="p-4 md:p-6">{children}</div>
        </main>
      </div>
    </div>
  );
}

export const citizenNav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/new-rti", label: "New RTI", icon: Workflow },
  { href: "/dashboard/history", label: "History", icon: Search },
  { href: "/dashboard/profile", label: "Profile", icon: UserCircle2 },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export const officerNav = [
  { href: "/officer", label: "Overview", icon: LayoutDashboard },
  { href: "/officer/queue", label: "Department Queue", icon: Users2 },
  { href: "/officer/analytics", label: "Analytics", icon: Shield },
];

export const adminNav = [
  { href: "/admin", label: "Overview", icon: LayoutDashboard },
  { href: "/admin/users", label: "Users", icon: Users2 },
  { href: "/admin/analytics", label: "Analytics", icon: Shield },
  { href: "/admin/langgraph", label: "Agent Ops", icon: Workflow },
  { href: "/admin/governance", label: "Governance", icon: Bot },
  { href: "/admin/corpus", label: "RAG Corpus", icon: Database },
  { href: "/admin/scraping", label: "Scraper Ops", icon: Globe },
  { href: "/admin/evaluation-center", label: "Evaluation", icon: FileSearch },
  { href: "/admin/approval-center", label: "Approvals", icon: CheckSquare },
  { href: "/admin/security", label: "Security", icon: Lock },
  { href: "/admin/system-health", label: "System Health", icon: Activity },
];

