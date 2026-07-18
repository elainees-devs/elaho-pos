import { Navigate, type RouteObject } from "react-router-dom";

import { ROUTES } from "@/config/routes/route-paths";
import AuthLayout from "@/features/auth/layouts/auth-layout";
import LoginPage from "@/features/auth/pages/login-page";
import RegisterBusinessPage from "@/features/auth/pages/register-business-page";
import RegisterUserPage from "@/features/auth/pages/register-user-page";

const AUTH_BASE_PATH = "/auth";

const childPath = (path: string) =>
  path.replace(/^\/auth\//, "").replace(/^\//, "");

export const authRoutes: RouteObject[] = [
  {
    path: AUTH_BASE_PATH,
    element: <AuthLayout />,
    children: [
      {
        index: true,
        element: <Navigate to={ROUTES.LOGIN} replace />,
      },
      {
        path: childPath(ROUTES.LOGIN),
        element: <LoginPage />,
      },
      {
        path: childPath(ROUTES.REGISTER),
        element: <RegisterUserPage />,
      },
      {
        path: childPath(ROUTES.REGISTER_BUSINESS),
        element: <RegisterBusinessPage />,
      },
      {
        path: "*",
        element: <Navigate to={ROUTES.LOGIN} replace />,
      },
    ],
  },
];