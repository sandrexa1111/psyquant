import React from 'react';
import { ArrowUp, ArrowDown } from 'lucide-react';

const StatCard = ({ title, value, subValue, trend, trendValue, icon: Icon, color, index }) => {
    const isPositive = trend === 'up';

    // Color mapping based on index or prop
    const colors = {
        blue: { border: 'border-b-blue-500', text: 'text-blue-500', bg: 'bg-blue-50' },
        red: { border: 'border-b-red-500', text: 'text-red-500', bg: 'bg-red-50' },
        amber: { border: 'border-b-amber-500', text: 'text-amber-500', bg: 'bg-amber-50' },
        emerald: { border: 'border-b-emerald-500', text: 'text-emerald-500', bg: 'bg-emerald-50' },
    };

    const theme = colors[color] || colors.blue;

    return (
        <div className={`bg-white p-6 rounded-xl shadow-sm border border-slate-100 relative overflow-hidden group hover:shadow-md transition-shadow`}>
            {/* Color Accent */}
            <div className={`absolute top-0 left-0 w-full h-1 ${theme.border}`}></div>

            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">{title}</h3>
                    <div className="flex items-baseline gap-2">
                        <span className="text-2xl font-bold text-slate-800">{value}</span>
                        {subValue && <span className="text-sm font-medium text-slate-400">{subValue}</span>}
                    </div>
                </div>
                <div className={`w-10 h-10 ${theme.bg} rounded-full flex items-center justify-center ${theme.text}`}>
                    {Icon && <Icon size={20} />}
                </div>
            </div>

            <div className="flex items-center gap-2">
                <span className={`flex items-center gap-1 text-sm font-bold ${isPositive ? 'text-emerald-500' : 'text-red-500'}`}>
                    {isPositive ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
                    {trendValue}
                </span>
                <span className="text-xs text-slate-400">since last month</span>
            </div>
        </div>
    );
};

export default StatCard;
