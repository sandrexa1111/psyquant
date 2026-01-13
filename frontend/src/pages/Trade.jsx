import React, { useEffect, useState } from 'react';
import MainLayout from '../components/layout/MainLayout';
import OrderTicket from '../components/trade/OrderTicket';
import ActiveOrderBook from '../components/trade/ActiveOrderBook';
import AlgoControl from '../components/trade/AlgoControl';
import { submitOrder, getOrders } from '../services/api';
import { ShieldAlert, AlertTriangle, X } from 'lucide-react';

const Trade = () => {
    const [orders, setOrders] = useState([]);
    const [history, setHistory] = useState([]);
    const [showHistory, setShowHistory] = useState(false);
    const [blockModal, setBlockModal] = useState({ isOpen: false, data: null, type: null });

    // Auto-refresh hook
    useEffect(() => {
        const refreshOrders = async () => {
            try {
                // Fetch 'open' active orders
                const activeData = await getOrders('open');
                setOrders(activeData);

                // Fetch 'closed' history if tab is open
                if (showHistory) {
                    const historyData = await getOrders('closed');
                    setHistory(historyData);
                }
            } catch (error) {
                console.error("Failed to load orders", error);
            }
        };

        refreshOrders();
        const interval = setInterval(refreshOrders, 2000);
        return () => clearInterval(interval);
    }, [showHistory]);

    const handleOrderSubmit = async (orderData) => {
        try {
            await submitOrder(orderData);
            // Implicit refresh via interval or could force here if extracted
        } catch (error) {
            if (error.response) {
                const status = error.response.status;
                const data = error.response.data?.detail;

                if (status === 403 && data?.code === 'RISK_FIREWALL_BLOCK') {
                    setBlockModal({ isOpen: true, data: data, type: 'critical' });
                } else if (status === 400 && data?.code === 'STRATEGY_MISMATCH') {
                    setBlockModal({ isOpen: true, data: data, type: 'warning' });
                } else {
                    alert(`Order failed: ${data?.detail || error.message}`);
                }
            } else {
                alert(`Order failed: ${error.message}`);
            }
        }
    };

    const handleOverride = async () => {
        if (!blockModal.data) return;

        // This logic mimics re-submission with override. 
        // In a real app, we'd pass the original order data again with override flags.
        // For this demo, we'll just alert the user (since we don't have the original orderData stored easily without refactoring)
        // To fix this properly, we should refactor handleOrderSubmit to store pendingOrder state.
        alert("Please resubmit the order with override (Logic to be linked to OrderTicket)");
        setBlockModal({ isOpen: false, data: null, type: null });
    };

    return (
        <MainLayout>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-slate-800">Active Trader</h1>
                <p className="text-slate-500 mt-1">Live simulation execution environment.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left: Order Ticket */}
                <div className="lg:col-span-1 space-y-6">
                    <OrderTicket onSubmit={handleOrderSubmit} />
                    <AlgoControl />

                    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
                        <h4 className="font-bold text-slate-600 text-sm mb-2">Paper Trading Mode</h4>
                        <p className="text-xs text-slate-500 leading-relaxed">
                            Orders are executed against real-time market data in a simulated environment.
                            Uses limit/market orders with TIF Day.
                        </p>
                    </div>
                </div>

                {/* Right: Order Book & History */}
                <div className="lg:col-span-2">
                    <ActiveOrderBook
                        orders={orders}
                        history={history}
                        showHistory={showHistory}
                        onToggleHistory={setShowHistory}
                    />
                </div>
            </div>

            {/* Risk Firewall Modal */}
            {blockModal.isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
                    <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden animate-in fade-in zoom-in duration-200">
                        <div className={`p-6 ${blockModal.type === 'critical' ? 'bg-red-50' : 'bg-amber-50'} border-b ${blockModal.type === 'critical' ? 'border-red-100' : 'border-amber-100'}`}>
                            <div className="flex items-center gap-3">
                                {blockModal.type === 'critical' ? (
                                    <ShieldAlert className="w-8 h-8 text-red-600" />
                                ) : (
                                    <AlertTriangle className="w-8 h-8 text-amber-600" />
                                )}
                                <div>
                                    <h3 className={`text-lg font-bold ${blockModal.type === 'critical' ? 'text-red-900' : 'text-amber-900'}`}>
                                        {blockModal.type === 'critical' ? 'Risk Firewall Triggered' : 'Strategy Mismatch'}
                                    </h3>
                                    <p className={`text-sm ${blockModal.type === 'critical' ? 'text-red-700' : 'text-amber-700'}`}>
                                        AI Protection System
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="p-6 space-y-4">
                            <p className="text-slate-700 leading-relaxed">
                                {blockModal.data.message}
                            </p>

                            <div className="bg-slate-50 rounded-lg p-3 text-sm space-y-2">
                                {blockModal.data.risk_score && (
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">Risk Score:</span>
                                        <span className="font-bold text-red-600">{blockModal.data.risk_score}/100</span>
                                    </div>
                                )}
                                {blockModal.data.compatibility_score && (
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">Compatibility:</span>
                                        <span className="font-bold text-amber-600">{blockModal.data.compatibility_score}%</span>
                                    </div>
                                )}
                                {blockModal.data.reason && (
                                    <div className="border-t border-slate-200 pt-2 mt-2">
                                        <span className="block text-xs uppercase tracking-wider text-slate-400 mb-1">Reason</span>
                                        <span className="text-slate-700">{blockModal.data.reason}</span>
                                    </div>
                                )}
                            </div>

                            <p className="text-xs text-slate-400 italic text-center">
                                "The best traders know when NOT to trade."
                            </p>
                        </div>

                        <div className="p-4 bg-slate-50 flex gap-3 justify-end border-t border-slate-100">
                            <button
                                onClick={() => setBlockModal({ ...blockModal, isOpen: false })}
                                className="px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 font-medium transition-colors"
                            >
                                Acknowledge & Stop
                            </button>
                            {/* Override button could go here if we implemented the callback */}
                        </div>
                    </div>
                </div>
            )}
        </MainLayout>
    );
};

export default Trade;
