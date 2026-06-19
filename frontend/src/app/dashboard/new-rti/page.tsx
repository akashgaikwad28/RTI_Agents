"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { FileDropzone } from "@/components/forms/file-dropzone";
import { SectionHeader } from "@/components/ui/section-header";
import { config } from "@/config";
import { rtiService } from "@/services/endpoints";
import type { NewRTIFormValues } from "@/types/governance";
import { useQueryClient } from "@tanstack/react-query";

const initialValues: NewRTIFormValues = {
  name: "",
  email: "",
  phone: "",
  address: "",
  department: config.departments[0].name,
  language: "en",
  query_text: "",
  attachments: [],
};

export default function NewRTIPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [form, setForm] = useState<NewRTIFormValues>(initialValues);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  return (
    <div className="space-y-6">
      <SectionHeader title="Create RTI Request" description="Submit a multilingual RTI request with optional supporting attachments." />
      <form
        className="grid gap-4 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5"
        onSubmit={async (event) => {
          event.preventDefault();
          setSubmitting(true);
          setError("");
          try {
            const response = await rtiService.submit({
              name: form.name,
              email: form.email,
              address: form.address,
              phone_number: form.phone,
              query_text: form.query_text,
              language: form.language,
            });
            queryClient.invalidateQueries({ queryKey: ["citizen-dashboard"] });
            queryClient.invalidateQueries({ queryKey: ["rti-history"] });
            router.push(`/dashboard/rti/${response.data.request_id}`);
          } catch {
            setError("We could not submit the RTI right now. Please try again.");
          } finally {
            setSubmitting(false);
          }
        }}
      >
        <div className="grid gap-4 md:grid-cols-2">
          <input required className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] px-3 py-2" placeholder="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
          <input required type="email" className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] px-3 py-2" placeholder="Email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
          <input required type="tel" className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] px-3 py-2" placeholder="Phone" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} />
          <select className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] px-3 py-2" value={form.department} onChange={(event) => setForm({ ...form, department: event.target.value })}>
            {config.departments.map((department) => (
              <option key={department.id} value={department.name}>
                {department.name}
              </option>
            ))}
          </select>
        </div>
        <textarea required minLength={5} className="min-h-28 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] px-3 py-2" placeholder="Address (Required)" value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} />
        <div className="grid gap-4 md:grid-cols-[180px_minmax(0,1fr)]">
          <select className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] px-3 py-2" value={form.language} onChange={(event) => setForm({ ...form, language: event.target.value as "en" | "hi" | "mr" })}>
            {config.languages.map((language) => (
              <option key={language.code} value={language.code}>
                {language.nativeName}
              </option>
            ))}
          </select>
          <textarea required minLength={10} className="min-h-36 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] px-3 py-2" placeholder="Describe the exact information you need (Required)" value={form.query_text} onChange={(event) => setForm({ ...form, query_text: event.target.value })} />
        </div>
        <FileDropzone files={form.attachments} onChange={(attachments) => setForm({ ...form, attachments })} />
        {error && <p className="text-sm text-red-500">{error}</p>}
        <div className="flex justify-end">
          <button type="submit" disabled={submitting} className="rounded-lg bg-[hsl(var(--accent))] px-4 py-2 text-sm font-medium text-white disabled:opacity-60">
            {submitting ? "Submitting..." : "Submit RTI"}
          </button>
        </div>
      </form>
    </div>
  );
}

