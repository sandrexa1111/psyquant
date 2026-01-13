import React, { useState } from 'react';
import { Loader2, DollarSign } from 'lucide-react';

const OrderTicket = ({ onSubmit }) => {
    const [symbol, setSymbol] = useState('');
    const [qty, setQty] = useState(1);
    const [side, setSide] = useState('buy');
    const [type, setType] = useState('market'); // market calls rarely need price
    const [limitPrice, setLimitPrice] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);

        try {
            const payload = {
                symbol,
                qty: parseFloat(qty),
                side,
                type,
                limit_price: type === 'limit' ? parseFloat(limitPrice) : null
            };

            await onSubmit(payload);
            setMessage({ type: 'success', text: 'Order Submitted Successfully' });
            // Reset form partly
            setQty(1);
        } catch (err) {
            const detail = err.response?.data?.detail;
            const errorText = typeof detail === 'object' ? JSON.stringify(detail) : (detail || err.message);
            setMessage({ type: 'error', text: errorText });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <h3 className="font-bold text-slate-800 mb-4">Order Ticket</h3>

            {message && (
                <div className={`p-3 rounded-lg text-sm mb-4 ${message.type === 'success' ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'
                    }`}>
                    {message.text}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                {/* Symbol & Side */}
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Symbol</label>
                        <input
                            type="text"
                            value={symbol}
                            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                            className="w-full p-2 border border-slate-200 rounded-lg text-sm font-mono font-bold uppercase focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            placeholder="SPY"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Side</label>
                        <div className="flex bg-slate-100 rounded-lg p-1">
                            {['buy', 'sell'].map((s) => (
                                <button
                                    key={s}
                                    type="button"
                                    onClick={() => setSide(s)}
                                    className={`flex-1 py-1.5 text-xs font-bold rounded-md uppercase transition-all ${side === s
                                        ? (s === 'buy' ? 'bg-emerald-500 text-white shadow-sm' : 'bg-rose-500 text-white shadow-sm')
                                        : 'text-slate-500 hover:text-slate-700'
                                        }`}
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Qty & Type */}
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Shares</label>
                        <input
                            type="number"
                            step="any"
                            value={qty}
                            onChange={(e) => setQty(e.target.value)}
                            className="w-full p-2 border border-slate-200 rounded-lg text-sm font-mono focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            min="0.0001"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Order Type</label>
                        <select
                            value={type}
                            onChange={(e) => setType(e.target.value)}
                            className="w-full p-2 border border-slate-200 rounded-lg text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        >
                            <option value="market">Market</option>
                            <option value="limit">Limit</option>
                        </select>
                    </div>
                </div>

                {/* Limit Price */}
                {type === 'limit' && (
                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Limit Price</label>
                        <div className="relative">
                            <DollarSign className="absolute left-2 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
                            <input
                                type="number"
                                step="0.01"
                                value={limitPrice}
                                onChange={(e) => setLimitPrice(e.target.value)}
                                className="w-full pl-8 p-2 border border-slate-200 rounded-lg text-sm font-mono focus:ring-2 focus:ring-blue-500 focus:outline-none"
                                required
                            />
                        </div>
                    </div>
                )}

                <button
                    type="submit"
                    disabled={loading}
                    className={`w-full py-3 rounded-xl font-bold text-white shadow-lg transition-all transform active:scale-95 flex items-center justify-center gap-2 ${side === 'buy' ? 'bg-emerald-500 hover:bg-emerald-600 shadow-emerald-200' : 'bg-rose-500 hover:bg-rose-600 shadow-rose-200'
                        }`}
                >
                    {loading && <Loader2 className="animate-spin" size={18} />}
                    {side === 'buy' ? 'BUY' : 'SELL'} {symbol}
                </button>
            </form>
        </div>
    );
};

export default OrderTicket;
