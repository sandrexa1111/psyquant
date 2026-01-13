import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import MainLayout from '../components/layout/MainLayout';
import TradeTimeline from '../components/replay/TradeTimeline';
import StockChart from '../components/dashboard/StockChart'; // Reuse for now
import { Loader2, ArrowLeft, Bot, Target, AlertTriangle } from 'lucide-react';
// We need an API call to get all orders/activities history to populate timeline
// And one to get specific replay
import { getOrders } from '../services/api';
import axios from 'axios';

const TradeReplay = () => {
    const { id } = useParams();
    const [trades, setTrades] = useState([]);
    const [selectedTrade, setSelectedTrade] = useState(null);
    const [replayData, setReplayData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                // Get all filled orders
                const res = await getOrders('closed'); // 'closed' or 'all' depending on API
                // Filter ensuring they are filled
                const filled = res.filter(o => o.status === 'filled');
                setTrades(filled);

                if (filled.length > 0) {
                    // Default to first or id param
                    setSelectedTrade(filled[0]);
                }
            } catch (err) {
                console.error("Failed history", err);
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, []);

    useEffect(() => {
        if (!selectedTrade) return;

        const fetchReplay = async () => {
            try {
                // Fetch snapshot from backend
                const res = await axios.get(`http://127.0.0.1:8000/trade/${selectedTrade.id}/replay`);
                setReplayData(res.data);
            } catch (err) {
                console.error("No replay data", err);
                setReplayData(null);
            }
        };
        fetchReplay();
    }, [selectedTrade]);

    if (loading) {
        return (
            <MainLayout>
                <div className="h-screen flex items-center justify-center">
                    <Loader2 className="animate-spin text-slate-400" />
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="mb-6">
                <button className="flex items-center text-slate-400 hover:text-slate-600 mb-2 transition-colors">
                    <ArrowLeft size={16} className="mr-1" /> Back to Dashboard
                </button>
                <h1 className="text-2xl font-bold text-slate-900">Trade Replay</h1>
                <p className="text-slate-500 text-sm">Analyze your past decisions to improve future performance.</p>
            </div>

            {/* Timeline */}
            <div className="mb-8 p-4 bg-slate-50 rounded-xl border border-slate-200">
                <h3 className="text-xs font-bold text-slate-400 uppercase mb-3 ml-1">Trade History Session</h3>
                <TradeTimeline
                    trades={trades}
                    selectedId={selectedTrade?.id}
                    onSelectTrade={setSelectedTrade}
                />
            </div>

            {selectedTrade && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main Replay Chart */}
                    <div className="lg:col-span-2 space-y-6">
                        <div className="bg-white p-1 rounded-xl shadow-sm border border-slate-200">
                            <div className="p-4 border-b border-slate-100 flex justify-between items-center">
                                <div>
                                    <h2 className="font-bold text-lg text-slate-800 flex items-center gap-2">
                                        {selectedTrade.symbol}
                                        <span className={`text-xs px-2 py-0.5 rounded uppercase ${selectedTrade.side === 'buy' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                                            {selectedTrade.side}
                                        </span>
                                    </h2>
                                    <span className="text-xs text-slate-400">
                                        Executed at {new Date(selectedTrade.filled_at || selectedTrade.created_at).toLocaleString()}
                                    </span>
                                </div>
                                <div className="text-right">
                                    <div className="text-xl font-mono font-bold text-slate-900">
                                        ${selectedTrade.filled_avg_price?.toFixed(2)}
                                    </div>
                                    <div className="text-xs text-slate-500">Avg Fill Price</div>
                                </div>
                            </div>

                            <div className="h-[400px] p-4 relative">
                                {replayData ? (
                                    <StockChart data={replayData.ohlcv} symbol={selectedTrade.symbol} />
                                ) : (
                                    <div className="h-full flex items-center justify-center text-slate-400 bg-slate-50 rounded">
                                        No Snapshot Data Available
                                    </div>
                                )}

                                {/* Overlay Marker (conceptual) */}
                                {replayData && (
                                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-indigo-600 text-white text-xs px-2 py-1 rounded shadow-lg pointer-events-none">
                                        Entry
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* News Context */}
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                            <h3 className="font-bold text-slate-800 mb-4">News Headlines at Execution</h3>
                            {replayData?.news ? (
                                <div className="space-y-3">
                                    {replayData.news.map((item, i) => (
                                        <div key={i} className="flex gap-3">
                                            <div className="text-xs font-mono text-slate-400 pt-0.5">{item.time}</div>
                                            <div>
                                                <p className="text-sm font-medium text-slate-700">{item.headline}</p>
                                                <span className="text-xs text-slate-400">{item.source}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-sm text-slate-400">No news context captured.</p>
                            )}
                        </div>
                    </div>

                    {/* AI Analysis Side Panel */}
                    <div className="space-y-6">
                        <div className="bg-indigo-50 border border-indigo-100 p-6 rounded-xl relative overflow-hidden">
                            <div className="absolute top-0 right-0 p-4 opacity-10">
                                <Bot size={100} className="text-indigo-600" />
                            </div>
                            <h3 className="flex items-center gap-2 font-bold text-indigo-900 mb-4 relative z-10">
                                <Bot size={20} /> AI Post-Trade Analysis
                            </h3>

                            <div className="space-y-4 relative z-10">
                                <section>
                                    <h4 className="text-xs font-bold text-indigo-400 uppercase mb-1">Why This Trade?</h4>
                                    <p className="text-sm text-indigo-800 leading-relaxed">
                                        You entered <strong>{selectedTrade.symbol}</strong> during a volatility spike.
                                        RSI was at {replayData?.indicators?.rsi.toFixed(0) || 'Unknown'}, indicating potential overuse.
                                    </p>
                                </section>

                                <section>
                                    <h4 className="text-xs font-bold text-indigo-400 uppercase mb-1">Pattern Match</h4>
                                    <div className="flex items-center gap-2 text-sm text-indigo-800">
                                        <AlertTriangle size={14} className="text-amber-500" />
                                        <span>Matches your "FOMO Entry" pattern.</span>
                                    </div>
                                </section>

                                <section>
                                    <h4 className="text-xs font-bold text-indigo-400 uppercase mb-1">Recommendation</h4>
                                    <p className="text-sm text-indigo-800">
                                        Next time, wait for a 5-min candle close above resistance before entering.
                                    </p>
                                </section>
                            </div>

                            <button className="mt-6 w-full py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-100 relative z-10">
                                Ask AI Coach About This
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </MainLayout>
    );
};

export default TradeReplay;
