import { useEffect, useMemo, useState } from "react";
import { useNavigate, Link, useParams, Navigate } from "react-router-dom";
import { Store, Eye, EyeOff, AlertCircle } from "lucide-react";

import { ROUTES } from "@/config/routes/route-paths";
import { useAuth } from "@/contexts/auth/auth.context";
import { useRegisterUser, useValidateInvitation } from "@/features/auth/hooks/use-invitation-registration";
import {
  invitationRegistrationSchema,
  type InvitationRegistrationFormValues,
} from "@/features/auth/validations/auth.validation";
import { Button } from "@/components/ui/actions/Button";
import { Spinner } from "@/components/ui/feedback/Spinner";
import { EmptyState } from "@/components/ui/feedback/EmptyState";
import { Badge } from "@/components/ui/data-display/Badge";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type PageStatus = "ready" | "success";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function RegisterUserPage() {
  const navigate = useNavigate();
  const { token = "" } = useParams<{ token: string }>();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const [status, setStatus] = useState<PageStatus>("ready");
  const [error, setError] = useState<string>("");
  const [fieldErrors, setFieldErrors] = useState<
    Partial<Record<keyof InvitationRegistrationFormValues, string>>
  >({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const validateInvitationQuery = useValidateInvitation(token);
  const registerMutation = useRegisterUser();

  const [form, setForm] = useState<InvitationRegistrationFormValues>({
    first_name: "",
    last_name: "",
    password: "",
    confirm_password: "",
  });

  const invitation = validateInvitationQuery.data;

  useEffect(() => {
    if (!invitation) {
      return;
    }

    setForm((prev) => ({
      ...prev,
      first_name: prev.first_name || invitation.first_name || "",
      last_name: prev.last_name || invitation.last_name || "",
    }));
  }, [invitation]);

  const invitationErrorMessage = useMemo(() => {
    const detail =
      (
        validateInvitationQuery.error as {
          response?: { data?: { detail?: string; message?: string } };
          message?: string;
        }
      )?.response?.data?.detail ||
      (
        validateInvitationQuery.error as {
          response?: { data?: { detail?: string; message?: string } };
          message?: string;
        }
      )?.response?.data?.message ||
      (
        validateInvitationQuery.error as {
          message?: string;
        }
      )?.message ||
      "Invalid invitation";

    const normalized = detail.toLowerCase();
    if (normalized.includes("expired")) {
      return "Invitation expired";
    }
    if (normalized.includes("already") || normalized.includes("used")) {
      return "Invitation already used";
    }
    if (normalized.includes("network")) {
      return "Network error while validating invitation";
    }
    if (normalized.includes("not found")) {
      return "Invitation not found";
    }
    return "Invalid invitation";
  }, [validateInvitationQuery.error]);

  if (!authLoading && isAuthenticated && !token) {
    return (
      <Navigate
        to={ROUTES.DASHBOARD}
        replace
      />
    );
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setFieldErrors((prev) => ({ ...prev, [name]: undefined }));
  }

  function validate(): boolean {
    const result = invitationRegistrationSchema.safeParse(form);
    if (result.success) {
      setFieldErrors({});
      return true;
    }

    const errors: Partial<Record<keyof InvitationRegistrationFormValues, string>> = {};
    for (const issue of result.error.issues) {
      const key = issue.path[0] as keyof InvitationRegistrationFormValues;
      if (!errors[key]) {
        errors[key] = issue.message;
      }
    }

    setFieldErrors(errors);
    return false;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (!validate()) return;

    const payload = {
      token,
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      password: form.password,
      confirm_password: form.confirm_password,
    };

    try {
      await registerMutation.mutateAsync(payload);
      setStatus("success");
      setError("Account created successfully. Please log in.");
      setTimeout(() => navigate(ROUTES.LOGIN, { replace: true }), 2000);
    } catch (err: unknown) {
      const detail = (
        err as {
          response?: { data?: { detail?: string; message?: string; errors?: Record<string, string[]> } };
          message?: string;
        }
      )?.response?.data;

      const backendFieldErrors = detail?.errors;
      if (backendFieldErrors) {
        const mappedErrors: Partial<Record<keyof InvitationRegistrationFormValues, string>> = {};
        if (backendFieldErrors.first_name?.[0]) mappedErrors.first_name = backendFieldErrors.first_name[0];
        if (backendFieldErrors.last_name?.[0]) mappedErrors.last_name = backendFieldErrors.last_name[0];
        if (backendFieldErrors.password?.[0]) mappedErrors.password = backendFieldErrors.password[0];
        if (backendFieldErrors.confirm_password?.[0]) {
          mappedErrors.confirm_password = backendFieldErrors.confirm_password[0];
        }
        setFieldErrors(mappedErrors);
      }

      const rawDetail = detail?.detail || detail?.message || (err as { message?: string })?.message;
      const normalized = (rawDetail ?? "").toLowerCase();

      if (normalized.includes("already") || normalized.includes("exists") || normalized.includes("duplicate")) {
        setError("A user with this invitation details already exists.");
      } else if (normalized.includes("weak") || normalized.includes("password")) {
        setError("Weak password. Please follow the password requirements.");
      } else if (normalized.includes("expired")) {
        setError("This invitation has expired. Request a new invitation.");
      } else if (normalized.includes("used")) {
        setError("This invitation has already been used.");
      } else if (normalized.includes("network")) {
        setError("Network error. Check your connection and try again.");
      } else if (normalized.includes("server")) {
        setError("Server error. Please try again in a moment.");
      } else {
        setError(rawDetail ?? "Unexpected error occurred. Please try again.");
      }
    }
  }

  // ---------------------------------------------------------------------------
  // Render states
  // ---------------------------------------------------------------------------

  if (validateInvitationQuery.isLoading || authLoading) {
    return (
      <div className="flex min-h-[300px] items-center justify-center">
        <div className="flex items-center gap-3 text-sm text-text-secondary">
          <Spinner size="sm" />
          <span>Validating invitation...</span>
        </div>
      </div>
    );
  }

  if (!token || validateInvitationQuery.isError || !invitation || invitation.valid === false) {
    return (
      <div className="space-y-4">
        <EmptyState
          icon={<AlertCircle />}
          title={invitationErrorMessage}
          description="Please request a new invitation link or return to the login page."
          action={
            <Link
              to={ROUTES.LOGIN}
              className="inline-flex items-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
            >
              Back to Login
            </Link>
          }
        />

        {validateInvitationQuery.isError ? (
          <div className="flex justify-center">
            <Button
              variant="secondary"
              type="button"
              onClick={() => validateInvitationQuery.refetch()}
            >
              Retry Validation
            </Button>
          </div>
        ) : null}
      </div>
    );
  }

  if (status === "success") {
    return (
      <div className="flex flex-col items-center gap-4 py-10 text-center">
        <div
          role="status"
          className="rounded-lg border border-success/20 bg-success/10 px-4 py-3 text-sm text-success"
        >
          Account created successfully. Please log in.
        </div>
        <p className="text-lg font-semibold text-success">Account created successfully.</p>
        <p className="text-sm text-text-secondary">Please log in. Redirecting...</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8 flex items-center gap-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-600 text-white">
          <Store size={18} />
        </div>
        <span className="text-lg font-semibold text-slate-800">Elaho POS</span>
      </div>

      <h1 className="mb-1 text-2xl font-bold text-slate-900">Create your account</h1>
      {invitation.invitation_type === "BUSINESS_OWNER" ? (
        <p className="mb-6 text-sm text-slate-500">
          Welcome! Complete your business owner account to start using the system.
        </p>
      ) : (
        <div className="mb-6 space-y-2 text-sm text-slate-500">
          <p>
            You&apos;ve been invited to join <span className="font-medium text-slate-700">{invitation.business_name}</span>
          </p>
          {invitation.role ? <Badge variant="info">{invitation.role}</Badge> : null}
        </div>
      )}

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-4">
        {/* Email – read-only */}
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-slate-700">Email</label>
          <input
            type="email"
            value={invitation.email}
            readOnly
            className="rounded-lg border border-slate-200 bg-slate-100 px-4 py-2.5 text-sm text-slate-500 cursor-not-allowed"
          />
        </div>

        {invitation.business_name ? (
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">Business Name</label>
            <input
              type="text"
              value={invitation.business_name}
              readOnly
              className="rounded-lg border border-slate-200 bg-slate-100 px-4 py-2.5 text-sm text-slate-500 cursor-not-allowed"
            />
          </div>
        ) : null}

        {invitation.invitation_type === "STAFF" ? (
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">Role</label>
            <input
              type="text"
              value={invitation.role ?? "N/A"}
              readOnly
              className="rounded-lg border border-slate-200 bg-slate-100 px-4 py-2.5 text-sm text-slate-500 cursor-not-allowed"
            />
          </div>
        ) : null}

        {/* Name row */}
        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col gap-1">
            <label htmlFor="first_name" className="text-sm font-medium text-slate-700">
              First name
            </label>
            <input
              id="first_name"
              name="first_name"
              type="text"
              autoComplete="given-name"
              value={form.first_name}
              onChange={handleChange}
              placeholder="Jane"
              className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            {fieldErrors.first_name && (
              <p className="text-xs text-red-600">{fieldErrors.first_name}</p>
            )}
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="last_name" className="text-sm font-medium text-slate-700">
              Last name
            </label>
            <input
              id="last_name"
              name="last_name"
              type="text"
              autoComplete="family-name"
              value={form.last_name}
              onChange={handleChange}
              placeholder="Doe"
              className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            {fieldErrors.last_name && (
              <p className="text-xs text-red-600">{fieldErrors.last_name}</p>
            )}
          </div>
        </div>

        {/* Password */}
        <div className="flex flex-col gap-1">
          <label htmlFor="password" className="text-sm font-medium text-slate-700">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              value={form.password}
              onChange={handleChange}
              placeholder="Create a strong password"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 pr-10 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {fieldErrors.password && (
            <p className="text-xs text-red-600">{fieldErrors.password}</p>
          )}
        </div>

        {/* Confirm password */}
        <div className="flex flex-col gap-1">
          <label htmlFor="confirm_password" className="text-sm font-medium text-slate-700">
            Confirm password
          </label>
          <div className="relative">
            <input
              id="confirm_password"
              name="confirm_password"
              type={showConfirm ? "text" : "password"}
              autoComplete="new-password"
              value={form.confirm_password}
              onChange={handleChange}
              placeholder="Repeat your password"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 pr-10 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <button
              type="button"
              onClick={() => setShowConfirm((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              aria-label={showConfirm ? "Hide password" : "Show password"}
            >
              {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {fieldErrors.confirm_password && (
            <p className="text-xs text-red-600">{fieldErrors.confirm_password}</p>
          )}
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={registerMutation.isPending}
          className="mt-2 rounded-lg bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
        >
          {registerMutation.isPending ? "Creating account..." : "Create Account"}
        </button>

        <Button
          variant="ghost"
          type="button"
          onClick={() => navigate(ROUTES.LOGIN)}
        >
          Cancel
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500">
        Already have an account?{" "}
        <Link to={ROUTES.LOGIN} className="font-medium text-blue-600 hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
