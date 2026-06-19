"use client";

import Link from "next/link";
import { FileText, PlusCircle } from "lucide-react";
import { NotificationCenter } from "@/components/feedback/notification-center";
import { StatCard } from "@/components/data-display/stat-card";
import { SectionHeader } from "@/components/ui/section-header";
import { useCitizenDashboard } from "@/hooks/use-dashboard-data";

export default function CitizenDashboardPage() {
  const { data } = useCitizenDashboard();
  const rows = data?.data ?? [];

  return (
    <div className="space-y-6">
      <SectionHeader title="RTI Workspace" description="Track live status, confidence, and approval progress for your applications." />
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard metric={{ label: "Requests", value: rows.length, hint: "Recent RTIs in your account" }} />
        <StatCard metric={{ label: "Pending", value: rows.filter((row) => row.status === "pending").length, tone: "warn" }} />
        <StatCard metric={{ label: "Approved", value: rows.filter((row) => row.approvalStatus === "approved").length, tone: "good" }} />
        <StatCard metric={{ label: "AI Traces", value: rows.filter((row) => row.aiRiskScore !== undefined).length, hint: "Requests with governance telemetry" }} />
      </div>
      <div className="grid gap-4 xl:grid-cols-[1.5fr_1fr]">
        <section className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-4">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-sm font-semibold">Recent Requests</h2>
            <Link href="/dashboard/new-rti" className="inline-flex items-center gap-2 rounded-lg bg-[hsl(var(--accent))] px-3 py-2 text-xs font-medium text-white">
              <PlusCircle className="h-4 w-4" />
              New RTI
            </Link>
          </div>
          <div className="space-y-3">
            {rows.slice(0, 5).map((row) => (
              <Link key={row.id} href={`/dashboard/rti/${row.id}`} className="block rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] p-4">
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{row.title || row.queryText}</p>
                    <p className="mt-1 text-xs text-[hsl(var(--text-muted))]">{row.department}</p>
                  </div>
                  <span className="rounded-full bg-[hsl(var(--accent)/0.1)] px-2 py-1 text-[10px] text-[hsl(var(--accent))]">{row.status}</span>
                </div>
              </Link>
            ))}
            {rows.length === 0 && <p className="text-sm text-[hsl(var(--text-muted))]">No RTIs yet. Start with a new request.</p>}
          </div>
        </section>
        <NotificationCenter />
      </div>
    </div>
  );
}

