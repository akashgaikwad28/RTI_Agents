"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  GitBranch,
  FileText,
  Tags,
  Search,
  ShieldCheck,
  UserCheck,
  RefreshCw,
  CheckCircle2,
  Play,
  Clock,
  Zap,
  Bot,
  Cpu,
} from "lucide-react";
import { cn } from "@/lib/utils";

type NodeStatus = "idle" | "running" | "completed" | "failed";

interface PipelineNode {
  id: string;
  label: string;
  description: string;
  icon: React.ElementType;
  status: NodeStatus;
  duration?: number;
  confidence?: number;
  tokens?: number;
}

const initialNodes: PipelineNode[] = [
  { id: "router", label: "Router", description: "Intent Detection", icon: GitBranch, status: "idle" },
  { id: "formatter", label: "Formatter", description: "Query Drafting", icon: FileText, status: "idle" },
  { id: "classifier", label: "Classifier", description: "Dept Routing", icon: Tags, status: "idle" },
  { id: "retrieval", label: "Retrieval", description: "Knowledge Search", icon: Search, status: "idle" },
  { id: "reviewer", label: "Reviewer", description: "Quality Check", icon: ShieldCheck, status: "idle" },
  { id: "approval", label: "Approval", description: "Human Review", icon: UserCheck, status: "idle" },
  { id: "tracker", label: "Tracker", description: "Finalization", icon: CheckCircle2, status: "idle" },
];

const statusStyles: Record<NodeStatus, string> = {
  idle: "border-[hsl(var(--border))] bg-[hsl(var(--surface))]",
  running: "border-[hsl(var(--accent))] bg-[hsl(var(--accent)/0.08)] animate-node-pulse",
  completed: "border-emerald-500/40 bg-emerald-500/8",
  failed: "border-red-500/40 bg-red-500/8",
};

const statusIcons: Record<NodeStatus, React.ElementType> = {
  idle: Clock,
  running: Cpu,
  completed: CheckCircle2,
  failed: RefreshCw,
};

export default function WorkflowPage() {
  const [nodes, setNodes] = useState<PipelineNode[]>(initialNodes);
  const [running, setRunning] = useState(false);
  const [currentIdx, setCurrentIdx] = useState(-1);
  const [totalDuration, setTotalDuration] = useState(0);

  const simulateExecution = () => {
    setNodes(initialNodes.map((n) => ({ ...n, status: "idle", duration: undefined, confidence: undefined, tokens: undefined })));
    setRunning(true);
    setCurrentIdx(0);
    setTotalDuration(0);
  };

  useEffect(() => {
    if (!running || currentIdx < 0 || currentIdx >= nodes.length) return;

    // Mark current as running
    setNodes((prev) =>
      prev.map((n, i) => (i === currentIdx ? { ...n, status: "running" } : n))
    );

    const duration = 800 + Math.random() * 1500;

    const timer = setTimeout(() => {
      const nodeDuration = Math.round(duration);
      const confidence = +(0.75 + Math.random() * 0.24).toFixed(2);
      const tokens = Math.round(200 + Math.random() * 800);

      setNodes((prev) =>
        prev.map((n, i) =>
          i === currentIdx
            ? { ...n, status: "completed", duration: nodeDuration, confidence, tokens }
            : n
        )
      );
      setTotalDuration((d) => d + nodeDuration);

      if (currentIdx < nodes.length - 1) {
        setCurrentIdx((i) => i + 1);
      } else {
        setRunning(false);
        setCurrentIdx(-1);
      }
    }, duration);

    return () => clearTimeout(timer);
  }, [running, currentIdx]);

  const completedCount = nodes.filter((n) => n.status === "completed").length;
  const avgConfidence = nodes.filter((n) => n.confidence).reduce((sum, n) => sum + (n.confidence ?? 0), 0) / (completedCount || 1);
  const totalTokens = nodes.reduce((sum, n) => sum + (n.tokens ?? 0), 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Bot className="w-6 h-6 text-[hsl(var(--accent))]" />
            AI Workflow Visualization
          </h2>
          <p className="text-sm text-[hsl(var(--text-muted))]">
            Watch the LangGraph pipeline process an RTI request in real time.
          </p>
        </div>
        <button
          onClick={simulateExecution}
          disabled={running}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[hsl(var(--accent))] text-white text-sm font-medium hover:opacity-90 disabled:opacity-50 transition-all shadow-lg shadow-[hsl(var(--accent)/0.2)]"
        >
          <Play className="w-4 h-4" />
          {running ? "Executing..." : "Run Pipeline"}
        </button>
      </div>

      {/* ── Metrics Bar ──────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Nodes Completed", value: `${completedCount}/${nodes.length}`, color: "text-emerald-400" },
          { label: "Total Duration", value: `${(totalDuration / 1000).toFixed(1)}s`, color: "text-blue-400" },
          { label: "Avg Confidence", value: `${(avgConfidence * 100).toFixed(0)}%`, color: "text-violet-400" },
          { label: "Tokens Used", value: totalTokens.toLocaleString(), color: "text-amber-400" },
        ].map((m) => (
          <div key={m.label} className="p-4 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))]">
            <p className="text-[10px] text-[hsl(var(--text-muted))] uppercase tracking-wider mb-1">{m.label}</p>
            <p className={cn("text-xl font-bold font-mono", m.color)}>{m.value}</p>
          </div>
        ))}
      </div>

      {/* ── Pipeline Graph ────────────────────────────────── */}
      <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-6 lg:p-8">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-4 lg:gap-0">
          {nodes.map((node, i) => {
            const StatusIcon = statusIcons[node.status];
            return (
              <div key={node.id} className="flex items-center gap-0 flex-1">
                {/* Node */}
                <motion.div
                  layout
                  className={cn(
                    "flex-1 p-4 rounded-xl border-2 transition-all duration-500 relative",
                    statusStyles[node.status]
                  )}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className={cn(
                      "w-9 h-9 rounded-lg flex items-center justify-center transition-all",
                      node.status === "completed" ? "bg-emerald-500/15" :
                      node.status === "running" ? "bg-[hsl(var(--accent)/0.15)]" :
                      "bg-[hsl(var(--surface2))]"
                    )}>
                      <node.icon className={cn(
                        "w-4.5 h-4.5 transition-colors",
                        node.status === "completed" ? "text-emerald-400" :
                        node.status === "running" ? "text-[hsl(var(--accent))]" :
                        "text-[hsl(var(--text-muted))]"
                      )} />
                    </div>
                    <div>
                      <p className="text-sm font-semibold">{node.label}</p>
                      <p className="text-[10px] text-[hsl(var(--text-muted))]">{node.description}</p>
                    </div>
                  </div>

                  {/* Stats Row */}
                  {node.status === "completed" && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      className="flex gap-4 mt-2 pt-2 border-t border-[hsl(var(--border)/0.5)]"
                    >
                      <div>
                        <p className="text-[9px] text-[hsl(var(--text-muted))] uppercase">Duration</p>
                        <p className="text-xs font-mono text-emerald-400">{node.duration}ms</p>
                      </div>
                      <div>
                        <p className="text-[9px] text-[hsl(var(--text-muted))] uppercase">Confidence</p>
                        <p className="text-xs font-mono text-blue-400">{((node.confidence ?? 0) * 100).toFixed(0)}%</p>
                      </div>
                      <div>
                        <p className="text-[9px] text-[hsl(var(--text-muted))] uppercase">Tokens</p>
                        <p className="text-xs font-mono text-amber-400">{node.tokens}</p>
                      </div>
                    </motion.div>
                  )}

                  {/* Status Badge */}
                  <div className="absolute -top-2 -right-2">
                    <div className={cn(
                      "w-5 h-5 rounded-full flex items-center justify-center",
                      node.status === "completed" ? "bg-emerald-500" :
                      node.status === "running" ? "bg-[hsl(var(--accent))]" :
                      node.status === "failed" ? "bg-red-500" :
                      "bg-[hsl(var(--border))]"
                    )}>
                      <StatusIcon className="w-3 h-3 text-white" />
                    </div>
                  </div>
                </motion.div>

                {/* Arrow */}
                {i < nodes.length - 1 && (
                  <div className="hidden lg:flex items-center px-2">
                    <div className={cn(
                      "w-8 h-0.5 transition-colors duration-500",
                      nodes[i + 1]?.status !== "idle" ? "bg-emerald-500/50" : "bg-[hsl(var(--border))]"
                    )} />
                    <Zap className={cn(
                      "w-3 h-3 transition-colors duration-500",
                      nodes[i + 1]?.status !== "idle" ? "text-emerald-400" : "text-[hsl(var(--text-muted)/0.3)]"
                    )} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Execution Log ─────────────────────────────────── */}
      <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] overflow-hidden">
        <div className="px-5 py-3 border-b border-[hsl(var(--border))] bg-[hsl(var(--surface2))]">
          <p className="text-xs font-mono text-[hsl(var(--text-muted))]">EXECUTION LOG</p>
        </div>
        <div className="p-4 font-mono text-xs space-y-1 max-h-60 overflow-auto">
          {nodes.filter((n) => n.status === "completed").map((n) => (
            <div key={n.id} className="flex gap-3 text-[hsl(var(--text-muted))]">
              <span className="text-emerald-400">✓</span>
              <span className="text-[hsl(var(--text))]">{n.label}</span>
              <span>completed in {n.duration}ms</span>
              <span className="text-blue-400">conf={((n.confidence ?? 0) * 100).toFixed(0)}%</span>
              <span className="text-amber-400">tokens={n.tokens}</span>
            </div>
          ))}
          {running && (
            <div className="flex gap-3 text-[hsl(var(--accent))]">
              <span className="animate-pulse">⟳</span>
              <span>{nodes[currentIdx]?.label} running...</span>
            </div>
          )}
          {!running && completedCount === 0 && (
            <div className="text-[hsl(var(--text-muted))]">Click &quot;Run Pipeline&quot; to start execution.</div>
          )}
        </div>
      </div>
    </div>
  );
}
