import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router-dom";
import { productsApi } from "../api/products-api";
import { categoriesApi } from "@/features/categories/api/categories-api";
import type { Product } from "@/types/api";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Modal } from "@/components/ui/Modal";
import { Badge } from "@/components/ui/Badge";
import { Table, TableHead, TableBody, Th, Td, EmptyRow } from "@/components/ui/Table";
import { extractErrorMessage } from "@/lib/api-client";
import { formatCurrency, formatNumber } from "@/lib/format";

const schema = z.object({
  sku: z.string().min(1, "El SKU es requerido"),
  name: z.string().min(1, "El nombre es requerido"),
  category_id: z.coerce.number().int().positive("Selecciona una categoria"),
  unit_of_measure: z.string().min(1, "La unidad es requerida"),
  cost_price: z.coerce.number().min(0),
  sale_price: z.coerce.number().min(0),
  min_stock: z.coerce.number().min(0),
  description: z.string().optional(),
  is_active: z.boolean(),
});
type FormValues = z.infer<typeof schema>;

export function ProductListPage() {
  const queryClient = useQueryClient();
  const { data: products, isLoading } = useQuery({ queryKey: ["products"], queryFn: productsApi.list });
  const { data: categories } = useQuery({ queryKey: ["categories"], queryFn: categoriesApi.list });
  const [editing, setEditing] = useState<Product | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { is_active: true },
  });

  function openCreate() {
    setEditing(null);
    reset({
      sku: "",
      name: "",
      category_id: categories?.[0]?.id ?? 0,
      unit_of_measure: "unidad",
      cost_price: 0,
      sale_price: 0,
      min_stock: 0,
      description: "",
      is_active: true,
    });
    setError(null);
    setShowForm(true);
  }

  function openEdit(product: Product) {
    setEditing(product);
    reset({
      sku: product.sku,
      name: product.name,
      category_id: product.category_id,
      unit_of_measure: product.unit_of_measure,
      cost_price: Number(product.cost_price),
      sale_price: Number(product.sale_price),
      min_stock: Number(product.min_stock),
      description: product.description ?? "",
      is_active: product.is_active,
    });
    setError(null);
    setShowForm(true);
  }

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      if (editing) {
        await productsApi.update(editing.id, values);
      } else {
        await productsApi.create(values);
      }
      await queryClient.invalidateQueries({ queryKey: ["products"] });
      setShowForm(false);
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  const deleteMutation = useMutation({
    mutationFn: productsApi.remove,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["products"] }),
  });

  function categoryName(id: number) {
    return categories?.find((c) => c.id === id)?.name ?? "-";
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Productos</h1>
        <Button onClick={openCreate}>Nuevo producto</Button>
      </div>

      <Table>
        <TableHead>
          <tr>
            <Th>SKU</Th>
            <Th>Nombre</Th>
            <Th>Categoria</Th>
            <Th>Costo</Th>
            <Th>Precio</Th>
            <Th>Stock</Th>
            <Th>Acciones</Th>
          </tr>
        </TableHead>
        <TableBody>
          {isLoading ? (
            <EmptyRow colSpan={7} label="Cargando..." />
          ) : !products || products.length === 0 ? (
            <EmptyRow colSpan={7} />
          ) : (
            products.map((p) => {
              const lowStock = Number(p.current_stock) < Number(p.min_stock);
              return (
                <tr key={p.id}>
                  <Td className="font-mono text-xs text-slate-500">{p.sku}</Td>
                  <Td>{p.name}</Td>
                  <Td className="text-slate-500">{categoryName(p.category_id)}</Td>
                  <Td>{formatCurrency(p.cost_price)}</Td>
                  <Td>{formatCurrency(p.sale_price)}</Td>
                  <Td>
                    <Badge tone={lowStock ? "red" : "green"}>{formatNumber(p.current_stock)}</Badge>
                  </Td>
                  <Td>
                    <div className="flex flex-wrap gap-2">
                      <Link
                        to={`/inventory?product_id=${p.id}`}
                        className="rounded-md bg-slate-100 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200"
                      >
                        Kardex
                      </Link>
                      <Button variant="secondary" onClick={() => openEdit(p)}>
                        Editar
                      </Button>
                      <Button
                        variant="danger"
                        onClick={() => {
                          if (confirm(`¿Eliminar el producto "${p.name}"?`)) {
                            deleteMutation.mutate(p.id);
                          }
                        }}
                      >
                        Eliminar
                      </Button>
                    </div>
                  </Td>
                </tr>
              );
            })
          )}
        </TableBody>
      </Table>

      {showForm && (
        <Modal title={editing ? "Editar producto" : "Nuevo producto"} onClose={() => setShowForm(false)}>
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3">
            <div className="grid grid-cols-2 gap-3">
              <Input label="SKU" error={errors.sku?.message} {...register("sku")} />
              <Input label="Unidad" error={errors.unit_of_measure?.message} {...register("unit_of_measure")} />
            </div>
            <Input label="Nombre" error={errors.name?.message} {...register("name")} />
            <Select label="Categoria" error={errors.category_id?.message} {...register("category_id")}>
              {categories?.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </Select>
            <div className="grid grid-cols-3 gap-3">
              <Input
                label="Costo"
                type="number"
                step="0.01"
                error={errors.cost_price?.message}
                {...register("cost_price")}
              />
              <Input
                label="Precio venta"
                type="number"
                step="0.01"
                error={errors.sale_price?.message}
                {...register("sale_price")}
              />
              <Input
                label="Stock minimo"
                type="number"
                step="0.01"
                error={errors.min_stock?.message}
                {...register("min_stock")}
              />
            </div>
            <Input label="Descripcion" {...register("description")} />
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
