"use client";

export function StateInspector() {
  return (
    <pre className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-4 text-xs overflow-auto">
{JSON.stringify({ retrieved_context: 5, selected_tools: ["hybrid_search"], ai_risk_score: 0.31 }, null, 2)}
    </pre>
  );
}

