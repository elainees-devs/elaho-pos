import { describe, it, expect } from "vitest";
import { ROUTES } from "@/config/routes/route-paths";

describe("Route Constants", () => {
  it("has all auth routes under /auth prefix", () => {
    expect(ROUTES.LOGIN).toBe("/auth/login");
    expect(ROUTES.REGISTER).toBe("/auth/register/:token");
    expect(ROUTES.REGISTER_BUSINESS).toBe("/auth/register-business");
    expect(ROUTES.FORGOT_PASSWORD).toBe("/auth/forgot-password");
    expect(ROUTES.RESET_PASSWORD).toBe("/auth/reset-password");
    expect(ROUTES.VERIFY_EMAIL).toBe("/auth/verify-email");
  });

  it("does not have any standalone auth routes without /auth prefix", () => {
    expect(ROUTES.LOGIN).not.toBe("/login");
    expect(ROUTES.REGISTER).not.toBe("/register/:token");
    expect(ROUTES.REGISTER_BUSINESS).not.toBe("/register-business");
  });

  it("uses a tokenized invitation registration route", () => {
    expect(ROUTES.REGISTER).toBe("/auth/register/:token");
  });

  it("has non-auth routes without /auth prefix", () => {
    expect(ROUTES.DASHBOARD).toBe("/");
    expect(ROUTES.PAYMENTS).toBe("/payments");
    expect(ROUTES.POS).toBe("/pos");
    expect(ROUTES.USERS).toBe("/users");
  });
});