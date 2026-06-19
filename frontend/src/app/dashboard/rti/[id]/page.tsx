"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  FileText,
  AlertTriangle,
  CheckCircle,
  Calendar,
  Layers,
  Sparkles,
  User,
  MapPin,
  Mail,
  Phone,
  Edit2,
  X,
  Check,
  Building2,
  Activity,
} from "lucide-react";
import { rtiService } from "@/services/endpoints";
import { StatCard } from "@/components/data-display/stat-card";
import { motion } from "framer-motion";

export default function CitizenRTIDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState("");
  const [submittingAction, setSubmittingAction] = useState(false);
  const [actionError, setActionError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["rti-detail", params.id],
    queryFn: async () => (await rtiService.getById(params.id)).data,
    refetchInterval: (queryData) => {
      // Poll every 3 seconds if status is processing to get live workflow updates
      const status = queryData?.state?.data?.status;
      return status === "processing" ? 3000 : false;
    },
  });

  // Pre-fill editedText when formalQuery loads
  useEffect(() => {
    if (data?.formalQuery && !editedText) {
      setEditedText(data.formalQuery);
    }
  }, [data?.formalQuery]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-[hsl(var(--accent)/0.2)] border-t-[hsl(var(--accent))] animate-spin" />
        <p className="text-sm text-[hsl(var(--text-muted))]">Fetching RTI details from secure ledger...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-8 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-red-400 mx-auto" />
        <h3 className="text-lg font-semibold">RTI Request Not Found</h3>
        <p className="text-sm text-[hsl(var(--text-muted))]">The requested application ID does not exist or you do not have permission to view it.</p>
        <button
          onClick={() => router.push("/dashboard/history")}
          className="px-4 py-2 text-sm font-medium bg-[hsl(var(--surface2))] rounded-lg border border-[hsl(var(--border))]"
        >
          Back to History
        </button>
      </div>
    );
  }

  const handleApproval = async (decision: "approved" | "rejected") => {
    setSubmittingAction(true);
    setActionError("");
    setSuccessMsg("");
    try {
      await rtiService.approve(params.id, {
        decision,
        approved_by: data?.userInput?.name || "citizen",
        edited_query: isEditing ? editedText : data?.formalQuery || "",
      });

      setSuccessMsg(`Application successfully ${decision}!`);
      setIsEditing(false);
      
      // Invalidate dashboard and detail queries
      queryClient.invalidateQueries({ queryKey: ["citizen-dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["rti-history"] });
      queryClient.invalidateQueries({ queryKey: ["rti-detail", params.id] });
      
      setTimeout(() => {
        refetch();
      }, 1000);
    } catch (err: any) {
      console.error(err);
      setActionError(err?.response?.data?.detail || err?.message || "Failed to submit approval choice.");
    } finally {
      setSubmittingAction(false);
    }
  };

  const isDraft = data.status === "awaiting_approval" && data.approvalStatus === "pending";
  const isProcessing = data.status === "processing";

  return (
    <div className="space-y-6 animate-fade-in">
      {/* ── Header ─────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[hsl(var(--border)/0.5)] pb-6">
        <div>
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[hsl(var(--surface2))] border border-[hsl(var(--border))] text-[hsl(var(--text-muted))]">
              ID: {data.requestId}
            </span>
            {data.trackingId && (
              <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-[hsl(var(--accent)/0.15)] text-[hsl(var(--accent))]">
                Tracking: {data.trackingId}
              </span>
            )}
          </div>
          <h2 className="text-2xl font-bold">RTI Application View</h2>
          <p className="text-xs text-[hsl(var(--text-muted))] flex items-center gap-1.5 mt-1.5">
            <Calendar className="w-3.5 h-3.5 text-[hsl(var(--accent))]" />
            Filed on {new Date(data.createdAt).toLocaleString()}
          </p>
        </div>

        {/* Action Status Badges */}
        <div className="flex gap-2">
          <span className={`text-xs font-semibold px-3 py-1.5 rounded-full border ${
            data.status === "completed" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" :
            data.status === "awaiting_approval" ? "bg-amber-500/10 text-amber-400 border-amber-500/20 animate-pulse" :
            data.status === "processing" ? "bg-blue-500/10 text-blue-400 border-blue-500/20" :
            "bg-[hsl(var(--surface2))] text-[hsl(var(--text-muted))] border-[hsl(var(--border))]"
          }`}>
            Status: {data.status}
          </span>
          <span className={`text-xs font-semibold px-3 py-1.5 rounded-full border ${
            data.approvalStatus === "approved" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" :
            data.approvalStatus === "rejected" ? "bg-red-500/10 text-red-400 border-red-500/20" :
            "bg-amber-500/10 text-amber-400 border-amber-500/20"
          }`}>
            Approval: {data.approvalStatus}
          </span>
        </div>
      </div>

      {/* ── Key Metrics ────────────────────────────── */}
      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-4">
        <StatCard metric={{ label: "Target Department", value: data.department || "Analyzing..." }} />
        <StatCard metric={{ label: "AI Retrieval Confidence", value: data.retrievalConfidence !== undefined ? `${(data.retrievalConfidence * 100).toFixed(0)}%` : "-" }} />
        <StatCard metric={{ label: "AI Risk Level", value: data.aiRiskScore !== undefined ? `${(data.aiRiskScore * 100).toFixed(0)}%` : "-", tone: (data.aiRiskScore ?? 0) > 0.5 ? "danger" : "good" }} />
        <StatCard metric={{ label: "Language Mode", value: data.language?.toUpperCase() || "EN" }} />
      </div>

      {/* ── Timeline & Processing State ─────────────────── */}
      {isProcessing && (
        <div className="p-6 rounded-xl border border-blue-500/15 bg-blue-500/5 space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 animate-spin">
              <Activity className="w-4.5 h-4.5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold">AI Agent Pipeline Running...</h3>
              <p className="text-xs text-[hsl(var(--text-muted))]">We are formulating your request, checking laws, and retrieving relevant information. Updates in real-time.</p>
            </div>
          </div>

          {/* Simple Pipeline Flow */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-2 pt-2 text-center text-xs">
            {[
              { label: "1. Router", status: "completed" },
              { label: "2. Formatter", status: "completed" },
              { label: "3. Classifier", status: "completed" },
              { label: "4. RAG Retrieval", status: "active" },
              { label: "5. Reviewer", status: "pending" },
              { label: "6. Tracker", status: "pending" }
            ].map((s) => (
              <div key={s.label} className={`p-2.5 rounded-lg border ${
                s.status === "completed" ? "bg-emerald-500/5 border-emerald-500/15 text-emerald-400" :
                s.status === "active" ? "bg-blue-500/10 border-blue-500/30 text-blue-300 font-medium animate-pulse" :
                "bg-[hsl(var(--surface2))] border-[hsl(var(--border))] text-[hsl(var(--text-muted))]"
              }`}>
                {s.label}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Human Approval Banner & Options ───────────────── */}
      {isDraft && (
        <div className="p-6 rounded-xl border border-amber-500/20 bg-amber-500/5 space-y-4">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-amber-500/15 flex items-center justify-center text-amber-400 shrink-0">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-semibold">Human Review & Approval Required</h3>
              <p className="text-sm text-[hsl(var(--text-muted))] leading-relaxed">
                Our AI agents have analyzed and professionally formulated your raw request. 
                Please review the drafted query below. You can approve it as is, edit it to your liking, or reject it.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-amber-500/30 text-amber-300 hover:bg-amber-500/10 text-xs font-semibold transition-colors"
              >
                <Edit2 className="w-3.5 h-3.5" />
                Edit AI Drafted Query
              </button>
            ) : (
              <button
                onClick={() => setIsEditing(false)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-[hsl(var(--border))] text-[hsl(var(--text))] hover:bg-[hsl(var(--surface2))] text-xs font-semibold transition-colors"
              >
                <X className="w-3.5 h-3.5" />
                Cancel Editing
              </button>
            )}

            <button
              onClick={() => handleApproval("approved")}
              disabled={submittingAction}
              className="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-emerald-500 hover:opacity-90 disabled:opacity-50 text-white text-xs font-semibold transition-all shadow-md shadow-emerald-500/10"
            >
              <Check className="w-4 h-4" />
              {isEditing ? "Save, Approve & Submit" : "Approve & Submit RTI"}
            </button>

            <button
              onClick={() => handleApproval("rejected")}
              disabled={submittingAction}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-red-500/30 text-red-400 hover:bg-red-500/10 disabled:opacity-50 text-xs font-semibold transition-all"
            >
              <X className="w-3.5 h-3.5" />
              Reject & Delete Draft
            </button>
          </div>

          {actionError && (
            <p className="text-sm text-red-400 mt-2 bg-red-500/10 border border-red-500/20 p-2.5 rounded-lg">{actionError}</p>
          )}
          {successMsg && (
            <p className="text-sm text-emerald-400 mt-2 bg-emerald-500/10 border border-emerald-500/20 p-2.5 rounded-lg font-semibold">{successMsg}</p>
          )}
        </div>
      )}

      {/* ── Official Response resolution section ─────────────── */}
      {data.finalResponse && (
        <section className="rounded-xl border-2 border-emerald-500/20 bg-emerald-500/8 p-6 space-y-3 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-bl-full pointer-events-none" />
          <h2 className="text-base font-bold text-emerald-400 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            Official Response Issued
          </h2>
          {data.respondedAt && (
            <p className="text-xs text-[hsl(var(--text-muted))]">
              Responded by department officer ({data.respondedBy || "Officer"}) on {new Date(data.respondedAt).toLocaleString()}
            </p>
          )}
          <div className="text-sm leading-relaxed text-[hsl(var(--text))] whitespace-pre-wrap font-sans bg-[hsl(var(--bg))] border border-[hsl(var(--border))] rounded-lg p-4 mt-2">
            {data.finalResponse}
          </div>
        </section>
      )}

      {/* ── Request Details Grid (Original vs Formatted) ────────────────── */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Original Query Card */}
        <section className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5 flex flex-col shadow-sm">
          <h3 className="text-sm font-semibold mb-3 flex items-center gap-2 border-b border-[hsl(var(--border)/0.5)] pb-3">
            <User className="w-4 h-4 text-[hsl(var(--accent))]" />
            Your Original Query
          </h3>
          <p className="whitespace-pre-wrap text-sm text-[hsl(var(--text-muted))] leading-relaxed flex-1">
            {data.queryText}
          </p>

          {data.userInput && (
            <div className="mt-4 pt-4 border-t border-[hsl(var(--border)/0.5)] grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-[hsl(var(--text-muted))] bg-[hsl(var(--surface2)/0.3)] p-3 rounded-lg">
              <div className="flex items-center gap-2">
                <User className="w-3.5 h-3.5 shrink-0 text-[hsl(var(--accent))]" />
                <span className="truncate">{data.userInput.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-3.5 h-3.5 shrink-0 text-[hsl(var(--accent))]" />
                <span className="truncate">{data.userInput.email}</span>
              </div>
              {data.userInput.phone_number && (
                <div className="flex items-center gap-2">
                  <Phone className="w-3.5 h-3.5 shrink-0 text-[hsl(var(--accent))]" />
                  <span>{data.userInput.phone_number}</span>
                </div>
              )}
              {data.userInput.address && (
                <div className="flex items-center gap-2">
                  <MapPin className="w-3.5 h-3.5 shrink-0 text-[hsl(var(--accent))]" />
                  <span className="truncate">{data.userInput.address}</span>
                </div>
              )}
            </div>
          )}
        </section>

        {/* AI Formatted Query Card */}
        <section className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5 flex flex-col shadow-sm">
          <h3 className="text-sm font-semibold mb-3 flex items-center justify-between border-b border-[hsl(var(--border)/0.5)] pb-3">
            <span className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-[hsl(var(--accent))]" />
              AI Formulated Application
            </span>
            {isEditing && (
              <span className="text-[10px] font-mono bg-amber-500/10 border border-amber-500/30 text-amber-300 px-1.5 py-0.5 rounded">
                Editing Draft...
              </span>
            )}
          </h3>

          {isEditing ? (
            <div className="flex-1 flex flex-col gap-2">
              <textarea
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
                rows={10}
                className="w-full flex-1 p-3 rounded-lg border border-amber-500/30 bg-[hsl(var(--bg))] text-sm text-[hsl(var(--text))] focus:outline-none focus:ring-2 focus:ring-amber-500/20 resize-none font-mono"
              />
              <p className="text-[10px] text-[hsl(var(--text-muted))]">
                Customize the AI formulated request below as needed before submission.
              </p>
            </div>
          ) : (
            <p className="whitespace-pre-wrap text-sm text-[hsl(var(--text-muted))] leading-relaxed flex-1 font-mono bg-[hsl(var(--bg))] border border-[hsl(var(--border)/0.5)] p-4 rounded-lg">
              {data.formalQuery || "Awaiting formal query compilation..."}
            </p>
          )}
        </section>
      </div>

      {/* ── Citations & retrieval context ─────────────────────── */}
      <section className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5 shadow-sm">
        <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <Building2 className="w-4 h-4 text-[hsl(var(--accent))]" />
          Knowledge Citations & Precedents
        </h2>
        
        {data.citations && data.citations.length > 0 ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {data.citations.map((citation, index) => (
              <div key={index} className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] p-4 text-xs text-[hsl(var(--text-muted))] leading-relaxed relative hover:border-[hsl(var(--accent)/0.3)] transition-colors">
                <div className="w-5 h-5 rounded bg-[hsl(var(--surface2))] flex items-center justify-center text-[10px] font-bold absolute top-2 right-2 border border-[hsl(var(--border))]">
                  {index + 1}
                </div>
                <p className="pr-6">{citation}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-4 rounded-lg bg-[hsl(var(--surface2))] border border-[hsl(var(--border))] text-xs text-[hsl(var(--text-muted))] text-center">
            No external citations or precedents registered for this request.
          </div>
        )}
      </section>

      {/* ── AI Governance & Reasoning trace timeline ─────────────────── */}
      {data.reasoningTrace && data.reasoningTrace.length > 0 && (
        <section className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-5 shadow-sm">
          <h2 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <Layers className="w-4 h-4 text-[hsl(var(--accent))]" />
            AI Governance & Reasoning Log
          </h2>

          <div className="space-y-4 font-mono text-xs leading-relaxed max-h-80 overflow-y-auto pr-2">
            {data.reasoningTrace.map((log, index) => (
              <div key={index} className="flex gap-3 text-[hsl(var(--text-muted))] hover:text-[hsl(var(--text))] transition-colors border-b border-[hsl(var(--border)/0.3)] pb-3 last:border-0 last:pb-0">
                <span className="text-[hsl(var(--accent))] font-bold shrink-0">[{index + 1}]</span>
                <div className="flex-1 space-y-1">
                  {log && typeof log === "object" && (log as any).node && (
                    <div className="text-xs font-semibold text-[hsl(var(--text))]">{String((log as any).node)}</div>
                  )}
                  <pre className="whitespace-pre-wrap font-sans text-xs bg-[hsl(var(--bg))] p-2.5 rounded border border-[hsl(var(--border)/0.5)] max-w-full overflow-x-auto text-[hsl(var(--text-muted))]">
                    {JSON.stringify(log, null, 2)}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
