import React from 'react';
import { Clock, CheckCircle, XCircle } from 'lucide-react';

const ActiveOrderBook = ({ orders, history, showHistory, onToggleHistory }) => {
    const displayOrders = showHistory ? history : orders;

    // Guard against null/undefined
    const safeOrders = displayOrders || [];

    if (!safeOrders || safeOrders.length === 0) {
        return (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-0 overflow-hidden">
                <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex gap-4">
                    <button
                        onClick={() => onToggleHistory(false)}
                        className={`text-sm font-bold ${!showHistory ? 'text-blue-600' : 'text-slate-400 hover:text-slate-600'}`}
                    >
                        Active
                    </button>
                    <span className="text-slate-300">|</span>
                    <button
                        onClick={() => onToggleHistory(true)}
                        className={`text-sm font-bold ${showHistory ? 'text-blue-600' : 'text-slate-400 hover:text-slate-600'}`}
                    >
                        History
                    </button>
                </div>
                <div className="p-8 text-center text-slate-400">
                    <p>No {showHistory ? 'history' : 'active orders'} found</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
                <div className="flex gap-4">
                    <button
                        onClick={() => onToggleHistory(false)}
                        className={`text-sm font-bold ${!showHistory ? 'text-blue-600' : 'text-slate-400 hover:text-slate-600'}`}
                    >
                        Active
                    </button>
                    <span className="text-slate-300">|</span>
                    <button
                        onClick={() => onToggleHistory(true)}
                        className={`text-sm font-bold ${showHistory ? 'text-blue-600' : 'text-slate-400 hover:text-slate-600'}`}
                    >
                        History
                    </button>
                </div>
                <span className="bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full text-xs font-bold">{safeOrders.length}</span>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full min-w-[500px]">
                    <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-bold">
                        <tr>
                            <th className="px-4 py-3 text-left">Symbol</th>
                            <th className="px-4 py-3 text-left">Side</th>
                            <th className="px-4 py-3 text-right">Qty</th>
                            <th className="px-4 py-3 text-left">Type</th>
                            <th className="px-4 py-3 text-left">Status</th>
                            <th className="px-4 py-3 text-right">Time</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {safeOrders.map((order) => (
                            <tr key={order.id} className="hover:bg-slate-50/80 transition-colors">
                                <td className="px-4 py-3 font-bold text-slate-700">{order.symbol}</td>
                                <td className="px-4 py-3">
                                    <span className={`text-xs font-bold uppercase px-2 py-1 rounded-md ${order.side === 'buy' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
                                        }`}>
                                        {order.side}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-right font-mono text-sm">{order.qty}</td>
                                <td className="px-4 py-3 text-xs uppercase text-slate-500">{order.type}</td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-1.5">
                                        {/* Fallback for icons based on status */}
                                        {(() => {
                                            const s = (order?.status || '').toLowerCase();
                                            if (s === 'filled') return <CheckCircle size={14} className="text-emerald-500" />;
                                            if (s === 'canceled') return <XCircle size={14} className="text-slate-400" />;
                                            if (s === 'new' || s === 'accepted') return <Clock size={14} className="text-blue-500" />;
                                            return <Clock size={14} className="text-amber-500" />;
                                        })()}
                                        <span className="text-sm font-medium capitalize text-slate-700">{order.status || 'Unknown'}</span>
                                    </div>
                                </td>
                                <td className="px-4 py-3 text-right text-xs text-slate-400">
                                    {order.created_at ? new Date(order.created_at).toLocaleTimeString() : '-'}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default ActiveOrderBook;
