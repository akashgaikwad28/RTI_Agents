"use client";

import { StatCard } from "@/components/data-display/stat-card";
import { DataTable } from "@/components/data-display/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { useCorpusData } from "@/hooks/use-dashboard-data";

export default function CorpusPage() {
  const { data } = useCorpusData();

  const staleRatio = data?.health?.stale_document_ratio;
  const corpusStatus = data?.status?.status ?? "unknown";

  const departmentRows =
    data?.health?.department_coverage &&
    typeof data.health.department_coverage === "object"
      ? Object.entries(data.health.department_coverage).map(([dept, count]) => ({
          department: dept,
          documents: count,
        }))
      : [];

  const languageRows =
    data?.health?.language_distribution &&
    typeof data.health.language_distribution === "object"
      ? Object.entries(data.health.language_distribution).map(([lang, count]) => ({
          language: lang,
          documents: count,
        }))
      : [];

  return (
    <div className="space-y-6">
      <SectionHeader
        title="RAG Corpus Management"
        description="Document inventory, department coverage, and corpus health."
      />

      {/* Primary metrics */}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          metric={{
            label: "Total Documents",
            value: data?.stats?.document_count ?? data?.status?.document_count ?? 0,
          }}
        />
        <StatCard
          metric={{
            label: "Total Chunks",
            value: data?.health?.total_chunks ?? 0,
          }}
        />
        <StatCard
          metric={{
            label: "Stale Ratio",
            value: staleRatio ?? "N/A",
            tone:
              typeof staleRatio === "number" && staleRatio > 0.2
                ? "warn"
                : undefined,
          }}
        />
        <StatCard
          metric={{
            label: "Corpus Status",
            value: corpusStatus,
            tone:
              corpusStatus === "ok" || corpusStatus === "healthy"
                ? "good"
                : undefined,
          }}
        />
      </div>

      {/* Department coverage table */}
      {Array.isArray(departmentRows) && departmentRows.length > 0 && (
        <DataTable
          title="Department Coverage"
          rows={departmentRows}
          columns={[
            { key: "department", label: "Department", sortable: true },
            { key: "documents", label: "Documents", sortable: true },
          ]}
        />
      )}

      {/* Language distribution table */}
      {Array.isArray(languageRows) && languageRows.length > 0 && (
        <DataTable
          title="Language Distribution"
          rows={languageRows}
          columns={[
            { key: "language", label: "Language", sortable: true },
            { key: "documents", label: "Documents", sortable: true },
          ]}
        />
      )}

      {/* Additional health metrics */}
      <div className="grid gap-4 md:grid-cols-2">
        <StatCard
          metric={{
            label: "OCR Failure Rate",
            value: data?.health?.ocr_failure_rate ?? "N/A",
          }}
        />
        <StatCard
          metric={{
            label: "Embedding Failure Rate",
            value: data?.health?.embedding_failure_rate ?? "N/A",
          }}
        />
      </div>
    </div>
  );
}
