import React, { useState, useEffect } from 'react';
import { getOrders } from '../../services/api';
import StockLogo from '../common/StockLogo';
import { Download, Filter, ArrowUpRight, ArrowDownRight, Clock, CheckCircle2, XCircle } from 'lucide-react';

const TransactionsTable = ({ onSelect }) => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchOrders = async () => {
            try {
                // Fetch all orders
                const data = await getOrders('all');
                setOrders(data);
            } catch (error) {
                console.error("Failed to fetch orders", error);
            } finally {
                setLoading(false);
            }
        };
        fetchOrders();
    }, []);

    const getStatusBadge = (status) => {
        switch (status) {
            case 'filled':
                return <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700"><CheckCircle2 size={12} /> Completed</span>;
            case 'canceled':
                return <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600"><XCircle size={12} /> Canceled</span>;
            default:
                return <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700"><Clock size={12} /> Pending</span>;
        }
    };

    if (loading) return <div className="p-8 text-center text-slate-400">Loading transactions...</div>;

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden h-full flex flex-col">
            <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                <h3 className="font-bold text-slate-800 text-lg">Latest Transactions</h3>
                <div className="flex gap-2">
                    <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
                        <Filter size={14} /> Filter
                    </button>
                    <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
                        <Download size={14} /> Export
                    </button>
                </div>
            </div>

            <div className="overflow-auto flex-1">
                <table className="w-full text-left border-collapse">
                    <thead className="bg-slate-50 sticky top-0 z-10">
                        <tr className="text-xs font-semibold text-slate-500 uppercase border-b border-slate-200">
                            <th className="py-3 px-6">Asset</th>
                            <th className="py-3 px-6">Type</th>
                            <th className="py-3 px-6 text-right">Price</th>
                            <th className="py-3 px-6 text-right">Qty</th>
                            <th className="py-3 px-6 text-right">Total</th>
                            <th className="py-3 px-6">Status</th>
                            <th className="py-3 px-6 text-right">Date</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-sm">
                        {orders.map((order) => {
                            const isBuy = order.side === 'buy';
                            const total = order.filled_qty * order.filled_avg_price || 0;
                            // Mock date if needed
                            const date = new Date(order.created_at || Date.now());

                            return (
                                <tr
                                    key={order.id}
                                    onClick={() => onSelect && onSelect(order.symbol)}
                                    className="hover:bg-indigo-50/30 transition-colors group cursor-pointer"
                                >
                                    <td className="py-3 px-6">
                                        <div className="flex items-center gap-3">
                                            <StockLogo symbol={order.symbol} size={32} />
                                            <div>
                                                <div className="font-bold text-slate-800">{order.symbol}</div>
                                                <div className="text-xs text-slate-400">Stock</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="py-3 px-6">
                                        <span className={`flex items-center gap-1 text-xs font-bold uppercase ${isBuy ? 'text-emerald-600' : 'text-rose-600'}`}>
                                            {isBuy ? <ArrowDownRight size={14} /> : <ArrowUpRight size={14} />}
                                            {order.side}
                                        </span>
                                    </td>
                                    <td className="py-3 px-6 text-right font-mono text-slate-700">
                                        ${(order.filled_avg_price || order.limit_price || 0).toFixed(2)}
                                    </td>
                                    <td className="py-3 px-6 text-right font-mono text-slate-600">
                                        {order.qty}
                                    </td>
                                    <td className="py-3 px-6 text-right font-mono font-medium text-slate-800">
                                        ${total.toFixed(2)}
                                    </td>
                                    <td className="py-3 px-6">
                                        {getStatusBadge(order.status)}
                                    </td>
                                    <td className="py-3 px-6 text-right text-xs text-slate-400">
                                        {date.toLocaleDateString()} <br />
                                        {date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </td>
                                </tr>
                            );
                        })}
                        {orders.length === 0 && (
                            <tr>
                                <td colSpan="7" className="py-12 text-center text-slate-400">
                                    No transaction history found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination Mock */}
            <div className="p-4 border-t border-slate-100 flex justify-between items-center bg-slate-50/50 text-xs text-slate-500">
                <span>Showing 1-{Math.min(10, orders.length)} of {orders.length} transactions</span>
                <div className="flex gap-2">
                    <button className="px-3 py-1 rounded border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-50" disabled>Previous</button>
                    <button className="px-3 py-1 rounded border border-slate-200 bg-white hover:bg-slate-50">Next</button>
                </div>
            </div>
        </div>
    );
};

export default TransactionsTable;
