"use client";

import { StatCard } from "@/components/data-display/stat-card";
import { DataTable } from "@/components/data-display/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { useSystemHealth } from "@/hooks/use-dashboard-data";

export default function AdminSystemHealthPage() {
  const { data } = useSystemHealth();

  const status = data?.status ?? "unknown";
  const statusTone = status === "healthy" ? "good" : "warn";

  const serviceRows = Object.entries(data?.services ?? {}).map(
    ([name, info]) => ({
      name,
      status:
        typeof info === "object" && info !== null
          ? (info as Record<string, unknown>).status ?? "unknown"
          : info,
    }),
  );

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Infrastructure Monitoring"
        description="Real-time health probes and service status."
      />

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          metric={{
            label: "Overall Status",
            value: String(status),
            tone: statusTone,
          }}
        />
        <StatCard
          metric={{
            label: "Version",
            value: String(data?.version ?? "—"),
          }}
        />
        <StatCard
          metric={{
            label: "Environment",
            value: String(data?.environment ?? "—"),
          }}
        />
      </div>

      <DataTable
        title="Service Health"
        rows={serviceRows}
        columns={[
          { key: "name", label: "Service", sortable: true },
          { key: "status", label: "Status", sortable: true },
        ]}
      />
    </div>
  );
}
