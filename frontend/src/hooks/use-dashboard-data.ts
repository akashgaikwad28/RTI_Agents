"use client";

import { useQuery } from "@tanstack/react-query";
import { adminService, analyticsService, evalService, governanceService, healthService, ragService, rtiService, toolsService } from "@/services/endpoints";

export function useCitizenDashboard() {
  return useQuery({
    queryKey: ["citizen-dashboard"],
    queryFn: async () => {
      const history = await rtiService.getMyRTIs(1, 5);
      return history.data;
    },
  });
}

export function useRTIHistory(page = 1, limit = 50) {
  return useQuery({
    queryKey: ["rti-history", page, limit],
    queryFn: async () => {
      const response = await rtiService.getMyRTIs(page, limit);
      return response.data;
    },
  });
}

export function useOfficerQueue() {
  return useQuery({
    queryKey: ["officer-queue"],
    queryFn: async () => (await rtiService.getAssigned(1, 20)).data,
  });
}

export function useAdminDashboard() {
  return useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: async () => {
      const [analytics, governance, health] = await Promise.all([
        analyticsService.getDashboard(),
        governanceService.getDashboard(),
        healthService.check(),
      ]);
      return { analytics: analytics.data, governance: governance.data, health: health.data };
    },
  });
}

export function useDetailedAnalytics() {
  return useQuery({
    queryKey: ["admin-detailed-analytics"],
    queryFn: async () => {
      const [dashboard, deptMetrics, aiMetrics] = await Promise.allSettled([
        analyticsService.getDashboard(),
        analyticsService.getDepartmentMetrics(),
        analyticsService.getAIMetrics(),
      ]);
      return {
        dashboard: dashboard.status === "fulfilled" ? dashboard.value.data : null,
        departmentMetrics: deptMetrics.status === "fulfilled" ? deptMetrics.value.data : null,
        aiMetrics: aiMetrics.status === "fulfilled" ? aiMetrics.value.data : null,
      };
    },
  });
}

export function useUsersTable() {
  return useQuery({
    queryKey: ["users-table"],
    queryFn: async () => (await adminService.getUsers(1, 50)).data,
  });
}

export function useCorpusData() {
  return useQuery({
    queryKey: ["admin-corpus"],
    queryFn: async () => {
      const [status, stats, health] = await Promise.allSettled([
        ragService.status(),
        ragService.stats(),
        ragService.corpusHealth(),
      ]);
      return {
        status: status.status === "fulfilled" ? status.value.data : null,
        stats: stats.status === "fulfilled" ? stats.value.data : null,
        health: health.status === "fulfilled" ? health.value.data : null,
      };
    },
  });
}

export function useEvalData() {
  return useQuery({
    queryKey: ["admin-eval"],
    queryFn: async () => {
      const [metrics, reports, benchmarks] = await Promise.allSettled([
        evalService.getMetrics(),
        evalService.getReports(),
        evalService.getBenchmarks(),
      ]);
      return {
        metrics: metrics.status === "fulfilled" ? metrics.value.data : null,
        reports: reports.status === "fulfilled" ? reports.value.data : null,
        benchmarks: benchmarks.status === "fulfilled" ? benchmarks.value.data : null,
      };
    },
  });
}

export function useToolsData() {
  return useQuery({
    queryKey: ["admin-tools"],
    queryFn: async () => {
      const [tools, status, metrics] = await Promise.allSettled([
        toolsService.list(),
        toolsService.status(),
        toolsService.metrics(),
      ]);
      return {
        tools: tools.status === "fulfilled" ? tools.value.data : null,
        status: status.status === "fulfilled" ? status.value.data : null,
        metrics: metrics.status === "fulfilled" ? metrics.value.data : null,
      };
    },
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ["admin-system-health"],
    queryFn: async () => (await healthService.check()).data,
    refetchInterval: 30000,
  });
}

export function useGovernanceData() {
  return useQuery({
    queryKey: ["admin-governance"],
    queryFn: async () => {
      const [dashboard, tools, events] = await Promise.allSettled([
        governanceService.getDashboard(),
        governanceService.getTools(),
        governanceService.getEvents(),
      ]);
      return {
        dashboard: dashboard.status === "fulfilled" ? dashboard.value.data : null,
        tools: tools.status === "fulfilled" ? tools.value.data : null,
        events: events.status === "fulfilled" ? events.value.data : null,
      };
    },
  });
}

export function useAllRTIs(page = 1, limit = 50) {
  return useQuery({
    queryKey: ["admin-all-rtis", page, limit],
    queryFn: async () => (await adminService.getAllRTIs(page, limit)).data,
  });
}

export function useAuditLogs(page = 1) {
  return useQuery({
    queryKey: ["admin-audit-logs", page],
    queryFn: async () => (await adminService.getAuditLogs(page)).data,
  });
}

