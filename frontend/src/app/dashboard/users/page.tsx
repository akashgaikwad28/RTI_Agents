"use client";

import { Users, Shield, UserCheck, UserX } from "lucide-react";
import { cn } from "@/lib/utils";

const users = [
  { id: "1", name: "Akash Gaikwad", email: "akash@demo.com", role: "citizen", dept: "-", status: "active" },
  { id: "2", name: "Priya Sharma", email: "priya@demo.com", role: "citizen", dept: "-", status: "active" },
  { id: "3", name: "Officer Singh", email: "officer@demo.com", role: "officer", dept: "Education", status: "active" },
  { id: "4", name: "Admin Kumar", email: "admin@demo.com", role: "admin", dept: "All", status: "active" },
  { id: "5", name: "Rahul Patil", email: "rahul@demo.com", role: "citizen", dept: "-", status: "inactive" },
];

const roleBadge: Record<string, string> = {
  citizen: "bg-blue-500/10 text-blue-400 border-blue-500/30",
  officer: "bg-violet-500/10 text-violet-400 border-violet-500/30",
  admin: "bg-amber-500/10 text-amber-400 border-amber-500/30",
};

export default function UsersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">User Management</h2>
        <p className="text-sm text-[hsl(var(--text-muted))]">Manage platform users and role assignments.</p>
      </div>

      <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[hsl(var(--border))] bg-[hsl(var(--surface2))]">
              <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">User</th>
              <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">Role</th>
              <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">Department</th>
              <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[hsl(var(--border)/0.5)]">
            {users.map((u) => (
              <tr key={u.id} className="hover:bg-[hsl(var(--surface2))] transition-colors">
                <td className="px-5 py-3">
                  <p className="font-medium">{u.name}</p>
                  <p className="text-[10px] text-[hsl(var(--text-muted))]">{u.email}</p>
                </td>
                <td className="px-5 py-3">
                  <span className={cn("text-[10px] font-mono px-2 py-0.5 rounded-full border", roleBadge[u.role])}>
                    {u.role}
                  </span>
                </td>
                <td className="px-5 py-3 text-[hsl(var(--text-muted))]">{u.dept}</td>
                <td className="px-5 py-3">
                  <span className={cn("text-[10px]", u.status === "active" ? "text-emerald-400" : "text-red-400")}>
                    ● {u.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
