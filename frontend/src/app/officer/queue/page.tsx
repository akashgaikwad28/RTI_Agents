"use client";

import Link from "next/link";
import { DataTable } from "@/components/data-display/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { useOfficerQueue } from "@/hooks/use-dashboard-data";

export default function OfficerQueuePage() {
  const { data } = useOfficerQueue();
  const rows = data?.data ?? [];

  return (
    <div className="space-y-6">
      <SectionHeader title="Department Queue" description="Filter and export all RTIs assigned to your office." />
      <DataTable
        title="Assigned RTIs"
        rows={rows}
        columns={[
          { key: "trackingId", label: "Tracking ID", sortable: true },
          { key: "department", label: "Department", sortable: true },
          { key: "status", label: "Status", sortable: true },
          { key: "approvalStatus", label: "Approval", sortable: true },
          {
            key: "id",
            label: "Action",
            render: (row) => (
              <Link href={`/officer/rti/${row.id}`} className="text-[hsl(var(--accent))]">
                Review
              </Link>
            ),
          },
        ]}
      />
    </div>
  );
}

