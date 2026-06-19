"use client";

import { DataTable } from "@/components/data-display/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { useUsersTable } from "@/hooks/use-dashboard-data";

export default function AdminUsersPage() {
  const { data } = useUsersTable();
  const rows = data?.data ?? [];

  return (
    <div className="space-y-6">
      <SectionHeader title="User Management" description="Search, sort, and monitor all registered users." />
      <DataTable title="Users" rows={rows} columns={[{ key: "name", label: "Name", sortable: true }, { key: "email", label: "Email", sortable: true }, { key: "role", label: "Role", sortable: true }]} />
    </div>
  );
}

