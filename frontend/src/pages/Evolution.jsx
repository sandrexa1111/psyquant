import React, { useEffect, useState } from 'react';
import MainLayout from '../components/layout/MainLayout';
import { TrendingUp, TrendingDown, Minus, RefreshCw, Calendar, Target, Shield, BarChart3, Clock, Loader2, ChevronDown, Award, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

// Import API functions
const API_BASE = 'http://localhost:8000';

const fetchEvolution = async (periodType = 'weekly', lookbackPeriods = 12) => {
    const response = await fetch(`${API_BASE}/ai/evolution?period_type=${periodType}&lookback_periods=${lookbackPeriods}`);
    return response.json();
};

const fetchImprovement = async (days = 21) => {
    const response = await fetch(`${API_BASE}/ai/improvement?days=${days}`);
    return response.json();
};

const fetchStrategyDrift = async (days = 30) => {
    const response = await fetch(`${API_BASE}/ai/strategy-drift?comparison_days=${days}`);
    return response.json();
};

const fetchRiskTrend = async (days = 30) => {
    const response = await fetch(`${API_BASE}/ai/risk-trend?days=${days}`);
    return response.json();
};

const Evolution = () => {
    const [evolution, setEvolution] = useState(null);
    const [improvement, setImprovement] = useState(null);
    const [drift, setDrift] = useState(null);
    const [riskTrend, setRiskTrend] = useState(null);
    const [loading, setLoading] = useState(true);
    const [periodType, setPeriodType] = useState('weekly');

    useEffect(() => {
        loadData();
    }, [periodType]);

    const loadData = async () => {
        setLoading(true);
        try {
            const [evoData, impData, driftData, riskData] = await Promise.all([
                fetchEvolution(periodType),
                fetchImprovement(),
                fetchStrategyDrift(),
                fetchRiskTrend()
            ]);
            setEvolution(evoData);
            setImprovement(impData);
            setDrift(driftData);
            setRiskTrend(riskData);
        } catch (error) {
            console.error('Failed to load evolution data:', error);
        }
        setLoading(false);
    };

    const getTrendIcon = (direction) => {
        if (direction === 'improving') return <TrendingUp className="text-emerald-500" size={18} />;
        if (direction === 'declining') return <TrendingDown className="text-red-500" size={18} />;
        return <Minus className="text-slate-400" size={18} />;
    };

    const getTrendColor = (direction) => {
        if (direction === 'improving') return 'text-emerald-600';
        if (direction === 'declining') return 'text-red-600';
        return 'text-slate-500';
    };

    const getMetricIcon = (metric) => {
        switch (metric) {
            case 'discipline': return <Target size={16} />;
            case 'risk_management': return <Shield size={16} />;
            case 'consistency': return <BarChart3 size={16} />;
            case 'profitability': return <TrendingUp size={16} />;
            case 'timing': return <Clock size={16} />;
            default: return <BarChart3 size={16} />;
        }
    };

    const formatMetricName = (name) => {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    // Prepare chart data
    const prepareEvolutionChart = () => {
        if (!evolution?.evolution) return [];
        return evolution.evolution.map((period, index) => ({
            name: period.period_label,
            discipline: period.metrics.discipline || 0,
            risk_management: period.metrics.risk_management || 0,
            consistency: period.metrics.consistency || 0,
            profitability: period.metrics.profitability || 0,
            composite: period.metrics.composite || 0
        }));
    };

    const prepareRadarData = () => {
        if (!evolution?.trends) return [];
        const metrics = ['discipline', 'risk_management', 'consistency', 'profitability', 'timing'];
        return metrics.map(m => ({
            metric: formatMetricName(m),
            current: evolution.trends[m]?.current || 0,
            previous: evolution.trends[m]?.previous || 0
        }));
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="flex items-center justify-center h-96">
                    <Loader2 className="animate-spin text-indigo-600" size={32} />
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="p-6 space-y-6">
                {/* Header */}
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold text-slate-900">Behavior Evolution</h1>
                        <p className="text-slate-500 mt-1">Track your trading growth over time</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <select
                            value={periodType}
                            onChange={(e) => setPeriodType(e.target.value)}
                            className="px-4 py-2 border border-slate-200 rounded-lg text-sm bg-white"
                        >
                            <option value="daily">Daily</option>
                            <option value="weekly">Weekly</option>
                            <option value="monthly">Monthly</option>
                        </select>
                        <button
                            onClick={loadData}
                            className="p-2 rounded-lg bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors"
                        >
                            <RefreshCw size={18} />
                        </button>
                    </div>
                </div>

                {/* Improvement Headline */}
                {improvement && (
                    <div className={`p-5 rounded-xl border ${improvement.overall_direction === 'improving'
                            ? 'bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200'
                            : improvement.overall_direction === 'declining'
                                ? 'bg-gradient-to-r from-red-50 to-orange-50 border-red-200'
                                : 'bg-gradient-to-r from-slate-50 to-gray-50 border-slate-200'
                        }`}>
                        <div className="flex items-start gap-4">
                            {improvement.overall_direction === 'improving' ? (
                                <Award className="text-emerald-500 mt-1" size={24} />
                            ) : improvement.overall_direction === 'declining' ? (
                                <AlertTriangle className="text-orange-500 mt-1" size={24} />
                            ) : (
                                <BarChart3 className="text-slate-500 mt-1" size={24} />
                            )}
                            <div>
                                <h3 className="text-lg font-semibold text-slate-900">{improvement.headline}</h3>
                                {improvement.narratives?.slice(0, 2).map((n, i) => (
                                    <p key={i} className="text-slate-600 mt-1">{n.message}</p>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Metrics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                    {evolution?.trends && Object.entries(evolution.trends).filter(([k]) => k !== 'composite').map(([metric, data]) => (
                        <div key={metric} className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2 text-slate-600">
                                    {getMetricIcon(metric)}
                                    <span className="text-sm font-medium">{formatMetricName(metric)}</span>
                                </div>
                                {getTrendIcon(data.direction)}
                            </div>
                            <div className="flex items-end justify-between">
                                <span className="text-2xl font-bold text-slate-900">{data.current?.toFixed(0)}</span>
                                <span className={`text-sm font-medium ${getTrendColor(data.direction)}`}>
                                    {data.change_pct > 0 ? '+' : ''}{data.change_pct?.toFixed(1)}%
                                </span>
                            </div>
                            <div className="mt-2 h-1 bg-slate-100 rounded-full overflow-hidden">
                                <div
                                    className={`h-full rounded-full ${data.direction === 'improving' ? 'bg-emerald-500' :
                                            data.direction === 'declining' ? 'bg-red-500' : 'bg-slate-400'
                                        }`}
                                    style={{ width: `${Math.min(100, data.current || 0)}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>

                {/* Charts Row */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Evolution Timeline */}
                    <div className="bg-white rounded-xl border border-slate-200 p-5">
                        <h3 className="text-lg font-semibold text-slate-900 mb-4">Composite Score Evolution</h3>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={prepareEvolutionChart()}>
                                    <defs>
                                        <linearGradient id="compositeGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                                    <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'white',
                                            border: '1px solid #e2e8f0',
                                            borderRadius: '8px'
                                        }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="composite"
                                        stroke="#6366f1"
                                        strokeWidth={2}
                                        fill="url(#compositeGradient)"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Radar Comparison */}
                    <div className="bg-white rounded-xl border border-slate-200 p-5">
                        <h3 className="text-lg font-semibold text-slate-900 mb-4">Current vs Previous Period</h3>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <RadarChart data={prepareRadarData()}>
                                    <PolarGrid stroke="#e2e8f0" />
                                    <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
                                    <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
                                    <Radar
                                        name="Current"
                                        dataKey="current"
                                        stroke="#6366f1"
                                        fill="#6366f1"
                                        fillOpacity={0.4}
                                    />
                                    <Radar
                                        name="Previous"
                                        dataKey="previous"
                                        stroke="#94a3b8"
                                        fill="#94a3b8"
                                        fillOpacity={0.2}
                                    />
                                    <Tooltip />
                                </RadarChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="flex justify-center gap-6 mt-2">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-indigo-500"></div>
                                <span className="text-sm text-slate-600">Current</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-slate-400"></div>
                                <span className="text-sm text-slate-600">Previous</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Strategy Drift Card */}
                {drift && (
                    <div className="bg-white rounded-xl border border-slate-200 p-5">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-slate-900">Strategy Drift Analysis</h3>
                            {drift.drift_detected && (
                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${drift.severity === 'major' ? 'bg-red-100 text-red-700' :
                                        drift.severity === 'significant' ? 'bg-orange-100 text-orange-700' :
                                            drift.severity === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
                                                'bg-slate-100 text-slate-700'
                                    }`}>
                                    {drift.severity?.charAt(0).toUpperCase() + drift.severity?.slice(1)} Drift
                                </span>
                            )}
                        </div>

                        {drift.drift_detected ? (
                            <div className="space-y-4">
                                <p className="text-slate-600">{drift.interpretation}</p>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    {drift.changed_dimensions?.slice(0, 3).map((change, i) => (
                                        <div key={i} className="bg-slate-50 rounded-lg p-3">
                                            <div className="text-sm text-slate-500">{change.dimension}</div>
                                            <div className="flex items-center gap-2 mt-1">
                                                <span className="text-slate-400">{change.old_value?.toFixed(1)}</span>
                                                <span className="text-slate-400">→</span>
                                                <span className="font-semibold text-slate-900">{change.new_value?.toFixed(1)}</span>
                                                <span className={`text-sm ${change.direction === 'increased' ? 'text-emerald-600' : 'text-red-600'}`}>
                                                    {change.direction === 'increased' ? '↑' : '↓'} {change.change_pct?.toFixed(0)}%
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <div className={`flex items-center gap-2 p-3 rounded-lg ${drift.is_positive ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
                                    }`}>
                                    {drift.is_positive ? (
                                        <>
                                            <TrendingUp size={18} />
                                            <span>This drift has improved your overall results</span>
                                        </>
                                    ) : (
                                        <>
                                            <AlertTriangle size={18} />
                                            <span>This drift may need attention - consider reviewing your approach</span>
                                        </>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <div className="text-center py-8 text-slate-500">
                                <BarChart3 className="mx-auto mb-3 text-slate-300" size={32} />
                                <p>Your trading style has been consistent.</p>
                                <p className="text-sm mt-1">No significant strategy drift detected in the last {drift.comparison_period_days || 30} days.</p>
                            </div>
                        )}
                    </div>
                )}

                {/* Risk Trend */}
                {riskTrend?.has_data && (
                    <div className="bg-white rounded-xl border border-slate-200 p-5">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-slate-900">Risk Score Trend</h3>
                            <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${riskTrend.trend === 'decreasing_risk' ? 'bg-emerald-100 text-emerald-700' :
                                    riskTrend.trend === 'increasing_risk' ? 'bg-red-100 text-red-700' :
                                        'bg-slate-100 text-slate-700'
                                }`}>
                                {riskTrend.trend === 'decreasing_risk' ? <TrendingDown size={14} /> :
                                    riskTrend.trend === 'increasing_risk' ? <TrendingUp size={14} /> :
                                        <Minus size={14} />}
                                <span>
                                    {riskTrend.trend === 'decreasing_risk' ? 'Decreasing Risk' :
                                        riskTrend.trend === 'increasing_risk' ? 'Increasing Risk' :
                                            'Stable'}
                                </span>
                            </div>
                        </div>
                        <div className="h-48">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={riskTrend.history}>
                                    <XAxis
                                        dataKey="date"
                                        tick={{ fontSize: 10 }}
                                        tickFormatter={(val) => new Date(val).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                    />
                                    <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                                    <Tooltip
                                        labelFormatter={(val) => new Date(val).toLocaleString()}
                                        contentStyle={{
                                            backgroundColor: 'white',
                                            border: '1px solid #e2e8f0',
                                            borderRadius: '8px'
                                        }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="score"
                                        stroke="#f43f5e"
                                        strokeWidth={2}
                                        dot={{ fill: '#f43f5e', r: 3 }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}
            </div>
        </MainLayout>
    );
};

export default Evolution;
