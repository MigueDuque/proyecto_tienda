const currencyFormatter = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

const numberFormatter = new Intl.NumberFormat("es-CO", { maximumFractionDigits: 2 });

export function formatCurrency(value: string | number): string {
  return currencyFormatter.format(Number(value));
}

export function formatNumber(value: string | number): string {
  return numberFormatter.format(Number(value));
}

export function formatDate(value: string | null): string {
  if (!value) return "-";
  return new Date(value).toLocaleString("es-CO", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}
