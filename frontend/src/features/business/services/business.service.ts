import httpClient from "@/services/http/client";
import type { RegisterBusinessDTO } from "@/types/dto/business.dto";
import type { AuthTokens } from "@/types/dto/auth.dto";

export const businessService = {
  register: (data: RegisterBusinessDTO) =>
    httpClient
      .post<AuthTokens>("/businesses/register/", data)
      .then((res) => res.data),
};
