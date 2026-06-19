"use client";

import { GraphCanvas } from "@/components/ai-graph/GraphCanvas";
import { AgentTimeline } from "@/components/ai-graph/AgentTimeline";
import { RetrievalPanel } from "@/components/ai-graph/RetrievalPanel";
import { ToolExecutionPanel } from "@/components/ai-graph/ToolExecutionPanel";
import { DebateVisualizer } from "@/components/ai-graph/DebateVisualizer";
import { ConfidenceHeatmap } from "@/components/ai-graph/ConfidenceHeatmap";
import { StateInspector } from "@/components/ai-graph/StateInspector";
import { StatCard } from "@/components/data-display/stat-card";
import { DataTable } from "@/components/data-display/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { useGovernanceData } from "@/hooks/use-dashboard-data";

export default function GovernancePage() {
  const { data: govData } = useGovernanceData();
  const dashboard = govData?.dashboard as any;

  const complianceRate = dashboard?.compliance_rate ?? 0;

  return (
    <div className="space-y-6">
      <GraphCanvas />
      <div className="grid xl:grid-cols-3 gap-4">
        <AgentTimeline />
        <RetrievalPanel />
        <ToolExecutionPanel />
      </div>
      <DebateVisualizer />
      <div className="grid xl:grid-cols-2 gap-4">
        <ConfidenceHeatmap />
        <StateInspector />
      </div>

      <SectionHeader
        title="Retrieval Intelligence"
        description="Performance metrics and source analytics."
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard metric={{ label: "Pending Approvals", value: dashboard?.pendingApprovals ?? 0, tone: "warn" }} />
        <StatCard metric={{ label: "Retrieval Events", value: dashboard?.retrieval_events ?? 0 }} />
        <StatCard metric={{ label: "Tool Logs", value: dashboard?.tool_logs ?? 0 }} />
        <StatCard
          metric={{
            label: "Compliance Rate",
            value: `${complianceRate}%`,
            tone: Number(complianceRate) >= 80 ? "good" : "warn",
          }}
        />
      </div>

      {Array.isArray(govData?.events) && (
        <DataTable
          title="Governance Events"
          rows={govData.events}
          columns={[
            { key: "type", label: "Type", sortable: true, render: (row: Record<string, unknown>) => String(row.type ?? row.event_type ?? "") },
            { key: "request_id", label: "Request ID", sortable: true },
            { key: "timestamp", label: "Timestamp", sortable: true },
          ]}
        />
      )}
    </div>
  );
}
