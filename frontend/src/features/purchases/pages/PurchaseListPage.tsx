import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { purchasesApi } from "../api/purchases-api";
import { partnersApi } from "@/features/partners/api/partners-api";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Table, TableHead, TableBody, Th, Td, EmptyRow } from "@/components/ui/Table";
import { formatCurrency, formatDate } from "@/lib/format";

export function PurchaseListPage() {
  const { data: purchases, isLoading } = useQuery({
    queryKey: ["purchases"],
    queryFn: purchasesApi.list,
  });
  const { data: partners } = useQuery({ queryKey: ["partners", undefined], queryFn: () => partnersApi.list() });

  function partnerName(id: number) {
    return partners?.find((p) => p.id === id)?.name ?? `#${id}`;
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Compras</h1>
        <Link to="/purchases/new">
          <Button>Nueva compra</Button>
        </Link>
      </div>

      <Table>
        <TableHead>
          <tr>
            <Th>Fecha</Th>
            <Th>Proveedor</Th>
            <Th>Items</Th>
            <Th>Pago</Th>
            <Th>Total</Th>
          </tr>
        </TableHead>
        <TableBody>
          {isLoading ? (
            <EmptyRow colSpan={5} label="Cargando..." />
          ) : !purchases || purchases.length === 0 ? (
            <EmptyRow colSpan={5} label="Aun no hay compras registradas" />
          ) : (
            purchases.map((p) => (
              <tr key={p.id}>
                <Td>{formatDate(p.date)}</Td>
                <Td>{partnerName(p.partner_id)}</Td>
                <Td className="text-slate-500">{p.items.length}</Td>
                <Td>
                  <Badge tone={p.payment_method === "CONTADO" ? "green" : "amber"}>
                    {p.payment_method}
                  </Badge>
                </Td>
                <Td className="font-medium">{formatCurrency(p.total)}</Td>
              </tr>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
