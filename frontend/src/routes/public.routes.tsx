import { Route } from "react-router-dom";

import { ROUTES } from "@/config/routes/route-paths";
import RegisterBusinessPage from "@/features/auth/pages/register-business-page";

export default function PublicRoutes() {
  return (
    <Route path={ROUTES.REGISTER_BUSINESS} element={<RegisterBusinessPage />} />
  );
}
