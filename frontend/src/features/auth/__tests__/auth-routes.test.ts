import { describe, it, expect } from "vitest";
import { authRoutes } from "../routes/auth.routes";
import { ROUTES } from "@/config/routes/route-paths";

describe("Auth Routes", () => {
  it("has a single /auth parent route", () => {
    expect(authRoutes).toHaveLength(1);
    expect(authRoutes[0].path).toBe("/auth");
  });

  it("has no duplicate routes", () => {
    const children = authRoutes[0].children ?? [];
    const paths = children
      .map((c) => ("index" in c && c.index ? "__index__" : c.path))
      .filter(Boolean);

    expect(new Set(paths).size).toBe(paths.length);
  });

  it("includes login, tokenized register, and register-business routes", () => {
    const children = authRoutes[0].children ?? [];
    const paths = children.map((c) => c.path).filter(Boolean);

    expect(paths).toContain("login");
    expect(paths).toContain("register/:token");
    expect(paths).toContain("register-business");
  });

  it("has a wildcard fallback route", () => {
    const children = authRoutes[0].children ?? [];
    const wildcard = children.find((c) => c.path === "*");

    expect(wildcard).toBeDefined();
  });

  it("has an index redirect route", () => {
    const children = authRoutes[0].children ?? [];
    const indexRoute = children.find((c) => "index" in c && c.index);

    expect(indexRoute).toBeDefined();
  });

  it("uses auth-prefixed route constants", () => {
    expect(ROUTES.LOGIN).toBe("/auth/login");
    expect(ROUTES.REGISTER).toBe("/auth/register/:token");
    expect(ROUTES.REGISTER_BUSINESS).toBe("/auth/register-business");
    expect(ROUTES.FORGOT_PASSWORD).toBe("/auth/forgot-password");
    expect(ROUTES.RESET_PASSWORD).toBe("/auth/reset-password");
    expect(ROUTES.VERIFY_EMAIL).toBe("/auth/verify-email");
  });
});