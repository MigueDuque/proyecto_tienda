import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/query-client";
import { AuthProvider } from "./AuthContext";
import { ProtectedRoute } from "./ProtectedRoute";
import { Layout } from "./Layout";

import { LoginPage } from "@/features/auth/pages/LoginPage";
import { DashboardPage } from "@/features/dashboard/pages/DashboardPage";
import { CategoryListPage } from "@/features/categories/pages/CategoryListPage";
import { ProductListPage } from "@/features/products/pages/ProductListPage";
import { PartnerListPage } from "@/features/partners/pages/PartnerListPage";
import { PurchaseListPage } from "@/features/purchases/pages/PurchaseListPage";
import { NewPurchasePage } from "@/features/purchases/pages/NewPurchasePage";
import { SaleListPage } from "@/features/sales/pages/SaleListPage";
import { NewSalePage } from "@/features/sales/pages/NewSalePage";
import { InventoryPage } from "@/features/inventory/pages/InventoryPage";
import { ChartOfAccountsPage } from "@/features/accounting/pages/ChartOfAccountsPage";
import { JournalEntriesPage } from "@/features/accounting/pages/JournalEntriesPage";
import { NewManualEntryPage } from "@/features/accounting/pages/NewManualEntryPage";

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route path="/" element={<DashboardPage />} />
              <Route path="/products" element={<ProductListPage />} />
              <Route path="/categories" element={<CategoryListPage />} />
              <Route path="/partners" element={<PartnerListPage />} />
              <Route path="/purchases" element={<PurchaseListPage />} />
              <Route path="/purchases/new" element={<NewPurchasePage />} />
              <Route path="/sales" element={<SaleListPage />} />
              <Route path="/sales/new" element={<NewSalePage />} />
              <Route path="/inventory" element={<InventoryPage />} />
              <Route path="/accounting/accounts" element={<ChartOfAccountsPage />} />
              <Route path="/accounting/journal" element={<JournalEntriesPage />} />
              <Route path="/accounting/journal/new" element={<NewManualEntryPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
