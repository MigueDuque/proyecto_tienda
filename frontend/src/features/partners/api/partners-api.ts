import { apiClient } from "@/lib/api-client";
import type { Partner, PartnerType } from "@/types/api";

export interface PartnerPayload {
  type: PartnerType;
  name: string;
  document_id?: string | null;
  phone?: string | null;
  email?: string | null;
  address?: string | null;
  is_active: boolean;
}

export const partnersApi = {
  list: (type?: PartnerType) =>
    apiClient
      .get<Partner[]>("/partners", { params: type ? { type } : undefined })
      .then((r) => r.data),
  create: (payload: PartnerPayload) =>
    apiClient.post<Partner>("/partners", payload).then((r) => r.data),
  update: (id: number, payload: PartnerPayload) =>
    apiClient.put<Partner>(`/partners/${id}`, payload).then((r) => r.data),
  remove: (id: number) => apiClient.delete(`/partners/${id}`),
};
