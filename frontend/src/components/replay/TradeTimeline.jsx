import React from 'react';
import { CheckCircle, XCircle, Clock } from 'lucide-react';

const TradeTimeline = ({ trades, onSelectTrade, selectedId }) => {
    return (
        <div className="flex gap-4 overflow-x-auto pb-4 px-1 custom-scrollbar">
            {trades.map((trade) => {
                const isWin = trade.profit_loss >= 0; // Assuming we have PL
                // For now, mocking PL logic based on random if not present
                const pnl = trade.filled_avg_price ? (trade.side === 'buy' ? 10 : -10) : 0;
                const isSelected = trade.id === selectedId;

                return (
                    <div
                        key={trade.id}
                        onClick={() => onSelectTrade(trade)}
                        className={`flex-shrink-0 w-48 p-3 rounded-xl border cursor-pointer transition-all ${isSelected
                                ? 'border-indigo-500 bg-indigo-50 shadow-md ring-2 ring-indigo-200'
                                : 'border-slate-200 bg-white hover:border-slate-300'
                            }`}
                    >
                        <div className="flex justify-between items-start mb-2">
                            <span className="font-bold text-slate-700">{trade.symbol}</span>
                            {/* Mock Win/Loss Icon */}
                            {trade.side === 'buy'
                                ? <CheckCircle size={16} className="text-emerald-500" />
                                : <XCircle size={16} className="text-rose-500" />
                            }
                        </div>
                        <div className="text-xs text-slate-500 mb-1 flex items-center gap-1">
                            <Clock size={12} />
                            {new Date(trade.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                        <div className="flex justify-between items-end mt-2">
                            <span className={`text-xs font-bold uppercase px-2 py-0.5 rounded ${trade.side === 'buy' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                                {trade.side}
                            </span>
                            <span className="text-sm font-mono font-bold text-slate-800">
                                ${trade.filled_avg_price?.toFixed(2)}
                            </span>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

export default TradeTimeline;
