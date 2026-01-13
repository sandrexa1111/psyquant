import React, { useEffect, useState } from 'react';
import MainLayout from '../components/layout/MainLayout';
import { Loader2 } from 'lucide-react';
import PerformanceMatrix from '../components/analytics/PerformanceMatrix';
import SkillProfile from '../components/analytics/SkillProfile';
import BiasList from '../components/analytics/BiasList';
import { getPortfolioMetrics, getSkillProfile, getBiases } from '../services/api';

const Analytics = () => {
    const [data, setData] = useState(null);
    const [skills, setSkills] = useState(null);
    const [biases, setBiases] = useState([]);
    const [loading, setLoading] = useState(true);
    const [period, setPeriod] = useState('1A');

    useEffect(() => {
        const fetchAllData = async () => {
            setLoading(true);
            try {
                // Parallel fetch for better performance
                const [metricsRes, skillsRes, biasesRes] = await Promise.all([
                    getPortfolioMetrics(period),
                    getSkillProfile(),
                    getBiases()
                ]);

                setData(metricsRes);
                setSkills(skillsRes);
                setBiases(biasesRes);
            } catch (error) {
                console.error("Failed to fetch analytics data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchAllData();
    }, [period]);

    return (
        <MainLayout>
            <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Portfolio Analytics</h1>
                    <p className="text-slate-500 mt-1">Deep dive into performance, skills, and psychology.</p>
                </div>

                {/* Timeframe Selector */}
                <div className="flex gap-2 bg-white border border-slate-200 rounded-lg p-1">
                    {['1M', '3M', '1A', 'ALL'].map((p) => (
                        <button
                            key={p}
                            onClick={() => setPeriod(p)}
                            className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${period === p
                                    ? 'bg-indigo-600 text-white'
                                    : 'text-slate-600 hover:bg-slate-50'
                                } `}
                        >
                            {p}
                        </button>
                    ))}
                </div>
            </div>

            {loading ? (
                <div className="flex items-center justify-center h-64">
                    <Loader2 className="animate-spin text-indigo-600" size={32} />
                </div>
            ) : data ? (
                <div className="space-y-6">
                    {/* AI Intelligence Layer */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-1">
                            <SkillProfile data={skills} />
                        </div>
                        <div className="lg:col-span-1">
                            <BiasList biases={biases} />
                        </div>
                        <div className="lg:col-span-1 bg-gradient-to-br from-indigo-600 to-purple-700 rounded-lg p-6 text-white text-center flex flex-col justify-center items-center shadow-md">
                            <h3 className="text-lg font-medium opacity-90 mb-2">AI Coach Insight</h3>
                            <p className="text-xl font-semibold">
                                "Your risk management score is solid. Focus on timing entries to improve profitability."
                            </p>
                            <div className="mt-4 text-xs opacity-75 uppercase tracking-wider">Analysis based on {period} history</div>
                        </div>
                    </div>

                    {/* Performance Summary Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                            <div className="text-sm text-slate-500 mb-1">Total Equity</div>
                            <div className="text-2xl font-bold text-slate-900">
                                ${data.summary.total_equity?.toLocaleString()}
                            </div>
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                            <div className="text-sm text-slate-500 mb-1">Total Return</div>
                            <div className={`text-2xl font-bold ${data.summary.total_return >= 0 ? 'text-emerald-600' : 'text-red-600'} `}>
                                {data.summary.total_return > 0 ? '+' : ''}{data.summary.total_return}%
                            </div>
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                            <div className="text-sm text-slate-500 mb-1">Sharpe Ratio</div>
                            <div className="text-2xl font-bold text-slate-900">
                                {data.summary.sharpe_ratio}
                            </div>
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                            <div className="text-sm text-slate-500 mb-1">Max Drawdown</div>
                            <div className="text-2xl font-bold text-red-600">
                                {data.summary.max_drawdown}%
                            </div>
                        </div>
                    </div>

                    {/* Charts Row */}
                    <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                        <h3 className="text-lg font-semibold text-slate-800 mb-4">Equity Curve</h3>
                        <div className="h-[300px] flex items-center justify-center bg-slate-50 rounded text-slate-400">
                            {/* Placeholder for Equity Chart or reuse existing */}
                            Chart Component Placeholder (Use Recharts LineChart here)
                        </div>
                    </div>

                    {/* Detailed Matrix */}
                    <PerformanceMatrix metrics={data.summary} />

                </div>
            ) : (
                <div className="text-center py-12 text-slate-500">
                    Failed to load analytics data.
                </div>
            )}
        </MainLayout>
    );
};

export default Analytics;
