import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { dashboardApi } from "../api/dashboard-api";
import { KpiCard } from "@/components/ui/KpiCard";
import { Badge } from "@/components/ui/Badge";
import { Table, TableHead, TableBody, Th, Td, EmptyRow } from "@/components/ui/Table";
import { formatCurrency, formatDate, formatNumber } from "@/lib/format";

export function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: dashboardApi.getSummary,
  });

  if (isLoading || !data) {
    return <div className="text-sm text-slate-400">Cargando dashboard...</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-xl font-semibold text-slate-800">Dashboard</h1>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <KpiCard label="Ventas de hoy" value={formatCurrency(data.sales_today_total)} />
        <KpiCard label="Ventas del mes" value={formatCurrency(data.sales_month_total)} />
        <KpiCard label="Saldo en caja" value={formatCurrency(data.cash_balance)} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section>
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-700">Stock bajo</h2>
            <Link to="/products" className="text-xs text-brand-700 hover:underline">
              Ver productos
            </Link>
          </div>
          <Table>
            <TableHead>
              <tr>
                <Th>Producto</Th>
                <Th>Stock</Th>
                <Th>Minimo</Th>
              </tr>
            </TableHead>
            <TableBody>
              {data.low_stock_products.length === 0 ? (
                <EmptyRow colSpan={3} label="Sin alertas de stock" />
              ) : (
                data.low_stock_products.map((p) => (
                  <tr key={p.id}>
                    <Td>{p.name}</Td>
                    <Td>
                      <Badge tone="red">{formatNumber(p.current_stock)}</Badge>
                    </Td>
                    <Td>{formatNumber(p.min_stock)}</Td>
                  </tr>
                ))
              )}
            </TableBody>
          </Table>
        </section>

        <section>
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-700">Ventas recientes</h2>
            <Link to="/sales" className="text-xs text-brand-700 hover:underline">
              Ver ventas
            </Link>
          </div>
          <Table>
            <TableHead>
              <tr>
                <Th>Fecha</Th>
                <Th>Total</Th>
                <Th>Pago</Th>
              </tr>
            </TableHead>
            <TableBody>
              {data.recent_sales.length === 0 ? (
                <EmptyRow colSpan={3} label="Sin ventas recientes" />
              ) : (
                data.recent_sales.map((s) => (
                  <tr key={s.id}>
                    <Td>{formatDate(s.date)}</Td>
                    <Td>{formatCurrency(s.total)}</Td>
                    <Td>
                      <Badge tone={s.payment_method === "CONTADO" ? "green" : "amber"}>
                        {s.payment_method}
                      </Badge>
                    </Td>
                  </tr>
                ))
              )}
            </TableBody>
          </Table>
        </section>
      </div>
    </div>
  );
}
