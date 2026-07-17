import { useState } from "react";
import {
  Plus,
  CheckCircle,
  XCircle,
  RotateCcw,
  Mail,
  Eye,
  MoreHorizontal,
  CreditCard,
} from "lucide-react";

import { usePayments, useDeletePayment } from "../hooks/use-payments";
import type { Payment, PaymentStatus } from "../types/payment.types";
import { Badge } from "@/components/ui/data-display/Badge";
import { Button } from "@/components/ui/actions/Button";
import { SearchInput } from "@/components/ui/forms/SearchInput";
import { Spinner } from "@/components/ui/feedback/Spinner";
import { EmptyState } from "@/components/ui/feedback/EmptyState";
import PaymentFormDialog from "../components/PaymentFormDialog";
import ConfirmActionDialog from "../components/ConfirmActionDialog";
import AuditLogDrawer from "../components/AuditLogDrawer";

const STATUS_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "All Statuses" },
  { value: "pending", label: "Pending" },
  { value: "paid", label: "Paid" },
  { value: "cancelled", label: "Cancelled" },
  { value: "refunded", label: "Refunded" },
];

const STATUS_BADGE_MAP: Record<PaymentStatus, "warning" | "success" | "danger" | "neutral"> = {
  pending: "warning",
  paid: "success",
  cancelled: "danger",
  refunded: "neutral",
};

const REGISTRATION_BADGE_MAP: Record<string, "success" | "warning" | "neutral"> = {
  registered: "success",
  pending_registration: "warning",
  no_invitation: "neutral",
};

const METHOD_LABELS: Record<string, string> = {
  mpesa: "M-Pesa",
  bank_transfer: "Bank Transfer",
  cash: "Cash",
  card: "Card",
  airtel_money: "Airtel Money",
  other: "Other",
};

export default function PaymentListPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingPayment, setEditingPayment] = useState<Payment | null>(null);
  const [actionPayment, setActionPayment] = useState<{ payment: Payment; action: "verify" | "cancel" | "refund" } | null>(null);
  const [auditPayment, setAuditPayment] = useState<Payment | null>(null);
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);

  const { data, isLoading } = usePayments({
    status: statusFilter || undefined,
    search: search || undefined,
  });

  const deleteMutation = useDeletePayment();

  const payments = data?.results ?? [];

  function handleEdit(payment: Payment) {
    setEditingPayment(payment);
    setShowForm(true);
    setOpenMenuId(null);
  }

  function handleCloseForm() {
    setShowForm(false);
    setEditingPayment(null);
  }

  function handleDelete(id: number) {
    if (confirm("Are you sure you want to delete this payment?")) {
      deleteMutation.mutate(id);
    }
    setOpenMenuId(null);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Payments</h1>
          <p className="text-sm text-slate-500">Manage and verify payment records</p>
        </div>
        <Button
          onClick={() => {
            setEditingPayment(null);
            setShowForm(true);
          }}
        >
          <Plus size={16} className="mr-2" />
          Add Payment
        </Button>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex-1">
          <SearchInput
            value={search}
            onChange={setSearch}
            placeholder="Search by business, owner, or email..."
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Spinner size="lg" />
        </div>
      ) : payments.length === 0 ? (
        <EmptyState
          icon={<CreditCard />}
          title="No payments found"
          description={search || statusFilter ? "Try adjusting your search or filters" : "Add your first payment record to get started"}
          action={
            !search && !statusFilter ? (
              <Button onClick={() => setShowForm(true)}>
                <Plus size={16} className="mr-2" />
                Add Payment
              </Button>
            ) : undefined
          }
        />
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Business
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Owner
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Plan
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Amount
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Method
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Reference
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Registration
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Verified By
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {payments.map((payment) => (
                <tr key={payment.id} className="transition hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{payment.business_name}</td>
                  <td className="px-4 py-3">
                    <div className="text-slate-900">{payment.owner_name}</div>
                    <div className="text-xs text-slate-500">{payment.owner_email}</div>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{payment.subscription_plan_name}</td>
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {payment.currency} {Number(payment.amount).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {METHOD_LABELS[payment.payment_method] ?? payment.payment_method}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-600">
                    {payment.reference_number}
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {new Date(payment.payment_date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={STATUS_BADGE_MAP[payment.status]}>
                      {payment.status.charAt(0).toUpperCase() + payment.status.slice(1)}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={REGISTRATION_BADGE_MAP[payment.registration_status]}>
                      {payment.registration_status === "registered"
                        ? "Registered"
                        : payment.registration_status === "pending_registration"
                          ? "Pending"
                          : "No Invitation"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {payment.verified_by_name ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="relative flex items-center justify-end gap-1">
                      {payment.status === "pending" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setActionPayment({ payment, action: "verify" })}
                          title="Verify"
                        >
                          <CheckCircle size={14} className="text-green-600" />
                        </Button>
                      )}
                      {(payment.status === "pending" || payment.status === "paid") && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setActionPayment({ payment, action: "cancel" })}
                          title="Cancel"
                        >
                          <XCircle size={14} className="text-red-600" />
                        </Button>
                      )}
                      {payment.status === "paid" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setActionPayment({ payment, action: "refund" })}
                          title="Refund"
                        >
                          <RotateCcw size={14} className="text-orange-600" />
                        </Button>
                      )}
                      {payment.status === "paid" && payment.registration_status !== "registered" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setActionPayment({ payment, action: "verify" });
                            setOpenMenuId(null);
                          }}
                          title="Resend Invitation"
                        >
                          <Mail size={14} className="text-blue-600" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setAuditPayment(payment);
                          setOpenMenuId(null);
                        }}
                        title="View Audit Log"
                      >
                        <Eye size={14} className="text-slate-600" />
                      </Button>
                      <div className="relative">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setOpenMenuId(openMenuId === payment.id ? null : payment.id)}
                        >
                          <MoreHorizontal size={14} />
                        </Button>
                        {openMenuId === payment.id && (
                          <>
                            <div
                              className="fixed inset-0 z-10"
                              onClick={() => setOpenMenuId(null)}
                            />
                            <div className="absolute right-0 z-20 mt-1 w-40 rounded-lg border border-slate-200 bg-white py-1 shadow-lg">
                              <button
                                onClick={() => handleEdit(payment)}
                                className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => handleDelete(payment.id)}
                                className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50"
                              >
                                Delete
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <PaymentFormDialog
          payment={editingPayment}
          onClose={handleCloseForm}
        />
      )}

      {actionPayment && (
        <ConfirmActionDialog
          payment={actionPayment.payment}
          action={actionPayment.action}
          onClose={() => setActionPayment(null)}
        />
      )}

      {auditPayment && (
        <AuditLogDrawer
          paymentId={auditPayment.id}
          paymentName={auditPayment.business_name}
          onClose={() => setAuditPayment(null)}
        />
      )}
    </div>
  );
}
