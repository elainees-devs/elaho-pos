import { useEffect, useState } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { Store, Eye, EyeOff } from "lucide-react";

import { inviteService } from "@/features/auth/services/invite.service";
import type { ValidateInviteResponse, RegisterFromInviteDTO } from "@/types/dto/auth.dto";
import { ROUTES } from "@/config/routes/route-paths";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface FormState {
  first_name: string;
  last_name: string;
  phone: string;
  password: string;
  confirm_password: string;
}

type PageStatus = "loading" | "invalid" | "ready" | "submitting" | "success";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function RegisterUserPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token") ?? "";

  const [status, setStatus] = useState<PageStatus>("loading");
  const [invite, setInvite] = useState<ValidateInviteResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<keyof FormState, string>>>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const [form, setForm] = useState<FormState>({
    first_name: "",
    last_name: "",
    phone: "",
    password: "",
    confirm_password: "",
  });

  // Validate token on mount
  useEffect(() => {
    if (!token) {
      setStatus("invalid");
      return;
    }

    inviteService
      .validate(token)
      .then((data) => {
        setInvite(data);
        setStatus("ready");
      })
      .catch(() => {
        setStatus("invalid");
      });
  }, [token]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setFieldErrors((prev) => ({ ...prev, [name]: undefined }));
  }

  function validate(): boolean {
    const errors: Partial<Record<keyof FormState, string>> = {};

    if (!form.first_name.trim() || form.first_name.trim().length < 2)
      errors.first_name = "First name must be at least 2 characters.";
    if (!form.last_name.trim() || form.last_name.trim().length < 2)
      errors.last_name = "Last name must be at least 2 characters.";
    if (!form.password)
      errors.password = "Password is required.";
    if (form.password !== form.confirm_password)
      errors.confirm_password = "Passwords do not match.";

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (!validate()) return;

    setStatus("submitting");

    const payload: RegisterFromInviteDTO = {
      token,
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      phone: form.phone.trim() || undefined,
      password: form.password,
    };

    try {
      const tokens = await inviteService.register(payload);
      // Store tokens then redirect to login
      localStorage.setItem("access_token", tokens.access);
      localStorage.setItem("refresh_token", tokens.refresh);
      setStatus("success");
      setTimeout(() => navigate(ROUTES.LOGIN, { replace: true }), 2000);
    } catch (err: unknown) {
      setStatus("ready");
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? "Something went wrong. Please try again.");
    }
  }

  // ---------------------------------------------------------------------------
  // Render states
  // ---------------------------------------------------------------------------

  if (status === "loading") {
    return (
      <div className="flex min-h-[300px] items-center justify-center">
        <p className="text-slate-500 text-sm">Validating invitation…</p>
      </div>
    );
  }

  if (status === "invalid") {
    return (
      <div className="flex flex-col items-center gap-4 py-10 text-center">
        <p className="text-lg font-semibold text-red-600">Invalid or expired invitation link.</p>
        <p className="text-sm text-slate-500">
          Please ask your business owner to send a new invitation.
        </p>
        <Link to={ROUTES.LOGIN} className="text-sm text-blue-600 underline">
          Back to login
        </Link>
      </div>
    );
  }

  if (status === "success") {
    return (
      <div className="flex flex-col items-center gap-4 py-10 text-center">
        <p className="text-lg font-semibold text-green-600">Account created successfully!</p>
        <p className="text-sm text-slate-500">Redirecting you to login…</p>
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
      <p className="mb-6 text-sm text-slate-500">
        You've been invited to join{" "}
        <span className="font-medium text-slate-700">{invite?.business_name}</span> as a{" "}
        <span className="font-medium text-slate-700">{invite?.role}</span>.
      </p>

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
            value={invite?.email ?? ""}
            readOnly
            className="rounded-lg border border-slate-200 bg-slate-100 px-4 py-2.5 text-sm text-slate-500 cursor-not-allowed"
          />
        </div>

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

        {/* Phone – optional */}
        <div className="flex flex-col gap-1">
          <label htmlFor="phone" className="text-sm font-medium text-slate-700">
            Phone <span className="text-slate-400">(optional)</span>
          </label>
          <input
            id="phone"
            name="phone"
            type="tel"
            autoComplete="tel"
            value={form.phone}
            onChange={handleChange}
            placeholder="+254 700 000 000"
            className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
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
          disabled={status === "submitting"}
          className="mt-2 rounded-lg bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
        >
          {status === "submitting" ? "Creating account…" : "Create account"}
        </button>
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
