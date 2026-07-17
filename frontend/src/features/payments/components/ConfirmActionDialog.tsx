import { useState } from "react";

import {
  useVerifyPayment,
  useCancelPayment,
  useRefundPayment,
} from "../hooks/use-payments";
import type { Payment } from "../types/payment.types";
import { Button } from "@/components/ui/actions/Button";

interface ConfirmActionDialogProps {
  payment: Payment;
  action: "verify" | "cancel" | "refund";
  onClose: () => void;
}

const ACTION_CONFIG = {
  verify: {
    title: "Verify Payment",
    description: "This will mark the payment as verified, generate a registration invitation, and send an email to the business owner.",
    confirmLabel: "Verify & Send Invitation",
    confirmColor: "bg-green-600 hover:bg-green-700 text-white",
    iconBg: "bg-green-100",
    icon: "✓",
    iconColor: "text-green-600",
  },
  cancel: {
    title: "Cancel Payment",
    description: "This will cancel the payment record. This action cannot be undone.",
    confirmLabel: "Cancel Payment",
    confirmColor: "bg-red-600 hover:bg-red-700 text-white",
    iconBg: "bg-red-100",
    icon: "✕",
    iconColor: "text-red-600",
  },
  refund: {
    title: "Refund Payment",
    description: "This will mark the payment as refunded. This action cannot be undone.",
    confirmLabel: "Confirm Refund",
    confirmColor: "bg-orange-600 hover:bg-orange-700 text-white",
    iconBg: "bg-orange-100",
    icon: "↩",
    iconColor: "text-orange-600",
  },
};

export default function ConfirmActionDialog({ payment, action, onClose }: ConfirmActionDialogProps) {
  const [reason, setReason] = useState("");
  const verifyMutation = useVerifyPayment();
  const cancelMutation = useCancelPayment();
  const refundMutation = useRefundPayment();

  const config = ACTION_CONFIG[action];

  function handleConfirm() {
    const onSuccess = onClose;

    if (action === "verify") {
      verifyMutation.mutate(payment.id, { onSuccess });
    } else if (action === "cancel") {
      cancelMutation.mutate({ id: payment.id, reason: reason || undefined }, { onSuccess });
    } else if (action === "refund") {
      refundMutation.mutate({ id: payment.id, reason: reason || undefined }, { onSuccess });
    }
  }

  const isLoading = verifyMutation.isPending || cancelMutation.isPending || refundMutation.isPending;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50 transition-opacity" onClick={onClose} />
      <div className="relative mx-4 w-full max-w-md rounded-xl bg-white p-6 shadow-2xl">
        <div className="flex items-start gap-4">
          <div className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full ${config.iconBg}`}>
            <span className={`text-lg font-bold ${config.iconColor}`}>{config.icon}</span>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-slate-900">{config.title}</h3>
            <p className="mt-2 text-sm text-slate-600">{config.description}</p>

            <div className="mt-4 rounded-lg bg-slate-50 p-3">
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span className="text-slate-500">Business:</span>
                <span className="font-medium text-slate-900">{payment.business_name}</span>
                <span className="text-slate-500">Owner:</span>
                <span className="font-medium text-slate-900">{payment.owner_name}</span>
                <span className="text-slate-500">Amount:</span>
                <span className="font-medium text-slate-900">
                  {payment.currency} {Number(payment.amount).toLocaleString()}
                </span>
                <span className="text-slate-500">Reference:</span>
                <span className="font-mono text-xs text-slate-900">{payment.reference_number}</span>
              </div>
            </div>

            {(action === "cancel" || action === "refund") && (
              <div className="mt-4 flex flex-col gap-1">
                <label className="text-sm font-medium text-slate-700">Reason (optional)</label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={3}
                  placeholder="Enter reason..."
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            )}
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <Button variant="secondary" onClick={onClose} disabled={isLoading}>
            Close
          </Button>
          <Button
            onClick={handleConfirm}
            loading={isLoading}
            className={config.confirmColor}
          >
            {config.confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
