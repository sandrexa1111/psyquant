import React, { useEffect, useState } from 'react';
import MainLayout from '../components/layout/MainLayout';
import { getStrategyDNA, rebuildStrategyDNA } from '../services/api';
import { Target, TrendingUp, Clock, Zap, RefreshCw, Award, BarChart2, Loader2 } from 'lucide-react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

const StrategyDNA = () => {
    const [loading, setLoading] = useState(true);
    const [rebuilding, setRebuilding] = useState(false);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);

    const fetchStrategyDNA = async () => {
        try {
            const result = await getStrategyDNA();
            setData(result);
        } catch (err) {
            console.error('Failed to fetch strategy DNA:', err);
            setError('Failed to load strategy data');
        } finally {
            setLoading(false);
        }
    };

    const handleRebuild = async () => {
        setRebuilding(true);
        try {
            await rebuildStrategyDNA(3);
            await fetchStrategyDNA();
        } catch (err) {
            console.error('Failed to rebuild:', err);
        } finally {
            setRebuilding(false);
        }
    };

    useEffect(() => {
        fetchStrategyDNA();
    }, []);

    if (loading) {
        return (
            <MainLayout>
                <div className="min-h-screen flex items-center justify-center">
                    <Loader2 className="animate-spin text-indigo-600" size={32} />
                </div>
            </MainLayout>
        );
    }

    const { fingerprints = [], total_strategies = 0 } = data || {};

    const getStyleColor = (style) => {
        const colors = {
            momentum: '#6366f1',
            mean_reversion: '#8b5cf6',
            breakout: '#06b6d4',
            scalping: '#f59e0b',
            swing: '#10b981'
        };
        return colors[style] || '#64748b';
    };

    const getStyleIcon = (style) => {
        switch (style) {
            case 'momentum': return <TrendingUp className="w-5 h-5" />;
            case 'scalping': return <Zap className="w-5 h-5" />;
            case 'swing': return <Clock className="w-5 h-5" />;
            default: return <Target className="w-5 h-5" />;
        }
    };

    const formatHoldTime = (seconds) => {
        if (!seconds) return 'N/A';
        if (seconds < 60) return `${seconds}s`;
        if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
        if (seconds < 86400) return `${Math.round(seconds / 3600)}h`;
        return `${Math.round(seconds / 86400)}d`;
    };

    return (
        <MainLayout>
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Strategy DNA</h1>
                    <p className="text-slate-500">AI-discovered trading strategies from your history</p>
                </div>
                <button
                    onClick={handleRebuild}
                    disabled={rebuilding}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
                >
                    <RefreshCw className={`w-4 h-4 ${rebuilding ? 'animate-spin' : ''}`} />
                    {rebuilding ? 'Analyzing...' : 'Rebuild DNA'}
                </button>
            </div>

            {fingerprints.length === 0 ? (
                <div className="bg-white rounded-2xl shadow-sm p-12 text-center">
                    <Target className="w-16 h-16 mx-auto mb-4 text-slate-300" />
                    <h3 className="text-xl font-semibold text-slate-700 mb-2">No Strategies Found</h3>
                    <p className="text-slate-500 mb-6">
                        Complete more trades to let AI discover your trading patterns
                    </p>
                    <button
                        onClick={handleRebuild}
                        className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
                    >
                        Analyze My Trades
                    </button>
                </div>
            ) : (
                <>
                    {/* Strategy Cards Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
                        {fingerprints.map((fp, index) => (
                            <div
                                key={fp.id || index}
                                className="bg-white rounded-2xl shadow-sm p-6 hover:shadow-md transition-shadow"
                            >
                                {/* Header */}
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <div
                                            className="w-10 h-10 rounded-xl flex items-center justify-center text-white"
                                            style={{ backgroundColor: getStyleColor(fp.entry_style) }}
                                        >
                                            {getStyleIcon(fp.entry_style)}
                                        </div>
                                        <div>
                                            <h3 className="font-semibold text-slate-800">{fp.strategy_name}</h3>
                                            <p className="text-sm text-slate-500 capitalize">{fp.entry_style?.replace('_', ' ')}</p>
                                        </div>
                                    </div>
                                    {index === 0 && (
                                        <span className="flex items-center gap-1 px-2 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-medium">
                                            <Award className="w-3 h-3" /> Best
                                        </span>
                                    )}
                                </div>

                                {/* Stats Grid */}
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    <div className="bg-slate-50 rounded-lg p-3">
                                        <div className="text-sm text-slate-500">Win Rate</div>
                                        <div className={`text-xl font-bold ${fp.win_rate >= 50 ? 'text-emerald-600' : 'text-red-500'}`}>
                                            {(fp.win_rate || 0).toFixed(1)}%
                                        </div>
                                    </div>
                                    <div className="bg-slate-50 rounded-lg p-3">
                                        <div className="text-sm text-slate-500">R:R Ratio</div>
                                        <div className="text-xl font-bold text-slate-800">
                                            {(fp.risk_reward_ratio || 0).toFixed(2)}
                                        </div>
                                    </div>
                                    <div className="bg-slate-50 rounded-lg p-3">
                                        <div className="text-sm text-slate-500">Avg Hold</div>
                                        <div className="text-xl font-bold text-slate-800">
                                            {formatHoldTime(fp.holding_time_avg)}
                                        </div>
                                    </div>
                                    <div className="bg-slate-50 rounded-lg p-3">
                                        <div className="text-sm text-slate-500">Trades</div>
                                        <div className="text-xl font-bold text-slate-800">
                                            {fp.trade_count || 0}
                                        </div>
                                    </div>
                                </div>

                                {/* P/L Summary */}
                                <div className="flex justify-between items-center pt-4 border-t border-slate-100">
                                    <div>
                                        <div className="text-sm text-slate-500">Total P/L</div>
                                        <div className={`text-lg font-bold ${(fp.total_pnl || 0) >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                                            ${(fp.total_pnl || 0).toFixed(2)}
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-sm text-slate-500">Avg P/L</div>
                                        <div className={`text-lg font-bold ${(fp.avg_pnl || 0) >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                                            ${(fp.avg_pnl || 0).toFixed(2)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Performance Comparison */}
                    <div className="bg-white rounded-2xl shadow-sm p-8">
                        <h2 className="text-lg font-semibold text-slate-800 mb-6">Strategy Performance Comparison</h2>

                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={fingerprints} layout="vertical">
                                <XAxis type="number" domain={[0, 100]} />
                                <YAxis
                                    type="category"
                                    dataKey="strategy_name"
                                    width={150}
                                    tick={{ fontSize: 12 }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1e293b',
                                        border: 'none',
                                        borderRadius: '8px',
                                        color: '#fff'
                                    }}
                                    formatter={(value) => [`${value.toFixed(1)}%`, 'Win Rate']}
                                />
                                <Bar dataKey="win_rate" radius={[0, 4, 4, 0]}>
                                    {fingerprints.map((fp, index) => (
                                        <Cell
                                            key={`cell-${index}`}
                                            fill={getStyleColor(fp.entry_style)}
                                        />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Insights */}
                    <div className="mt-8 bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl p-8 text-white">
                        <h2 className="text-lg font-semibold mb-4">🎯 AI Strategy Recommendation</h2>
                        {fingerprints.length > 0 && (
                            <p className="text-indigo-100">
                                Your strongest strategy is <strong>{fingerprints[0]?.strategy_name}</strong> with
                                a <strong>{fingerprints[0]?.win_rate?.toFixed(1)}%</strong> win rate.
                                {fingerprints[0]?.win_rate >= 50
                                    ? ' Focus more trades using this pattern for consistent results.'
                                    : ' Consider refining your entry criteria to improve performance.'}
                            </p>
                        )}
                        {fingerprints.length > 1 && fingerprints[fingerprints.length - 1]?.win_rate < 40 && (
                            <p className="text-indigo-200 mt-3 text-sm">
                                ⚠️ Consider reducing exposure to <strong>{fingerprints[fingerprints.length - 1]?.strategy_name}</strong> which
                                has a lower win rate.
                            </p>
                        )}
                    </div>
                </>
            )}
        </MainLayout>
    );
};

export default StrategyDNA;
