import httpClient from "@/services/http/client";
import type { RegisterBusinessDTO } from "@/types/dto/business.dto";
import {
  PasswordChangeDTO,
  PasswordResetConfirmDTO,
  PasswordResetRequestDTO,
  VerifyEmailDTO,
} from "@/types/dto/auth.dto";

export const authService = {
  refresh: (refreshToken: string) =>
    httpClient.post<{ access: string }>("/auth/refresh/", {
      refresh: refreshToken,
    }),

  sendVerification: () => {
    httpClient.post("/auth/send-verification/");
  },

  verifyEmail: (data: VerifyEmailDTO) => {
    httpClient.post("/auth/verify-email/", data);
  },

  requestPasswordReset: (data: PasswordResetRequestDTO) => {
    httpClient.post("/auth/password-reset", data);
  },

  confirmPasswordReset: (data: PasswordResetConfirmDTO) => {
    httpClient.post("/auth/password-reset/confirm/", data);
  },

  changePassword: (data: PasswordChangeDTO) => {
    httpClient.post("/auth/password-change/", data);
  },

  registerBusiness: (data: RegisterBusinessDTO) =>
    httpClient.post<{ access: string; refresh: string }>(
      "/auth/register-business/",
      data
    ),
};
