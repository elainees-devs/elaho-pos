import httpClient from "@services/http/client";
import { PaginatedResponse } from "@/types/api/api.types";
import { User } from "@/types/models/user.types";
import { AuthTokens, CreateUserDTO, InviteUserDTO } from "@/types/dto/auth.dto";

interface RegistrationResponse {
  user: User;
  tokens: AuthTokens;
}

export const userService = {
  list: (params?: { page?: number; search?: string }) =>
    httpClient.get<PaginatedResponse<User>>("/users/", { params }),

  getById: (id: number) => httpClient.get<User>(`/users/${id}/`),

  create: (data: CreateUserDTO) =>
    httpClient.post<RegistrationResponse>("/users/", data).then((res) => res.data),

  update: (id: number, data: Partial<CreateUserDTO>) =>
    httpClient.patch<User>(`/users/${id}/`, data),

  delete: (id: number) => httpClient.delete(`/users/${id}/`),

  invite: (data: InviteUserDTO) =>
    httpClient
      .post<{ detail: string }>("/users/invite/", data)
      .then((res) => res.data),
};
