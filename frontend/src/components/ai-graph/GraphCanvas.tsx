"use client";

import { GitBranch } from "lucide-react";

const nodes = ["Router", "Planner", "Formatter", "Classifier", "Tools", "Retrieval", "Debate", "Critic", "Verifier", "Reviewer", "Approval", "Consensus", "Memory", "Tracker"];

export function GraphCanvas() {
  return (
    <section className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-4">
      <div className="flex items-center gap-2 mb-4">
        <GitBranch className="w-4 h-4 text-[hsl(var(--accent))]" />
        <h2 className="font-semibold text-sm">Live LangGraph Execution</h2>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-7 gap-3">
        {nodes.map((node, index) => (
          <div key={node} className="relative rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] p-3 min-h-20">
            <p className="text-xs font-semibold">{node}</p>
            <p className="mt-2 text-[10px] text-[hsl(var(--text-muted))]">step {index + 1}</p>
            {index === 5 && <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-[hsl(var(--accent))] animate-node-pulse" />}
          </div>
        ))}
      </div>
    </section>
  );
}

