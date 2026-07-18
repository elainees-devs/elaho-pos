import { Route } from "react-router-dom";

import { ROUTES } from "@/config/routes/route-paths";
import RegisterUserPage from "@/features/auth/pages/register-user-page";

export default function PublicRoutes() {
  return <Route path={ROUTES.REGISTER} element={<RegisterUserPage />} />;
}