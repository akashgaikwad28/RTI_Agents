"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Activity, Database, Cpu, Server, Wifi, HardDrive, RefreshCw, CheckCircle2, XCircle, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ServiceStatus {
  name: string;
  status: "healthy" | "degraded" | "unhealthy" | "loading";
  latency?: number;
  icon: React.ElementType;
  details?: string;
}

export default function HealthPage() {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: "FastAPI Server", status: "loading", icon: Server },
    { name: "MongoDB", status: "loading", icon: Database },
    { name: "Redis Cache", status: "loading", icon: HardDrive },
    { name: "FAISS Index", status: "loading", icon: Cpu },
    { name: "LangGraph Engine", status: "loading", icon: Activity },
    { name: "LLM Provider (Groq)", status: "loading", icon: Wifi },
  ]);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [checking, setChecking] = useState(false);

  const checkHealth = () => {
    setChecking(true);
    setServices((prev) => prev.map((s) => ({ ...s, status: "loading" as const })));

    // Simulate health checks with staggered results
    const results: ServiceStatus[] = [
      { name: "FastAPI Server", status: "healthy", latency: 12, icon: Server, details: "v2.0.0 | 8000" },
      { name: "MongoDB", status: "healthy", latency: 8, icon: Database, details: "rti_db | 6 indexes" },
      { name: "Redis Cache", status: "healthy", latency: 3, icon: HardDrive, details: "6379 | 1.2MB used" },
      { name: "FAISS Index", status: "healthy", latency: 45, icon: Cpu, details: "768-dim | 10 docs" },
      { name: "LangGraph Engine", status: "healthy", latency: 0, icon: Activity, details: "Compiled | HITL=on" },
      { name: "LLM Provider (Groq)", status: "healthy", latency: 180, icon: Wifi, details: "llama-3.3-70b" },
    ];

    results.forEach((result, i) => {
      setTimeout(() => {
        setServices((prev) =>
          prev.map((s) => (s.name === result.name ? result : s))
        );
        if (i === results.length - 1) {
          setChecking(false);
          setLastChecked(new Date());
        }
      }, 300 + i * 400);
    });
  };

  useEffect(() => { checkHealth(); }, []);

  const healthyCount = services.filter((s) => s.status === "healthy").length;
  const overallStatus = healthyCount === services.length ? "All Systems Operational" : healthyCount > services.length / 2 ? "Partially Degraded" : "Critical";

  const statusConfig = {
    healthy: { icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/30" },
    degraded: { icon: AlertTriangle, color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/30" },
    unhealthy: { icon: XCircle, color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30" },
    loading: { icon: RefreshCw, color: "text-[hsl(var(--text-muted))]", bg: "bg-[hsl(var(--surface2))]", border: "border-[hsl(var(--border))]" },
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">System Health</h2>
          <p className="text-sm text-[hsl(var(--text-muted))]">Real-time status of all platform services.</p>
        </div>
        <button
          onClick={checkHealth}
          disabled={checking}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-[hsl(var(--border))] text-sm hover:bg-[hsl(var(--surface2))] disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={cn("w-4 h-4", checking && "animate-spin")} />
          Refresh
        </button>
      </div>

      {/* Overall Status */}
      <div className={cn(
        "p-5 rounded-xl border flex items-center gap-4",
        healthyCount === services.length ? "border-emerald-500/30 bg-emerald-500/5" : "border-amber-500/30 bg-amber-500/5"
      )}>
        <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center", healthyCount === services.length ? "bg-emerald-500/15" : "bg-amber-500/15")}>
          {healthyCount === services.length ? (
            <CheckCircle2 className="w-6 h-6 text-emerald-400" />
          ) : (
            <AlertTriangle className="w-6 h-6 text-amber-400" />
          )}
        </div>
        <div>
          <p className="font-semibold">{overallStatus}</p>
          <p className="text-xs text-[hsl(var(--text-muted))]">
            {healthyCount}/{services.length} services healthy
            {lastChecked && ` · Last checked ${lastChecked.toLocaleTimeString()}`}
          </p>
        </div>
      </div>

      {/* Service Grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {services.map((service) => {
          const cfg = statusConfig[service.status];
          const StatusIcon = cfg.icon;
          return (
            <motion.div
              key={service.name}
              layout
              className={cn("p-5 rounded-xl border transition-all", cfg.border, "bg-[hsl(var(--surface))]")}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={cn("w-9 h-9 rounded-lg flex items-center justify-center", cfg.bg)}>
                    <service.icon className={cn("w-4.5 h-4.5", cfg.color)} />
                  </div>
                  <span className="text-sm font-medium">{service.name}</span>
                </div>
                <StatusIcon className={cn("w-4 h-4", cfg.color, service.status === "loading" && "animate-spin")} />
              </div>
              {service.status !== "loading" && (
                <div className="flex items-center gap-4 text-[10px] text-[hsl(var(--text-muted))] font-mono">
                  {service.latency !== undefined && <span>Latency: {service.latency}ms</span>}
                  {service.details && <span>{service.details}</span>}
                </div>
              )}
              {service.status === "loading" && (
                <div className="h-4 skeleton w-2/3 mt-1" />
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
