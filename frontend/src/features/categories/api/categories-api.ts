import { apiClient } from "@/lib/api-client";
import type { Category } from "@/types/api";

export interface CategoryPayload {
  name: string;
  description?: string | null;
}

export const categoriesApi = {
  list: () => apiClient.get<Category[]>("/categories").then((r) => r.data),
  create: (payload: CategoryPayload) =>
    apiClient.post<Category>("/categories", payload).then((r) => r.data),
  update: (id: number, payload: CategoryPayload) =>
    apiClient.put<Category>(`/categories/${id}`, payload).then((r) => r.data),
  remove: (id: number) => apiClient.delete(`/categories/${id}`),
};
