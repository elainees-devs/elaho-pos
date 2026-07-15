import type { Role } from "./role.types";
import type { Business } from "./business.types";

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  email_verified: boolean;
  is_active: boolean;
  role: Role | null;
  business: Business | null;
  created_at: string;
  updated_at: string;
}