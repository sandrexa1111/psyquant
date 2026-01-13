import React, { useEffect, useState } from 'react';
import MainLayout from '../components/layout/MainLayout';
import NewsFeed from '../components/market/NewsFeed';
import StockScreener from '../components/market/StockScreener';
import InteractiveChart from '../components/dashboard/InteractiveChart';
import IndicatorChart from '../components/dashboard/IndicatorChart';
import { getNews, getScreener, getChartData } from '../services/api';
import { Loader2, Search } from 'lucide-react';

const Market = () => {
    const [news, setNews] = useState([]);
    const [screenerData, setScreenerData] = useState([]);
    const [chartData, setChartData] = useState(null); // New state
    const [loading, setLoading] = useState(true);
    const [symbol, setSymbol] = useState('SPY');
    const [searchInput, setSearchInput] = useState('');

    useEffect(() => {
        let interval;

        const fetchData = async () => {
            // First load full loading state
            // subsequent updates silent
            try {
                const [newsData, screenData, chartD] = await Promise.all([
                    getNews(symbol),
                    getScreener(),
                    getChartData(symbol)
                ]);
                setNews(newsData);
                setScreenerData(screenData);
                setChartData(chartD);
            } catch (error) {
                console.error("Failed to fetch market data", error);
            } finally {
                setLoading(false);
            }
        };

        setLoading(true);
        fetchData();

        // Poll every 5 seconds for "Live" charts
        interval = setInterval(async () => {
            try {
                const chartD = await getChartData(symbol);
                setChartData(chartD);
            } catch (e) { console.log("Polling error", e); }
        }, 5000);

        return () => clearInterval(interval);
    }, [symbol]);

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchInput.trim()) {
            setSymbol(searchInput.toUpperCase());
            setSearchInput('');
        }
    };

    return (
        <MainLayout>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-slate-800">Market Intelligence</h1>
                <p className="text-slate-500 mt-1">Real-time news coverage and discovery.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: News */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Search Bar for News */}
                    <form onSubmit={handleSearch} className="flex gap-2">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                            <input
                                type="text"
                                placeholder="Search news (e.g., AAPL, TSLA)..."
                                value={searchInput}
                                onChange={(e) => setSearchInput(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                            />
                        </div>
                        <button type="submit" className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors">
                            Search
                        </button>
                    </form>

                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-bold text-slate-700">Headlines: <span className="text-blue-600">{symbol}</span></h2>
                    </div>

                    {loading ? (
                        <div className="h-48 flex items-center justify-center">
                            <Loader2 className="animate-spin text-slate-400" size={32} />
                        </div>
                    ) : (
                        <>
                            {/* Chart Section */}
                            {chartData && (
                                <div className="space-y-4">
                                    <InteractiveChart data={chartData} />
                                    {/* Indicators Grid */}
                                    {chartData.indicators && (
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {/* RSI Pane */}
                                            {chartData.indicators.rsi && (
                                                <IndicatorChart
                                                    data={chartData.indicators.rsi}
                                                    type="RSI (14)"
                                                    color="#8b5cf6"
                                                />
                                            )}
                                            {/* MACD Pane - Visualizing Histogram */}
                                            {chartData.indicators.macd_hist && (
                                                <IndicatorChart
                                                    data={chartData.indicators.macd_hist}
                                                    type="MACD Histogram"
                                                    color="#f59e0b" // Amber
                                                />
                                            )}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* News Section */}
                            <NewsFeed news={news} />
                        </>
                    )}
                </div>

                {/* Right Column: Screener */}
                <div className="space-y-6">
                    <StockScreener data={screenerData} />

                    <div className="bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl p-6 text-white shadow-lg">
                        <h3 className="font-bold text-lg mb-2">Alpha Discovery</h3>
                        <p className="text-indigo-100 text-sm mb-4">
                            Upgrade to Pro to filter by custom indicators, sector performance, and AI-predicted breakout signals.
                        </p>
                        <button className="w-full py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-sm font-semibold transition-colors">
                            Unlock Pro Filters
                        </button>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
};

export default Market;
