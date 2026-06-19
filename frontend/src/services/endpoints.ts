import api from "./api";
import type { AppUser, GovernanceSnapshot, RTIDetail, RTIListItem } from "@/types/governance";
import type { ApprovalPayload, AnalyticsData, FeedbackPayload, RTISubmitPayload, SystemHealth, User } from "@/types";

export const authService = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string; refresh_token?: string; user?: AppUser }>("/auth/login", { email, password }),
  register: (data: {
    name: string;
    email: string;
    password: string;
    confirm_password: string;
    role?: "citizen" | "officer";
    department?: string;
    phone?: string;
    language?: "en" | "hi" | "mr";
  }) => api.post<{ access_token: string; refresh_token?: string; user?: AppUser }>("/auth/register", data),

  refresh: (refreshToken: string) =>
    api.post<{ access_token: string; refresh_token?: string }>("/auth/refresh", { refresh_token: refreshToken }),

  logout: () => api.post("/auth/logout"),
  me: () => api.get<AppUser>("/auth/me"),

  changePassword: (payload: { current_password: string; new_password: string }) =>
    api.post("/auth/change-password", payload),

  forgotPassword: (payload: { email: string }) => api.post("/auth/forgot-password", payload),
  resetPassword: (payload: { token: string; new_password: string }) =>
    api.post("/auth/reset-password", payload),
};


export const rtiService = {
  submit: (data: RTISubmitPayload) => api.post<{ request_id: string; thread_id: string; status: string; stream_url: string }>("/api/v1/submit", data),
  getMyRTIs: (page = 1, limit = 20) => api.get<{ data: RTIListItem[]; total: number }>(`/api/v1/rtis?page=${page}&limit=${limit}`),
  getAssigned: (page = 1, limit = 20) => api.get<{ data: RTIListItem[]; total: number }>(`/api/v1/rtis/assigned?page=${page}&limit=${limit}`),
  getStatus: (trackingId: string) => api.get<RTIDetail>(`/api/v1/status/${trackingId}`),
  getById: (id: string) => api.get<RTIDetail>(`/api/v1/rtis/${id}`),
  approve: (requestId: string, data: ApprovalPayload) => api.post(`/api/v1/approve/${requestId}`, data),
  feedback: (data: FeedbackPayload) => api.post("/api/v1/feedback", data),
  respond: (id: string, responseText: string) => api.post(`/api/v1/rtis/${id}/respond`, { response_text: responseText }),
};

export const analyticsService = {
  getDashboard: () => api.get<AnalyticsData>("/api/v1/analytics"),
  getDepartmentMetrics: () => api.get("/api/v1/analytics/departments"),
  getAIMetrics: () => api.get("/api/v1/analytics/ai"),
};

export const governanceService = {
  getDashboard: () => api.get<GovernanceSnapshot>("/api/v1/governance/dashboard"),
  getTools: () => api.get("/api/v1/governance/tools"),
  getEvents: (requestId?: string) =>
    api.get("/api/v1/governance/events", { params: requestId ? { request_id: requestId } : undefined }),
  evaluate: (state: Record<string, unknown>) => api.post("/api/v1/governance/evaluate", state),
};

export const adminService = {
  getUsers: (page = 1, limit = 50) => api.get<{ data: User[]; total: number }>(`/api/v1/users?page=${page}&limit=${limit}`),
  getDepartments: () => api.get("/api/v1/departments"),
  getAuditLogs: (page = 1) => api.get(`/api/v1/audit?page=${page}`),
  getAllRTIs: (page = 1, limit = 50) => api.get<{ data: RTIListItem[]; total: number }>(`/api/v1/rtis/all?page=${page}&limit=${limit}`),
};

export const ragService = {
  status: () => api.get("/api/v1/rag/status"),
  stats: () => api.get("/api/v1/rag/stats"),
  corpusHealth: () => api.get("/api/v1/rag/corpus-health"),
  documentHistory: (docId: string) => api.get(`/api/v1/rag/document-history/${docId}`),
  queryTest: (payload: { query: string; department?: string; language?: string; k?: number }) => api.post("/api/v1/rag/query-test", payload),
  multilingualQuery: (payload: { query: string; department?: string; language?: "en" | "hi" | "mr"; k?: number }) =>
    api.post("/api/v1/rag/multilingual-query", payload),
};

export const multilingualService = {
  detect: (payload: { text: string }) => api.post("/api/v1/multilingual/detect", payload),
  translate: (payload: { text: string; target_language: "en" | "hi" | "mr"; source_language?: "en" | "hi" | "mr" | "unknown" }) =>
    api.post("/api/v1/multilingual/translate", payload),
  retrieve: (payload: { query: string; department?: string; response_language?: "en" | "hi" | "mr"; k?: number }) =>
    api.post("/api/v1/multilingual/retrieve", payload),
  ocr: (payload: { path: string; languages?: string[] }) => api.post("/api/v1/multilingual/ocr", payload),
  stats: (language: "en" | "hi" | "mr" = "en") => api.get("/api/v1/multilingual/stats", { params: { language } }),
};

export const healthService = {
  check: () => api.get<SystemHealth>("/health"),
};

export const workflowService = {
  getExecution: (requestId: string) => api.get(`/api/v1/workflow/${requestId}`),
};

export const evalService = {
  getMetrics: () => api.get("/api/v1/eval/metrics"),
  getReports: () => api.get("/api/v1/eval/reports"),
  getBenchmarks: () => api.get("/api/v1/eval/benchmarks"),
  hallucinationCheck: (payload: { query: string; response: string; sources: string[] }) =>
    api.post("/api/v1/eval/hallucination-check", payload),
};

export const toolsService = {
  list: () => api.get("/api/v1/tools"),
  status: () => api.get("/api/v1/tools/status"),
  metrics: () => api.get("/api/v1/tools/metrics"),
  getTrace: (traceId: string) => api.get(`/api/v1/tools/traces/${traceId}`),
};
