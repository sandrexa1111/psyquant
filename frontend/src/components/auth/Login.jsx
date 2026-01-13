import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { User, Lock, Loader2, ArrowRight, Mail } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AuthPage = () => {
    const { signIn, signUp } = useAuth();
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    const toggleMode = () => {
        setIsLogin(!isLogin);
        setError('');
        setSuccessMessage('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccessMessage('');

        try {
            if (isLogin) {
                const { error } = await signIn({ email, password });
                if (error) throw error;
                // Redirect to Onboarding to select mode
                window.location.href = '/onboarding';
            } else {
                const { error } = await signUp({ email, password });
                if (error) throw error;
                setSuccessMessage('Account created! Please check your email for verification tailored to our demo settings.');
                // In a real app, you might want to switch them to login or auto-login depending on config
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-900 overflow-hidden relative">
            {/* Ambient Background Elements */}
            <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-blue-600/20 rounded-full blur-[120px] animate-pulse"></div>
            <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px] animate-pulse delay-1000"></div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md relative z-10"
            >
                <div className="bg-white/10 backdrop-blur-xl border border-white/20 p-8 rounded-2xl shadow-2xl">
                    <div className="text-center mb-8">
                        <motion.h1
                            layoutId="title"
                            className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent"
                        >
                            Architect
                        </motion.h1>
                        <motion.p
                            layout
                            className="text-slate-400 mt-2 text-sm"
                        >
                            {isLogin ? 'Welcome back, trader.' : 'Start your journey.'}
                        </motion.p>
                    </div>

                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-3 rounded-lg mb-4 text-center"
                        >
                            {error}
                        </motion.div>
                    )}

                    {successMessage && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm p-3 rounded-lg mb-4 text-center"
                        >
                            {successMessage}
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="space-y-1">
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider ml-1">Email</label>
                            <div className="relative group">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-400 transition-colors" size={18} />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-200 text-sm placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
                                    placeholder="name@company.com"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider ml-1">Password</label>
                            <div className="relative group">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-400 transition-colors" size={18} />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-200 text-sm placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
                                    placeholder="••••••••"
                                    required
                                    minLength={6}
                                />
                            </div>
                        </div>

                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium rounded-xl text-sm transition-all shadow-lg shadow-blue-900/20 disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
                        >
                            {loading ? <Loader2 className="animate-spin" size={18} /> : (
                                <>
                                    {isLogin ? 'Sign In' : 'Create Account'}
                                    <ArrowRight size={16} />
                                </>
                            )}
                        </motion.button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-slate-500 text-sm">
                            {isLogin ? "Don't have an account?" : "Already have an account?"}
                            <button
                                onClick={toggleMode}
                                className="ml-2 text-blue-400 hover:text-blue-300 font-medium transition-colors focus:outline-none"
                            >
                                {isLogin ? 'Sign Up' : 'Sign In'}
                            </button>
                        </p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default AuthPage;
