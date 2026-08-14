import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { accountingApi } from "../api/accounting-api";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { formatCurrency, formatDate } from "@/lib/format";
import type { JournalEntryReferenceType } from "@/types/api";

const refTone: Record<JournalEntryReferenceType, "green" | "amber" | "blue"> = {
  SALE: "green",
  PURCHASE: "amber",
  MANUAL: "blue",
};

export function JournalEntriesPage() {
  const { data: entries, isLoading } = useQuery({
    queryKey: ["journal-entries"],
    queryFn: accountingApi.listJournalEntries,
  });
  const { data: accounts } = useQuery({ queryKey: ["accounts"], queryFn: accountingApi.listAccounts });

  function accountLabel(id: number) {
    const account = accounts?.find((a) => a.id === id);
    return account ? `${account.code} - ${account.name}` : `#${id}`;
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Libro Diario</h1>
        <Link to="/accounting/journal/new">
          <Button>Nuevo asiento manual</Button>
        </Link>
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-400">Cargando...</p>
      ) : !entries || entries.length === 0 ? (
        <p className="text-sm text-slate-400">Aun no hay asientos contables</p>
      ) : (
        <div className="flex flex-col gap-3">
          {entries.map((entry) => (
            <div key={entry.id} className="rounded-lg border border-slate-200 bg-white p-4">
              <div className="mb-2 flex items-center justify-between">
                <div>
                  <span className="font-medium text-slate-800">{entry.description}</span>
                  <span className="ml-2 text-xs text-slate-400">{formatDate(entry.date)}</span>
                </div>
                <Badge tone={refTone[entry.reference_type]}>{entry.reference_type}</Badge>
              </div>
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase text-slate-400">
                  <tr>
                    <th className="py-1 font-medium">Cuenta</th>
                    <th className="py-1 font-medium">Debito</th>
                    <th className="py-1 font-medium">Credito</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {entry.lines.map((line) => (
                    <tr key={line.id}>
                      <td className="py-1.5 text-slate-600">{accountLabel(line.account_id)}</td>
                      <td className="py-1.5">{Number(line.debit) > 0 ? formatCurrency(line.debit) : "-"}</td>
                      <td className="py-1.5">{Number(line.credit) > 0 ? formatCurrency(line.credit) : "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
