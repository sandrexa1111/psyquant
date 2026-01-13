import React from 'react';
import { TrendingUp, TrendingDown, Percent, Activity } from 'lucide-react';

const MetricCard = ({ label, value, subtext, icon: Icon, color }) => {
    const colors = {
        emerald: "bg-emerald-100 text-emerald-600",
        rose: "bg-rose-100 text-rose-600",
        blue: "bg-blue-100 text-blue-600",
        amber: "bg-amber-100 text-amber-600",
        indigo: "bg-indigo-100 text-indigo-600"
    };

    const theme = colors[color] || colors.blue;

    return (
        <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
                <div>
                    <h4 className="text-slate-400 text-xs font-bold uppercase tracking-wider">{label}</h4>
                    <div className="mt-2 flex items-baseline gap-2">
                        <span className="text-2xl font-bold text-slate-800">{value}</span>
                    </div>
                    {subtext && <p className="mt-1 text-xs text-slate-400">{subtext}</p>}
                </div>
                <div className={`p-3 rounded-lg ${theme}`}>
                    <Icon size={20} />
                </div>
            </div>
        </div>
    );
};

const PerformanceMatrix = ({ metrics }) => {
    if (!metrics || !metrics.summary) return null;

    const { summary } = metrics;

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <MetricCard
                    label="Sharpe Ratio"
                    value={summary.sharpe_ratio}
                    subtext="Risk-adjusted return (Higher is better)"
                    icon={Activity}
                    color="indigo"
                />
                <MetricCard
                    label="Max Drawdown"
                    value={`${summary.max_drawdown}%`}
                    subtext="Peak-to-trough decline"
                    icon={TrendingDown}
                    color="rose"
                />
                <MetricCard
                    label="Win Rate"
                    value={`${summary.win_rate}%`}
                    subtext="Percentage of profitable days"
                    icon={Percent}
                    color="emerald"
                />
                <MetricCard
                    label="Total Return"
                    value={`${summary.total_return}%`}
                    subtext="Over selected period"
                    icon={TrendingUp}
                    color={summary.total_return >= 0 ? "emerald" : "rose"}
                />
            </div>

            {/* Context / Explanation Section */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
                <h4 className="text-sm font-bold text-slate-700 mb-2">Institutional Metrics Analysis</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-600">
                    <p>
                        <span className="font-semibold text-indigo-600">Sharpe Ratio:</span> Measure of excess return per unit of risk. A value &gt; 1.0 is considered good, &gt; 2.0 is excellent.
                    </p>
                    <p>
                        <span className="font-semibold text-rose-600">Max Drawdown:</span> Shows the worst possible loss for the period. Crucial for understanding risk exposure.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default PerformanceMatrix;
