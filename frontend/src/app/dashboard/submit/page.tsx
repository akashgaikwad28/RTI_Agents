"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  Send,
  User,
  Mail,
  Phone,
  MapPin,
  Building2,
  Globe,
  FileText,
  Bot,
  Loader2,
  CheckCircle2,
  Sparkles,
} from "lucide-react";
import { config } from "@/config";
import { useAuthStore } from "@/store";
import { rtiService } from "@/services/endpoints";
import { useQueryClient } from "@tanstack/react-query";

export default function SubmitRTIPage() {
  const user = useAuthStore((s) => s.user);
  const router = useRouter();
  const queryClient = useQueryClient();
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [trackingId, setTrackingId] = useState("");
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    name: user?.name ?? "",
    email: user?.email ?? "",
    phone: user?.phone ?? "",
    address: user?.address ?? "",
    department: "",
    queryText: "",
    language: "en",
  });

  const charCount = form.queryText.length;
  const maxChars = 2000;

  const handleChange = (field: string, value: string) => {
    setForm((f) => ({ ...f, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await rtiService.submit({
        name: form.name,
        email: form.email,
        address: form.address,
        phone_number: form.phone,
        query_text: form.queryText,
        language: form.language,
      });

      // Invalidate queries so dashboard and history update
      queryClient.invalidateQueries({ queryKey: ["citizen-dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["rti-history"] });

      const reqId = response.data.request_id;
      setTrackingId(reqId);
      setSubmitted(true);
    } catch (err: any) {
      console.error("Submission failed:", err);
      setError(err?.response?.data?.detail || err?.message || "Submission failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-lg mx-auto text-center py-16"
      >
        <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center mx-auto mb-6">
          <CheckCircle2 className="w-8 h-8 text-emerald-400" />
        </div>
        <h2 className="text-2xl font-bold mb-2">RTI Submitted Successfully</h2>
        <p className="text-sm text-[hsl(var(--text-muted))] mb-6">
          Your request has been submitted and is being processed by our AI agents.
        </p>
        <div className="inline-flex items-center gap-2 px-5 py-3 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] mb-8">
          <span className="text-xs text-[hsl(var(--text-muted))]">Request ID:</span>
          <span className="font-mono text-sm font-semibold text-[hsl(var(--accent))]">{trackingId}</span>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={() => router.push(`/dashboard/rti/${trackingId}`)}
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-[hsl(var(--accent))] text-white text-sm font-medium hover:opacity-90 transition-opacity"
          >
            <Bot className="w-4 h-4" />
            View AI Workflow & Details
          </button>
          <button
            onClick={() => { setSubmitted(false); setForm((f) => ({ ...f, queryText: "", department: "" })); }}
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl border border-[hsl(var(--border))] text-sm font-medium hover:bg-[hsl(var(--surface2))] transition-colors"
          >
            File Another RTI
          </button>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-1">Submit RTI Application</h2>
        <p className="text-sm text-[hsl(var(--text-muted))]">
          Fill in the details below. Our AI agents will format, classify, and validate your request.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* ── Personal Info ──────────────────────────────── */}
        <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-6">
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <User className="w-4 h-4 text-[hsl(var(--accent))]" />
            Personal Information
          </h3>
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-[hsl(var(--text-muted))] mb-1.5">Full Name *</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
                <input type="text" required value={form.name} onChange={(e) => handleChange("name", e.target.value)} placeholder="Your full name" className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all" />
              </div>
            </div>
            <div>
              <label className="block text-xs text-[hsl(var(--text-muted))] mb-1.5">Email *</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
                <input type="email" required value={form.email} onChange={(e) => handleChange("email", e.target.value)} placeholder="you@example.com" className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all" />
              </div>
            </div>
            <div>
              <label className="block text-xs text-[hsl(var(--text-muted))] mb-1.5">Phone</label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
                <input type="tel" value={form.phone} onChange={(e) => handleChange("phone", e.target.value)} placeholder="+91 XXXXX XXXXX" className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all" />
              </div>
            </div>
            <div>
              <label className="block text-xs text-[hsl(var(--text-muted))] mb-1.5">Address *</label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
                <input type="text" required value={form.address} onChange={(e) => handleChange("address", e.target.value)} placeholder="City, State" className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all" />
              </div>
            </div>
          </div>
        </div>

        {/* ── RTI Details ────────────────────────────────── */}
        <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-6">
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-4 h-4 text-[hsl(var(--accent))]" />
            RTI Details
          </h3>

          <div className="grid sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs text-[hsl(var(--text-muted))] mb-1.5">Department *</label>
              <div className="relative">
                <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
                <select required value={form.department} onChange={(e) => handleChange("department", e.target.value)} className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all appearance-none">
                  <option value="">Select department...</option>
                  {config.departments.map((d) => (
                    <option key={d.id} value={d.name}>{d.name}</option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-xs text-[hsl(var(--text-muted))] mb-1.5">Language</label>
              <div className="relative">
                <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
                <select value={form.language} onChange={(e) => handleChange("language", e.target.value)} className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all appearance-none">
                  {config.languages.map((l) => (
                    <option key={l.code} value={l.code}>{l.name} ({l.nativeName})</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-xs text-[hsl(var(--text-muted))] mb-1.5">Your Query *</label>
            <textarea
              required
              rows={5}
              maxLength={maxChars}
              value={form.queryText}
              onChange={(e) => handleChange("queryText", e.target.value)}
              placeholder="Describe the information you want to request under RTI Act 2005..."
              className="w-full px-4 py-3 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all leading-relaxed"
            />
            <div className="flex items-center justify-between mt-1.5">
              <p className="text-[10px] text-[hsl(var(--text-muted))]">
                AI will format this into a formal RTI application
              </p>
              <p className={`text-[10px] font-mono ${charCount > maxChars * 0.9 ? "text-red-400" : "text-[hsl(var(--text-muted))]"}`}>
                {charCount}/{maxChars}
              </p>
            </div>
          </div>

          {/* AI Preview Hint */}
          {form.queryText.length > 20 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="mt-4 p-4 rounded-lg bg-[hsl(var(--accent)/0.06)] border border-[hsl(var(--accent)/0.15)]"
            >
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-3.5 h-3.5 text-[hsl(var(--accent))]" />
                <span className="text-[10px] font-mono text-[hsl(var(--accent))]">AI PREVIEW</span>
              </div>
              <p className="text-xs text-[hsl(var(--text-muted))] leading-relaxed">
                Your query will be processed by 7 AI agents: Router → Formatter → Classifier → Retrieval → Reviewer → Approval → Tracker.
                {form.department && <> The AI will route this to <strong className="text-[hsl(var(--text))]">{form.department}</strong>.</>}
              </p>
            </motion.div>
          )}
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400">
            {error}
          </div>
        )}

        {/* ── Submit Button ──────────────────────────────── */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || !form.name || !form.email || !form.address || !form.department || !form.queryText}
            className="inline-flex items-center gap-2 px-8 py-3 rounded-xl bg-[hsl(var(--accent))] text-white text-sm font-medium hover:opacity-90 disabled:opacity-40 transition-all shadow-lg shadow-[hsl(var(--accent)/0.2)]"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                AI Processing...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                Submit RTI
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
