export type PartnerType = "CLIENTE" | "PROVEEDOR" | "AMBOS";
export type PaymentMethod = "CONTADO" | "CREDITO";
export type AccountType = "ACTIVO" | "PASIVO" | "PATRIMONIO" | "INGRESO" | "GASTO" | "COSTO";
export type MovementType = "ENTRADA_COMPRA" | "SALIDA_VENTA" | "AJUSTE_ENTRADA" | "AJUSTE_SALIDA";
export type JournalEntryReferenceType = "SALE" | "PURCHASE" | "MANUAL";

export interface Category {
  id: number;
  name: string;
  description: string | null;
}

export interface Product {
  id: number;
  sku: string;
  name: string;
  category_id: number;
  unit_of_measure: string;
  cost_price: string;
  sale_price: string;
  current_stock: string;
  min_stock: string;
  description: string | null;
  is_active: boolean;
}

export interface Partner {
  id: number;
  type: PartnerType;
  name: string;
  document_id: string | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  is_active: boolean;
}

export interface PurchaseItem {
  id: number;
  product_id: number;
  quantity: string;
  unit_cost: string;
  subtotal: string;
}

export interface Purchase {
  id: number;
  partner_id: number;
  payment_method: PaymentMethod;
  subtotal: string;
  total: string;
  date: string | null;
  items: PurchaseItem[];
}

export interface SaleItem {
  id: number;
  product_id: number;
  quantity: string;
  unit_price: string;
  unit_cost: string;
  subtotal: string;
}

export interface Sale {
  id: number;
  partner_id: number | null;
  payment_method: PaymentMethod;
  subtotal: string;
  total: string;
  date: string | null;
  items: SaleItem[];
}

export interface InventoryMovement {
  id: number;
  product_id: number;
  movement_type: MovementType;
  quantity: string;
  unit_cost: string;
  balance_after: string;
  reference_type: string;
  reference_id: number;
  notes: string | null;
  created_at: string | null;
}

export interface Account {
  id: number;
  code: string;
  name: string;
  type: AccountType;
  parent_id: number | null;
  is_active: boolean;
}

export interface JournalEntryLine {
  id: number;
  account_id: number;
  debit: string;
  credit: string;
  description: string | null;
}

export interface JournalEntry {
  id: number;
  description: string;
  reference_type: JournalEntryReferenceType;
  reference_id: number | null;
  date: string | null;
  lines: JournalEntryLine[];
}

export interface DashboardSummary {
  sales_today_total: string;
  sales_month_total: string;
  cash_balance: string;
  low_stock_products: Product[];
  recent_sales: Sale[];
  recent_purchases: Purchase[];
}

export interface ApiError {
  detail: string | { msg: string }[];
}
