import React from 'react';
import { MoreHorizontal } from 'lucide-react';
import StockLogo from '../common/StockLogo';

const PositionsTable = ({ positions }) => {
    if (!positions || positions.length === 0) {
        return (
            <div className="text-center py-12 bg-slate-50 rounded-xl border-dashed border-2 border-slate-200">
                <p className="text-slate-500 mb-2">No Active Positions</p>
                <p className="text-sm text-slate-400">Time to hunt for new opportunities.</p>
            </div>
        );
    }

    return (
        <div className="overflow-x-auto">
            <div className="min-w-full inline-block align-middle">
                <div className="border-hidden rounded-lg">
                    {/* Header */}
                    <div className="grid grid-cols-6 gap-4 px-6 py-3 bg-slate-50/50 text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-100">
                        <div className="col-span-2">Asset Name</div>
                        <div>Date</div>
                        <div>Price</div>
                        <div>Category</div>
                        <div>Status</div>
                    </div>

                    {/* Rows */}
                    <div className="divide-y divide-slate-50">
                        {positions.map((pos) => {
                            const isProfitable = pos.unrealized_pl >= 0;
                            return (
                                <div key={pos.symbol} className="grid grid-cols-6 gap-4 px-6 py-4 items-center hover:bg-slate-50/50 transition-colors group">
                                    {/* Asset Name */}
                                    <div className="col-span-2 flex items-center gap-3">
                                        <StockLogo symbol={pos.symbol} size={36} />
                                        <div>
                                            <div className="font-bold text-slate-800 text-sm">{pos.symbol}</div>
                                            <div className="text-xs text-slate-400">Quantity: {pos.qty}</div>
                                        </div>
                                    </div>

                                    {/* Date (Mocked for now as we don't have entry date in pos object easily, using 'Today') */}
                                    <div className="text-sm text-slate-500 font-medium">
                                        Today, 10:00 AM
                                    </div>

                                    {/* Price */}
                                    <div className="font-mono text-sm font-medium text-slate-800">
                                        ${pos.current_price.toFixed(2)}
                                    </div>

                                    {/* Category (Side) */}
                                    <div>
                                        <span className={`text-xs font-medium px-2 py-1 rounded bg-slate-100 text-slate-600`}>
                                            {pos.side === 'long' ? 'Stock' : 'Short'}
                                        </span>
                                    </div>

                                    {/* Status (P/L) */}
                                    <div className="flex justify-between items-center">
                                        <span className={`text-xs font-bold px-2 py-1 rounded-full ${isProfitable ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                                            {isProfitable ? 'Success' : 'Pending'} {isProfitable ? '+' : ''}{pos.unrealized_plpc ? (pos.unrealized_plpc * 100).toFixed(2) : '0.00'}%
                                        </span>
                                        <button className="text-slate-300 hover:text-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <MoreHorizontal size={16} />
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PositionsTable;
