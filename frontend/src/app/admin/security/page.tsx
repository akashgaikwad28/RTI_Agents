"use client";

import { SectionHeader } from "@/components/ui/section-header";
import { StatCard } from "@/components/data-display/stat-card";
import { DataTable } from "@/components/data-display/data-table";
import { useAuditLogs } from "@/hooks/use-dashboard-data";
import { ShieldAlert } from "lucide-react";

export default function SecurityCenterPage() {
  const { data } = useAuditLogs();

  const logs = Array.isArray(data?.data)
    ? data.data
    : Array.isArray(data)
      ? data
      : [];

  const securityIncidents = logs.filter(
    (l: any) => l.classification === "SECURITY" || l.type === "security"
  ).length;

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Security Center"
        description="Authentication events, access control, and threat monitoring."
      />

      {/* Security Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          metric={{ label: "Total Events", value: logs.length }}
        />
        <StatCard
          metric={{
            label: "Security Incidents",
            value: securityIncidents,
            tone: "warn",
          }}
        />
      </div>

      {/* Audit Log */}
      <DataTable
        title="Audit Log"
        rows={logs}
        columns={[
          {
            key: "actor",
            label: "Actor",
            sortable: true,
            render: (row: any) => row.actor ?? row.user ?? "—",
          },
          {
            key: "action",
            label: "Action",
            sortable: true,
            render: (row: any) => row.action ?? row.event ?? "—",
          },
          {
            key: "reason",
            label: "Detail",
            sortable: false,
            render: (row: any) => row.reason ?? row.detail ?? "—",
          },
          {
            key: "timestamp",
            label: "Timestamp",
            sortable: true,
            render: (row: any) => row.timestamp ?? row.created_at ?? "—",
          },
        ]}
      />

      {/* Prometheus Info */}
      <div className="flex items-start gap-3 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-4">
        <ShieldAlert className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--text-muted))]" />
        <p className="text-sm text-[hsl(var(--text-muted))]">
          Prometheus security metrics are available at the{" "}
          <code className="rounded bg-[hsl(var(--bg))] px-1.5 py-0.5 text-xs font-mono">
            /metrics
          </code>{" "}
          endpoint. Monitor{" "}
          <code className="rounded bg-[hsl(var(--bg))] px-1.5 py-0.5 text-xs font-mono">
            rti_security_events_total
          </code>{" "}
          for real-time threat detection.
        </p>
      </div>
    </div>
  );
}
