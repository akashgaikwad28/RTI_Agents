"use client";

import { useState } from "react";
import { useAuthStore, useThemeStore, useLanguageStore } from "@/store";
import { useTheme } from "next-themes";
import { User, Palette, Globe, Shield, Save, Moon, Sun } from "lucide-react";
import { config } from "@/config";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const { theme, setTheme } = useTheme();
  const { language, setLanguage } = useLanguageStore();
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Settings</h2>
        <p className="text-sm text-[hsl(var(--text-muted))]">Manage your preferences and account settings.</p>
      </div>

      {/* Profile */}
      <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-6">
        <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
          <User className="w-4 h-4 text-[hsl(var(--accent))]" />
          Profile
        </h3>
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-[hsl(var(--text-muted))] mb-1.5">Name</label>
            <input type="text" defaultValue={user?.name} className="w-full px-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] transition-all" />
          </div>
          <div>
            <label className="block text-xs text-[hsl(var(--text-muted))] mb-1.5">Email</label>
            <input type="email" defaultValue={user?.email} disabled className="w-full px-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm opacity-60 cursor-not-allowed" />
          </div>
        </div>
      </div>

      {/* Appearance */}
      <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-6">
        <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
          <Palette className="w-4 h-4 text-[hsl(var(--accent))]" />
          Appearance
        </h3>
        <div className="flex gap-3">
          {(["dark", "light"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTheme(t)}
              className={cn(
                "flex items-center gap-2 px-4 py-2.5 rounded-lg border text-sm transition-all",
                theme === t ? "border-[hsl(var(--accent))] bg-[hsl(var(--accent)/0.1)] text-[hsl(var(--accent))]" : "border-[hsl(var(--border))] hover:bg-[hsl(var(--surface2))]"
              )}
            >
              {t === "dark" ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Language */}
      <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-6">
        <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
          <Globe className="w-4 h-4 text-[hsl(var(--accent))]" />
          Language
        </h3>
        <div className="flex gap-3">
          {config.languages.map((l) => (
            <button
              key={l.code}
              onClick={() => setLanguage(l.code)}
              className={cn(
                "px-4 py-2.5 rounded-lg border text-sm transition-all",
                language === l.code ? "border-[hsl(var(--accent))] bg-[hsl(var(--accent)/0.1)] text-[hsl(var(--accent))]" : "border-[hsl(var(--border))] hover:bg-[hsl(var(--surface2))]"
              )}
            >
              {l.nativeName}
            </button>
          ))}
        </div>
      </div>

      {/* Save */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[hsl(var(--accent))] text-white text-sm font-medium hover:opacity-90 transition-all"
        >
          <Save className="w-4 h-4" />
          {saved ? "Saved ✓" : "Save Changes"}
        </button>
      </div>
    </div>
  );
}
