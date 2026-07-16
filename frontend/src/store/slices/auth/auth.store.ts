import { AuthTokens } from "@/types/dto/auth.dto";
import { User } from "@/types/models/user.types";

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  setTokens: (tokens: AuthTokens) => void;
  logout: () => void;
  setUser: (user: User) => void;
  refreshUser: Promise<void>;
}
