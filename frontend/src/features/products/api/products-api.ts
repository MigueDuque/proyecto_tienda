import { apiClient } from "@/lib/api-client";
import type { Product } from "@/types/api";

export interface ProductPayload {
  sku: string;
  name: string;
  category_id: number;
  unit_of_measure: string;
  cost_price: number;
  sale_price: number;
  min_stock: number;
  description?: string | null;
  is_active: boolean;
}

export const productsApi = {
  list: () => apiClient.get<Product[]>("/products").then((r) => r.data),
  create: (payload: ProductPayload) =>
    apiClient.post<Product>("/products", payload).then((r) => r.data),
  update: (id: number, payload: ProductPayload) =>
    apiClient.put<Product>(`/products/${id}`, payload).then((r) => r.data),
  remove: (id: number) => apiClient.delete(`/products/${id}`),
};
