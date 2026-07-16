import { create } from "zustand";
import { AxiosError } from "axios";
import { AuthTokens, CreateUserDTO } from "@/types/dto/auth.dto";
import { User } from "@/types/models/user.types";
import { userService } from "@/features/users/services/user.service";

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  isRegistering: boolean;
  registerError: string | null;
  registerSuccess: boolean;

  setTokens: (tokens: AuthTokens) => void;
  setUser: (user: User) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;

  register: (payload: CreateUserDTO) => Promise<void>;
  resetRegistrationState: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: false,

  isRegistering: false,
  registerError: null,
  registerSuccess: false,

  setTokens: (tokens) => set({ tokens, isAuthenticated: !!tokens.access }),
  setUser: (user) => set({ user }),
  logout: () => set({ user: null, tokens: null, isAuthenticated: false }),
  refreshUser: async () => {
    // implement when /me endpoint is ready
  },

  register: async (payload) => {
    set({ isRegistering: true, registerError: null, registerSuccess: false });
    try {
      const response = await userService.create(payload);

      set({
        user: response.user,
        tokens: response.tokens,
        isAuthenticated: true,
        registerSuccess: true,
      });
    } catch (error) {
      const err = error as AxiosError<{
        detail?: string;
        message?: string;
      }>;

      const message =
        err.response?.data?.detail ??
        err.response?.data?.message ??
        "Registration failed";

      set({ registerError: message });
      throw error;
    } finally {
      set({ isRegistering: false });
    }
  },

  resetRegistrationState: () =>
    set({ registerError: null, registerSuccess: false }),
}))

