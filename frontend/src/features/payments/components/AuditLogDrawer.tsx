import { usePaymentAuditLog } from "../hooks/use-payments";
import { Spinner } from "@/components/ui/feedback/Spinner";

interface AuditLogDrawerProps {
  paymentId: number;
  paymentName: string;
  onClose: () => void;
}

const ACTION_LABELS: Record<string, string> = {
  created: "Created",
  verified: "Verified",
  invitation_sent: "Invitation Sent",
  invitation_resent: "Invitation Resent",
  cancelled: "Cancelled",
  refunded: "Refunded",
  updated: "Updated",
};

const ACTION_COLORS: Record<string, string> = {
  created: "bg-blue-100 text-blue-700",
  verified: "bg-green-100 text-green-700",
  invitation_sent: "bg-purple-100 text-purple-700",
  invitation_resent: "bg-purple-100 text-purple-700",
  cancelled: "bg-red-100 text-red-700",
  refunded: "bg-orange-100 text-orange-700",
  updated: "bg-slate-100 text-slate-700",
};

export default function AuditLogDrawer({ paymentId, paymentName, onClose }: AuditLogDrawerProps) {
  const { data: logs, isLoading } = usePaymentAuditLog(paymentId);

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="fixed inset-0 bg-black/50 transition-opacity" onClick={onClose} />
      <div className="relative h-full w-full max-w-md overflow-y-auto bg-white shadow-2xl">
        <div className="sticky top-0 z-10 border-b border-slate-200 bg-white px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Audit Log</h2>
              <p className="text-sm text-slate-500">{paymentName}</p>
            </div>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
              ✕
            </button>
          </div>
        </div>

        <div className="p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-10">
              <Spinner size="md" />
            </div>
          ) : !logs?.length ? (
            <p className="py-10 text-center text-sm text-slate-500">No audit log entries found.</p>
          ) : (
            <div className="space-y-4">
              {logs.map((log) => (
                <div key={log.id} className="flex gap-3">
                  <div className="flex flex-col items-center">
                    <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium ${ACTION_COLORS[log.action] ?? "bg-slate-100 text-slate-700"}`}>
                      {log.action.charAt(0).toUpperCase()}
                    </div>
                    <div className="mt-1 h-full w-px bg-slate-200" />
                  </div>
                  <div className="flex-1 pb-4">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-slate-900">
                        {ACTION_LABELS[log.action] ?? log.action}
                      </span>
                      <span className="text-xs text-slate-400">
                        {new Date(log.timestamp).toLocaleString()}
                      </span>
                    </div>
                    {log.performed_by_name && (
                      <p className="mt-0.5 text-xs text-slate-500">
                        by {log.performed_by_name}
                      </p>
                    )}
                    {log.description && (
                      <p className="mt-1 text-sm text-slate-600">{log.description}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
