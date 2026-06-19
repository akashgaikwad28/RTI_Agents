"use client";

import { StatCard } from "@/components/data-display/stat-card";
import { SectionHeader } from "@/components/ui/section-header";
import { useOfficerQueue } from "@/hooks/use-dashboard-data";

export default function OfficerAnalyticsPage() {
  const { data } = useOfficerQueue();
  const rows = data?.data ?? [];

  return (
    <div className="space-y-6">
      <SectionHeader title="Officer Analytics" description="Track queue quality, response time, and AI confidence by department." />
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard metric={{ label: "Queue Size", value: rows.length }} />
        <StatCard metric={{ label: "Awaiting Approval", value: rows.filter((row) => row.approvalStatus === "pending").length, tone: "warn" }} />
        <StatCard metric={{ label: "Average Risk", value: rows.length ? (rows.reduce((total, row) => total + (row.aiRiskScore ?? 0), 0) / rows.length).toFixed(2) : "0.00" }} />
        <StatCard metric={{ label: "Retrieval Quality", value: rows.length ? `${Math.round((rows.reduce((total, row) => total + (row.retrievalConfidence ?? 0), 0) / rows.length) * 100)}%` : "0%" }} />
      </div>
    </div>
  );
}

