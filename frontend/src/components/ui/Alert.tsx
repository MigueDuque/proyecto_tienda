import type { ReactNode } from "react";

type Tone = "error" | "warning" | "info";

const toneClasses: Record<Tone, string> = {
  error: "border-red-300 bg-red-50 text-red-800",
  warning: "border-amber-300 bg-amber-50 text-amber-900",
  info: "border-blue-300 bg-blue-50 text-blue-800",
};

const toneIcons: Record<Tone, string> = {
  error: "⚠",
  warning: "⚠",
  info: "ℹ",
};

interface AlertProps {
  tone?: Tone;
  title?: string;
  children: ReactNode;
}

export function Alert({ tone = "error", title, children }: AlertProps) {
  return (
    <div
      role="alert"
      className={`flex items-start gap-2.5 rounded-md border px-3.5 py-3 text-sm ${toneClasses[tone]}`}
    >
      <span aria-hidden="true" className="mt-px text-base leading-none">
        {toneIcons[tone]}
      </span>
      <div>
        {title && <p className="font-semibold">{title}</p>}
        <div className={title ? "mt-0.5" : undefined}>{children}</div>
      </div>
    </div>
  );
}
