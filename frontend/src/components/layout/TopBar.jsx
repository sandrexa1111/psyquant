import React, { useState, useEffect } from 'react';
import { Search, Bell, Grid, User, LogOut } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const TopBar = () => {
    const { signOut } = useAuth();
    const navigate = useNavigate();
    const [notificationsEnabled, setNotificationsEnabled] = useState(false);
    const [showToast, setShowToast] = useState(false);
    const [mode, setMode] = useState('sim'); // Default to sim

    useEffect(() => {
        // Poll for mode status periodically or just once on load
        const fetchStatus = async () => {
            try {
                // We'll use a direct fetch or import api helper if available, let's assume fetch for layout simplicity without circular deps
                // But generally using 'api' service is better.
                // Let's rely on a simple fetch for now to avoid extensive rewrites of checking imports.
                const token = localStorage.getItem('token');
                const res = await fetch('http://127.0.0.1:8000/settings/status', {
                    headers: token ? { Authorization: `Bearer ${token}` } : {}
                });
                if (res.ok) {
                    const data = await res.json();
                    setMode(data.mode);
                }
            } catch (e) {
                console.error("Failed to fetch mode", e);
            }
        };
        fetchStatus();
    }, []);

    const handleLogout = async () => {
        await signOut();
        navigate('/login');
    };

    const toggleNotifications = () => {
        setNotificationsEnabled(!notificationsEnabled);
        setShowToast(true);
        setTimeout(() => setShowToast(false), 3000);
    };

    const getModeBadge = () => {
        switch (mode) {
            case 'live': return <span className="bg-red-100 text-red-700 text-xs font-bold px-3 py-1 rounded-full border border-red-200">LIVE MARKET</span>;
            case 'paper': return <span className="bg-orange-100 text-orange-700 text-xs font-bold px-3 py-1 rounded-full border border-orange-200">PAPER TRADNG</span>;
            case 'sim':
            default: return <span className="bg-blue-100 text-blue-700 text-xs font-bold px-3 py-1 rounded-full border border-blue-200">SIMULATION</span>;
        }
    };

    return (
        <div className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 fixed top-0 right-0 left-0 md:left-64 z-10">
            {/* Left: Search & Mode */}
            <div className="flex items-center gap-6">
                {getModeBadge()}
                <div className="relative hidden sm:block">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                        type="text"
                        placeholder="Search..."
                        className="pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-400 w-64 transition-all"
                    />
                </div>
            </div>

            {/* Right: Actions & Profile */}
            <div className="flex items-center gap-4">
                <button className="p-2 text-slate-500 hover:bg-slate-100 rounded-full transition-colors">
                    <Grid size={20} />
                </button>

                <div className="relative">
                    <button
                        onClick={toggleNotifications}
                        className={`p-2 rounded-full transition-colors relative ${notificationsEnabled ? 'text-indigo-600 bg-indigo-50' : 'text-slate-500 hover:bg-slate-100'}`}
                    >
                        <Bell size={20} />
                        {notificationsEnabled && <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border border-white"></span>}
                    </button>
                    {showToast && (
                        <div className="absolute top-12 right-0 w-48 bg-slate-800 text-white text-xs py-2 px-3 rounded shadow-lg z-50 animate-in fade-in slide-in-from-top-1">
                            {notificationsEnabled ? 'Notifications Enabled' : 'Notifications Disabled'}
                        </div>
                    )}
                </div>

                <div className="h-8 w-px bg-slate-200 mx-2"></div>

                <Link to="/profile" className="flex items-center gap-3 hover:bg-slate-50 p-2 rounded-lg transition-colors group">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-medium text-slate-900">Alina Mclourd</p>
                        <p className="text-xs text-slate-500 group-hover:text-indigo-600 transition-colors">VP People Manager</p>
                    </div>
                    <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600">
                        <User size={20} />
                    </div>
                </Link>

                <button
                    onClick={handleLogout}
                    className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                    title="Sign Out"
                >
                    <LogOut size={20} />
                </button>
            </div>
        </div>
    );
};

export default TopBar;
