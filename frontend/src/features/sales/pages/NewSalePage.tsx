import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { salesApi } from "../api/sales-api";
import { partnersApi } from "@/features/partners/api/partners-api";
import { productsApi } from "@/features/products/api/products-api";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { extractErrorMessage } from "@/lib/api-client";
import { formatCurrency, formatNumber } from "@/lib/format";

const itemSchema = z.object({
  product_id: z.coerce.number().int().positive("Selecciona un producto"),
  quantity: z.coerce.number().positive("Debe ser mayor a 0"),
  unit_price: z.coerce.number().min(0),
});

const schema = z.object({
  partner_id: z.preprocess(
    (v) => (v === "" || v === undefined ? undefined : Number(v)),
    z.number().int().positive().optional(),
  ),
  payment_method: z.enum(["CONTADO", "CREDITO"]),
  items: z.array(itemSchema).min(1, "Agrega al menos un item"),
});
type FormValues = z.infer<typeof schema>;

export function NewSalePage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const { data: customers } = useQuery({
    queryKey: ["partners", "CLIENTE-or-AMBOS"],
    queryFn: async () => {
      const [clientes, ambos] = await Promise.all([
        partnersApi.list("CLIENTE"),
        partnersApi.list("AMBOS"),
      ]);
      return [...clientes, ...ambos];
    },
  });
  const { data: products } = useQuery({ queryKey: ["products"], queryFn: productsApi.list });

  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      payment_method: "CONTADO",
      items: [{ product_id: 0, quantity: 1, unit_price: 0 }],
    },
  });
  const { fields, append, remove } = useFieldArray({ control, name: "items" });
  const items = watch("items");
  const total =
    items?.reduce(
      (sum, item) => sum + (Number(item.quantity) || 0) * (Number(item.unit_price) || 0),
      0,
    ) ?? 0;

  // Warn about insufficient stock while the user types, instead of waiting for
  // the server to reject the sale on submit. The backend still validates it —
  // this only surfaces the mistake earlier.
  const stockWarnings = (items ?? []).map((item) => {
    const product = products?.find((p) => p.id === Number(item.product_id));
    if (!product) return null;
    const requested = Number(item.quantity) || 0;
    const available = Number(product.current_stock);
    if (requested <= available) return null;
    return { name: product.name, requested, available };
  });
  const hasStockProblem = stockWarnings.some((w) => w !== null);

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await salesApi.create(values);
      navigate("/sales");
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-xl font-semibold text-slate-800">Nueva venta</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="flex max-w-3xl flex-col gap-4">
        <div className="grid grid-cols-2 gap-3">
          <Select label="Cliente (opcional)" {...register("partner_id")}>
            <option value="">Consumidor final</option>
            {customers?.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </Select>
          <Select label="Forma de pago" {...register("payment_method")}>
            <option value="CONTADO">Contado</option>
            <option value="CREDITO">Credito</option>
          </Select>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-700">Items</span>
            <Button
              type="button"
              variant="secondary"
              onClick={() => append({ product_id: 0, quantity: 1, unit_price: 0 })}
            >
              Agregar item
            </Button>
          </div>

          {fields.map((field, index) => {
            const warning = stockWarnings[index];
            return (
              <div key={field.id} className="flex flex-col gap-1">
                <div className="grid grid-cols-[1fr_100px_120px_auto] items-end gap-2">
                  <Select {...register(`items.${index}.product_id`)}>
                    <option value="">Producto...</option>
                    {products?.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} — disponible: {formatNumber(p.current_stock)}
                      </option>
                    ))}
                  </Select>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="Cant."
                    className={warning ? "border-red-400 bg-red-50" : undefined}
                    {...register(`items.${index}.quantity`)}
                  />
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="Precio unit."
                    {...register(`items.${index}.unit_price`)}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => fields.length > 1 && remove(index)}
                    disabled={fields.length === 1}
                  >
                    Quitar
                  </Button>
                </div>
                {warning && (
                  <p className="text-xs font-medium text-red-600">
                    No hay suficiente "{warning.name}": pides {formatNumber(warning.requested)} y
                    solo hay {formatNumber(warning.available)}.
                  </p>
                )}
              </div>
            );
          })}
          {errors.items?.message && <p className="text-sm text-red-600">{errors.items.message}</p>}
        </div>

        <div className="flex items-center justify-end gap-2 border-t border-slate-200 pt-3">
          <span className="text-sm text-slate-500">Total:</span>
          <span className="text-lg font-semibold text-slate-800">{formatCurrency(total)}</span>
        </div>

        {hasStockProblem && (
          <Alert tone="warning" title="No se puede registrar la venta">
            No tienes suficiente inventario para uno o mas productos. Ajusta las cantidades o
            registra primero una compra.
          </Alert>
        )}

        {error && <Alert title="No se pudo registrar la venta">{error}</Alert>}

        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={() => navigate("/sales")}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting || hasStockProblem}>
            Registrar venta
          </Button>
        </div>
      </form>
    </div>
  );
}
