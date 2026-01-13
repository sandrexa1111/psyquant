import React, { useEffect, useState } from 'react';
import MainLayout from '../components/layout/MainLayout';
import { getBehaviorPatterns, generateBehaviorChain } from '../services/api';
import { GitBranch, Brain, Target, CheckCircle2, Lightbulb, Heart, Loader2, ChevronDown, ChevronRight } from 'lucide-react';

const BehaviorGraph = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);
    const [expandedChain, setExpandedChain] = useState(null);

    useEffect(() => {
        const fetchPatterns = async () => {
            try {
                const result = await getBehaviorPatterns(30);
                setData(result);
            } catch (err) {
                console.error('Failed to fetch behavior patterns:', err);
                setError('Failed to load behavior data');
            } finally {
                setLoading(false);
            }
        };

        fetchPatterns();
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

    const { chains = [], patterns = {}, total_chains = 0 } = data || {};

    const eventIcons = {
        emotion: <Heart className="w-5 h-5" />,
        decision: <Brain className="w-5 h-5" />,
        execution: <Target className="w-5 h-5" />,
        outcome: <CheckCircle2 className="w-5 h-5" />,
        reflection: <Lightbulb className="w-5 h-5" />
    };

    const eventColors = {
        emotion: 'bg-pink-500',
        decision: 'bg-purple-500',
        execution: 'bg-blue-500',
        outcome: 'bg-emerald-500',
        reflection: 'bg-amber-500'
    };

    const eventLabels = {
        emotion: 'Emotion',
        decision: 'Decision',
        execution: 'Execution',
        outcome: 'Outcome',
        reflection: 'Reflection'
    };

    return (
        <MainLayout>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-slate-800">Behavior Graph</h1>
                <p className="text-slate-500">Visualize your trading psychology journey</p>
            </div>

            {/* Pattern Summary */}
            {Object.keys(patterns).length > 0 && (
                <div className="bg-white rounded-2xl shadow-sm p-6 mb-8">
                    <h2 className="text-lg font-semibold text-slate-800 mb-4">Detected Patterns</h2>
                    <div className="flex flex-wrap gap-3">
                        {Object.entries(patterns).map(([pattern, count]) => (
                            <div
                                key={pattern}
                                className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-700 rounded-full"
                            >
                                <span className="font-medium">{pattern.replace('_', ' ')}</span>
                                <span className="px-2 py-0.5 bg-red-200 rounded-full text-xs font-bold">
                                    {count}x
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Behavior Chain Legend */}
            <div className="bg-white rounded-2xl shadow-sm p-6 mb-8">
                <h2 className="text-lg font-semibold text-slate-800 mb-4">Chain Structure</h2>
                <div className="flex items-center justify-between overflow-x-auto pb-2">
                    {['emotion', 'decision', 'execution', 'outcome', 'reflection'].map((type, index) => (
                        <React.Fragment key={type}>
                            <div className="flex flex-col items-center min-w-[100px]">
                                <div className={`w-12 h-12 rounded-full ${eventColors[type]} text-white flex items-center justify-center`}>
                                    {eventIcons[type]}
                                </div>
                                <span className="mt-2 text-sm font-medium text-slate-700">
                                    {eventLabels[type]}
                                </span>
                            </div>
                            {index < 4 && (
                                <div className="flex-1 h-0.5 bg-slate-200 mx-2 min-w-[30px]" />
                            )}
                        </React.Fragment>
                    ))}
                </div>
            </div>

            {/* Behavior Chains */}
            <div className="bg-white rounded-2xl shadow-sm p-6">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-lg font-semibold text-slate-800">
                        Behavior Chains ({total_chains})
                    </h2>
                </div>

                {chains.length === 0 ? (
                    <div className="text-center py-12">
                        <GitBranch className="w-16 h-16 mx-auto mb-4 text-slate-300" />
                        <h3 className="text-xl font-semibold text-slate-700 mb-2">No Behavior Chains Yet</h3>
                        <p className="text-slate-500 mb-6">
                            Behavior chains are generated when you analyze trades.
                        </p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {chains.slice(0, 10).map((chain, chainIndex) => {
                            const isExpanded = expandedChain === chainIndex;
                            const sortedEvents = [...chain].sort((a, b) => a.sequence_order - b.sequence_order);
                            const emotionEvent = sortedEvents.find(e => e.event_type === 'emotion');
                            const outcomeEvent = sortedEvents.find(e => e.event_type === 'outcome');

                            return (
                                <div
                                    key={chainIndex}
                                    className="border border-slate-200 rounded-xl overflow-hidden"
                                >
                                    {/* Chain Header */}
                                    <button
                                        onClick={() => setExpandedChain(isExpanded ? null : chainIndex)}
                                        className="w-full flex items-center justify-between p-4 hover:bg-slate-50 transition-colors"
                                    >
                                        <div className="flex items-center gap-4">
                                            {isExpanded ? (
                                                <ChevronDown className="w-5 h-5 text-slate-500" />
                                            ) : (
                                                <ChevronRight className="w-5 h-5 text-slate-500" />
                                            )}
                                            <div className="flex items-center gap-2">
                                                {sortedEvents.map((event, idx) => (
                                                    <div
                                                        key={idx}
                                                        className={`w-8 h-8 rounded-full ${eventColors[event.event_type]} text-white flex items-center justify-center text-xs`}
                                                        title={eventLabels[event.event_type]}
                                                    >
                                                        {React.cloneElement(eventIcons[event.event_type], { className: 'w-4 h-4' })}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            {emotionEvent?.content?.state && (
                                                <span className="px-3 py-1 bg-pink-100 text-pink-700 rounded-full text-sm font-medium">
                                                    {emotionEvent.content.state}
                                                </span>
                                            )}
                                            {outcomeEvent?.content?.outcome_type && (
                                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${outcomeEvent.content.outcome_type === 'profit'
                                                        ? 'bg-emerald-100 text-emerald-700'
                                                        : outcomeEvent.content.outcome_type === 'loss'
                                                            ? 'bg-red-100 text-red-700'
                                                            : 'bg-slate-100 text-slate-700'
                                                    }`}>
                                                    {outcomeEvent.content.outcome_type}
                                                </span>
                                            )}
                                        </div>
                                    </button>

                                    {/* Expanded Content */}
                                    {isExpanded && (
                                        <div className="border-t border-slate-200 p-4 bg-slate-50">
                                            <div className="space-y-4">
                                                {sortedEvents.map((event, idx) => (
                                                    <div key={idx} className="flex gap-4">
                                                        <div className={`w-10 h-10 rounded-full ${eventColors[event.event_type]} text-white flex items-center justify-center flex-shrink-0`}>
                                                            {eventIcons[event.event_type]}
                                                        </div>
                                                        <div className="flex-1">
                                                            <div className="font-medium text-slate-800">
                                                                {eventLabels[event.event_type]}
                                                            </div>
                                                            <div className="text-sm text-slate-600 mt-1">
                                                                {event.event_type === 'emotion' && event.content && (
                                                                    <>
                                                                        State: <strong>{event.content.state}</strong>
                                                                        {event.content.intensity && (
                                                                            <> • Intensity: <strong>{event.content.intensity}%</strong></>
                                                                        )}
                                                                    </>
                                                                )}
                                                                {event.event_type === 'decision' && event.content && (
                                                                    <>
                                                                        {event.content.symbol} • {event.content.side?.toUpperCase()} • {event.content.quantity} shares
                                                                    </>
                                                                )}
                                                                {event.event_type === 'execution' && event.content && (
                                                                    <>
                                                                        Entry: ${event.content.entry_price?.toFixed(2)}
                                                                        {event.content.exit_price && (
                                                                            <> → Exit: ${event.content.exit_price.toFixed(2)}</>
                                                                        )}
                                                                    </>
                                                                )}
                                                                {event.event_type === 'outcome' && event.content && (
                                                                    <>
                                                                        P/L: <span className={event.content.pnl >= 0 ? 'text-emerald-600' : 'text-red-500'}>
                                                                            ${event.content.pnl?.toFixed(2)}
                                                                        </span>
                                                                        {' '}({event.content.pnl_pct?.toFixed(2)}%)
                                                                    </>
                                                                )}
                                                                {event.event_type === 'reflection' && event.content && (
                                                                    <>
                                                                        {event.content.lessons_learned?.[0] || 'No lessons recorded'}
                                                                    </>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </MainLayout>
    );
};

export default BehaviorGraph;
