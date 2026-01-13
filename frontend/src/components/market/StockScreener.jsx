import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

const StockScreener = ({ data }) => {
    if (!data || data.length === 0) return null;

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50/50">
                <h3 className="font-bold text-slate-700">Market Movers (Tech)</h3>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-bold">
                        <tr>
                            <th className="px-4 py-3 text-left">Symbol</th>
                            <th className="px-4 py-3 text-right">Price</th>
                            <th className="px-4 py-3 text-right">Change</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {data.map((stock) => (
                            <tr key={stock.symbol} className="hover:bg-slate-50/80 transition-colors">
                                <td className="px-4 py-3">
                                    <span className="font-bold text-slate-700">{stock.symbol}</span>
                                </td>
                                <td className="px-4 py-3 text-right font-mono text-sm text-slate-600">
                                    ${stock.price.toFixed(2)}
                                </td>
                                <td className="px-4 py-3 text-right">
                                    <div className={`flex items-center justify-end gap-1 ${stock.change >= 0 ? 'text-emerald-600' : 'text-rose-600'
                                        }`}>
                                        {stock.change >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                                        <span className="font-bold text-sm">{Math.abs(stock.change).toFixed(2)}%</span>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default StockScreener;
