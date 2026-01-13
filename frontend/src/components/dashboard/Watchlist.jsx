import React, { useState, useEffect } from 'react';
import { ArrowUpRight, ArrowDownRight, Plus, Search, X, Loader2 } from 'lucide-react';
import StockLogo from '../common/StockLogo';
import { getMarketData } from '../../services/api';

// Initial default list
const DEFAULT_SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMD', 'AMZN'];

// Map for names (since API might not return full name in market-data)
const NAME_MAP = {
    'SPY': 'SPDR S&P 500 ETF',
    'QQQ': 'Invesco QQQ Trust',
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corp.',
    'NVDA': 'NVIDIA Corp.',
    'TSLA': 'Tesla, Inc.',
    'AMD': 'Adv. Micro Devices',
    'AMZN': 'Amazon.com',
    'GOOGL': 'Alphabet Inc.',
    'META': 'Meta Platforms'
};

const Watchlist = ({ onSelect }) => {
    const [watchlist, setWatchlist] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [isAdding, setIsAdding] = useState(false);
    const [newSymbol, setNewSymbol] = useState('');
    const [addingLoading, setAddingLoading] = useState(false);

    const fetchWatchlistData = async (symbols) => {
        try {
            const promises = symbols.map(sym => getMarketData(sym).catch(e => null));
            const results = await Promise.all(promises);

            const processedData = results.map((res, index) => {
                if (!res || !res.data || res.data.length === 0) return null;

                const candles = res.data;
                const lastCandle = candles[candles.length - 1];
                const firstCandle = candles[0];

                const price = lastCandle.close;
                const change = ((price - firstCandle.open) / firstCandle.open) * 100;

                return {
                    symbol: res.symbol,
                    name: NAME_MAP[res.symbol] || res.symbol,
                    price: price,
                    change: change,
                    shares: 0 // Placeholder as we don't have position data mapped here yet
                };
            }).filter(item => item !== null);

            setWatchlist(processedData);
        } catch (error) {
            console.error("Failed to fetch watchlist", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchWatchlistData(DEFAULT_SYMBOLS);

        // Refresh every minute
        const interval = setInterval(() => {
            const symbols = watchlist.length > 0 ? watchlist.map(w => w.symbol) : DEFAULT_SYMBOLS;
            fetchWatchlistData(symbols);
        }, 60000);

        return () => clearInterval(interval);
    }, []);

    const handleAddStock = async () => {
        if (!newSymbol) return;
        setAddingLoading(true);
        try {
            const res = await getMarketData(newSymbol.toUpperCase());
            if (res && res.data && res.data.length > 0) {
                const candles = res.data;
                const lastCandle = candles[candles.length - 1];
                const firstCandle = candles[0];
                const price = lastCandle.close;
                const change = ((price - firstCandle.open) / firstCandle.open) * 100;

                const newItem = {
                    symbol: res.symbol,
                    name: NAME_MAP[res.symbol] || res.symbol,
                    price: price,
                    change: change,
                    shares: 0
                };

                setWatchlist(prev => [...prev, newItem]);
                setIsAdding(false);
                setNewSymbol('');
            }
        } catch (error) {
            console.error("Could not add stock", error);
            // Optionally show error toast
        } finally {
            setAddingLoading(false);
        }
    };

    const displayList = watchlist.filter(item =>
        item.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm h-full flex flex-col">
            <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50 rounded-t-xl">
                <h3 className="font-bold text-slate-800 text-lg">Watchlist</h3>
                <button
                    onClick={() => setIsAdding(!isAdding)}
                    className="p-1.5 rounded-lg bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors"
                >
                    <Plus size={18} />
                </button>
            </div>

            {isAdding && (
                <div className="p-4 border-b border-slate-100 bg-slate-50 animate-in slide-in-from-top-2">
                    <div className="relative flex gap-2">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                            <input
                                type="text"
                                placeholder="Add symbol (e.g. GOOGL)..."
                                className="w-full pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                                autoFocus
                                value={newSymbol}
                                onChange={(e) => setNewSymbol(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAddStock()}
                            />
                        </div>
                        <button
                            onClick={() => setIsAdding(false)}
                            className="p-2 text-slate-400 hover:text-slate-600"
                        >
                            <X size={18} />
                        </button>
                    </div>
                    {addingLoading && <div className="text-xs text-indigo-500 mt-2">Checking symbol...</div>}
                </div>
            )}

            <div className="flex-1 overflow-auto p-4 space-y-3">
                {loading ? (
                    <div className="flex justify-center items-center h-40">
                        <Loader2 className="animate-spin text-indigo-500" />
                    </div>
                ) : (
                    displayList.map((stock) => {
                        const isPositive = stock.change >= 0;
                        return (
                            <div
                                key={stock.symbol}
                                onClick={() => onSelect && onSelect(stock.symbol)}
                                className="bg-white border border-slate-200 rounded-xl p-4 hover:shadow-md hover:border-indigo-100 transition-all cursor-pointer group relative"
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex items-center gap-3">
                                        <StockLogo symbol={stock.symbol} size={40} />
                                        <div>
                                            <h4 className="font-bold text-slate-900">{stock.symbol}</h4>
                                            <p className="text-xs text-slate-500 font-medium truncate max-w-[100px]">{stock.name}</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="font-mono font-bold text-slate-800">${stock.price.toFixed(2)}</div>
                                        <div className={`flex items-center justify-end text-xs font-bold ${isPositive ? 'text-emerald-600' : 'text-rose-600'}`}>
                                            {isPositive ? <ArrowUpRight size={12} className="mr-0.5" /> : <ArrowDownRight size={12} className="mr-0.5" />}
                                            {Math.abs(stock.change).toFixed(2)}%
                                        </div>
                                    </div>
                                </div>

                                {/* Actions overlay on hover */}
                                <div className="mt-3 pt-3 border-t border-slate-50 flex justify-between items-center">
                                    <span className="text-xs text-slate-400 font-medium bg-slate-50 px-2 py-0.5 rounded">
                                        {stock.shares > 0 ? `${stock.shares} Shares` : 'Watching'}
                                    </span>
                                    <div className="flex gap-2 opacity-100 sm:opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button
                                            className="text-xs font-semibold bg-indigo-50 text-indigo-600 px-3 py-1.5 rounded-md hover:bg-indigo-100"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                // Trigger trade
                                            }}
                                        >
                                            Trade
                                        </button>
                                    </div>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
};

export default Watchlist;
