"use client";

import { Wheat, Route, GraduationCap, Heart, Building2, Users, FileText, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

const departments = [
  { name: "Agriculture", icon: Wheat, color: "#22c55e", officers: 5, pending: 8, total: 85 },
  { name: "Road & Transport", icon: Route, color: "#3b82f6", officers: 7, pending: 12, total: 120 },
  { name: "Education", icon: GraduationCap, color: "#a855f7", officers: 4, pending: 6, total: 95 },
  { name: "Health", icon: Heart, color: "#ef4444", officers: 6, pending: 4, total: 70 },
  { name: "Municipal Corporation", icon: Building2, color: "#f59e0b", officers: 8, pending: 15, total: 110 },
];

export default function DepartmentsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Department Management</h2>
        <p className="text-sm text-[hsl(var(--text-muted))]">Overview of all government departments and their RTI workload.</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {departments.map((dept) => (
          <div key={dept.name} className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5 hover:border-opacity-50 transition-all">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `${dept.color}15`, color: dept.color }}>
                <dept.icon className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-sm">{dept.name}</h3>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <p className="text-lg font-bold">{dept.officers}</p>
                <p className="text-[10px] text-[hsl(var(--text-muted))]">Officers</p>
              </div>
              <div>
                <p className="text-lg font-bold text-amber-400">{dept.pending}</p>
                <p className="text-[10px] text-[hsl(var(--text-muted))]">Pending</p>
              </div>
              <div>
                <p className="text-lg font-bold">{dept.total}</p>
                <p className="text-[10px] text-[hsl(var(--text-muted))]">Total RTIs</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
