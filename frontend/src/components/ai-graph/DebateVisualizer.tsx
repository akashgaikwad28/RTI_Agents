"use client";

const personas = ["Legal Expert", "Governance Expert", "Information Auditor", "RTI Compliance", "Risk Assessment"];

export function DebateVisualizer() {
  return (
    <section className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-4">
      <h2 className="font-semibold text-sm mb-4">Debate Agents</h2>
      <div className="grid sm:grid-cols-2 xl:grid-cols-5 gap-3">
        {personas.map((persona) => (
          <div key={persona} className="rounded-lg bg-[hsl(var(--bg))] border border-[hsl(var(--border))] p-3">
            <p className="text-xs font-semibold">{persona}</p>
            <p className="text-[10px] text-[hsl(var(--text-muted))] mt-2">Checks reasoning, citations, and risk.</p>
          </div>
        ))}
      </div>
    </section>
  );
}

