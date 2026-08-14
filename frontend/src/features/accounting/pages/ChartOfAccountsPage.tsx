import { useQuery } from "@tanstack/react-query";
import { accountingApi } from "../api/accounting-api";
import { Badge } from "@/components/ui/Badge";
import { Table, TableHead, TableBody, Th, Td, EmptyRow } from "@/components/ui/Table";
import { formatCurrency } from "@/lib/format";
import type { AccountType } from "@/types/api";

const typeTone: Record<AccountType, "green" | "red" | "amber" | "blue" | "slate"> = {
  ACTIVO: "green",
  PASIVO: "red",
  PATRIMONIO: "blue",
  INGRESO: "amber",
  GASTO: "slate",
  COSTO: "slate",
};

function AccountBalanceCell({ accountId }: { accountId: number }) {
  const { data } = useQuery({
    queryKey: ["account-balance", accountId],
    queryFn: () => accountingApi.getAccountBalance(accountId),
  });
  return <Td className="font-medium">{data ? formatCurrency(data.balance) : "..."}</Td>;
}

export function ChartOfAccountsPage() {
  const { data: accounts, isLoading } = useQuery({
    queryKey: ["accounts"],
    queryFn: accountingApi.listAccounts,
  });

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-xl font-semibold text-slate-800">Plan de Cuentas</h1>

      <Table>
        <TableHead>
          <tr>
            <Th>Codigo</Th>
            <Th>Nombre</Th>
            <Th>Tipo</Th>
            <Th>Saldo</Th>
          </tr>
        </TableHead>
        <TableBody>
          {isLoading ? (
            <EmptyRow colSpan={4} label="Cargando..." />
          ) : !accounts || accounts.length === 0 ? (
            <EmptyRow colSpan={4} />
          ) : (
            accounts.map((a) => (
              <tr key={a.id}>
                <Td className="font-mono text-xs text-slate-500">{a.code}</Td>
                <Td>{a.name}</Td>
                <Td>
                  <Badge tone={typeTone[a.type]}>{a.type}</Badge>
                </Td>
                <AccountBalanceCell accountId={a.id} />
              </tr>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
