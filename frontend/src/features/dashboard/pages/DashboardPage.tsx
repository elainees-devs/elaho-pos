import { DollarSign, Clock, CheckCircle, TrendingUp, XCircle } from "lucide-react";
import { useDashboardMetrics } from "@/features/payments/hooks/use-payments";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
}

function MetricCard({ title, value, icon, color, bgColor }: MetricCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
        </div>
        <div className={`flex h-12 w-12 items-center justify-center rounded-lg ${bgColor}`}>
          <div className={color}>{icon}</div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { data: metrics, isLoading } = useDashboardMetrics();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-300 border-t-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-500">Overview of your payment and subscription activity</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <MetricCard
          title="Total Payments"
          value={metrics?.total_payments ?? 0}
          icon={<DollarSign size={24} />}
          color="text-blue-600"
          bgColor="bg-blue-100"
        />
        <MetricCard
          title="Pending Payments"
          value={metrics?.pending_payments ?? 0}
          icon={<Clock size={24} />}
          color="text-yellow-600"
          bgColor="bg-yellow-100"
        />
        <MetricCard
          title="Verified Payments"
          value={metrics?.verified_payments ?? 0}
          icon={<CheckCircle size={24} />}
          color="text-green-600"
          bgColor="bg-green-100"
        />
        <MetricCard
          title="Active Subscriptions"
          value={metrics?.active_subscriptions ?? 0}
          icon={<TrendingUp size={24} />}
          color="text-emerald-600"
          bgColor="bg-emerald-100"
        />
        <MetricCard
          title="Monthly Revenue"
          value={`KES ${Number(metrics?.monthly_revenue ?? 0).toLocaleString()}`}
          icon={<DollarSign size={24} />}
          color="text-purple-600"
          bgColor="bg-purple-100"
        />
        <MetricCard
          title="Expired Subscriptions"
          value={metrics?.expired_subscriptions ?? 0}
          icon={<XCircle size={24} />}
          color="text-red-600"
          bgColor="bg-red-100"
        />
      </div>
    </div>
  );
}
