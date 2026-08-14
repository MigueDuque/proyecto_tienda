import { apiClient } from "@/lib/api-client";
import type { DashboardSummary } from "@/types/api";

export const dashboardApi = {
  getSummary: () => apiClient.get<DashboardSummary>("/dashboard/summary").then((r) => r.data),
};
