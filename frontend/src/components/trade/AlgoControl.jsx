import React, { useState, useEffect } from 'react';
import { Play, Square, Activity, Terminal } from 'lucide-react';
import { startAlgo, stopAlgo, getAlgoStatus } from '../../services/api';

const AlgoControl = () => {
    const [status, setStatus] = useState({ running: false, symbol: 'SPY', logs: [] });
    const [loading, setLoading] = useState(false);

    const refreshStatus = async () => {
        try {
            const data = await getAlgoStatus();
            setStatus(data);
        } catch (err) {
            // console.log("Algo status offline");
        }
    };

    useEffect(() => {
        refreshStatus();
        const interval = setInterval(refreshStatus, 2000);
        return () => clearInterval(interval);
    }, []);

    const handleToggle = async () => {
        setLoading(true);
        try {
            if (status.running) {
                await stopAlgo();
            } else {
                await startAlgo();
            }
            await refreshStatus();
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-full">
            <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <Activity size={18} className="text-purple-600" />
                    <h3 className="font-bold text-slate-700">Algo Engine (SMA Bot)</h3>
                </div>
                <div className={`text-xs font-bold px-2 py-1 rounded uppercase ${status.running ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-500'
                    }`}>
                    {status.running ? 'Running' : 'Stopped'}
                </div>
            </div>

            <div className="p-6 flex-1 flex flex-col gap-6">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-xs text-slate-500 font-bold uppercase mb-1">Target Asset</p>
                        <p className="text-xl font-mono font-bold text-slate-800">{status.symbol}</p>
                    </div>
                    <button
                        onClick={handleToggle}
                        disabled={loading}
                        className={`px-6 py-3 rounded-lg font-bold text-white shadow-md transition-all active:scale-95 flex items-center gap-2 ${status.running
                                ? 'bg-rose-500 hover:bg-rose-600 shadow-rose-200'
                                : 'bg-emerald-500 hover:bg-emerald-600 shadow-emerald-200'
                            }`}
                    >
                        {loading ? '...' : status.running ? (
                            <><Square size={16} fill="white" /> STOP BOT</>
                        ) : (
                            <><Play size={16} fill="white" /> START BOT</>
                        )}
                    </button>
                </div>

                <div className="flex-1 bg-slate-900 rounded-lg p-4 font-mono text-xs overflow-hidden flex flex-col">
                    <div className="flex items-center gap-2 text-slate-400 mb-2 pb-2 border-b border-slate-800">
                        <Terminal size={12} />
                        <span>Live Logs</span>
                    </div>
                    <div className="flex-1 overflow-y-auto space-y-1 scrollbar-hide">
                        {status.logs.length === 0 && <span className="text-slate-600">Waiting for logs...</span>}
                        {status.logs.map((log, i) => (
                            <div key={i} className="flex gap-2">
                                <span className="text-slate-500">[{log.time}]</span>
                                <span className={`${log.action === 'SIGNAL_BUY' ? 'text-emerald-400 font-bold' :
                                        log.action === 'SIGNAL_SELL' ? 'text-rose-400 font-bold' :
                                            log.action === 'ERROR' ? 'text-red-500' :
                                                'text-slate-300'
                                    }`}>
                                    {log.action}
                                </span>
                                {log.price > 0 && (
                                    <span className="text-slate-500">
                                        (P: {log.price.toFixed(2)} | SMA: {log.sma.toFixed(2)})
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AlgoControl;
