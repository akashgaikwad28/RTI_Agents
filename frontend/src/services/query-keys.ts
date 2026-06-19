export const queryKeys = {
  me: ["me"] as const,
  dashboard: ["dashboard"] as const,
  rtiHistory: ["rti-history"] as const,
  workflow: (requestId: string) => ["workflow", requestId] as const,
  notifications: ["notifications"] as const,
};

