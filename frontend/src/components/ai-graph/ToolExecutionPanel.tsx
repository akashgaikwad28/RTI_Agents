"use client";

export function ToolExecutionPanel() {
  return (
    <section className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-4">
      <h2 className="font-semibold text-sm mb-3">Tool Execution</h2>
      {["hybrid_search", "scheme_lookup", "grounding_score", "risk_analyzer"].map((tool) => (
        <div key={tool} className="flex items-center justify-between border-b border-[hsl(var(--border))] py-2 last:border-0">
          <span className="text-xs">{tool}</span>
          <span className="text-[10px] text-emerald-500">healthy</span>
        </div>
      ))}
    </section>
  );
}

