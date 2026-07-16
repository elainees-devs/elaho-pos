import {
	createElement,
	createContext,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useState,
	type ReactNode,
} from "react";

import type { AuthTokens } from "@/types/dto/auth.dto";
import type { User } from "@/types/models/user.types";

const USER_STORAGE_KEY = "auth_user";
const TOKENS_STORAGE_KEY = "tokens";
const ACCESS_TOKEN_STORAGE_KEY = "access_token";

function readTokensFromStorage(): AuthTokens | null {
	if (typeof window === "undefined") {
		return null;
	}

	const rawTokens = window.localStorage.getItem(TOKENS_STORAGE_KEY);
	if (rawTokens) {
		try {
			const parsed = JSON.parse(rawTokens) as Partial<AuthTokens>;
			if (parsed.access && parsed.refresh) {
				return { access: parsed.access, refresh: parsed.refresh };
			}
		} catch {
			// Ignore malformed localStorage JSON.
		}
	}

	const access = window.localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
	if (access) {
		return { access, refresh: "" };
	}

	return null;
}

function readUserFromStorage(): User | null {
	if (typeof window === "undefined") {
		return null;
	}

	const rawUser = window.localStorage.getItem(USER_STORAGE_KEY);
	if (!rawUser) {
		return null;
	}

	try {
		return JSON.parse(rawUser) as User;
	} catch {
		return null;
	}
}

export interface AuthContextValue {
	currentUser: User | null;
	tokens: AuthTokens | null;
	isAuthenticated: boolean;
	isLoading: boolean;
	setAuth: (params: { user: User | null; tokens: AuthTokens | null }) => void;
	setCurrentUser: (user: User | null) => void;
	clearAuth: () => void;
	hasPermission: (permission: string) => boolean;
	hasAnyPermission: (permissions: string[]) => boolean;
	hasAllPermissions: (permissions: string[]) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export interface AuthProviderProps {
	children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
	const [isLoading, setIsLoading] = useState(true);
	const [currentUser, setCurrentUserState] = useState<User | null>(null);
	const [tokens, setTokensState] = useState<AuthTokens | null>(null);

	useEffect(() => {
		setCurrentUserState(readUserFromStorage());
		setTokensState(readTokensFromStorage());
		setIsLoading(false);
	}, []);

	const setCurrentUser = useCallback((user: User | null) => {
		setCurrentUserState(user);

		if (typeof window === "undefined") {
			return;
		}

		if (user) {
			window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
			return;
		}

		window.localStorage.removeItem(USER_STORAGE_KEY);
	}, []);

	const setAuth = useCallback(
		({ user, tokens: nextTokens }: { user: User | null; tokens: AuthTokens | null }) => {
			setCurrentUser(user);
			setTokensState(nextTokens);

			if (typeof window === "undefined") {
				return;
			}

			if (nextTokens) {
				window.localStorage.setItem(TOKENS_STORAGE_KEY, JSON.stringify(nextTokens));
				window.localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, nextTokens.access);
			} else {
				window.localStorage.removeItem(TOKENS_STORAGE_KEY);
				window.localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
			}
		},
		[setCurrentUser]
	);

	const clearAuth = useCallback(() => {
		setCurrentUserState(null);
		setTokensState(null);

		if (typeof window === "undefined") {
			return;
		}

		window.localStorage.removeItem(USER_STORAGE_KEY);
		window.localStorage.removeItem(TOKENS_STORAGE_KEY);
		window.localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
	}, []);

	const permissionSet = useMemo(
		() => new Set(currentUser?.role?.permissions ?? []),
		[currentUser]
	);

	const hasPermission = useCallback(
		(permission: string) => permissionSet.has(permission),
		[permissionSet]
	);

	const hasAnyPermission = useCallback(
		(permissions: string[]) => permissions.some((permission) => permissionSet.has(permission)),
		[permissionSet]
	);

	const hasAllPermissions = useCallback(
		(permissions: string[]) => permissions.every((permission) => permissionSet.has(permission)),
		[permissionSet]
	);

	const value = useMemo<AuthContextValue>(
		() => ({
			currentUser,
			tokens,
			isAuthenticated: Boolean(tokens?.access),
			isLoading,
			setAuth,
			setCurrentUser,
			clearAuth,
			hasPermission,
			hasAnyPermission,
			hasAllPermissions,
		}),
		[
			clearAuth,
			currentUser,
			hasAllPermissions,
			hasAnyPermission,
			hasPermission,
			isLoading,
			setAuth,
			setCurrentUser,
			tokens,
		]
	);

	return createElement(AuthContext.Provider, { value }, children);
}

export function useAuth(): AuthContextValue {
	const context = useContext(AuthContext);
	if (!context) {
		throw new Error("useAuth must be used within AuthProvider");
	}
	return context;
}