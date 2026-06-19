"use client";

import { StatCard } from "@/components/data-display/stat-card";
import { SectionHeader } from "@/components/ui/section-header";
import { useCorpusData } from "@/hooks/use-dashboard-data";

export default function ScrapingPage() {
  const { data } = useCorpusData();

  const corpusStatus = data?.status?.status ?? "unknown";

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Scraper Operations Center"
        description="Web crawling status, recent scrapes, and failure tracking."
      />

      <div className="grid gap-4 md:grid-cols-3">
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
        <StatCard
          metric={{
            label: "Document Count",
            value: data?.stats?.document_count ?? 0,
          }}
        />
        <StatCard
          metric={{
            label: "Vector Store",
            value: (data?.status?.vector_store as any)?.type ?? (data?.status?.vectorstore as any)?.type ?? "N/A",
          }}
        />
      </div>

      {/* Telemetry note */}
      <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5">
        <p className="text-sm text-[hsl(var(--text-muted))]">
          Scraper telemetry is collected in server logs and Prometheus metrics.
          Use the <code className="rounded bg-[hsl(var(--bg))] px-1.5 py-0.5 text-xs font-mono">/metrics</code> endpoint
          or Grafana dashboard for detailed crawl analytics.
        </p>
      </div>
    </div>
  );
}
