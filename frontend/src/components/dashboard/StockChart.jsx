import React, { useState } from 'react';
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Maximize2 } from 'lucide-react';

const StockChart = ({ data, symbol }) => {
    const [timeframe, setTimeframe] = useState('1D');

    // Filter/Slice data based on timeframe (Mock logic as data is usually pre-fetched)
    const displayData = data;

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 h-full flex flex-col p-2">
            {/* Header */}
            <div className="px-4 py-3 border-b border-slate-100 flex justify-between items-center bg-slate-50/30 rounded-t-lg">
                <div className="flex items-center gap-4">
                    <h3 className="text-lg font-bold text-slate-800 ml-1">{symbol} Analysis</h3>
                    <div className="hidden sm:flex bg-slate-100 p-1 rounded-lg">
                        {['1D', '1W', '1M', '3M', '1Y'].map(tf => (
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
                    <div className="flex items-center gap-2 text-xs">
                        <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                        <span className="text-slate-500 font-medium">Price</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                        <span className="w-2 h-2 rounded-full bg-slate-300"></span>
                        <span className="text-slate-500 font-medium">Vol</span>
                    </div>
                    <button className="text-slate-400 hover:text-indigo-600 transition-colors p-1">
                        <Maximize2 size={16} />
                    </button>
                </div>
            </div>

            {/* Chart Area */}
            <div className="flex-1 w-full min-h-[300px] p-4">
                <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={displayData} margin={{ top: 10, right: 0, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.1} />
                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid vertical={false} stroke="#f1f5f9" strokeDasharray="3 3" />
                        <XAxis
                            dataKey="time"
                            axisLine={false}
                            tickLine={false}
                            minTickGap={60}
                            tick={{ fill: '#94a3b8', fontSize: 11 }}
                            tickFormatter={(str) => {
                                const d = new Date(str);
                                return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                            }}
                        />
                        <YAxis
                            yAxisId="left"
                            domain={['auto', 'auto']}
                            orientation="left"
                            tick={{ fill: '#64748b', fontSize: 11, fontWeight: 500 }}
                            axisLine={false}
                            tickLine={false}
                            tickFormatter={(val) => `$${val.toFixed(0)}`}
                            width={50}
                        />
                        <YAxis
                            yAxisId="right"
                            orientation="right"
                            domain={['0', 'dataMax * 3']} // Push volume bars down
                            hide
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
                        />
                        <Bar
                            yAxisId="right"
                            dataKey="volume"
                            fill="#e2e8f0"
                            radius={[2, 2, 0, 0]}
                            barSize={4}
                        />
                        <Line
                            yAxisId="left"
                            type="monotone"
                            dataKey="close"
                            stroke="#6366f1" // Indigo-500
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 4, strokeWidth: 0, fill: '#6366f1' }}
                        />
                    </ComposedChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default StockChart;
