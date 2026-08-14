import type { ReactNode } from "react";

interface KpiCardProps {
  label: string;
  value: string;
  hint?: string;
  icon?: ReactNode;
}

export function KpiCard({ label, value, hint, icon }: KpiCardProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-500">{label}</span>
        {icon && <span className="text-brand-700">{icon}</span>}
      </div>
      <div className="mt-1 text-2xl font-semibold text-slate-900">{value}</div>
      {hint && <div className="mt-0.5 text-xs text-slate-400">{hint}</div>}
    </div>
  );
}
