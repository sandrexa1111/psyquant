import React, { useState, useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import { Save, Shield, Server, Activity } from 'lucide-react';
import api from '../services/api';

const Settings = () => {
    const [mode, setMode] = useState('sim');
    const [status, setStatus] = useState('offline');
    const [apiKey, setApiKey] = useState('');
    const [apiSecret, setApiSecret] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const res = await api.get('/settings/status');
                setMode(res.data.mode);
                setStatus(res.data.alpaca_connected ? 'connected' : 'missing_keys');
            } catch (e) {
                console.error(e);
            }
        };
        fetchStatus();
    }, []);

    const handleSaveKeys = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.post('/settings/keys', {
                key_id: apiKey,
                secret_key: apiSecret,
                mode: 'paper'
            });
            setMessage({ type: 'success', text: 'Keys saved securely! Switched to Alpaca Paper mode.' });
            setMode('paper');
            setStatus('connected');
            setApiKey('');
            setApiSecret('');
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to save keys.' });
        } finally {
            setLoading(false);
        }
    };

    const handleModeSwitch = async (newMode) => {
        try {
            await api.post(`/settings/mode/${newMode}`);
            setMode(newMode);
            window.location.reload(); // Reload to refresh data context
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <MainLayout>
            <div className="max-w-4xl mx-auto">
                <header className="mb-8">
                    <h1 className="text-2xl font-bold text-slate-800">Platform Settings</h1>
                    <p className="text-slate-500">Manage connections and security.</p>
                </header>

                <div className="grid grid-cols-1 gap-6">
                    {/* Mode Selection */}
                    <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                        <div className="flex items-center gap-3 mb-4">
                            <Server className="text-indigo-600" size={24} />
                            <h2 className="text-lg font-semibold text-slate-800">Trading Engine Mode</h2>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <button
                                onClick={() => handleModeSwitch('sim')}
                                className={`p-4 border-2 rounded-lg text-left transition-all ${mode === 'sim'
                                    ? 'border-indigo-600 bg-indigo-50 ring-1 ring-indigo-600'
                                    : 'border-slate-200 hover:border-slate-300'
                                    }`}
                            >
                                <div className="font-bold text-slate-900 mb-1">Local Simulation</div>
                                <div className="text-sm text-slate-500">Risk-free sandbox with $100k virtual cash. No API keys required.</div>
                            </button>

                            <button
                                onClick={() => handleModeSwitch('paper')}
                                className={`p-4 border-2 rounded-lg text-left transition-all ${mode === 'paper'
                                    ? 'border-indigo-600 bg-indigo-50 ring-1 ring-indigo-600'
                                    : 'border-slate-200 hover:border-slate-300'
                                    }`}
                            >
                                <div className="flex justify-between items-start">
                                    <div className="font-bold text-slate-900 mb-1">Alpaca Paper Trading</div>
                                    {status === 'connected' && <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-bold">CONNECTED</span>}
                                </div>
                                <div className="text-sm text-slate-500">Connect your own Alpaca account for realistic market data and execution.</div>
                            </button>
                        </div>
                    </div>

                    {/* API Keys Form */}
                    <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                        <div className="flex items-center gap-3 mb-4">
                            <Shield className="text-emerald-600" size={24} />
                            <h2 className="text-lg font-semibold text-slate-800">Secure Connection</h2>
                        </div>

                        <p className="text-sm text-slate-600 mb-6 bg-yellow-50 p-3 rounded border border-yellow-200">
                            <strong>Security Note:</strong> Your keys are encrypted with AES-256 before being stored. They are never logged purely.
                        </p>

                        <form onSubmit={handleSaveKeys} className="space-y-4 max-w-lg">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Alpaca Key ID (Paper)</label>
                                <input
                                    type="text"
                                    name="alpaca_key_id"
                                    autoComplete="off"
                                    required
                                    value={apiKey}
                                    onChange={(e) => setApiKey(e.target.value)}
                                    placeholder="PK..."
                                    className="w-full p-2 border border-slate-300 rounded focus:ring-2 focus:ring-emerald-500 outline-none font-mono text-sm"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Alpaca Secret Key</label>
                                <input
                                    type="password"
                                    name="alpaca_secret_key"
                                    autoComplete="new-password"
                                    required
                                    value={apiSecret}
                                    onChange={(e) => setApiSecret(e.target.value)}
                                    placeholder="..................................."
                                    className="w-full p-2 border border-slate-300 rounded focus:ring-2 focus:ring-emerald-500 outline-none font-mono text-sm"
                                />
                            </div>

                            {message && (
                                <div className={`p-3 rounded text-sm ${message.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
                                    {message.text}
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={loading}
                                className="flex items-center justify-center gap-2 w-full bg-slate-900 text-white py-2 rounded hover:bg-slate-800 transition-colors"
                            >
                                {loading ? <Activity size={18} className="animate-spin" /> : <Save size={18} />}
                                Encrypt & Connect
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
};

export default Settings;
