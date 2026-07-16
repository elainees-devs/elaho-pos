import httpClient from "@services/http/client";
import { PaginatedResponse } from "@/types/api/api.types";
import { User } from "@/types/models/user.types";
import { CreateUserDTO } from "@/types/dto/auth.dto";

export const userService = {
  list: (params?: { page?: number; search?: string }) =>
    httpClient.get<PaginatedResponse<User>>("/users/", { params }),

  getById: (id: number) => httpClient.get<User>(`/users/${id}/`),

  create: (data: CreateUserDTO) => httpClient.post<User>("/users/", data),

  update: (id: number, data: Partial<CreateUserDTO>) =>
    httpClient.patch<User>(`/users/${id}/`, data),

  delete: (id: number) => httpClient.delete(`/users/${id}/`),
};
