"use client";

import { SectionHeader } from "@/components/ui/section-header";
import { StatCard } from "@/components/data-display/stat-card";
import { DataTable } from "@/components/data-display/data-table";
import { useAllRTIs } from "@/hooks/use-dashboard-data";

export default function ApprovalCenterPage() {
  const { data } = useAllRTIs();

  const allRtis = Array.isArray(data?.data)
    ? data.data
    : Array.isArray(data)
      ? data
      : [];

  const pending = allRtis.filter(
    (r: any) => r.approvalStatus === "pending" || r.approval_status === "pending"
  );

  const history = allRtis.filter(
    (r: any) => r.approvalStatus !== "pending" && r.approval_status !== "pending"
  );

  const approvedCount = history.filter(
    (r: any) => r.approvalStatus === "approved" || r.approval_status === "approved"
  ).length;

  const rejectedCount = history.filter(
    (r: any) => r.approvalStatus === "rejected" || r.approval_status === "rejected"
  ).length;

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Human Approval Center"
        description="Pending approvals, approval history, and audit trail."
      />

      {/* Approval Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          metric={{ label: "Pending", value: pending.length, tone: "warn" }}
        />
        <StatCard
          metric={{ label: "Approved", value: approvedCount, tone: "good" }}
        />
        <StatCard
          metric={{ label: "Rejected", value: rejectedCount, tone: "danger" }}
        />
        <StatCard metric={{ label: "Total", value: allRtis.length }} />
      </div>

      {/* Pending Approvals */}
      <DataTable
        title="Pending Approvals"
        rows={pending}
        columns={[
          {
            key: "trackingId",
            label: "Tracking ID",
            sortable: true,
            render: (row: any) => row.trackingId ?? row.tracking_id ?? "—",
          },
          { key: "department", label: "Department", sortable: true },
          { key: "status", label: "Status", sortable: true },
          {
            key: "createdAt",
            label: "Created At",
            sortable: true,
            render: (row: any) => row.createdAt ?? row.created_at ?? "—",
          },
        ]}
      />

      {/* Approval History */}
      <DataTable
        title="Approval History"
        rows={history}
        columns={[
          {
            key: "trackingId",
            label: "Tracking ID",
            sortable: true,
            render: (row: any) => row.trackingId ?? row.tracking_id ?? "—",
          },
          { key: "department", label: "Department", sortable: true },
          {
            key: "approvalStatus",
            label: "Status",
            sortable: true,
            render: (row: any) =>
              row.approvalStatus ?? row.approval_status ?? "—",
          },
          {
            key: "updatedAt",
            label: "Updated At",
            sortable: true,
            render: (row: any) => row.updatedAt ?? row.updated_at ?? "—",
          },
        ]}
      />
    </div>
  );
}
