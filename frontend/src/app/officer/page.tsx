"use client";

import Link from "next/link";
import { StatCard } from "@/components/data-display/stat-card";
import { SectionHeader } from "@/components/ui/section-header";
import { useOfficerQueue } from "@/hooks/use-dashboard-data";

export default function OfficerHomePage() {
  const { data } = useOfficerQueue();
  const rows = data?.data ?? [];

  return (
    <div className="space-y-6">
      <SectionHeader title="Department Overview" description="Review AI-assisted RTIs assigned to your department and manage approvals." />
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard metric={{ label: "Assigned", value: rows.length }} />
        <StatCard metric={{ label: "Pending Review", value: rows.filter((row) => row.approvalStatus === "pending").length, tone: "warn" }} />
        <StatCard metric={{ label: "Escalation Risk", value: rows.filter((row) => (row.aiRiskScore ?? 0) > 0.55).length, tone: "danger" }} />
        <StatCard metric={{ label: "High Confidence", value: rows.filter((row) => (row.retrievalConfidence ?? 0) > 0.7).length, tone: "good" }} />
      </div>
      <section className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-4">
        <h2 className="mb-3 text-sm font-semibold">Priority Queue</h2>
        <div className="space-y-3">
          {rows.slice(0, 5).map((row) => (
            <Link key={row.id} href={`/officer/rti/${row.id}`} className="block rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium">{row.title || row.queryText}</p>
                  <p className="mt-1 text-xs text-[hsl(var(--text-muted))]">{row.department}</p>
                </div>
                <span className="text-xs text-[hsl(var(--accent))]">Open</span>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

