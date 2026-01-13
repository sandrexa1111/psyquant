import React from 'react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';
import StockLogo from '../common/StockLogo';

const MetricCard = ({ title, value, change, changeLabel, data, type = 'neutral', symbol = null }) => {
    const isPositive = change >= 0;

    // Determine colors
    const trendColor = isPositive ? 'text-emerald-500' : 'text-rose-500';
    const chartColor = isPositive ? '#10b981' : '#f43f5e';
    const bgTrend = isPositive ? 'bg-emerald-50' : 'bg-rose-50';

    return (
        <div className="bg-white rounded-xl p-6 shadow-[0_2px_10px_-4px_rgba(0,0,0,0.05)] border border-slate-100 h-full flex flex-col justify-between hover:shadow-lg transition-shadow duration-300">
            <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                    {symbol ? (
                        <StockLogo symbol={symbol} size={42} />
                    ) : (
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${type === 'neutral' ? 'bg-blue-50 text-blue-600' : bgTrend}`}>
                            <span className="font-bold text-xs">{title.substring(0, 2)}</span>
                        </div>
                    )}
                    <div>
                        <h3 className="text-slate-500 font-medium text-xs uppercase tracking-wider">{symbol || title}</h3>
                        {symbol && <div className="text-xs text-slate-400">{title}</div>}
                    </div>
                </div>

                <div className={`flex items-center text-xs font-bold px-2 py-1 rounded-full ${bgTrend} ${trendColor}`}>
                    {isPositive ? <ArrowUpRight size={14} className="mr-1" /> : <ArrowDownRight size={14} className="mr-1" />}
                    {Math.abs(change).toFixed(2)}%
                </div>
            </div>

            <div className="flex items-end justify-between">
                <div>
                    <div className="text-2xl font-bold text-slate-800 tracking-tight">{value}</div>
                    <p className="text-xs text-slate-400 mt-1">{changeLabel}</p>
                </div>

                {data && data.length > 0 && (
                    <div className="w-20 h-10">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data}>
                                <Area
                                    type="monotone"
                                    dataKey="value"
                                    stroke={chartColor}
                                    fill={chartColor}
                                    fillOpacity={0.1}
                                    strokeWidth={2}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MetricCard;
