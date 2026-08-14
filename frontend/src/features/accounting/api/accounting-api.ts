import { apiClient } from "@/lib/api-client";
import type { Account, JournalEntry } from "@/types/api";

export interface ManualEntryLinePayload {
  account_id: number;
  debit: number;
  credit: number;
  description?: string | null;
}

export interface ManualEntryPayload {
  description: string;
  lines: ManualEntryLinePayload[];
}

export const accountingApi = {
  listAccounts: () => apiClient.get<Account[]>("/accounting/accounts").then((r) => r.data),
  getAccountBalance: (accountId: number) =>
    apiClient
      .get<{ account_id: number; balance: string }>(`/accounting/accounts/${accountId}/balance`)
      .then((r) => r.data),
  listJournalEntries: () =>
    apiClient.get<JournalEntry[]>("/accounting/journal-entries").then((r) => r.data),
  createManualEntry: (payload: ManualEntryPayload) =>
    apiClient.post<JournalEntry>("/accounting/journal-entries", payload).then((r) => r.data),
};
