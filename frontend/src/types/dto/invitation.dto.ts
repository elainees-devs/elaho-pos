export type InvitationType = "BUSINESS_OWNER" | "STAFF";

export interface ValidateInvitationResponse {
  valid: boolean;
  invitation_type: InvitationType;
  email: string;
  first_name: string;
  last_name: string;
  business_name?: string;
  role?: string;
  expires_at: string;
}

export interface RegisterUserDTO {
  token: string;
  first_name: string;
  last_name: string;
  password: string;
  confirm_password: string;
}
