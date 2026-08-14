import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { purchasesApi } from "../api/purchases-api";
import { partnersApi } from "@/features/partners/api/partners-api";
import { productsApi } from "@/features/products/api/products-api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { extractErrorMessage } from "@/lib/api-client";
import { formatCurrency } from "@/lib/format";

const itemSchema = z.object({
  product_id: z.coerce.number().int().positive("Selecciona un producto"),
  quantity: z.coerce.number().positive("Debe ser mayor a 0"),
  unit_cost: z.coerce.number().min(0),
});

const schema = z.object({
  partner_id: z.coerce.number().int().positive("Selecciona un proveedor"),
  payment_method: z.enum(["CONTADO", "CREDITO"]),
  items: z.array(itemSchema).min(1, "Agrega al menos un item"),
});
type FormValues = z.infer<typeof schema>;

export function NewPurchasePage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const { data: suppliers } = useQuery({
    queryKey: ["partners", "PROVEEDOR-or-AMBOS"],
    queryFn: async () => {
      const [proveedores, ambos] = await Promise.all([
        partnersApi.list("PROVEEDOR"),
        partnersApi.list("AMBOS"),
      ]);
      return [...proveedores, ...ambos];
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
    defaultValues: { payment_method: "CONTADO", items: [{ product_id: 0, quantity: 1, unit_cost: 0 }] },
  });
  const { fields, append, remove } = useFieldArray({ control, name: "items" });
  const items = watch("items");
  const total = items?.reduce((sum, item) => sum + (Number(item.quantity) || 0) * (Number(item.unit_cost) || 0), 0) ?? 0;

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await purchasesApi.create(values);
      navigate("/purchases");
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-xl font-semibold text-slate-800">Nueva compra</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="flex max-w-3xl flex-col gap-4">
        <div className="grid grid-cols-2 gap-3">
          <Select label="Proveedor" error={errors.partner_id?.message} {...register("partner_id")}>
            <option value="">Selecciona...</option>
            {suppliers?.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
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
              onClick={() => append({ product_id: 0, quantity: 1, unit_cost: 0 })}
            >
              Agregar item
            </Button>
          </div>

          {fields.map((field, index) => (
            <div key={field.id} className="grid grid-cols-[1fr_100px_120px_auto] items-end gap-2">
              <Select {...register(`items.${index}.product_id`)}>
                <option value="">Producto...</option>
                {products?.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </Select>
              <Input type="number" step="0.01" placeholder="Cant." {...register(`items.${index}.quantity`)} />
              <Input
                type="number"
                step="0.01"
                placeholder="Costo unit."
                {...register(`items.${index}.unit_cost`)}
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
          ))}
          {errors.items?.message && <p className="text-sm text-red-600">{errors.items.message}</p>}
        </div>

        <div className="flex items-center justify-end gap-2 border-t border-slate-200 pt-3">
          <span className="text-sm text-slate-500">Total:</span>
          <span className="text-lg font-semibold text-slate-800">{formatCurrency(total)}</span>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={() => navigate("/purchases")}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            Registrar compra
          </Button>
        </div>
      </form>
    </div>
  );
}
