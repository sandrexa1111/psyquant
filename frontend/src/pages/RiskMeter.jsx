import React, { useEffect, useState } from 'react';
import MainLayout from '../components/layout/MainLayout';
import { getRiskScore } from '../services/api';
import { AlertTriangle, TrendingUp, TrendingDown, Activity, Clock, BarChart3, Loader2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

const RiskMeter = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [riskData, setRiskData] = useState(null);

    useEffect(() => {
        const fetchRiskScore = async () => {
            try {
                const data = await getRiskScore(30);
                setRiskData(data);
            } catch (err) {
                console.error('Failed to fetch risk score:', err);
                setError('Failed to load risk data');
            } finally {
                setLoading(false);
            }
        };

        fetchRiskScore();
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

    if (error) {
        return (
            <MainLayout>
                <div className="p-8 text-center text-red-500">{error}</div>
            </MainLayout>
        );
    }

    const { score, risk_state, factors, trades_analyzed, history } = riskData || {};

    const getRiskColor = (state) => {
        switch (state) {
            case 'low': return 'text-emerald-500';
            case 'moderate': return 'text-yellow-500';
            case 'high': return 'text-orange-500';
            case 'critical': return 'text-red-500';
            default: return 'text-gray-500';
        }
    };

    const getRiskBgColor = (state) => {
        switch (state) {
            case 'low': return 'bg-emerald-500';
            case 'moderate': return 'bg-yellow-500';
            case 'high': return 'bg-orange-500';
            case 'critical': return 'bg-red-500';
            default: return 'bg-gray-500';
        }
    };

    const getGaugeRotation = (score) => {
        // -90 to 90 degrees for 0-100 score
        return -90 + (score / 100) * 180;
    };

    return (
        <MainLayout>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-slate-800">Psychological Risk Meter</h1>
                <p className="text-slate-500">Monitor your trading psychology health in real-time</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Risk Gauge */}
                <div className="bg-white rounded-2xl shadow-sm p-8">
                    <h2 className="text-lg font-semibold text-slate-800 mb-6">Risk Score (PRS)</h2>

                    <div className="relative flex flex-col items-center">
                        {/* Gauge SVG */}
                        <svg className="w-64 h-32" viewBox="0 0 200 100">
                            {/* Gauge background */}
                            <path
                                d="M 20 100 A 80 80 0 0 1 180 100"
                                fill="none"
                                stroke="#e2e8f0"
                                strokeWidth="12"
                                strokeLinecap="round"
                            />
                            {/* Risk zones */}
                            <path
                                d="M 20 100 A 80 80 0 0 1 55 35"
                                fill="none"
                                stroke="#10b981"
                                strokeWidth="12"
                                strokeLinecap="round"
                            />
                            <path
                                d="M 55 35 A 80 80 0 0 1 100 20"
                                fill="none"
                                stroke="#f59e0b"
                                strokeWidth="12"
                            />
                            <path
                                d="M 100 20 A 80 80 0 0 1 145 35"
                                fill="none"
                                stroke="#f97316"
                                strokeWidth="12"
                            />
                            <path
                                d="M 145 35 A 80 80 0 0 1 180 100"
                                fill="none"
                                stroke="#ef4444"
                                strokeWidth="12"
                                strokeLinecap="round"
                            />
                            {/* Needle */}
                            <line
                                x1="100"
                                y1="100"
                                x2="100"
                                y2="30"
                                stroke="#1e293b"
                                strokeWidth="3"
                                strokeLinecap="round"
                                transform={`rotate(${getGaugeRotation(score || 0)}, 100, 100)`}
                            />
                            <circle cx="100" cy="100" r="8" fill="#1e293b" />
                        </svg>

                        {/* Score Display */}
                        <div className="mt-6 text-center">
                            <div className={`text-5xl font-bold ${getRiskColor(risk_state)}`}>
                                {score}
                            </div>
                            <div className={`text-lg font-medium uppercase tracking-wide mt-2 ${getRiskColor(risk_state)}`}>
                                {risk_state} Risk
                            </div>
                            <div className="text-sm text-slate-500 mt-2">
                                Based on {trades_analyzed} trades analyzed
                            </div>
                        </div>
                    </div>
                </div>

                {/* Factor Breakdown */}
                <div className="bg-white rounded-2xl shadow-sm p-8">
                    <h2 className="text-lg font-semibold text-slate-800 mb-6">Risk Factor Breakdown</h2>

                    <div className="space-y-6">
                        {/* Loss Streak */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-2">
                                    <TrendingDown className="w-5 h-5 text-red-500" />
                                    <span className="font-medium text-slate-700">Loss Streak</span>
                                </div>
                                <span className="font-semibold text-slate-800">
                                    {Math.round(factors?.loss_streak || 0)}%
                                </span>
                            </div>
                            <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-red-400 to-red-600 rounded-full transition-all duration-500"
                                    style={{ width: `${factors?.loss_streak || 0}%` }}
                                />
                            </div>
                        </div>

                        {/* Position Deviation */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-2">
                                    <BarChart3 className="w-5 h-5 text-orange-500" />
                                    <span className="font-medium text-slate-700">Position Deviation</span>
                                </div>
                                <span className="font-semibold text-slate-800">
                                    {Math.round(factors?.position_deviation || 0)}%
                                </span>
                            </div>
                            <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-orange-400 to-orange-600 rounded-full transition-all duration-500"
                                    style={{ width: `${factors?.position_deviation || 0}%` }}
                                />
                            </div>
                        </div>

                        {/* Frequency Change */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-2">
                                    <Activity className="w-5 h-5 text-yellow-500" />
                                    <span className="font-medium text-slate-700">Frequency Change</span>
                                </div>
                                <span className="font-semibold text-slate-800">
                                    {Math.round(factors?.frequency_change || 0)}%
                                </span>
                            </div>
                            <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-full transition-all duration-500"
                                    style={{ width: `${factors?.frequency_change || 0}%` }}
                                />
                            </div>
                        </div>

                        {/* Holding Anomaly */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-2">
                                    <Clock className="w-5 h-5 text-purple-500" />
                                    <span className="font-medium text-slate-700">Holding Anomaly</span>
                                </div>
                                <span className="font-semibold text-slate-800">
                                    {Math.round(factors?.holding_anomaly || 0)}%
                                </span>
                            </div>
                            <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-purple-400 to-purple-600 rounded-full transition-all duration-500"
                                    style={{ width: `${factors?.holding_anomaly || 0}%` }}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Risk History Chart */}
            <div className="mt-8 bg-white rounded-2xl shadow-sm p-8">
                <h2 className="text-lg font-semibold text-slate-800 mb-6">Risk Score History</h2>

                {history && history.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={history}>
                            <defs>
                                <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <XAxis
                                dataKey="created_at"
                                tickFormatter={(value) => new Date(value).toLocaleDateString()}
                                stroke="#94a3b8"
                                fontSize={12}
                            />
                            <YAxis domain={[0, 100]} stroke="#94a3b8" fontSize={12} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1e293b',
                                    border: 'none',
                                    borderRadius: '8px',
                                    color: '#fff'
                                }}
                                formatter={(value) => [`${value}`, 'PRS']}
                                labelFormatter={(label) => new Date(label).toLocaleString()}
                            />
                            <Area
                                type="monotone"
                                dataKey="score"
                                stroke="#6366f1"
                                strokeWidth={2}
                                fill="url(#riskGradient)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="h-64 flex items-center justify-center text-slate-500">
                        <div className="text-center">
                            <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                            <p>No historical data yet</p>
                            <p className="text-sm">Risk scores will be tracked over time</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Risk Alerts */}
            {risk_state === 'high' || risk_state === 'critical' ? (
                <div className="mt-8 bg-red-50 border border-red-200 rounded-2xl p-6">
                    <div className="flex items-start gap-4">
                        <AlertTriangle className="w-6 h-6 text-red-500 flex-shrink-0 mt-1" />
                        <div>
                            <h3 className="font-semibold text-red-700">High Risk Alert</h3>
                            <p className="text-red-600 mt-1">
                                Your psychological risk score is elevated. Consider taking a break from trading
                                and reviewing your recent decisions before making new trades.
                            </p>
                            <div className="mt-4 flex gap-3">
                                <button className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors">
                                    Review Recent Trades
                                </button>
                                <button className="px-4 py-2 bg-white text-red-600 border border-red-300 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors">
                                    Set Trading Pause
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            ) : null}
        </MainLayout>
    );
};

export default RiskMeter;
