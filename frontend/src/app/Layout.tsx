import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "./AuthContext";

const navItems = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/products", label: "Productos" },
  { to: "/categories", label: "Categorias" },
  { to: "/partners", label: "Terceros" },
  { to: "/purchases", label: "Compras" },
  { to: "/sales", label: "Ventas" },
  { to: "/inventory", label: "Inventario" },
  { to: "/accounting/accounts", label: "Plan de Cuentas" },
  { to: "/accounting/journal", label: "Libro Diario" },
];

export function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="flex w-60 shrink-0 flex-col border-r border-slate-200 bg-white">
        <div className="flex items-center gap-2 border-b border-slate-100 px-5 py-4">
          <span className="flex h-8 w-8 items-center justify-center rounded-md bg-brand-700 text-sm font-bold text-white">
            G
          </span>
          <span className="text-lg font-semibold text-slate-800">Granero</span>
        </div>
        <nav className="flex-1 space-y-0.5 px-3 py-4">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `block rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-brand-50 text-brand-800"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-slate-100 px-4 py-3">
          <div className="mb-2 truncate text-xs text-slate-500">{user?.email}</div>
          <button
            onClick={logout}
            className="w-full rounded-md px-3 py-1.5 text-left text-sm font-medium text-slate-600 hover:bg-slate-100"
          >
            Cerrar sesion
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-x-hidden p-6">
        <Outlet />
      </main>
    </div>
  );
}
