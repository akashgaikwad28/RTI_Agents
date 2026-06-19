"use client";

import { motion } from "framer-motion";
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import {
  TrendingUp, Users, Clock, CheckCircle2, BarChart3, Activity,
} from "lucide-react";
import { cn } from "@/lib/utils";

const monthlyData = [
  { month: "Jan", rtis: 45, approved: 38, rejected: 7 },
  { month: "Feb", rtis: 52, approved: 44, rejected: 8 },
  { month: "Mar", rtis: 61, approved: 53, rejected: 8 },
  { month: "Apr", rtis: 78, approved: 68, rejected: 10 },
  { month: "May", rtis: 95, approved: 82, rejected: 13 },
];

const departmentData = [
  { name: "Agriculture", value: 85, color: "#22c55e" },
  { name: "Road & Transport", value: 120, color: "#3b82f6" },
  { name: "Education", value: 95, color: "#a855f7" },
  { name: "Health", value: 70, color: "#ef4444" },
  { name: "Municipal", value: 110, color: "#f59e0b" },
];

const aiMetrics = [
  { month: "Jan", accuracy: 88, latency: 2.1, hallucinations: 3 },
  { month: "Feb", accuracy: 91, latency: 1.9, hallucinations: 2 },
  { month: "Mar", accuracy: 93, latency: 1.7, hallucinations: 1 },
  { month: "Apr", accuracy: 95, latency: 1.5, hallucinations: 1 },
  { month: "May", accuracy: 96, latency: 1.3, hallucinations: 0 },
];

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.08, duration: 0.5 } }),
};

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
        <p className="text-sm text-[hsl(var(--text-muted))]">Platform performance, AI metrics, and department insights.</p>
      </div>

      {/* ── KPI Cards ──────────────────────────────────── */}
      <motion.div initial="hidden" animate="visible" className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Total RTIs", value: "480", change: "+12%", icon: BarChart3, color: "text-blue-400", bg: "bg-blue-500/10" },
          { label: "AI Success Rate", value: "96%", change: "+3%", icon: Activity, color: "text-emerald-400", bg: "bg-emerald-500/10" },
          { label: "Avg Response", value: "18s", change: "-22%", icon: Clock, color: "text-violet-400", bg: "bg-violet-500/10" },
          { label: "Active Officers", value: "24", change: "+4", icon: Users, color: "text-amber-400", bg: "bg-amber-500/10" },
        ].map((stat, i) => (
          <motion.div key={stat.label} variants={fadeUp} custom={i} className="p-5 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))]">
            <div className="flex items-center justify-between mb-3">
              <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center", stat.bg)}>
                <stat.icon className={cn("w-5 h-5", stat.color)} />
              </div>
              <span className="flex items-center gap-1 text-emerald-400 text-xs font-mono">
                <TrendingUp className="w-3 h-3" />
                {stat.change}
              </span>
            </div>
            <p className="text-2xl font-bold">{stat.value}</p>
            <p className="text-xs text-[hsl(var(--text-muted))]">{stat.label}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* ── Charts Grid ────────────────────────────────── */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Monthly Trend */}
        <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5">
          <h3 className="text-sm font-semibold mb-4">Monthly RTI Trend</h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={monthlyData}>
              <defs>
                <linearGradient id="colorRti" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(224, 28%, 18%)" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: "hsl(215, 16%, 57%)" }} />
              <YAxis tick={{ fontSize: 11, fill: "hsl(215, 16%, 57%)" }} />
              <Tooltip contentStyle={{ background: "hsl(223, 47%, 9%)", border: "1px solid hsl(224, 28%, 18%)", borderRadius: "8px", fontSize: 12 }} />
              <Area type="monotone" dataKey="rtis" stroke="hsl(217, 91%, 60%)" fill="url(#colorRti)" strokeWidth={2} />
              <Area type="monotone" dataKey="approved" stroke="#22c55e" fill="transparent" strokeWidth={1.5} strokeDasharray="4 4" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Department Distribution */}
        <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5">
          <h3 className="text-sm font-semibold mb-4">Department Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={departmentData} cx="50%" cy="50%" outerRadius={100} innerRadius={55} dataKey="value" strokeWidth={2} stroke="hsl(223, 47%, 9%)">
                {departmentData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "hsl(223, 47%, 9%)", border: "1px solid hsl(224, 28%, 18%)", borderRadius: "8px", fontSize: 12 }} />
              <Legend iconType="circle" wrapperStyle={{ fontSize: 11 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* AI Accuracy */}
        <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5">
          <h3 className="text-sm font-semibold mb-4">AI Classification Accuracy</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={aiMetrics}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(224, 28%, 18%)" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: "hsl(215, 16%, 57%)" }} />
              <YAxis tick={{ fontSize: 11, fill: "hsl(215, 16%, 57%)" }} domain={[80, 100]} />
              <Tooltip contentStyle={{ background: "hsl(223, 47%, 9%)", border: "1px solid hsl(224, 28%, 18%)", borderRadius: "8px", fontSize: 12 }} />
              <Line type="monotone" dataKey="accuracy" stroke="#22c55e" strokeWidth={2} dot={{ fill: "#22c55e", r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Processing Latency */}
        <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5">
          <h3 className="text-sm font-semibold mb-4">Processing Latency (seconds)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={aiMetrics}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(224, 28%, 18%)" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: "hsl(215, 16%, 57%)" }} />
              <YAxis tick={{ fontSize: 11, fill: "hsl(215, 16%, 57%)" }} />
              <Tooltip contentStyle={{ background: "hsl(223, 47%, 9%)", border: "1px solid hsl(224, 28%, 18%)", borderRadius: "8px", fontSize: 12 }} />
              <Bar dataKey="latency" fill="hsl(217, 91%, 60%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
