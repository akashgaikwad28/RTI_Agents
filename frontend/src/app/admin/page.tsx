"use client";

import { StatCard } from "@/components/data-display/stat-card";
import { DataTable } from "@/components/data-display/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { useAdminDashboard } from "@/hooks/use-dashboard-data";

export default function AdminHomePage() {
  const { data } = useAdminDashboard();
  const analytics = data?.analytics as any;
  const governance = data?.governance as any;
  const health = data?.health;

  const aiGovernanceScore = Math.round(
    (analytics?.aiSuccessRate ?? 0) * 0.7 +
      (100 - (governance?.pendingApprovals ?? 0)) * 0.3,
  );

  const healthStatus = health?.status ?? "unknown";
  const healthTone = healthStatus === "healthy" ? "good" : "warn";

  const recentActivity = Array.isArray(governance?.recentActivity)
    ? governance.recentActivity
    : [];

  const departmentBreakdown = Array.isArray(analytics?.departmentBreakdown)
    ? analytics.departmentBreakdown
    : [];

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Admin Overview"
        description="Global monitoring across users, departments, AI quality, and system health."
      />

      {/* Row 1 — Core metrics */}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard metric={{ label: "Total RTIs", value: analytics?.totalRTIs ?? 0 }} />
        <StatCard metric={{ label: "Pending", value: analytics?.pendingRTIs ?? 0, tone: "warn" }} />
        <StatCard metric={{ label: "Pending Approvals", value: governance?.pendingApprovals ?? 0, tone: "warn" }} />
        <StatCard metric={{ label: "AI Success Rate", value: `${analytics?.aiSuccessRate ?? 0}%`, tone: "good" }} />
      </div>

      {/* Row 2 — Derived insights */}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          metric={{
            label: "AI Governance Score",
            value: `${aiGovernanceScore}%`,
            hint: "Weighted: 70% AI success + 30% approval pressure",
            tone: aiGovernanceScore >= 80 ? "good" : aiGovernanceScore >= 60 ? "warn" : "danger",
          }}
        />
        <StatCard
          metric={{
            label: "Daily Activity",
            value: governance?.recentActivity?.length ?? 0,
            hint: "Events in recent window",
          }}
        />
        <StatCard
          metric={{
            label: "Department Load",
            value: `${analytics?.departmentBreakdown?.length ?? 0} departments`,
          }}
        />
        <StatCard
          metric={{
            label: "System Readiness",
            value: healthStatus,
            tone: healthTone,
          }}
        />
      </div>

      {/* Row 3 — Recent Activity */}
      <DataTable
        title="Recent Activity"
        rows={recentActivity}
        columns={[
          { key: "trackingId" as string, label: "Tracking ID", sortable: true, render: (row: Record<string, unknown>) => String(row.trackingId ?? row.tracking_id ?? "") },
          { key: "department", label: "Department", sortable: true },
          { key: "status", label: "Status", sortable: true },
          { key: "created_at", label: "Created", sortable: true },
        ]}
      />

      {/* Row 4 — Department Load */}
      <DataTable
        title="Department Load"
        rows={departmentBreakdown}
        columns={[
          { key: "department" as string, label: "Department", sortable: true, render: (row: Record<string, unknown>) => String(row.department ?? row._id ?? "") },
          { key: "count", label: "Count", sortable: true },
        ]}
      />
    </div>
  );
}
