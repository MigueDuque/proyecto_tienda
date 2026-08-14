import { apiClient } from "@/lib/api-client";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface MeResponse {
  id: number;
  email: string;
  full_name: string;
}

export const authApi = {
  login: (payload: LoginPayload) =>
    apiClient.post<TokenResponse>("/auth/login", payload).then((r) => r.data),
  me: () => apiClient.get<MeResponse>("/auth/me").then((r) => r.data),
};
