"use client";

const events = ["Plan created", "Tools selected", "RAG retrieved", "Debate completed", "Verifier passed", "Consensus queued"];

export function AgentTimeline() {
  return (
    <section className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-4">
      <h2 className="font-semibold text-sm mb-4">Agent Timeline</h2>
      <div className="space-y-3">
        {events.map((event, index) => (
          <div key={event} className="flex items-center gap-3">
            <span className="h-6 w-6 rounded-full bg-[hsl(var(--accent)/0.12)] text-[10px] text-[hsl(var(--accent))] flex items-center justify-center">{index + 1}</span>
            <span className="text-sm">{event}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

