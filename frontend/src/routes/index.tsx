import { Routes, Route } from "react-router-dom";

import PublicRoutes from "./public.routes";
import ProtectedRoutes from "./protected.routes";
import { authRoutes } from "@/features/auth/routes/auth.routes";
import NotFoundPage from "@/pages/errors/NotFoundPage";

export default function AppRoutes() {
  return (
    <Routes>
      {authRoutes.map((route) => (
        <Route key={route.path} path={route.path} element={route.element}>
          {route.children?.map((child) => (
            <Route
              key={child.path}
              path={child.path}
              element={child.element}
            />
          ))}
        </Route>
      ))}
      <PublicRoutes />
      <ProtectedRoutes />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
