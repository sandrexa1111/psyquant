import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const PortfolioWidgets = ({ positions }) => {
    // Process positions for allocation chart
    const data = positions.map(p => ({
        name: p.symbol,
        value: p.market_value || (p.qty * p.current_price)
    }));

    // Add Cash if we had account data passed in, but for now just positions
    // Sort by value
    data.sort((a, b) => b.value - a.value);

    const COLORS = ['#6366F1', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B', '#64748B'];

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 h-full flex flex-col">
            <h3 className="font-bold text-slate-800 mb-4">Asset Allocation</h3>

            {data.length > 0 ? (
                <div className="flex-1 min-h-[200px] flex items-center justify-center relative">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} strokeWidth={0} />
                                ))}
                            </Pie>
                            <Tooltip
                                formatter={(value) => `$${value.toFixed(2)}`}
                                contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                    {/* Center Text */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                        <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Total</span>
                        <span className="text-xl font-bold text-slate-800">{data.length} Assets</span>
                    </div>
                </div>
            ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-slate-400 text-sm min-h-[200px]">
                    <div className="w-24 h-24 rounded-full border-4 border-slate-100 mb-2 border-t-indigo-100 flex items-center justify-center">
                        <div className="w-16 h-16 rounded-full bg-slate-50"></div>
                    </div>
                    No assets held
                </div>
            )}

            {/* Legend */}
            <div className="mt-4 grid grid-cols-2 gap-2">
                {data.slice(0, 4).map((entry, index) => (
                    <div key={entry.name} className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }}></span>
                            <span className="text-slate-600 font-medium">{entry.name}</span>
                        </div>
                        <span className="text-slate-400">{((entry.value / data.reduce((a, b) => a + b.value, 0)) * 100).toFixed(0)}%</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PortfolioWidgets;
