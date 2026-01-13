import React, { useEffect, useState } from 'react';
import MainLayout from '../components/layout/MainLayout';
import MetricCard from '../components/dashboard/MetricCard';
import PortfolioChart from '../components/dashboard/PortfolioChart';
import TransactionsTable from '../components/dashboard/TransactionsTable';
import PortfolioWidgets from '../components/dashboard/PortfolioWidgets';
import Watchlist from '../components/dashboard/Watchlist';
import FloatingCoach from '../components/ai/FloatingCoach';
import { getAccount, getPositions, getMarketData, getHistory } from '../services/api';
import { Loader2, Zap } from 'lucide-react';

const Dashboard = () => {
    const [selectedSymbol, setSelectedSymbol] = useState('SPY');
    const [loading, setLoading] = useState(true);
    const [account, setAccount] = useState(null);
    const [positions, setPositions] = useState([]);
    const [marketData, setMarketData] = useState([]);
    const [history, setHistory] = useState([]);
    const [error, setError] = useState(null);

    // Fetch data when component mounts or symbol changes
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [accData, posData, mktData, histData] = await Promise.all([
                    getAccount(),
                    getPositions(),
                    getMarketData(selectedSymbol),
                    getHistory()
                ]);

                setAccount(accData);
                setPositions(posData);
                setMarketData(mktData.data);
                setHistory(histData);
            } catch (err) {
                console.error("Failed to fetch dashboard data:", err);
                setError("Failed to load dashboard data. Ensure backend is running.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, [selectedSymbol]);

    if (loading) return <div className="min-h-screen flex items-center justify-center bg-slate-50"><Loader2 className="animate-spin text-indigo-600" size={32} /></div>;
    if (error) return <div className="p-8 text-center text-red-500">{error}</div>;

    // Calculations
    const totalPL = positions.reduce((acc, p) => acc + p.unrealized_pl, 0);
    const totalPLPC = account?.portfolio_value ? (totalPL / account.portfolio_value) * 100 : 0;
    const historyData = history.map(h => ({ value: h.equity }));

    return (
        <MainLayout>
            <FloatingCoach />

            {/* Header (Simplified) */}
            <div className="flex justify-between items-end mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Overview</h1>
                    <p className="text-slate-500 text-sm">Welcome back, Alina</p>
                </div>
                <div className="flex gap-3">
                    <button className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors shadow-sm">
                        <Zap size={16} className="text-yellow-300" />
                        Execute Trade
                    </button>
                </div>
            </div>

            {/* Metric Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
                <MetricCard
                    title="Buying Power"
                    value={account?.buying_power ? `$${account.buying_power.toLocaleString()}` : '$0'}
                    change={0.00}
                    changeLabel="Stable"
                    type="neutral"
                    symbol="USD"
                />
                <MetricCard
                    title="Portfolio Value"
                    value={account?.portfolio_value ? `$${account.portfolio_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '$0.00'}
                    change={totalPLPC}
                    changeLabel="Total Return"
                    data={historyData}
                    symbol="PORT"
                />
                <MetricCard
                    title="Unrealized P/L"
                    value={`$${totalPL.toFixed(2)}`}
                    change={totalPLPC}
                    changeLabel="Open Positions"
                    data={historyData}
                    type={totalPL >= 0 ? 'success' : 'danger'}
                    variant='highlight'
                />
                <MetricCard
                    title="Day Trades"
                    value={account?.daytrade_count}
                    change={0}
                    changeLabel="Remaining: Unlimited"
                    type="neutral"
                />
            </div>

            {/* Main Layout Grid (12 Columns) */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8 h-[calc(100vh-340px)] min-h-[800px]">

                {/* LEFT COLUMN (Analytics & Charts) */}
                <div className="md:col-span-12 xl:col-span-8 flex flex-col gap-8 h-full">
                    {/* Market Chart (Fixed Height) */}
                    <div className="h-[500px] flex-shrink-0">
                        <PortfolioChart
                            data={history.map(h => ({
                                timestamp: h.timestamp,
                                equity: h.equity
                            }))}
                            periodChange={totalPLPC.toFixed(2)}
                        />
                    </div>

                    {/* New Widgets Area */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 flex-1">
                        <PortfolioWidgets positions={positions} />
                        {/* Placeholder for another widget */}
                        <div className="bg-gradient-to-br from-indigo-600 to-violet-700 rounded-xl p-6 text-white shadow-lg flex flex-col justify-between">
                            <div>
                                <h3 className="text-indigo-100 font-medium mb-1">Weekly Performance</h3>
                                <div className="text-3xl font-bold">+4.2%</div>
                                <p className="text-xs text-indigo-200 mt-2">Outperforming SPY by 1.8%</p>
                            </div>
                            <div className="h-32 bg-white/10 rounded-lg mt-4 flex items-center justify-center border border-white/10">
                                <span className="text-xs text-indigo-200">Processing AI Insights...</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* RIGHT COLUMN (Watchlist & Activity) */}
                <div className="md:col-span-12 xl:col-span-4 flex flex-col gap-8 h-full">
                    {/* Watchlist */}
                    <div className="h-[450px] flex-shrink-0">
                        <Watchlist onSelect={setSelectedSymbol} />
                    </div>

                    {/* Latest Transactions (Scrollable) */}
                    <div className="flex-1 min-h-[300px]">
                        <TransactionsTable onSelect={setSelectedSymbol} />
                    </div>
                </div>
            </div>
        </MainLayout>
    );
};

export default Dashboard;
