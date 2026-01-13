import React from 'react';
import { PieChart } from 'lucide-react';

const AllocationDonut = ({ data }) => {
    // Handling empty state
    if (!data || data.length === 0) {
        return (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 h-full flex flex-col items-center justify-center text-slate-400">
                <PieChart size={48} className="mb-2 opacity-50" />
                <p>No Positions Held</p>
            </div>
        );
    }

    // Colors for segments
    const colors = [
        'bg-indigo-500', 'bg-blue-500', 'bg-sky-500', 'bg-emerald-500',
        'bg-amber-500', 'bg-orange-500', 'bg-rose-500', 'bg-slate-400'
    ];

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 h-full">
            <h3 className="font-bold text-slate-700 mb-4">Asset Allocation</h3>

            <div className="space-y-4">
                {data.map((item, index) => (
                    <div key={item.symbol} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-full ${colors[index % colors.length]}`} />
                            <span className="font-semibold text-slate-700">{item.symbol}</span>
                        </div>
                        <div className="text-right">
                            <div className="font-bold text-slate-800">{item.percentage}%</div>
                            <div className="text-xs text-slate-500 sm:hidden md:block">
                                ${item.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Simulated Visual Bar (since we don't have a charting lib for Pie yet, this is cleaner) */}
            <div className="mt-8 flex h-4 w-full rounded-full overflow-hidden">
                {data.map((item, index) => (
                    <div
                        key={item.symbol}
                        style={{ width: `${item.percentage}%` }}
                        className={colors[index % colors.length]}
                        title={`${item.symbol}: ${item.percentage}%`}
                    />
                ))}
            </div>
        </div>
    );
};

export default AllocationDonut;
