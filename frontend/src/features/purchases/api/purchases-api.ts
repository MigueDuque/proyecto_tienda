import { apiClient } from "@/lib/api-client";
import type { PaymentMethod, Purchase } from "@/types/api";

export interface PurchaseItemPayload {
  product_id: number;
  quantity: number;
  unit_cost: number;
}

export interface PurchasePayload {
  partner_id: number;
  payment_method: PaymentMethod;
  items: PurchaseItemPayload[];
}

export const purchasesApi = {
  list: () => apiClient.get<Purchase[]>("/purchases").then((r) => r.data),
  create: (payload: PurchasePayload) =>
    apiClient.post<Purchase>("/purchases", payload).then((r) => r.data),
};
