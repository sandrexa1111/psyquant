import React from 'react';
import { Home, PieChart, BarChart2, Folder, Settings, User, Menu, Brain, Target, Gauge, GitBranch, TrendingUp, Book } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
    const location = useLocation();

    // Helper to check active state
    const isActive = (path) => location.pathname === path;

    return (
        <div className="w-64 h-screen bg-white border-r border-slate-200 flex flex-col fixed left-0 top-0 z-10 hidden md:flex">
            {/* Logo Area */}
            <div className="h-16 flex items-center px-6 border-b border-slate-100">
                <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    Architect
                </span>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto py-4">
                <div className="px-4 mb-2">
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Menu</p>
                    <ul className="space-y-1">
                        <li>
                            <Link to="/" className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${isActive('/')
                                ? 'bg-blue-50/50 text-blue-600'
                                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                }`}>
                                <Home size={18} />
                                Dashboards
                            </Link>
                        </li>
                        <li>
                            <Link to="/analytics" className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${isActive('/analytics')
                                ? 'bg-blue-50/50 text-blue-600'
                                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                }`}>
                                <BarChart2 size={18} />
                                Analytics
                            </Link>
                        </li>
                        <li>
                            <Link to="/market" className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${isActive('/market')
                                ? 'bg-blue-50/50 text-blue-600'
                                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                }`}>
                                <Folder size={18} />
                                News & Market
                            </Link>
                        </li>
                        <li>
                            <Link to="/trade" className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${isActive('/trade')
                                ? 'bg-blue-50/50 text-blue-600'
                                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                }`}>
                                <PieChart size={18} />
                                Active Trader
                            </Link>
                        </li>
                    </ul>
                </div>

                {/* Behavior Intelligence Section */}
                <div className="px-4 mb-2 mt-4">
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">AI Intelligence</p>
                    <ul className="space-y-1">
                        <li>
                            <Link to="/psychology" className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${isActive('/psychology')
                                ? 'bg-indigo-50/50 text-indigo-600'
                                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                }`}>
                                <Brain size={18} />
                                Psychology Center
                            </Link>
                        </li>
                        <li>
                            <Link to="/risk-meter" className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${isActive('/risk-meter')
                                ? 'bg-indigo-50/50 text-indigo-600'
                                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                }`}>
                                <Gauge size={18} />
                                Risk Meter
                            </Link>
                        </li>
                        <li>
                            <Link to="/strategy-dna" className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${isActive('/strategy-dna')
                                ? 'bg-indigo-50/50 text-indigo-600'
                                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                }`}>
                                <Target size={18} />
                                Strategy DNA
                            </Link>
                        </li>
                        <li>
                            <Link to="/behavior" className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${isActive('/behavior')
                                ? 'bg-indigo-50/50 text-indigo-600'
                                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                }`}>
                                <GitBranch size={18} />
                                Behavior Graph
                            </Link>
                        </li>
                        <li>
                            <Link to="/evolution" className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${isActive('/evolution')
                                ? 'bg-indigo-50/50 text-indigo-600'
                                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                }`}>
                                <TrendingUp size={18} />
                                Evolution
                            </Link>
                        </li>
                        <li>
                            <Link to="/journal" className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${isActive('/journal')
                                ? 'bg-indigo-50/50 text-indigo-600'
                                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                }`}>
                                <Book size={18} />
                                Reflection Journal
                            </Link>
                        </li>
                    </ul>
                </div>
            </nav>


            {/* Bottom Section */}
            <div className="p-4 border-t border-slate-100">
                <Link to="/settings" className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg w-full transition-colors ${isActive('/settings')
                    ? 'bg-blue-50/50 text-blue-600'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    }`}>
                    <Settings size={18} />
                    Settings
                </Link>
            </div>
        </div>
    );
};

export default Sidebar;
