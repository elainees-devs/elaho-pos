import { createBrowserRouter } from "react-router-dom"
import AuthGuard from "./guards/auth-guard"

const LoginPage = () => import("@features/auth/pages/login-page")
const DashboardPage = () => import("@features/dashboard/pages/dashboard-page")

import { lazy, Suspense } from "react"

function lazyRoute(factory: () => Promise<{ default: React.ComponentType }>) {
  const Component = lazy(factory)
  return (
    <Suspense fallback={<div className="p-4">Loading...</div>}>
      <Component />
    </Suspense>
  )
}

export const router = createBrowserRouter([
  {
    path: "/login",
    lazy: async () => {
      const { default: Component } = await import("@features/auth/pages/login-page")
      return { Component }
    },
  },
  {
    element: <AuthGuard />,
    children: [
      {
        path: "/",
        lazy: async () => {
          const { default: Component } = await import("@features/dashboard/pages/dashboard-page")
          return { Component }
        },
      },
    ],
  },
])
