"use client";

import { useState } from "react";
import { FileDropzone } from "@/components/forms/file-dropzone";
import { SectionHeader } from "@/components/ui/section-header";
import { useAuthStore } from "@/store";

export default function ProfilePage() {
  const user = useAuthStore((state) => state.user);
  const updateProfile = useAuthStore((state) => state.updateProfile);
  const [files, setFiles] = useState<File[]>([]);

  return (
    <div className="space-y-6">
      <SectionHeader title="Profile" description="Manage your public profile, language, and avatar." />
      <section className="grid gap-4 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5 md:grid-cols-2">
        <input className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] px-3 py-2" defaultValue={user?.name} onBlur={(event) => updateProfile({ name: event.target.value })} />
        <input className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] px-3 py-2" defaultValue={user?.email} onBlur={(event) => updateProfile({ email: event.target.value })} />
        <input className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] px-3 py-2" defaultValue={user?.phone} onBlur={(event) => updateProfile({ phone: event.target.value })} />
        <input className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] px-3 py-2" defaultValue={user?.address} onBlur={(event) => updateProfile({ address: event.target.value })} />
      </section>
      <FileDropzone files={files} onChange={setFiles} accept=".png,.jpg,.jpeg" multiple={false} />
    </div>
  );
}

