// Request interceptor: inject access token from Zustand store
// Response interceptor: on 401, attempt token refresh
// If refresh fails, redirect to auth entry route