import { TrendingDown, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";
import type { DashboardMetric } from "@/types/governance";

export function StatCard({ metric }: { metric: DashboardMetric }) {
  const toneClass = {
    default: "border-[hsl(var(--border))]",
    good: "border-emerald-500/30",
    warn: "border-amber-500/30",
    danger: "border-red-500/30",
  }[metric.tone ?? "default"];

  return (
    <article className={cn("rounded-lg border bg-[hsl(var(--surface))] p-4", toneClass)}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-[hsl(var(--text-muted))]">{metric.label}</p>
          <p className="mt-2 text-2xl font-semibold">{metric.value}</p>
          {metric.hint && <p className="mt-1 text-xs text-[hsl(var(--text-muted))]">{metric.hint}</p>}
        </div>
        {typeof metric.trend === "number" && (
          <span className={cn("inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs", metric.trend >= 0 ? "bg-emerald-500/10 text-emerald-500" : "bg-red-500/10 text-red-500")}>
            {metric.trend >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            {Math.abs(metric.trend)}%
          </span>
        )}
      </div>
    </article>
  );
}

