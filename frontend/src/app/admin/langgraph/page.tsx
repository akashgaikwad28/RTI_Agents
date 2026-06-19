"use client";

import { GraphCanvas } from "@/components/ai-graph/GraphCanvas";
import { AgentTimeline } from "@/components/ai-graph/AgentTimeline";
import { DebateVisualizer } from "@/components/ai-graph/DebateVisualizer";
import { StatCard } from "@/components/data-display/stat-card";
import { DataTable } from "@/components/data-display/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { useGovernanceData, useToolsData } from "@/hooks/use-dashboard-data";

export default function AdminLangGraphPage() {
  const { data: govData } = useGovernanceData();
  const { data: toolsData } = useToolsData();

  const totalTools = Array.isArray(toolsData?.tools) ? toolsData.tools.length : 0;
  const healthyTools: string | number = Array.isArray(toolsData?.status)
    ? toolsData.status.filter((t: any) => t?.healthy === true || t?.status === "healthy").length
    : "N/A";
  const activeEvents = Array.isArray(govData?.events) ? govData.events.length : 0;

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Agent Operations Center"
        description="Agent health, execution traces, and workflow analytics."
      />

      <GraphCanvas />
      <AgentTimeline />
      <DebateVisualizer />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <StatCard metric={{ label: "Total Tools", value: totalTools }} />
        <StatCard metric={{ label: "Tool Health", value: healthyTools, tone: "good" }} />
        <StatCard metric={{ label: "Active Events", value: activeEvents }} />
      </div>

      {Array.isArray(toolsData?.tools) && (
        <DataTable
          title="Registered Tools"
          rows={toolsData.tools}
          columns={[
            { key: "name", label: "Name", sortable: true },
            { key: "description", label: "Description" },
            { key: "status", label: "Status", sortable: true },
          ]}
        />
      )}

      {Array.isArray(govData?.events) && (
        <DataTable
          title="Recent Workflow Events"
          rows={govData.events}
          columns={[
            { key: "event_type", label: "Event Type", sortable: true, render: (row: Record<string, unknown>) => String(row.event_type ?? row.type ?? "") },
            { key: "request_id", label: "Request ID", sortable: true },
            { key: "timestamp", label: "Timestamp", sortable: true, render: (row: Record<string, unknown>) => String(row.timestamp ?? row.created_at ?? "") },
          ]}
        />
      )}
    </div>
  );
}
