import { useEffect, useState } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { Store, Eye, EyeOff } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { paymentService } from "@/features/payments/services/payment.service";
import {
  registerFromPaymentSchema,
  type RegisterFromPaymentFormValues,
} from "@/features/payments/validations/payment.validation";
import type { ValidateRegistrationTokenResponse } from "@/features/payments/types/payment.types";
import { ROUTES } from "@/config/routes/route-paths";

type PageStatus = "loading" | "invalid" | "ready" | "submitting" | "success";

export default function RegisterBusinessPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token") ?? "";

  const [status, setStatus] = useState<PageStatus>("loading");
  const [invite, setInvite] = useState<ValidateRegistrationTokenResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFromPaymentFormValues>({
    resolver: zodResolver(registerFromPaymentSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      phone: "",
      password: "",
      confirm_password: "",
    },
  });

  useEffect(() => {
    if (!token) {
      setStatus("invalid");
      return;
    }
    paymentService
      .validateRegistrationToken(token)
      .then((data) => {
        setInvite(data);
        setStatus("ready");
      })
      .catch(() => {
        setStatus("invalid");
      });
  }, [token]);

  async function onSubmit(data: RegisterFromPaymentFormValues) {
    setError("");
    setStatus("submitting");
    try {
      const tokens = await paymentService.registerFromPayment({
        token,
        first_name: data.first_name,
        last_name: data.last_name,
        phone: data.phone || undefined,
        password: data.password,
      });
      localStorage.setItem("access_token", tokens.access);
      localStorage.setItem("refresh_token", tokens.refresh);
      setStatus("success");
      setTimeout(() => navigate(ROUTES.DASHBOARD, { replace: true }), 2000);
    } catch (err: unknown) {
      setStatus("ready");
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? "Something went wrong. Please try again.");
    }
  }

  if (status === "loading") {
    return (
      <div className="flex min-h-[300px] items-center justify-center">
        <div className="flex items-center gap-3 text-slate-500 text-sm">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-blue-600" />
          Validating invitation…
        </div>
      </div>
    );
  }

  if (status === "invalid") {
    return (
      <div className="flex flex-col items-center gap-4 py-10 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-100">
          <span className="text-2xl">✕</span>
        </div>
        <p className="text-lg font-semibold text-red-600">Invalid or expired invitation link.</p>
        <p className="text-sm text-slate-500">
          Please ask the system administrator to send a new invitation.
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
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-green-100">
          <span className="text-2xl">✓</span>
        </div>
        <p className="text-lg font-semibold text-green-600">Account created successfully!</p>
        <p className="text-sm text-slate-500">Redirecting you to the dashboard…</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex items-center gap-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-600 text-white">
          <Store size={18} />
        </div>
        <span className="text-lg font-semibold text-slate-800">Elaho POS</span>
      </div>

      <h1 className="mb-1 text-2xl font-bold text-slate-900">Set up your business</h1>
      <p className="mb-6 text-sm text-slate-500">
        Register{" "}
        <span className="font-medium text-slate-700">{invite?.business_name}</span> on the{" "}
        <span className="font-medium text-slate-700">{invite?.subscription_plan}</span> plan (
        {invite?.billing_cycle}).
      </p>

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-slate-700">Email</label>
          <input
            type="email"
            value={invite?.email ?? ""}
            readOnly
            className="rounded-lg border border-slate-200 bg-slate-100 px-4 py-2.5 text-sm text-slate-500 cursor-not-allowed"
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col gap-1">
            <label htmlFor="first_name" className="text-sm font-medium text-slate-700">
              First name
            </label>
            <input
              id="first_name"
              {...register("first_name")}
              placeholder="Jane"
              className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            {errors.first_name && (
              <p className="text-xs text-red-600">{errors.first_name.message}</p>
            )}
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="last_name" className="text-sm font-medium text-slate-700">
              Last name
            </label>
            <input
              id="last_name"
              {...register("last_name")}
              placeholder="Doe"
              className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            {errors.last_name && (
              <p className="text-xs text-red-600">{errors.last_name.message}</p>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="phone" className="text-sm font-medium text-slate-700">
            Phone <span className="text-slate-400">(optional)</span>
          </label>
          <input
            id="phone"
            type="tel"
            {...register("phone")}
            placeholder="+254 700 000 000"
            className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="password" className="text-sm font-medium text-slate-700">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              {...register("password")}
              placeholder="Create a strong password"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 pr-10 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {errors.password && <p className="text-xs text-red-600">{errors.password.message}</p>}
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="confirm_password" className="text-sm font-medium text-slate-700">
            Confirm password
          </label>
          <div className="relative">
            <input
              id="confirm_password"
              type={showConfirm ? "text" : "password"}
              {...register("confirm_password")}
              placeholder="Repeat your password"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 pr-10 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <button
              type="button"
              onClick={() => setShowConfirm((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {errors.confirm_password && (
            <p className="text-xs text-red-600">{errors.confirm_password.message}</p>
          )}
        </div>

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
