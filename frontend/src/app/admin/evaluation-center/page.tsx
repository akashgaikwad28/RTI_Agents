"use client";

import { SectionHeader } from "@/components/ui/section-header";
import { StatCard } from "@/components/data-display/stat-card";
import { DataTable } from "@/components/data-display/data-table";
import { useEvalData } from "@/hooks/use-dashboard-data";

export default function EvaluationCenterPage() {
  const { data } = useEvalData();
  const metrics = data?.metrics;

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Evaluation Center"
        description="Hallucination detection, benchmarks, and quality metrics."
      />

      {/* Quality Metrics */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          metric={{
            label: "Hallucination Rate",
            value: metrics?.hallucination_rate ?? "N/A",
            tone: "warn",
          }}
        />
        <StatCard
          metric={{
            label: "Retrieval Precision",
            value: metrics?.retrieval_precision ?? "N/A",
            tone: "good",
          }}
        />
        <StatCard
          metric={{
            label: "Reasoning Completeness",
            value: metrics?.reasoning_completeness ?? "N/A",
          }}
        />
        <StatCard
          metric={{
            label: "Compliance Score",
            value: metrics?.compliance_score ?? "N/A",
            tone: "good",
          }}
        />
      </div>

      {/* Evaluation Reports */}
      {Array.isArray(data?.reports) && (
        <DataTable
          title="Evaluation Reports"
          rows={data.reports}
          columns={[
            { key: "name", label: "Report Name", sortable: true },
            { key: "created_at", label: "Date", sortable: true },
          ]}
        />
      )}

      {/* Golden Datasets */}
      {Array.isArray(data?.benchmarks) && (
        <DataTable
          title="Golden Datasets"
          rows={data.benchmarks}
          columns={[
            { key: "name", label: "Name", sortable: true },
            { key: "description", label: "Type", sortable: true },
          ]}
        />
      )}
    </div>
  );
}
