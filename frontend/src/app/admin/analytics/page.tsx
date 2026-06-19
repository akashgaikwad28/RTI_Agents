"use client";

import { StatCard } from "@/components/data-display/stat-card";
import { DataTable } from "@/components/data-display/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { useDetailedAnalytics } from "@/hooks/use-dashboard-data";

export default function AdminAnalyticsPage() {
  const { data } = useDetailedAnalytics();
  const dashboard = data?.dashboard as any;
  const deptMetrics = data?.departmentMetrics as any;
  const aiMetrics = data?.aiMetrics as any;

  const departmentBreakdown = Array.isArray(dashboard?.departmentBreakdown)
    ? dashboard.departmentBreakdown
    : [];

  const deptMetricsRows = Array.isArray(deptMetrics) 
    ? deptMetrics 
    : typeof deptMetrics === 'object' && deptMetrics !== null 
      ? Object.entries(deptMetrics).map(([k, v]) => ({ metric: k, value: String(v) }))
      : [];

  const aiMetricsRows = Array.isArray(aiMetrics)
    ? aiMetrics
    : typeof aiMetrics === 'object' && aiMetrics !== null
      ? Object.entries(aiMetrics).map(([k, v]) => ({ metric: k, value: String(v) }))
      : [];

  return (
    <div className="space-y-6">
      <SectionHeader 
        title="Analytics Dashboard" 
        description="Submission volume, officer performance, latency, and department metrics." 
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard metric={{ label: "Total RTIs", value: dashboard?.totalRTIs ?? 0 }} />
        <StatCard metric={{ label: "Pending", value: dashboard?.pendingRTIs ?? 0, tone: "warn" }} />
        <StatCard metric={{ label: "Resolved", value: dashboard?.resolvedRTIs ?? 0, tone: "good" }} />
        <StatCard metric={{ label: "AI Success Rate", value: `${dashboard?.aiSuccessRate ?? 0}%`, tone: "good" }} />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <DataTable
          title="Department Breakdown"
          rows={departmentBreakdown}
          columns={[
            { key: "department" as string, label: "Department", sortable: true, render: (row: Record<string, unknown>) => String(row.department ?? row._id ?? "") },
            { key: "count", label: "Count", sortable: true },
          ]}
        />

        {deptMetricsRows.length > 0 && (
          <DataTable
            title="Department Metrics"
            rows={deptMetricsRows}
            columns={[
              { key: "department" as string, label: "Department / Metric", sortable: true, render: (row: Record<string, unknown>) => String(row.department ?? row.metric ?? "") },
              { key: "count" as string, label: "Value / Count", sortable: true, render: (row: Record<string, unknown>) => String(row.count ?? row.value ?? "") },
              { key: "avg_time" as string, label: "Avg Time", render: (row: Record<string, unknown>) => row.avg_time ? String(row.avg_time) : "—" },
            ]}
          />
        )}
      </div>

      {aiMetricsRows.length > 0 && (
        <DataTable
          title="AI Metrics"
          rows={aiMetricsRows}
          columns={[
            { key: "metric" as string, label: "Metric", sortable: true, render: (row: Record<string, unknown>) => String(row.metric ?? row.name ?? "") },
            { key: "value" as string, label: "Value", render: (row: Record<string, unknown>) => String(row.value ?? row.score ?? "") },
          ]}
        />
      )}
    </div>
  );
}
