import React, { useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Maximize2, TrendingUp, TrendingDown } from 'lucide-react';

const PortfolioChart = ({ data, periodChange }) => {
    const [timeframe, setTimeframe] = useState('1M');

    // In a real app, you'd filter `data` based on `timeframe`. 
    // For now, we use the `data` passed in (which corresponds to equity history).
    const displayData = data;

    // Determine trend color based on overall change
    const isPositive = periodChange >= 0;
    const strokeColor = isPositive ? '#10b981' : '#f43f5e'; // Emerald or Rose
    const fillColor = isPositive ? '#10b981' : '#f43f5e';

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 h-full flex flex-col p-2">
            {/* Header */}
            <div className="px-4 py-3 border-b border-slate-100 flex justify-between items-center bg-slate-50/30 rounded-t-lg">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <div className={`p-1.5 rounded-lg ${isPositive ? 'bg-emerald-100 text-emerald-600' : 'bg-rose-100 text-rose-600'}`}>
                            {isPositive ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
                        </div>
                        <h3 className="text-lg font-bold text-slate-800">Portfolio Performance</h3>
                    </div>

                    <div className="hidden sm:flex bg-slate-100 p-1 rounded-lg">
                        {['1D', '1W', '1M', '3M', '1Y', 'ALL'].map(tf => (
                            <button
                                key={tf}
                                onClick={() => setTimeframe(tf)}
                                className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${timeframe === tf ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                            >
                                {tf}
                            </button>
                        ))}
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <span className={`text-sm font-bold ${isPositive ? 'text-emerald-600' : 'text-rose-600'}`}>
                        {isPositive ? '+' : ''}{periodChange}%
                    </span>
                    <button className="text-slate-400 hover:text-indigo-600 transition-colors p-1">
                        <Maximize2 size={16} />
                    </button>
                </div>
            </div>

            {/* Chart Area */}
            <div className="flex-1 w-full min-h-[300px] p-4">
                {displayData && displayData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={displayData} margin={{ top: 10, right: 0, left: 0, bottom: 0 }}>
                            <defs>
                                <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={strokeColor} stopOpacity={0.1} />
                                    <stop offset="95%" stopColor={strokeColor} stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid vertical={false} stroke="#f1f5f9" strokeDasharray="3 3" />
                            <XAxis
                                dataKey="timestamp"
                                axisLine={false}
                                tickLine={false}
                                minTickGap={60}
                                tick={{ fill: '#94a3b8', fontSize: 11 }}
                                tickFormatter={(str) => {
                                    if (!str) return '';
                                    const d = new Date(str);
                                    return d.toLocaleDateString();
                                }}
                            />
                            <YAxis
                                domain={['auto', 'auto']}
                                orientation="left"
                                tick={{ fill: '#64748b', fontSize: 11, fontWeight: 500 }}
                                axisLine={false}
                                tickLine={false}
                                tickFormatter={(val) => `$${val.toLocaleString()}`}
                                width={60}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#fff',
                                    borderRadius: '12px',
                                    border: '1px solid #e2e8f0',
                                    boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'
                                }}
                                itemStyle={{ color: '#1e293b', fontSize: '12px', fontWeight: 600 }}
                                labelStyle={{ color: '#64748b', marginBottom: '8px', fontSize: '11px' }}
                                labelFormatter={(label) => new Date(label).toLocaleString()}
                                formatter={(value) => [`$${value.toLocaleString()}`, 'Equity']}
                            />
                            <Area
                                type="monotone"
                                dataKey="equity"
                                stroke={strokeColor}
                                strokeWidth={3}
                                fill="url(#colorEquity)"
                                activeDot={{ r: 6, strokeWidth: 0, fill: strokeColor }}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="flex items-center justify-center h-full text-slate-400 text-sm">
                        No portfolio history available
                    </div>
                )}
            </div>
        </div>
    );
};

export default PortfolioChart;
