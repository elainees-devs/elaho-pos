export type PaymentStatus = "pending" | "paid" | "cancelled" | "refunded";
export type PaymentMethod = "mpesa" | "bank_transfer" | "cash" | "card" | "airtel_money" | "other";
export type BillingCycle = "monthly" | "annual";
export type AuditAction = "created" | "verified" | "invitation_sent" | "invitation_resent" | "cancelled" | "refunded" | "updated";

export interface SubscriptionPlan {
  id: number;
  name: string;
  slug: string;
  description: string;
  monthly_price: string;
  annual_price: string;
  max_users: number;
  max_branches: number;
  max_products: number;
  is_active: boolean;
}

export interface Payment {
  id: number;
  uuid: string;
  owner_name: string;
  owner_email: string;
  owner_phone: string;
  business_name: string;
  subscription_plan: number;
  subscription_plan_name: string;
  billing_cycle: BillingCycle;
  amount: string;
  currency: string;
  payment_method: PaymentMethod;
  reference_number: string;
  payment_date: string;
  status: PaymentStatus;
  verified_by: number | null;
  verified_by_name: string | null;
  verified_at: string | null;
  registration_status: "registered" | "pending_registration" | "no_invitation";
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface PaymentAuditLog {
  id: number;
  payment: number;
  action: AuditAction;
  performed_by: number | null;
  performed_by_name: string | null;
  description: string;
  timestamp: string;
}

export interface RegistrationInvitation {
  id: number;
  payment: number;
  email: string;
  owner_name: string;
  business_name: string;
  is_used: boolean;
  expires_at: string;
  created_by: number | null;
  created_at: string;
}

export interface DashboardMetrics {
  total_payments: number;
  pending_payments: number;
  verified_payments: number;
  active_subscriptions: number;
  monthly_revenue: string;
  expired_subscriptions: number;
}

export interface ValidateRegistrationTokenResponse {
  email: string;
  owner_name: string;
  business_name: string;
  subscription_plan: string;
  billing_cycle: string;
}

export interface RegisterFromPaymentDTO {
  token: string;
  first_name: string;
  last_name: string;
  phone?: string;
  password: string;
}

export interface CreatePaymentDTO {
  owner_name: string;
  owner_email: string;
  owner_phone: string;
  business_name: string;
  subscription_plan: number;
  billing_cycle: BillingCycle;
  amount: string;
  currency: string;
  payment_method: PaymentMethod;
  reference_number: string;
  payment_date: string;
  notes?: string;
}

export type UpdatePaymentDTO = Partial<CreatePaymentDTO>;

export interface Subscription {
  id: number;
  business: number;
  plan: number;
  billing_cycle: BillingCycle;
  amount: string;
  start_date: string;
  end_date: string;
  status: string;
  is_active: boolean;
  auto_renew: boolean;
  created_at: string;
}
