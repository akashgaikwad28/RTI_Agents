"use client";

import { Languages } from "lucide-react";
import { useUIStore } from "@/stores/ui-store";

export function LanguageSwitcher() {
  const locale = useUIStore((state) => state.locale);
  const setLocale = useUIStore((state) => state.setLocale);

  return (
    <label className="flex items-center gap-2 rounded-lg border border-[hsl(var(--border))] px-3 py-2 text-xs">
      <Languages className="h-4 w-4 text-[hsl(var(--text-muted))]" />
      <select
        aria-label="Switch language"
        className="bg-transparent outline-none"
        value={locale}
        onChange={(event) => setLocale(event.target.value as "en" | "hi" | "mr")}
      >
        <option value="en">English</option>
        <option value="hi">Hindi</option>
        <option value="mr">Marathi</option>
      </select>
    </label>
  );
}

