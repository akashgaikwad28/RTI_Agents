"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { SectionHeader } from "@/components/ui/section-header";
import { rtiService } from "@/services/endpoints";

export default function OfficerRTIPage() {
  const params = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const [responseText, setResponseText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["officer-rti", params.id],
    queryFn: async () => (await rtiService.getById(params.id)).data,
  });

  const handleSubmitResponse = async () => {
    if (!responseText.trim()) {
      setErrorMsg("Please write a response before submitting.");
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      await rtiService.respond(params.id, responseText);
      setSuccessMsg("Your official response has been successfully sent to the citizen!");
      setResponseText("");
      // Refetch current request to update UI
      queryClient.invalidateQueries({ queryKey: ["officer-rti", params.id] });
      queryClient.invalidateQueries({ queryKey: ["officer-queue"] });
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.response?.data?.message ?? "Failed to submit response. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent"></div>
        <span className="ml-3 text-sm text-[hsl(var(--text-muted))]">Loading application details...</span>
      </div>
    );
  }

  const citizen = data?.userInput ?? {};
  // Determine if the officer has responded. Ignore citizen workflow submission messages in finalResponse.
  const displayedResponse = data?.officerResponse;
  const isResponded = !!displayedResponse;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <SectionHeader 
        title={`Officer Console — ${data?.trackingId || "RTI Application"}`} 
        description="Verify citizen identity, review the formal RTI request, and dispatch your official reply." 
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Citizen profile and Application content */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Citizen Metadata Profile */}
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4 text-emerald-500 flex items-center gap-2">
              👤 Applicant Identity
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wider">Citizen Name</p>
                <p className="text-sm font-medium text-[hsl(var(--text))]">{citizen.name || "Anonymous Citizen"}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wider">Email Address</p>
                <p className="text-sm font-medium text-[hsl(var(--text))]">{citizen.email || "N/A"}</p>
              </div>
              <div className="space-y-1 sm:col-span-2">
                <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wider">Mailing Address</p>
                <p className="text-sm font-medium text-[hsl(var(--text))]">{citizen.address || "N/A"}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wider">Submitted On</p>
                <p className="text-sm font-medium text-[hsl(var(--text))]">
                  {data?.createdAt ? new Date(data.createdAt).toLocaleString() : "N/A"}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold text-[hsl(var(--text-muted))] uppercase tracking-wider">Tracking ID</p>
                <p className="text-sm font-mono text-emerald-500 font-bold">{data?.trackingId || "N/A"}</p>
              </div>
            </div>
          </div>

          {/* Formatted Request */}
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-6 shadow-sm">
            <div>
              <h2 className="text-lg font-semibold text-[hsl(var(--text))] mb-3">
                Formal RTI Application
              </h2>
              {data?.formalQuery ? (
                <div className="rounded-lg bg-[hsl(var(--bg))] p-5 text-sm font-mono text-[hsl(var(--text))] border border-[hsl(var(--border))] whitespace-pre-wrap leading-relaxed">
                  {data.formalQuery}
                </div>
              ) : (
                <p className="text-sm text-[hsl(var(--text-muted))] italic">No formal application draft was found.</p>
              )}
            </div>
          </div>

        </div>

        {/* Right Side: Action Panel and Status */}
        <div className="space-y-6">
          
          {/* Status Indicator */}
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-6 shadow-sm">
            <h2 className="text-sm font-semibold mb-3 text-[hsl(var(--text-muted))] uppercase tracking-wider">Request Status</h2>
            <div className="flex items-center gap-3">
              <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium border ${
                isResponded 
                  ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-500" 
                  : "bg-amber-500/15 border-amber-500/30 text-amber-500"
              }`}>
                {isResponded ? "COMPLETED" : (data?.status ? data.status.toUpperCase() : "SUBMITTED")}
              </span>
              <span className="text-xs text-[hsl(var(--text-muted))]">
                Last updated {data?.updatedAt ? new Date(data.updatedAt).toLocaleDateString() : "N/A"}
              </span>
            </div>
          </div>

          {/* Officer Response Editor */}
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-6 shadow-sm space-y-4">
            <h2 className="text-lg font-semibold text-emerald-500">
              ✍️ Official Reply Console
            </h2>

            {isResponded ? (
              <div className="space-y-3">
                <p className="text-sm text-[hsl(var(--text-muted))]">Below is the official response sent to the citizen:</p>
                <div className="rounded-lg bg-emerald-500/5 p-4 text-sm text-[hsl(var(--text))] border border-emerald-500/20 whitespace-pre-wrap">
                  {displayedResponse}
                </div>
                <div className="text-xs text-[hsl(var(--text-muted))] italic">
                  Responded by: {data?.respondedBy || "Officer"}
                </div>
                {data?.respondedAt && (
                  <div className="text-xs text-[hsl(var(--text-muted))] italic">
                    Date & Time: {new Date(data.respondedAt).toLocaleString()}
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-[hsl(var(--text-muted))]">Type your official response below. The response will be registered in MongoDB, updated on the citizen's dashboard, and emailed directly to the citizen.</p>
                
                <textarea 
                  className="w-full min-h-36 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] p-3 text-sm text-[hsl(var(--text))] focus:border-emerald-500 focus:outline-none transition font-sans" 
                  placeholder="Type the official department response/scheme details here..." 
                  value={responseText}
                  onChange={(e) => setResponseText(e.target.value)}
                  disabled={isSubmitting}
                />

                {errorMsg && (
                  <div className="rounded-lg bg-red-500/15 border border-red-500/25 p-3 text-xs text-red-500">
                    ⚠️ {errorMsg}
                  </div>
                )}

                {successMsg && (
                  <div className="rounded-lg bg-emerald-500/15 border border-emerald-500/25 p-3 text-xs text-emerald-500">
                    🎉 {successMsg}
                  </div>
                )}

                <button 
                  onClick={handleSubmitResponse}
                  disabled={isSubmitting}
                  className="w-full rounded-lg bg-emerald-600 hover:bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white transition flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                      Sending response...
                    </>
                  ) : (
                    "Submit Response & Notify Citizen"
                  )}
                </button>
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
