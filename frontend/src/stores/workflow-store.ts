"use client";

import { create } from "zustand";
import type { WorkflowTraceNode } from "@/types/governance";

interface WorkflowState {
  activeRequestId: string | null;
  nodes: WorkflowTraceNode[];
  setActiveRequestId: (requestId: string | null) => void;
  setNodes: (nodes: WorkflowTraceNode[]) => void;
  updateNode: (id: string, patch: Partial<WorkflowTraceNode>) => void;
  reset: () => void;
}

export const useWorkflowGraphStore = create<WorkflowState>((set) => ({
  activeRequestId: null,
  nodes: [],
  setActiveRequestId: (activeRequestId) => set({ activeRequestId }),
  setNodes: (nodes) => set({ nodes }),
  updateNode: (id, patch) =>
    set((state) => ({
      nodes: state.nodes.map((node) => (node.id === id ? { ...node, ...patch } : node)),
    })),
  reset: () => set({ activeRequestId: null, nodes: [] }),
}));

