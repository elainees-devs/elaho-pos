import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { useCreatePayment, useUpdatePayment, useSubscriptionPlans } from "../hooks/use-payments";
import {
  createPaymentSchema,
  type CreatePaymentFormValues,
} from "../validations/payment.validation";
import type { Payment } from "../types/payment.types";
import { Button } from "@/components/ui/actions/Button";

interface PaymentFormDialogProps {
  payment: Payment | null;
  onClose: () => void;
}

const PAYMENT_METHODS = [
  { value: "mpesa", label: "M-Pesa" },
  { value: "bank_transfer", label: "Bank Transfer" },
  { value: "cash", label: "Cash" },
  { value: "card", label: "Card" },
  { value: "airtel_money", label: "Airtel Money" },
  { value: "other", label: "Other" },
];

export default function PaymentFormDialog({ payment, onClose }: PaymentFormDialogProps) {
  const isEditing = !!payment;
  const createMutation = useCreatePayment();
  const updateMutation = useUpdatePayment();
  const { data: plans } = useSubscriptionPlans();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<CreatePaymentFormValues>({
    resolver: zodResolver(createPaymentSchema),
    defaultValues: {
      owner_name: payment?.owner_name ?? "",
      owner_email: payment?.owner_email ?? "",
      owner_phone: payment?.owner_phone ?? "",
      business_name: payment?.business_name ?? "",
      subscription_plan: payment?.subscription_plan ?? 0,
      billing_cycle: payment?.billing_cycle ?? "monthly",
      amount: payment?.amount ?? "",
      currency: payment?.currency ?? "KES",
      payment_method: payment?.payment_method ?? "mpesa",
      reference_number: payment?.reference_number ?? "",
      payment_date: payment?.payment_date ?? new Date().toISOString().split("T")[0],
      notes: payment?.notes ?? "",
    },
  });

  const selectedPlan = watch("subscription_plan");
  const selectedCycle = watch("billing_cycle");

  useEffect(() => {
    if (plans && selectedPlan && selectedCycle) {
      const plan = plans.find((p) => p.id === Number(selectedPlan));
      if (plan) {
        const price = selectedCycle === "annual" ? plan.annual_price : plan.monthly_price;
        setValue("amount", price);
      }
    }
  }, [plans, selectedPlan, selectedCycle, setValue]);

  function onSubmit(data: CreatePaymentFormValues) {
    const payload = {
      ...data,
      subscription_plan: Number(data.subscription_plan),
    };

    if (isEditing) {
      updateMutation.mutate(
        { id: payment.id, data: payload },
        { onSuccess: onClose }
      );
    } else {
      createMutation.mutate(payload, { onSuccess: onClose });
    }
  }

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50 transition-opacity" onClick={onClose} />
      <div className="relative mx-4 max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl bg-white shadow-2xl">
        <div className="sticky top-0 z-10 border-b border-slate-200 bg-white px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">
              {isEditing ? "Edit Payment" : "Add Payment"}
            </h2>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
              ✕
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-slate-700">Owner Name *</label>
                <input
                  {...register("owner_name")}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                {errors.owner_name && <p className="text-xs text-red-600">{errors.owner_name.message}</p>}
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-slate-700">Owner Email *</label>
                <input
                  {...register("owner_email")}
                  type="email"
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                {errors.owner_email && <p className="text-xs text-red-600">{errors.owner_email.message}</p>}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-slate-700">Owner Phone *</label>
                <input
                  {...register("owner_phone")}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                {errors.owner_phone && <p className="text-xs text-red-600">{errors.owner_phone.message}</p>}
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-slate-700">Business Name *</label>
                <input
                  {...register("business_name")}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                {errors.business_name && <p className="text-xs text-red-600">{errors.business_name.message}</p>}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-slate-700">Subscription Plan *</label>
                <select
                  {...register("subscription_plan")}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">Select plan</option>
                  {plans?.map((plan) => (
                    <option key={plan.id} value={plan.id}>
                      {plan.name}
                    </option>
                  ))}
                </select>
                {errors.subscription_plan && <p className="text-xs text-red-600">{errors.subscription_plan.message}</p>}
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-slate-700">Billing Cycle *</label>
                <select
                  {...register("billing_cycle")}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="monthly">Monthly</option>
                  <option value="annual">Annual</option>
                </select>
                {errors.billing_cycle && <p className="text-xs text-red-600">{errors.billing_cycle.message}</p>}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-slate-700">Amount *</label>
                <input
                  {...register("amount")}
                  type="number"
                  step="0.01"
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                {errors.amount && <p className="text-xs text-red-600">{errors.amount.message}</p>}
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-slate-700">Currency</label>
                <input
                  {...register("currency")}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-slate-700">Payment Method *</label>
                <select
                  {...register("payment_method")}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  {PAYMENT_METHODS.map((m) => (
                    <option key={m.value} value={m.value}>
                      {m.label}
                    </option>
                  ))}
                </select>
                {errors.payment_method && <p className="text-xs text-red-600">{errors.payment_method.message}</p>}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-slate-700">Reference Number *</label>
                <input
                  {...register("reference_number")}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                {errors.reference_number && <p className="text-xs text-red-600">{errors.reference_number.message}</p>}
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-slate-700">Payment Date *</label>
                <input
                  {...register("payment_date")}
                  type="date"
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                {errors.payment_date && <p className="text-xs text-red-600">{errors.payment_date.message}</p>}
              </div>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-slate-700">Notes</label>
              <textarea
                {...register("notes")}
                rows={3}
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="mt-6 flex justify-end gap-3">
            <Button variant="secondary" onClick={onClose} type="button">
              Cancel
            </Button>
            <Button type="submit" loading={isSubmitting}>
              {isEditing ? "Save Changes" : "Create Payment"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
