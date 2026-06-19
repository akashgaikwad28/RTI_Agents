"use client";

export function RetrievalPanel() {
  return <Panel title="Retrieval" rows={["Hybrid FAISS search", "Metadata filter", "Citation build", "Recency boost"]} />;
}

function Panel({ title, rows }: { title: string; rows: string[] }) {
  return (
    <section className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-4">
      <h2 className="font-semibold text-sm mb-3">{title}</h2>
      <div className="space-y-2">{rows.map((row) => <p key={row} className="text-xs text-[hsl(var(--text-muted))]">{row}</p>)}</div>
    </section>
  );
}

