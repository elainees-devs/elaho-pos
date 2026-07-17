import { z } from "zod";

export const createPaymentSchema = z.object({
  owner_name: z.string().min(1, "Owner name is required"),
  owner_email: z.string().email("Invalid email address"),
  owner_phone: z.string().min(1, "Phone number is required"),
  business_name: z.string().min(1, "Business name is required"),
  subscription_plan: z.number().min(1, "Select a subscription plan"),
  billing_cycle: z.union([z.literal("monthly"), z.literal("annual")]),
  amount: z.string().min(1, "Amount is required"),
  currency: z.string().min(1, "Currency is required"),
  payment_method: z.union([
    z.literal("mpesa"),
    z.literal("bank_transfer"),
    z.literal("cash"),
    z.literal("card"),
    z.literal("airtel_money"),
    z.literal("other"),
  ]),
  reference_number: z.string().min(1, "Reference number is required"),
  payment_date: z.string().min(1, "Payment date is required"),
  notes: z.string().optional(),
});

export type CreatePaymentFormValues = z.infer<typeof createPaymentSchema>;

export const cancelPaymentSchema = z.object({
  reason: z.string().optional(),
});

export const refundPaymentSchema = z.object({
  reason: z.string().optional(),
});

export const registerFromPaymentSchema = z.object({
  first_name: z.string().min(2, "First name must be at least 2 characters"),
  last_name: z.string().min(2, "Last name must be at least 2 characters"),
  phone: z.string().optional(),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Must contain at least one uppercase letter")
    .regex(/[0-9]/, "Must contain at least one number"),
  confirm_password: z.string(),
}).refine((data) => data.password === data.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"],
});

export type RegisterFromPaymentFormValues = z.infer<typeof registerFromPaymentSchema>;
