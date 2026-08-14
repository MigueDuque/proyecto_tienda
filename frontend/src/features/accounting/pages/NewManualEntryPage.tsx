import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { accountingApi } from "../api/accounting-api";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { extractErrorMessage } from "@/lib/api-client";
import { formatCurrency } from "@/lib/format";

const lineSchema = z.object({
  account_id: z.coerce.number().int().positive("Selecciona una cuenta"),
  debit: z.coerce.number().min(0),
  credit: z.coerce.number().min(0),
  description: z.string().optional(),
});

const schema = z.object({
  description: z.string().min(1, "La descripcion es requerida"),
  lines: z.array(lineSchema).min(2, "Se requieren al menos dos lineas"),
});
type FormValues = z.infer<typeof schema>;

export function NewManualEntryPage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const { data: accounts } = useQuery({ queryKey: ["accounts"], queryFn: accountingApi.listAccounts });

  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      description: "",
      lines: [
        { account_id: 0, debit: 0, credit: 0 },
        { account_id: 0, debit: 0, credit: 0 },
      ],
    },
  });
  const { fields, append, remove } = useFieldArray({ control, name: "lines" });
  const lines = watch("lines");
  const totalDebit = lines?.reduce((sum, l) => sum + (Number(l.debit) || 0), 0) ?? 0;
  const totalCredit = lines?.reduce((sum, l) => sum + (Number(l.credit) || 0), 0) ?? 0;
  const isBalanced = totalDebit === totalCredit && totalDebit > 0;

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await accountingApi.createManualEntry(values);
      navigate("/accounting/journal");
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-xl font-semibold text-slate-800">Nuevo asiento manual</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="flex max-w-3xl flex-col gap-4">
        <Input label="Descripcion" error={errors.description?.message} {...register("description")} />

        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-700">Lineas</span>
            <Button
              type="button"
              variant="secondary"
              onClick={() => append({ account_id: 0, debit: 0, credit: 0 })}
            >
              Agregar linea
            </Button>
          </div>

          {fields.map((field, index) => (
            <div key={field.id} className="grid grid-cols-[1fr_110px_110px_auto] items-end gap-2">
              <Select {...register(`lines.${index}.account_id`)}>
                <option value="">Cuenta...</option>
                {accounts?.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.code} - {a.name}
                  </option>
                ))}
              </Select>
              <Input type="number" step="0.01" placeholder="Debito" {...register(`lines.${index}.debit`)} />
              <Input type="number" step="0.01" placeholder="Credito" {...register(`lines.${index}.credit`)} />
              <Button
                type="button"
                variant="ghost"
                onClick={() => fields.length > 2 && remove(index)}
                disabled={fields.length === 2}
              >
                Quitar
              </Button>
            </div>
          ))}
          {errors.lines?.message && <p className="text-sm text-red-600">{errors.lines.message}</p>}
        </div>

        <div className="flex items-center justify-end gap-4 border-t border-slate-200 pt-3 text-sm">
          <span>
            Debitos: <strong>{formatCurrency(totalDebit)}</strong>
          </span>
          <span>
            Creditos: <strong>{formatCurrency(totalCredit)}</strong>
          </span>
          <span className={isBalanced ? "text-green-600" : "text-red-600"}>
            {isBalanced ? "Balanceado" : "Descuadrado"}
          </span>
        </div>

        {error && <Alert>{error}</Alert>}

        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={() => navigate("/accounting/journal")}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isSubmitting || !isBalanced}>
            Registrar asiento
          </Button>
        </div>
      </form>
    </div>
  );
}
