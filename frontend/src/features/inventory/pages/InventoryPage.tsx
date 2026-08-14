import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { inventoryApi } from "../api/inventory-api";
import { productsApi } from "@/features/products/api/products-api";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Modal } from "@/components/ui/Modal";
import { Badge } from "@/components/ui/Badge";
import { Table, TableHead, TableBody, Th, Td, EmptyRow } from "@/components/ui/Table";
import { extractErrorMessage } from "@/lib/api-client";
import { formatDate, formatNumber } from "@/lib/format";
import type { MovementType } from "@/types/api";

const movementTone: Record<MovementType, "green" | "red" | "amber"> = {
  ENTRADA_COMPRA: "green",
  SALIDA_VENTA: "red",
  AJUSTE_ENTRADA: "green",
  AJUSTE_SALIDA: "amber",
};

const schema = z.object({
  product_id: z.coerce.number().int().positive("Selecciona un producto"),
  quantity_delta: z.coerce.number().refine((v) => v !== 0, "Debe ser distinto de cero"),
  notes: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

export function InventoryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const productIdParam = searchParams.get("product_id");
  const productId = productIdParam ? Number(productIdParam) : undefined;
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: products } = useQuery({ queryKey: ["products"], queryFn: productsApi.list });
  const { data: movements, isLoading } = useQuery({
    queryKey: ["inventory-movements", productId],
    queryFn: () => inventoryApi.listMovements(productId),
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  function productName(id: number) {
    return products?.find((p) => p.id === id)?.name ?? `#${id}`;
  }

  function openAdjustment() {
    reset({ product_id: productId ?? 0, quantity_delta: 0, notes: "" });
    setError(null);
    setShowForm(true);
  }

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await inventoryApi.adjustStock(values);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["inventory-movements"] }),
        queryClient.invalidateQueries({ queryKey: ["products"] }),
      ]);
      setShowForm(false);
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Inventario / Kardex</h1>
        <Button onClick={openAdjustment}>Ajuste de stock</Button>
      </div>

      <Select
        value={productId ?? ""}
        onChange={(e) => {
          const value = e.target.value;
          setSearchParams(value ? { product_id: value } : {});
        }}
        className="max-w-xs"
      >
        <option value="">Todos los productos</option>
        {products?.map((p) => (
          <option key={p.id} value={p.id}>
            {p.name}
          </option>
        ))}
      </Select>

      <Table>
        <TableHead>
          <tr>
            <Th>Fecha</Th>
            {!productId && <Th>Producto</Th>}
            <Th>Tipo</Th>
            <Th>Cantidad</Th>
            <Th>Costo unit.</Th>
            <Th>Saldo</Th>
            <Th>Notas</Th>
          </tr>
        </TableHead>
        <TableBody>
          {isLoading ? (
            <EmptyRow colSpan={7} label="Cargando..." />
          ) : !movements || movements.length === 0 ? (
            <EmptyRow colSpan={7} label="Sin movimientos" />
          ) : (
            movements.map((m) => (
              <tr key={m.id}>
                <Td>{formatDate(m.created_at)}</Td>
                {!productId && <Td>{productName(m.product_id)}</Td>}
                <Td>
                  <Badge tone={movementTone[m.movement_type]}>{m.movement_type}</Badge>
                </Td>
                <Td>{formatNumber(m.quantity)}</Td>
                <Td>{formatNumber(m.unit_cost)}</Td>
                <Td className="font-medium">{formatNumber(m.balance_after)}</Td>
                <Td className="text-slate-500">{m.notes ?? "-"}</Td>
              </tr>
            ))
          )}
        </TableBody>
      </Table>

      {showForm && (
        <Modal title="Ajuste de stock" onClose={() => setShowForm(false)}>
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3">
            <Select label="Producto" error={errors.product_id?.message} {...register("product_id")}>
              <option value="">Selecciona...</option>
              {products?.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} (stock actual: {formatNumber(p.current_stock)})
                </option>
              ))}
            </Select>
            <Input
              label="Cantidad (+ entrada / - salida)"
              type="number"
              step="0.01"
              error={errors.quantity_delta?.message}
              {...register("quantity_delta")}
            />
            <Input label="Notas" {...register("notes")} />
            {error && <Alert>{error}</Alert>}
            <div className="mt-2 flex justify-end gap-2">
              <Button type="button" variant="secondary" onClick={() => setShowForm(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                Guardar
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
