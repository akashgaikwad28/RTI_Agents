"use client";

export function NodeRenderer({ name, status }: { name: string; status: string }) {
  return (
    <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-3">
      <p className="text-xs font-semibold">{name}</p>
      <p className="text-[10px] text-[hsl(var(--text-muted))]">{status}</p>
    </div>
  );
}

