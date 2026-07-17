import { Route } from "react-router-dom";

import { ROUTES } from "@/config/routes/route-paths";
import DashboardPage from "@/features/dashboard/pages/DashboardPage";
import PaymentListPage from "@/features/payments/pages/PaymentListPage";

export default function ProtectedRoutes() {
  return (
    <>
      <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />
      <Route path={ROUTES.PAYMENTS} element={<PaymentListPage />} />
    </>
  );
}
