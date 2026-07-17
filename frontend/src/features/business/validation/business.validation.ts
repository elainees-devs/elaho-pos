import { z } from "zod";

export const registerBusinessSchema = z
  .object({
    business_name: z
      .string()
      .min(2, "Business name must be at least 2 characters")
      .max(100, "Business name must be at most 100 characters"),
    business_phone: z.string().optional(),
    business_email: z
      .string()
      .email("Invalid email address")
      .optional()
      .or(z.literal("")),
    business_address: z.string().optional(),
    kra_pin: z
      .string()
      .min(1, "KRA PIN is required")
      .max(20, "KRA PIN must be at most 20 characters"),
    first_name: z
      .string()
      .min(2, "First name must be at least 2 characters")
      .max(50, "First name must be at most 50 characters"),
    last_name: z
      .string()
      .min(2, "Last name must be at least 2 characters")
      .max(50, "Last name must be at most 50 characters"),
    email: z.string().email("Invalid email address"),
    phone: z.string().optional(),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Must contain at least one uppercase letter")
      .regex(/[0-9]/, "Must contain at least one number"),
    confirm_password: z.string(),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

export type RegisterBusinessFormValues = z.infer<typeof registerBusinessSchema>;
