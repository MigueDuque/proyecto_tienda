import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { categoriesApi } from "../api/categories-api";
import type { Category } from "@/types/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Table, TableHead, TableBody, Th, Td, EmptyRow } from "@/components/ui/Table";
import { extractErrorMessage } from "@/lib/api-client";

const schema = z.object({
  name: z.string().min(1, "El nombre es requerido"),
  description: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

export function CategoryListPage() {
  const queryClient = useQueryClient();
  const { data: categories, isLoading } = useQuery({
    queryKey: ["categories"],
    queryFn: categoriesApi.list,
  });
  const [editing, setEditing] = useState<Category | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  function openCreate() {
    setEditing(null);
    reset({ name: "", description: "" });
    setError(null);
    setShowForm(true);
  }

  function openEdit(category: Category) {
    setEditing(category);
    reset({ name: category.name, description: category.description ?? "" });
    setError(null);
    setShowForm(true);
  }

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      if (editing) {
        await categoriesApi.update(editing.id, values);
      } else {
        await categoriesApi.create(values);
      }
      await queryClient.invalidateQueries({ queryKey: ["categories"] });
      setShowForm(false);
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  const deleteMutation = useMutation({
    mutationFn: categoriesApi.remove,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["categories"] }),
  });

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Categorias</h1>
        <Button onClick={openCreate}>Nueva categoria</Button>
      </div>

      <Table>
        <TableHead>
          <tr>
            <Th>Nombre</Th>
            <Th>Descripcion</Th>
            <Th>Acciones</Th>
          </tr>
        </TableHead>
        <TableBody>
          {isLoading ? (
            <EmptyRow colSpan={3} label="Cargando..." />
          ) : !categories || categories.length === 0 ? (
            <EmptyRow colSpan={3} />
          ) : (
            categories.map((c) => (
              <tr key={c.id}>
                <Td>{c.name}</Td>
                <Td className="text-slate-500">{c.description ?? "-"}</Td>
                <Td>
                  <div className="flex gap-2">
                    <Button variant="secondary" onClick={() => openEdit(c)}>
                      Editar
                    </Button>
                    <Button
                      variant="danger"
                      onClick={() => {
                        if (confirm(`¿Eliminar la categoria "${c.name}"?`)) {
                          deleteMutation.mutate(c.id);
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
        <Modal title={editing ? "Editar categoria" : "Nueva categoria"} onClose={() => setShowForm(false)}>
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3">
            <Input label="Nombre" error={errors.name?.message} {...register("name")} />
            <Input label="Descripcion" {...register("description")} />
            {error && <p className="text-sm text-red-600">{error}</p>}
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
