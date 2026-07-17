import httpClient from "@/services/http/client";
import type { AuthTokens, ValidateInviteResponse, RegisterFromInviteDTO } from "@/types/dto/auth.dto";

export const inviteService = {
  validate: (token: string) =>
    httpClient
      .get<ValidateInviteResponse>("/auth/invite/validate/", { params: { token } })
      .then((res) => res.data),

  register: (data: RegisterFromInviteDTO) =>
    httpClient
      .post<AuthTokens>("/auth/register/", data)
      .then((res) => res.data),
};
