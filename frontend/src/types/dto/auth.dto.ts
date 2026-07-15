export interface CreateUserDTO{
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  password: string;
  role?: number
}
export interface VerifyEmailDTO{
   token: string;
   email: string;

}
export interface PasswordResetRequestDTO {
  email: string;
}

export interface PasswordResetConfirmDTO {
  token: string;
  email: string;
  password: string;
}

export interface PasswordChangeDTO {
  current_password: string;
  new_password: string;
}