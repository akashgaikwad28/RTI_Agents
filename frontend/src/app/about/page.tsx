import { SectionHeader } from "@/components/ui/section-header";

export default function AboutPage() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-20">
      <SectionHeader title="About RTI-Agent" description="RTI-Agent is an AI-native governance platform for filing, reviewing, and monitoring Right to Information workflows." />
      <div className="grid gap-4 md:grid-cols-3">
        {["Citizen portal", "Officer workflow", "Governance console"].map((item) => (
          <section key={item} className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5">
            <h2 className="text-sm font-semibold">{item}</h2>
            <p className="mt-2 text-sm text-[hsl(var(--text-muted))]">Enterprise frontend for secure, multilingual, real-time RTI operations.</p>
          </section>
        ))}
      </div>
    </main>
  );
}
