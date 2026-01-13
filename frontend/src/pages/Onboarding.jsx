import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Gamepad2, Globe, ArrowRight, Shield, Check, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';

const Onboarding = () => {
    const navigate = useNavigate();
    const [selectedMode, setSelectedMode] = useState(null); // 'sim' or 'paper'
    const [apiKey, setApiKey] = useState('');
    const [apiSecret, setApiSecret] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSimStart = async () => {
        setLoading(true);
        try {
            await api.post('/settings/mode/sim');
            // Add a small delay for effect/state propagation
            setTimeout(() => navigate('/'), 800);
        } catch (e) {
            console.error(e);
            setLoading(false);
        }
    };

    const handlePaperConnect = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.post('/settings/keys', {
                key_id: apiKey,
                secret_key: apiSecret,
                mode: 'paper'
            });
            setTimeout(() => navigate('/'), 800);
        } catch (e) {
            console.error(e);
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black z-0"></div>
            <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[100px]"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[100px]"></div>

            <div className="relative z-10 max-w-5xl w-full">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-16"
                >
                    <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-indigo-200 to-white bg-clip-text text-transparent mb-4">
                        Choose Your Reality
                    </h1>
                    <p className="text-slate-400 text-lg max-w-2xl mx-auto">
                        Select how you want to interact with the markets today. You can switch this later in Settings.
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
                    {/* Option 1: Simulation */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                        className={`relative group cursor-pointer rounded-2xl p-1 bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 hover:border-indigo-500/50 transition-all duration-300 ${selectedMode === 'sim' ? 'ring-2 ring-indigo-500' : ''}`}
                        onClick={() => setSelectedMode('sim')}
                    >
                        <div className="bg-slate-900/90 h-full rounded-xl p-8 flex flex-col items-center text-center">
                            <div className="w-16 h-16 bg-indigo-500/10 rounded-2xl flex items-center justify-center mb-6 text-indigo-400 group-hover:scale-110 transition-transform">
                                <Gamepad2 size={32} />
                            </div>
                            <h2 className="text-2xl font-bold text-white mb-2">Sandbox Simulation</h2>
                            <p className="text-slate-400 mb-8">
                                Risk-free environment with <span className="text-indigo-300 font-mono">$100k</span> virtual capital. Perfect for testing strategies and AI signals.
                            </p>

                            <ul className="space-y-3 text-left w-full mb-8 text-slate-300 text-sm">
                                <li className="flex items-center gap-2"><Check size={16} className="text-emerald-500" /> Instant execution (Market Orders)</li>
                                <li className="flex items-center gap-2"><Check size={16} className="text-emerald-500" /> Zero configuration required</li>
                                <li className="flex items-center gap-2"><Check size={16} className="text-emerald-500" /> Test AI Bias Detections safely</li>
                            </ul>

                            <button
                                onClick={(e) => { e.stopPropagation(); handleSimStart(); }}
                                disabled={loading}
                                className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all shadow-lg shadow-indigo-900/20 flex items-center justify-center gap-2"
                            >
                                {loading && selectedMode === 'sim' ? <Loader2 className="animate-spin" /> : 'Enter Sandbox'}
                            </button>
                        </div>
                    </motion.div>

                    {/* Option 2: Live/Paper */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className={`relative group cursor-pointer rounded-2xl p-1 bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 hover:border-emerald-500/50 transition-all duration-300 ${selectedMode === 'paper' ? 'ring-2 ring-emerald-500' : ''}`}
                        onClick={() => setSelectedMode('paper')}
                    >
                        <div className="bg-slate-900/90 h-full rounded-xl p-8 flex flex-col items-center text-center">
                            <div className="w-16 h-16 bg-emerald-500/10 rounded-2xl flex items-center justify-center mb-6 text-emerald-400 group-hover:scale-110 transition-transform">
                                <Globe size={32} />
                            </div>
                            <h2 className="text-2xl font-bold text-white mb-2">Alpaca Integration</h2>
                            <p className="text-slate-400 mb-8">
                                Connect your real Alpaca account. Use Paper Trading keys for realistic validation or Live keys for execution.
                            </p>

                            <AnimatePresence>
                                {selectedMode !== 'paper' ? (
                                    <ul className="space-y-3 text-left w-full mb-8 text-slate-300 text-sm">
                                        <li className="flex items-center gap-2"><Check size={16} className="text-emerald-500" /> Real market data feed</li>
                                        <li className="flex items-center gap-2"><Check size={16} className="text-emerald-500" /> Sync with existing portfolio</li>
                                        <li className="flex items-center gap-2"><Check size={16} className="text-emerald-500" /> AES-256 Encrypted Storage</li>
                                    </ul>
                                ) : (
                                    <motion.form
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="w-full text-left space-y-4 mb-4"
                                        onSubmit={handlePaperConnect}
                                        onClick={(e) => e.stopPropagation()}
                                    >
                                        <div>
                                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Key ID</label>
                                            <input
                                                type="text"
                                                name="alpaca_key_id"
                                                autoComplete="off"
                                                value={apiKey}
                                                onChange={(e) => setApiKey(e.target.value)}
                                                className="w-full mt-1 p-3 bg-slate-800 border border-slate-700 rounded-lg text-white font-mono text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                                                placeholder="PK..."
                                                required
                                            />
                                        </div>
                                        <div>
                                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Secret Key</label>
                                            <input
                                                type="password"
                                                name="alpaca_secret_key"
                                                autoComplete="new-password"
                                                value={apiSecret}
                                                onChange={(e) => setApiSecret(e.target.value)}
                                                className="w-full mt-1 p-3 bg-slate-800 border border-slate-700 rounded-lg text-white font-mono text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                                                placeholder=".................."
                                                required
                                            />
                                        </div>
                                    </motion.form>
                                )}
                            </AnimatePresence>

                            <button
                                onClick={(e) => {
                                    if (selectedMode !== 'paper') {
                                        setSelectedMode('paper');
                                        e.stopPropagation();
                                    }
                                    // If already paper, submitting form handles it
                                }}
                                disabled={loading}
                                type={selectedMode === 'paper' ? 'submit' : 'button'}
                                className={`w-full py-4 font-semibold rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 ${selectedMode === 'paper'
                                    ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/20'
                                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                                    }`}
                                form={selectedMode === 'paper' ? undefined : undefined} // Implicit form submission inside
                            >
                                {loading && selectedMode === 'paper' ? <Loader2 className="animate-spin" /> : (selectedMode === 'paper' ? 'Connect & Start' : 'Configure Connection')}
                            </button>
                        </div>
                    </motion.div>
                </div>
            </div>
        </div>
    );
};

export default Onboarding;
