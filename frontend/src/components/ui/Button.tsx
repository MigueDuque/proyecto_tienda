import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "danger" | "ghost";

// `disabled:hover:*` keeps a blocked button from darkening on hover, which
// otherwise makes it look clickable when it is not.
const variantClasses: Record<Variant, string> = {
  primary:
    "bg-brand-700 text-white hover:bg-brand-800 disabled:bg-brand-300 disabled:hover:bg-brand-300",
  secondary:
    "bg-slate-100 text-slate-700 hover:bg-slate-200 disabled:text-slate-400 disabled:hover:bg-slate-100",
  danger: "bg-red-600 text-white hover:bg-red-700 disabled:bg-red-300 disabled:hover:bg-red-300",
  ghost: "bg-transparent text-slate-600 hover:bg-slate-100 disabled:hover:bg-transparent",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

export function Button({ variant = "primary", className = "", ...props }: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-1.5 rounded-md px-3.5 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed ${variantClasses[variant]} ${className}`}
      {...props}
    />
  );
}
