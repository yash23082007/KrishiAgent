import { ReactNode } from "react";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  description?: string;
  trend?: string;
  trendColor?: "green" | "red" | "yellow";
}

export default function StatCard({
  title,
  value,
  icon,
  description,
  trend,
  trendColor = "green",
}: StatCardProps) {
  const getTrendColorClass = () => {
    if (trendColor === "green") return "text-green-400";
    if (trendColor === "red") return "text-red-400";
    return "text-yellow-400";
  };

  return (
    <div className="glass-panel rounded-2xl p-6 transition-all duration-300 hover:border-zinc-700 hover:translate-y-[-2px] flex flex-col justify-between">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-zinc-400 tracking-wide">{title}</span>
        <div className="bg-zinc-900 border border-zinc-800 p-2.5 rounded-xl text-zinc-300">
          {icon}
        </div>
      </div>
      
      <div className="mt-4">
        <div className="text-3xl font-bold tracking-tight text-white">{value}</div>
        
        {description && (
          <div className="mt-2 flex items-center gap-1.5 text-xs">
            {trend && (
              <span className={`font-semibold ${getTrendColorClass()}`}>
                {trend}
              </span>
            )}
            <span className="text-zinc-500">{description}</span>
          </div>
        )}
      </div>
    </div>
  );
}
