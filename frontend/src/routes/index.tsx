import { Routes, Route } from "react-router-dom";

import PublicRoutes from "./public.routes";
import ProtectedRoutes from "./protected.routes";
import NotFoundPage from "@/pages/errors/NotFoundPage";

export default function AppRoutes() {
  return (
    <Routes>
      <PublicRoutes />
      <ProtectedRoutes />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
