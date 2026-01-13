import React, { useState } from 'react';

// Common stock to domain mapping for logo fetching
const TICKER_DOMAINS = {
    AAPL: 'apple.com',
    MSFT: 'microsoft.com',
    GOOGL: 'abc.xyz',
    GOOG: 'abc.xyz',
    AMZN: 'amazon.com',
    TSLA: 'tesla.com',
    NVDA: 'nvidia.com',
    META: 'meta.com',
    NFLX: 'netflix.com',
    AMD: 'amd.com',
    INTC: 'intel.com',
    CRM: 'salesforce.com',
    ADBE: 'adobe.com',
    PYPL: 'paypal.com',
    SQ: 'block.xyz',
    COIN: 'coinbase.com',
    HOOD: 'robinhood.com',
    SPY: 'state street', // Hard to get generic ETF logos, might fail
    QQQ: 'invesco.com',
    IWM: 'ishares.com'
};

const StockLogo = ({ symbol, size = 40, className = "" }) => {
    const [error, setError] = useState(false);
    const s = symbol?.toUpperCase();
    const domain = TICKER_DOMAINS[s];

    // Colors for fallback avatars
    const colors = [
        'bg-blue-500', 'bg-emerald-500', 'bg-indigo-500',
        'bg-violet-500', 'bg-rose-500', 'bg-amber-500', 'bg-cyan-500'
    ];
    // Deterministic color based on symbol char code
    const colorIndex = s ? s.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length : 0;
    const bgColor = colors[colorIndex];

    if (domain && !error) {
        return (
            <img
                src={`https://logo.clearbit.com/${domain}`}
                alt={symbol}
                style={{ width: size, height: size }}
                className={`rounded-full object-contain bg-white shadow-sm border border-slate-100 ${className}`}
                onError={() => setError(true)}
            />
        );
    }

    return (
        <div
            style={{ width: size, height: size }}
            className={`rounded-full flex items-center justify-center text-white font-bold text-xs shadow-sm ${bgColor} ${className}`}
        >
            {s ? s.substring(0, 2) : '?'}
        </div>
    );
};

export default StockLogo;
