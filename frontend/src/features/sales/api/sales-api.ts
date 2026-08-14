import { apiClient } from "@/lib/api-client";
import type { PaymentMethod, Sale } from "@/types/api";

export interface SaleItemPayload {
  product_id: number;
  quantity: number;
  unit_price: number;
}

export interface SalePayload {
  partner_id?: number | null;
  payment_method: PaymentMethod;
  items: SaleItemPayload[];
}

export const salesApi = {
  list: () => apiClient.get<Sale[]>("/sales").then((r) => r.data),
  create: (payload: SalePayload) => apiClient.post<Sale>("/sales", payload).then((r) => r.data),
};
