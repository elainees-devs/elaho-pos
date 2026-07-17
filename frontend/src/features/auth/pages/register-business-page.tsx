import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Store, Eye, EyeOff, Building2 } from "lucide-react";
import { businessService } from "@/features/business/services/business.service";
import { registerBusinessSchema } from "@/features/business/validation/business.validation";
import type { RegisterBusinessFormValues } from "@/features/business/validation/business.validation";
import { ROUTES } from "@/config/routes/route-paths";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type PageStatus = "ready" | "submitting" | "success";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function RegisterBusinessPage() {
  const navigate = useNavigate();

  const [status, setStatus] = useState<PageStatus>("ready");
  const [error, setError] = useState<string>("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<
    Partial<Record<keyof RegisterBusinessFormValues, string>>
  >({});

  const [form, setForm] = useState<RegisterBusinessFormValues>({
    business_name: "",
    business_phone: "",
    business_email: "",
    business_address: "",
    kra_pin: "",
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    password: "",
    confirm_password: "",
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setFieldErrors((prev) => ({ ...prev, [name]: undefined }));
  }

  function validate(): boolean {
    const result = registerBusinessSchema.safeParse(form);
    if (result.success) {
      setFieldErrors({});
      return true;
    }

    const errors: Partial<Record<keyof RegisterBusinessFormValues, string>> = {};
    for (const issue of result.error.issues) {
      const key = issue.path[0] as keyof RegisterBusinessFormValues;
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

    setStatus("submitting");

    try {
      await businessService.register({
        business_name: form.business_name.trim(),
        business_phone: form.business_phone?.trim() || undefined,
        business_email: form.business_email?.trim() || undefined,
        business_address: form.business_address?.trim() || undefined,
        kra_pin: form.kra_pin.trim(),
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        email: form.email.trim(),
        phone: form.phone?.trim() || undefined,
        password: form.password,
      });

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

  if (status === "success") {
    return (
      <div className="flex flex-col items-center gap-4 py-10 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-success/10">
          <span className="text-2xl text-success">&#10003;</span>
        </div>
        <p className="text-lg font-semibold text-success">Business registered successfully!</p>
        <p className="text-sm text-text-secondary">Redirecting you to sign in&hellip;</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8 flex items-center gap-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-primary-foreground">
          <Store size={18} />
        </div>
        <span className="text-lg font-semibold text-text-primary">Elaho POS</span>
      </div>

      <h1 className="mb-1 text-2xl font-bold text-text-primary">Set up your business</h1>
      <p className="mb-6 text-sm text-text-secondary">
        Create your account and start managing your store.
      </p>

      {error && (
        <div className="mb-4 rounded-lg bg-danger/10 px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-4">
        {/* ── Business info ────────────────────────────────────────────── */}
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-text-muted">
          <Building2 size={14} />
          Business details
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="business_name" className="text-sm font-medium text-text-primary">
            Business name
          </label>
          <input
            id="business_name"
            name="business_name"
            type="text"
            autoComplete="organization"
            value={form.business_name}
            onChange={handleChange}
            placeholder="Acme Ltd"
            className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
          {fieldErrors.business_name && (
            <p className="text-xs text-danger">{fieldErrors.business_name}</p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col gap-1">
            <label htmlFor="business_phone" className="text-sm font-medium text-text-primary">
              Business phone <span className="text-text-muted">(optional)</span>
            </label>
            <input
              id="business_phone"
              name="business_phone"
              type="tel"
              autoComplete="tel"
              value={form.business_phone}
              onChange={handleChange}
              placeholder="+254 700 000 000"
              className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
            {fieldErrors.business_phone && (
              <p className="text-xs text-danger">{fieldErrors.business_phone}</p>
            )}
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="business_email" className="text-sm font-medium text-text-primary">
              Business email <span className="text-text-muted">(optional)</span>
            </label>
            <input
              id="business_email"
              name="business_email"
              type="email"
              autoComplete="email"
              value={form.business_email}
              onChange={handleChange}
              placeholder="info@acme.co.ke"
              className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
            {fieldErrors.business_email && (
              <p className="text-xs text-danger">{fieldErrors.business_email}</p>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="business_address" className="text-sm font-medium text-text-primary">
            Business address <span className="text-text-muted">(optional)</span>
          </label>
          <input
            id="business_address"
            name="business_address"
            type="text"
            value={form.business_address}
            onChange={handleChange}
            placeholder="123 Moi Avenue, Nairobi"
            className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="kra_pin" className="text-sm font-medium text-text-primary">
            KRA PIN
          </label>
          <input
            id="kra_pin"
            name="kra_pin"
            type="text"
            value={form.kra_pin}
            onChange={handleChange}
            placeholder="A001234567B"
            className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
          {fieldErrors.kra_pin && (
            <p className="text-xs text-danger">{fieldErrors.kra_pin}</p>
          )}
        </div>

        {/* ── Divider ─────────────────────────────────────────────────── */}
        <hr className="border-border" />

        {/* ── Owner info ───────────────────────────────────────────────── */}
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-text-muted">
          <Store size={14} />
          Your details
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col gap-1">
            <label htmlFor="first_name" className="text-sm font-medium text-text-primary">
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
              className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
            {fieldErrors.first_name && (
              <p className="text-xs text-danger">{fieldErrors.first_name}</p>
            )}
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="last_name" className="text-sm font-medium text-text-primary">
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
              className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
            {fieldErrors.last_name && (
              <p className="text-xs text-danger">{fieldErrors.last_name}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col gap-1">
            <label htmlFor="email" className="text-sm font-medium text-text-primary">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              value={form.email}
              onChange={handleChange}
              placeholder="jane@acme.co.ke"
              className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
            {fieldErrors.email && (
              <p className="text-xs text-danger">{fieldErrors.email}</p>
            )}
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="phone" className="text-sm font-medium text-text-primary">
              Phone <span className="text-text-muted">(optional)</span>
            </label>
            <input
              id="phone"
              name="phone"
              type="tel"
              autoComplete="tel"
              value={form.phone}
              onChange={handleChange}
              placeholder="+254 700 000 000"
              className="rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
        </div>

        {/* ── Password ─────────────────────────────────────────────────── */}
        <div className="flex flex-col gap-1">
          <label htmlFor="password" className="text-sm font-medium text-text-primary">
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
              placeholder="Min. 8 characters"
              className="w-full rounded-lg border border-border bg-surface px-4 py-2.5 pr-10 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {fieldErrors.password && (
            <p className="text-xs text-danger">{fieldErrors.password}</p>
          )}
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="confirm_password" className="text-sm font-medium text-text-primary">
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
              className="w-full rounded-lg border border-border bg-surface px-4 py-2.5 pr-10 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <button
              type="button"
              onClick={() => setShowConfirm((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary"
              aria-label={showConfirm ? "Hide password" : "Show password"}
            >
              {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {fieldErrors.confirm_password && (
            <p className="text-xs text-danger">{fieldErrors.confirm_password}</p>
          )}
        </div>

        {/* ── Submit ───────────────────────────────────────────────────── */}
        <button
          type="submit"
          disabled={status === "submitting"}
          className="mt-2 rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground transition hover:bg-primary-hover disabled:opacity-60"
        >
          {status === "submitting" ? "Creating account\u2026" : "Create account"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-text-secondary">
        Already have an account?{" "}
        <Link
          to={ROUTES.LOGIN}
          className="font-medium text-primary hover:underline"
        >
          Sign in
        </Link>
      </p>
    </div>
  );
}
