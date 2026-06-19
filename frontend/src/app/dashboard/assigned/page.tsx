"use client";

import { cn, statusColor, formatDate } from "@/lib/utils";
import { ClipboardCheck, CheckCircle2, XCircle, Eye, MessageSquare } from "lucide-react";
import { useState } from "react";

const assignedCases = [
  { id: "RTI-202605-D4E5F6", citizen: "Akash Gaikwad", query: "Mid-Day Meal scheme status in Pune schools", status: "pending", score: 0.91, date: "2025-05-09" },
  { id: "RTI-202605-X7Y8Z9", citizen: "Priya Sharma", query: "Teacher recruitment details for Pune district", status: "pending", score: 0.88, date: "2025-05-10" },
  { id: "RTI-202604-P1Q2R3", citizen: "Rahul Patil", query: "School infrastructure grant utilization report", status: "approved", score: 0.95, date: "2025-04-28" },
];

export default function AssignedPage() {
  const [selected, setSelected] = useState<string | null>(null);

  const handleApprove = (id: string) => {
    alert(`Approved: ${id}`);
  };
  const handleReject = (id: string) => {
    alert(`Rejected: ${id}`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Assigned Cases</h2>
        <p className="text-sm text-[hsl(var(--text-muted))]">Review and approve RTI applications assigned to your department.</p>
      </div>

      <div className="space-y-4">
        {assignedCases.map((c) => (
          <div key={c.id} className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5">
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-xs text-[hsl(var(--accent))]">{c.id}</span>
                  <span className={cn("text-[10px] font-mono px-2 py-0.5 rounded-full border", statusColor(c.status))}>{c.status}</span>
                </div>
                <p className="text-sm font-medium mb-1">{c.query}</p>
                <p className="text-xs text-[hsl(var(--text-muted))]">By: {c.citizen} · Score: {(c.score * 100).toFixed(0)}% · {c.date}</p>
              </div>
              {c.status === "pending" && (
                <div className="flex gap-2">
                  <button onClick={() => handleApprove(c.id)} className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-medium hover:bg-emerald-500/20 transition-colors">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Approve
                  </button>
                  <button onClick={() => handleReject(c.id)} className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-red-500/10 text-red-400 border border-red-500/30 text-xs font-medium hover:bg-red-500/20 transition-colors">
                    <XCircle className="w-3.5 h-3.5" /> Reject
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
