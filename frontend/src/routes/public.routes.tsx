import { Route } from "react-router-dom";

import { ROUTES } from "@/config/routes/route-paths";
import RegisterBusinessPage from "@/pages/auth/RegisterBusinessPage";

export default function PublicRoutes() {
  return (
    <Route path={ROUTES.REGISTER} element={<RegisterBusinessPage />} />
  );
}
