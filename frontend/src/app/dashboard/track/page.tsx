"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Search, FileText, Clock, Filter, ArrowUpDown } from "lucide-react";
import { cn, statusColor, formatDate } from "@/lib/utils";
import Link from "next/link";

const demoRTIs = [
  { id: "RTI-202605-A1B2C3", query: "Road construction budget details for Pune district FY 2024-25", dept: "Road & Transport", status: "approved", confidence: "high", score: 0.95, date: "2025-05-08T10:30:00Z" },
  { id: "RTI-202605-D4E5F6", query: "Mid-Day Meal scheme status in Pune schools", dept: "Education", status: "processing", confidence: "high", score: 0.91, date: "2025-05-09T14:15:00Z" },
  { id: "RTI-202605-G7H8I9", query: "Water supply pipeline project for Hadapsar area", dept: "Municipal Corporation", status: "pending", confidence: "medium", score: 0.82, date: "2025-05-10T09:45:00Z" },
  { id: "RTI-202604-J1K2L3", query: "PM-KISAN beneficiary list for Satara district", dept: "Agriculture", status: "completed", confidence: "high", score: 0.97, date: "2025-04-20T16:00:00Z" },
  { id: "RTI-202604-M4N5O6", query: "COVID vaccination wastage data for Maharashtra", dept: "Health", status: "rejected", confidence: "low", score: 0.65, date: "2025-04-15T11:30:00Z" },
];

export default function TrackPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const filtered = demoRTIs.filter((rti) => {
    const matchesSearch = rti.id.toLowerCase().includes(searchQuery.toLowerCase()) || rti.query.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || rti.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Track RTI Applications</h2>
        <p className="text-sm text-[hsl(var(--text-muted))]">Search and monitor the status of your RTI requests.</p>
      </div>

      {/* Search & Filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by tracking ID or query..."
            className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="pl-10 pr-8 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] appearance-none"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      {/* Results Table */}
      <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[hsl(var(--border))] bg-[hsl(var(--surface2))]">
                <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">Tracking ID</th>
                <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">Query</th>
                <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">Department</th>
                <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">Status</th>
                <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">AI Score</th>
                <th className="px-5 py-3 text-left text-[10px] font-mono text-[hsl(var(--text-muted))] uppercase tracking-wider">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[hsl(var(--border)/0.5)]">
              {filtered.map((rti) => (
                <motion.tr
                  key={rti.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="hover:bg-[hsl(var(--surface2))] transition-colors cursor-pointer"
                >
                  <td className="px-5 py-3">
                    <Link href={`/dashboard/workflow?id=${rti.id}`} className="font-mono text-xs text-[hsl(var(--accent))] hover:underline">
                      {rti.id}
                    </Link>
                  </td>
                  <td className="px-5 py-3 max-w-[300px]">
                    <p className="truncate text-[hsl(var(--text))]">{rti.query}</p>
                  </td>
                  <td className="px-5 py-3 text-[hsl(var(--text-muted))]">{rti.dept}</td>
                  <td className="px-5 py-3">
                    <span className={cn("text-[10px] font-mono px-2 py-0.5 rounded-full border", statusColor(rti.status))}>
                      {rti.status}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <span className={cn("font-mono text-xs", rti.score >= 0.9 ? "text-emerald-400" : rti.score >= 0.7 ? "text-amber-400" : "text-red-400")}>
                      {(rti.score * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="px-5 py-3 text-xs text-[hsl(var(--text-muted))]">{formatDate(rti.date)}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
        {filtered.length === 0 && (
          <div className="p-12 text-center text-sm text-[hsl(var(--text-muted))]">
            No RTI applications found matching your criteria.
          </div>
        )}
      </div>
    </div>
  );
}
