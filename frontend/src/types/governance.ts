export type UserRole = "citizen" | "officer" | "admin";

export type WorkflowNodeStatus = "idle" | "running" | "completed" | "failed" | "warning";

export interface AuthTokens {
  accessToken: string;
  refreshToken?: string;
  expiresAt?: number;
}

export interface AppUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  department?: string;
  avatar?: string;
  phone?: string;
  address?: string;
  language: "en" | "hi" | "mr";
  createdAt?: string;
  created_at?: string;
}

export interface RTIListItem {
  id: string;
  requestId: string;
  trackingId: string;
  title: string;
  queryText: string;
  formalQuery?: string;
  department: string;
  status: string;
  approvalStatus: string;
  confidence: string;
  retrievalConfidence?: number;
  aiRiskScore?: number;
  createdAt: string;
  updatedAt: string;
}

export interface RTIDetail extends RTIListItem {
  citations: string[];
  reasoningTrace: Array<Record<string, unknown>>;
  workflowPath: string[];
  agentDurations: Record<string, number>;
  hallucinationFlags: string[];
  officerNotes?: string;
  governanceNotes?: string[];
  userInput?: Record<string, any>;
  language?: string;
  finalResponse?: string;
  officerResponse?: string;
  respondedBy?: string;
  respondedAt?: string;
}

export interface TableColumn<T> {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  render?: (row: T) => React.ReactNode;
}

export interface DashboardMetric {
  label: string;
  value: string | number;
  hint?: string;
  trend?: number;
  tone?: "default" | "good" | "warn" | "danger";
}

export interface AnalyticsSeriesPoint {
  label: string;
  value: number;
}

export interface WorkflowTraceNode {
  id: string;
  label: string;
  description: string;
  status: WorkflowNodeStatus;
  durationMs?: number;
  confidence?: number;
  details?: string;
}

export interface GovernanceSnapshot {
  pendingApprovals: number;
  retrievalEvents: number;
  toolLogs: number;
  memoryEvents: number;
}

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
  read: boolean;
  createdAt: string;
  href?: string;
}

export interface NewRTIFormValues {
  name: string;
  email: string;
  phone: string;
  address: string;
  department: string;
  language: "en" | "hi" | "mr";
  query_text: string;
  attachments: File[];
}

