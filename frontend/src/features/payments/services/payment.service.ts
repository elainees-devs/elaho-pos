import httpClient from "@services/http/client";
import type {
  Payment,
  DashboardMetrics,
  SubscriptionPlan,
  PaymentAuditLog,
  CreatePaymentDTO,
  UpdatePaymentDTO,
  ValidateRegistrationTokenResponse,
  RegisterFromPaymentDTO,
  Subscription,
} from "../types/payment.types";

export const paymentService = {
  list: (params?: { status?: string; search?: string; page?: number }) =>
    httpClient.get<{ results: Payment[]; count: number }>("/payments/", { params }).then((res) => res.data),

  getById: (id: number) =>
    httpClient.get<Payment>(`/payments/${id}/`).then((res) => res.data),

  create: (data: CreatePaymentDTO) =>
    httpClient.post<Payment>("/payments/", data).then((res) => res.data),

  update: (id: number, data: UpdatePaymentDTO) =>
    httpClient.patch<Payment>(`/payments/${id}/`, data).then((res) => res.data),

  remove: (id: number) =>
    httpClient.delete(`/payments/${id}/`),

  verify: (id: number) =>
    httpClient.post<{ detail: string }>(`/payments/${id}/verify/`).then((res) => res.data),

  cancel: (id: number, reason?: string) =>
    httpClient.post<{ detail: string }>(`/payments/${id}/cancel/`, { reason }).then((res) => res.data),

  refund: (id: number, reason?: string) =>
    httpClient.post<{ detail: string }>(`/payments/${id}/refund/`, { reason }).then((res) => res.data),

  resendInvitation: (id: number) =>
    httpClient.post<{ detail: string }>(`/payments/${id}/resend-invitation/`).then((res) => res.data),

  getAuditLog: (id: number) =>
    httpClient.get<PaymentAuditLog[]>(`/payments/${id}/audit-log/`).then((res) => res.data),

  getDashboard: () =>
    httpClient.get<DashboardMetrics>("/payments/dashboard/").then((res) => res.data),

  getSubscriptionPlans: () =>
    httpClient.get<SubscriptionPlan[]>("/payments/subscription-plans/").then((res) => res.data),

  getSubscriptions: (params?: { status?: string }) =>
    httpClient.get<Subscription[]>("/payments/subscriptions/", { params }).then((res) => res.data),

  getCurrentSubscription: () =>
    httpClient.get<Subscription>("/payments/subscriptions/current/").then((res) => res.data),

  validateRegistrationToken: (token: string) =>
    httpClient.get<ValidateRegistrationTokenResponse>(`/payments/registration-invitations/${token}/`).then((res) => res.data),

  registerFromPayment: (data: RegisterFromPaymentDTO) =>
    httpClient.post<{ access: string; refresh: string }>("/payments/register/", data).then((res) => res.data),
};
