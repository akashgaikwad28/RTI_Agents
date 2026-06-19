"use client";

export function ConfidenceHeatmap() {
  const values = [82, 74, 91, 63, 88, 70, 79, 84];
  return (
    <section className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-4">
      <h2 className="font-semibold text-sm mb-3">Confidence Heatmap</h2>
      <div className="grid grid-cols-4 gap-2">
        {values.map((value) => (
          <div key={value} className="h-16 rounded-lg flex items-center justify-center text-xs font-semibold" style={{ background: `hsl(152 69% ${Math.max(24, value / 2)}% / .24)` }}>
            {value}%
          </div>
        ))}
      </div>
    </section>
  );
}

