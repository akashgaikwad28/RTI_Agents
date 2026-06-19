"use client";

import Link from "next/link";
import { DataTable } from "@/components/data-display/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { useRTIHistory } from "@/hooks/use-dashboard-data";

export default function HistoryPage() {
  const { data, isLoading } = useRTIHistory(1, 50);
  const rows = data?.data ?? [];

  return (
    <div className="space-y-6">
      <SectionHeader title="RTI History" description="Search, sort, and export your application history." />
      {isLoading && (
        <div className="flex items-center justify-center p-8 text-sm text-[hsl(var(--text-muted))] bg-[hsl(var(--surface))] rounded-lg border border-[hsl(var(--border))]">
          Loading your application history...
        </div>
      )}
      <DataTable
        title="Citizen Requests"
        rows={rows}
        columns={[
          { key: "trackingId", label: "Tracking ID", sortable: true },
          { key: "department", label: "Department", sortable: true },
          { key: "status", label: "Status", sortable: true },
          { key: "formalQuery", label: "Formatted Request", sortable: false },
          { key: "approvalStatus", label: "Approval", sortable: true },
          {
            key: "id",
            label: "Open",
            render: (row) => (
              <Link href={`/dashboard/rti/${row.id}`} className="text-[hsl(var(--accent))]">
                View
              </Link>
            ),
          },
        ]}
      />
    </div>
  );
}

