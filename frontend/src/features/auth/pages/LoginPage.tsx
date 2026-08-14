import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/app/AuthContext";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { extractErrorMessage } from "@/lib/api-client";

const schema = z.object({
  email: z.string().email("Correo invalido"),
  password: z.string().min(1, "La contrasena es requerida"),
});
type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const { user, login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  if (user) return <Navigate to="/" replace />;

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await login(values.email, values.password);
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-md bg-brand-700 text-base font-bold text-white">
            G
          </span>
          <div>
            <h1 className="text-lg font-semibold text-slate-800">Granero</h1>
            <p className="text-xs text-slate-500">Administracion de tienda</p>
          </div>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3">
          <Input
            id="email"
            label="Correo"
            type="email"
            placeholder="admin@granero.com"
            error={errors.email?.message}
            {...register("email")}
          />
          <Input
            id="password"
            label="Contrasena"
            type="password"
            placeholder="********"
            error={errors.password?.message}
            {...register("password")}
          />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" disabled={isSubmitting} className="mt-2 w-full">
            {isSubmitting ? "Ingresando..." : "Ingresar"}
          </Button>
        </form>
      </div>
    </div>
  );
}
