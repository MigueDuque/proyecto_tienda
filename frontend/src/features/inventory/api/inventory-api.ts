import { apiClient } from "@/lib/api-client";
import type { InventoryMovement } from "@/types/api";

export interface StockAdjustmentPayload {
  product_id: number;
  quantity_delta: number;
  notes?: string | null;
}

export const inventoryApi = {
  listMovements: (productId?: number) =>
    apiClient
      .get<InventoryMovement[]>("/inventory/movements", {
        params: productId ? { product_id: productId } : undefined,
      })
      .then((r) => r.data),
  adjustStock: (payload: StockAdjustmentPayload) =>
    apiClient.post<InventoryMovement>("/inventory/adjustments", payload).then((r) => r.data),
};
