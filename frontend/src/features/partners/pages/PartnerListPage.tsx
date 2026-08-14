import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { partnersApi } from "../api/partners-api";
import type { Partner, PartnerType } from "@/types/api";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Modal } from "@/components/ui/Modal";
import { Badge } from "@/components/ui/Badge";
import { Table, TableHead, TableBody, Th, Td, EmptyRow } from "@/components/ui/Table";
import { extractErrorMessage } from "@/lib/api-client";

const schema = z.object({
  type: z.enum(["CLIENTE", "PROVEEDOR", "AMBOS"]),
  name: z.string().min(1, "El nombre es requerido"),
  document_id: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().optional(),
  address: z.string().optional(),
  is_active: z.boolean(),
});
type FormValues = z.infer<typeof schema>;

const typeTone: Record<PartnerType, "blue" | "green" | "amber"> = {
  CLIENTE: "blue",
  PROVEEDOR: "green",
  AMBOS: "amber",
};

const filters: { label: string; value: PartnerType | undefined }[] = [
  { label: "Todos", value: undefined },
  { label: "Clientes", value: "CLIENTE" },
  { label: "Proveedores", value: "PROVEEDOR" },
  { label: "Ambos", value: "AMBOS" },
];

export function PartnerListPage() {
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<PartnerType | undefined>(undefined);
  const { data: partners, isLoading } = useQuery({
    queryKey: ["partners", filter],
    queryFn: () => partnersApi.list(filter),
  });
  const [editing, setEditing] = useState<Partner | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { is_active: true } });

  function openCreate() {
    setEditing(null);
    reset({
      type: "CLIENTE",
      name: "",
      document_id: "",
      phone: "",
      email: "",
      address: "",
      is_active: true,
    });
    setError(null);
    setShowForm(true);
  }

  function openEdit(partner: Partner) {
    setEditing(partner);
    reset({
      type: partner.type,
      name: partner.name,
      document_id: partner.document_id ?? "",
      phone: partner.phone ?? "",
      email: partner.email ?? "",
      address: partner.address ?? "",
      is_active: partner.is_active,
    });
    setError(null);
    setShowForm(true);
  }

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      if (editing) {
        await partnersApi.update(editing.id, values);
      } else {
        await partnersApi.create(values);
      }
      await queryClient.invalidateQueries({ queryKey: ["partners"] });
      setShowForm(false);
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  const deleteMutation = useMutation({
    mutationFn: partnersApi.remove,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["partners"] }),
  });

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Terceros</h1>
        <Button onClick={openCreate}>Nuevo tercero</Button>
      </div>

      <div className="flex gap-2">
        {filters.map((f) => (
          <button
            key={f.label}
            onClick={() => setFilter(f.value)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              filter === f.value ? "bg-brand-700 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <Table>
        <TableHead>
          <tr>
            <Th>Nombre</Th>
            <Th>Tipo</Th>
            <Th>Documento</Th>
            <Th>Telefono</Th>
            <Th>Acciones</Th>
          </tr>
        </TableHead>
        <TableBody>
          {isLoading ? (
            <EmptyRow colSpan={5} label="Cargando..." />
          ) : !partners || partners.length === 0 ? (
            <EmptyRow colSpan={5} />
          ) : (
            partners.map((p) => (
              <tr key={p.id}>
                <Td>{p.name}</Td>
                <Td>
                  <Badge tone={typeTone[p.type]}>{p.type}</Badge>
                </Td>
                <Td className="text-slate-500">{p.document_id ?? "-"}</Td>
                <Td className="text-slate-500">{p.phone ?? "-"}</Td>
                <Td>
                  <div className="flex gap-2">
                    <Button variant="secondary" onClick={() => openEdit(p)}>
                      Editar
                    </Button>
                    <Button
                      variant="danger"
                      onClick={() => {
                        if (confirm(`¿Eliminar el tercero "${p.name}"?`)) {
                          deleteMutation.mutate(p.id);
                        }
                      }}
                    >
                      Eliminar
                    </Button>
                  </div>
                </Td>
              </tr>
            ))
          )}
        </TableBody>
      </Table>

      {showForm && (
        <Modal title={editing ? "Editar tercero" : "Nuevo tercero"} onClose={() => setShowForm(false)}>
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3">
            <Select label="Tipo" error={errors.type?.message} {...register("type")}>
              <option value="CLIENTE">Cliente</option>
              <option value="PROVEEDOR">Proveedor</option>
              <option value="AMBOS">Ambos</option>
            </Select>
            <Input label="Nombre" error={errors.name?.message} {...register("name")} />
            <div className="grid grid-cols-2 gap-3">
              <Input label="Documento" {...register("document_id")} />
              <Input label="Telefono" {...register("phone")} />
            </div>
            <Input label="Correo" type="email" {...register("email")} />
            <Input label="Direccion" {...register("address")} />
            <label className="flex items-center gap-2 text-sm text-slate-600">
              <input type="checkbox" {...register("is_active")} />
              Activo
            </label>
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
