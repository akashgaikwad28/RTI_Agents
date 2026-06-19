// ─── TypeScript Definitions for RTI-Agent Frontend ───

export type UserRole = "citizen" | "officer" | "admin";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  department?: string;
  avatar?: string;
  phone?: string;
  address?: string;
  language: string;
  createdAt: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface RTIRequest {
  id: string;
  requestId: string;
  trackingId: string;
  name: string;
  email: string;
  phone?: string;
  address: string;
  queryText: string;
  formalQuery: string;
  department: string;
  subDepartment?: string;
  status: RTIStatus;
  approvalStatus: ApprovalStatus;
  confidence: string;
  language: string;
  reviewScore: number;
  groundingScore: number;
  hallucinationFlags: string[];
  retryCount: number;
  workflowPath: string[];
  agentDurations: Record<string, number>;
  approvedBy?: string;
  officerNotes?: string;
  createdAt: string;
  updatedAt: string;
}

export type RTIStatus =
  | "submitted"
  | "processing"
  | "under_review"
  | "ai_processing"
  | "assigned"
  | "department_review"
  | "response_generated"
  | "approved"
  | "rejected"
  | "completed"
  | "closed";

export type ApprovalStatus = "pending" | "approved" | "rejected";

export interface Department {
  id: string;
  name: string;
  shortName: string;
  icon: string;
  officerCount: number;
  pendingRTIs: number;
  totalRTIs: number;
  color: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
  read: boolean;
  createdAt: string;
  link?: string;
}

export interface AnalyticsData {
  totalRTIs: number;
  pendingRTIs: number;
  approvedRTIs: number;
  rejectedRTIs: number;
  avgResponseTime: number;
  aiSuccessRate: number;
  activeOfficers: number;
  monthlyTrend: { month: string; count: number }[];
  departmentMetrics: { department: string; count: number; approved: number }[];
  approvalRatio: number;
}

export interface WorkflowNode {
  id: string;
  name: string;
  status: "idle" | "running" | "completed" | "failed" | "skipped";
  duration?: number;
  confidence?: number;
  tokenCount?: number;
  output?: string;
}

export interface WorkflowExecution {
  requestId: string;
  nodes: WorkflowNode[];
  currentNode: string;
  startedAt: string;
  completedAt?: string;
  totalDuration?: number;
  retryCount: number;
}

export interface SystemHealth {
  status: string;
  version: string;
  environment: string;
  services: Record<string, string>;
}

export interface RTISubmitPayload {
  name: string;
  email: string;
  address: string;
  query_text: string;
  phone_number?: string;
  state?: string;
  district?: string;
  pincode?: string;
  language?: string;
  thread_id?: string;
}

export interface ApprovalPayload {
  decision: "approved" | "rejected";
  approved_by?: string;
  edited_query?: string;
}

export interface FeedbackPayload {
  tracking_id: string;
  rating: number;
  comment?: string;
  was_helpful: boolean;
}

// SSE Event types
export interface AgentStartEvent {
  agent: string;
  status: "running";
}

export interface AgentDoneEvent {
  agent: string;
  status: "done";
  duration_ms: number;
}

export interface ApprovalRequiredEvent {
  message: string;
  request_id: string;
  approve_url: string;
}

export interface CompleteEvent {
  tracking_id: string;
  status: string;
  message: string;
}
