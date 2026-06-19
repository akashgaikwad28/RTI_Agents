export default function HallucinationCenterPage() {
  return <Surface title="Hallucination Center" items={["Grounding alerts", "Unsupported claims", "Citation gaps", "Escalations"]} />;
}
function Surface({ title, items }: { title: string; items: string[] }) { return <section className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5"><h1 className="font-semibold mb-4">{title}</h1>{items.map((i) => <p className="text-sm py-2 border-b border-[hsl(var(--border))]" key={i}>{i}</p>)}</section>; }

