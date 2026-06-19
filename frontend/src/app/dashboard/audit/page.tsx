"use client";

import { FileText, Clock } from "lucide-react";

const logs = [
  { time: "2025-05-10T17:30:00Z", action: "RTI Approved", user: "Officer Singh", target: "RTI-202605-A1B2C3", ip: "192.168.1.45" },
  { time: "2025-05-10T17:15:00Z", action: "RTI Submitted", user: "Akash Gaikwad", target: "RTI-202605-G7H8I9", ip: "103.21.58.12" },
  { time: "2025-05-10T16:45:00Z", action: "User Login", user: "Admin Kumar", target: "-", ip: "10.0.0.1" },
  { time: "2025-05-10T16:30:00Z", action: "RTI Rejected", user: "Officer Desai", target: "RTI-202604-M4N5O6", ip: "192.168.1.78" },
  { time: "2025-05-10T15:00:00Z", action: "System Health Check", user: "System", target: "All Services", ip: "-" },
  { time: "2025-05-10T14:30:00Z", action: "FAISS Index Rebuilt", user: "System", target: "10 documents", ip: "-" },
];

export default function AuditPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Audit Logs</h2>
        <p className="text-sm text-[hsl(var(--text-muted))]">Tamper-proof audit trail of all platform actions.</p>
      </div>

      <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[hsl(var(--border))] bg-[hsl(var(--surface2))]">
              <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">Timestamp</th>
              <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">Action</th>
              <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">User</th>
              <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">Target</th>
              <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">IP</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[hsl(var(--border)/0.5)]">
            {logs.map((log, i) => (
              <tr key={i} className="hover:bg-[hsl(var(--surface2))] transition-colors">
                <td className="px-5 py-3 font-mono text-xs text-[hsl(var(--text-muted))]">
                  {new Date(log.time).toLocaleString("en-IN", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "short" })}
                </td>
                <td className="px-5 py-3 font-medium">{log.action}</td>
                <td className="px-5 py-3 text-[hsl(var(--text-muted))]">{log.user}</td>
                <td className="px-5 py-3 font-mono text-xs text-[hsl(var(--accent))]">{log.target}</td>
                <td className="px-5 py-3 font-mono text-xs text-[hsl(var(--text-muted))]">{log.ip}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
